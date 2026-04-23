use std::{net::SocketAddr, sync::Arc};

use anyhow::{Context, Result};
use quinn::{crypto::rustls::QuicClientConfig, ClientConfig, Endpoint, ServerConfig};
use rcgen::{generate_simple_self_signed, CertifiedKey};
use rustls::{
    client::danger::{HandshakeSignatureValid, ServerCertVerified, ServerCertVerifier},
    crypto::{ring::default_provider, verify_tls12_signature, verify_tls13_signature},
    DigitallySignedStruct, SignatureScheme,
};
use rustls_pki_types::{CertificateDer, PrivateKeyDer, PrivatePkcs8KeyDer, ServerName, UnixTime};
use serde::{de::DeserializeOwned, Serialize};
use tokio::io::{AsyncReadExt, AsyncWriteExt};

pub const DEV_SERVER_NAME: &str = "gozar.local";

pub fn make_server_endpoint(bind_addr: SocketAddr) -> Result<Endpoint> {
    let CertifiedKey { cert, key_pair } = generate_simple_self_signed(vec![
        "localhost".to_string(),
        DEV_SERVER_NAME.to_string(),
    ])?;
    let certificate: CertificateDer<'static> = cert.der().clone();
    let key = PrivateKeyDer::Pkcs8(PrivatePkcs8KeyDer::from(key_pair.serialize_der()));
    let server_config = ServerConfig::with_single_cert(vec![certificate], key)?;
    Endpoint::server(server_config, bind_addr).context("failed to bind quic server endpoint")
}

pub fn make_client_endpoint(bind_addr: SocketAddr) -> Result<Endpoint> {
    let mut endpoint =
        Endpoint::client(bind_addr).context("failed to bind quic client endpoint")?;
    let crypto = rustls::ClientConfig::builder()
        .dangerous()
        .with_custom_certificate_verifier(Arc::new(SkipServerVerification::new()))
        .with_no_client_auth();
    let client_config = ClientConfig::new(Arc::new(
        QuicClientConfig::try_from(crypto).context("failed to create quic client config")?,
    ));
    endpoint.set_default_client_config(client_config);
    Ok(endpoint)
}

pub async fn send_json_request<TReq, TResp>(
    remote_addr: SocketAddr,
    payload: &TReq,
) -> Result<TResp>
where
    TReq: Serialize,
    TResp: DeserializeOwned,
{
    let endpoint = make_client_endpoint("0.0.0.0:0".parse().expect("socket addr"))?;
    let connection = endpoint
        .connect(remote_addr, DEV_SERVER_NAME)
        .context("failed to create outgoing quic connection")?
        .await
        .context("quic handshake failed")?;
    let (mut send, mut recv) = connection
        .open_bi()
        .await
        .context("failed to open bidirectional stream")?;

    write_json(&mut send, payload).await?;
    send.finish().context("failed to finish quic send stream")?;
    let response = read_json(&mut recv).await?;

    connection.close(0u32.into(), b"done");
    endpoint.wait_idle().await;
    Ok(response)
}

pub async fn write_json<T: Serialize>(
    send: &mut quinn::SendStream,
    value: &T,
) -> Result<()> {
    let body = serde_json::to_vec(value).context("failed to serialize quic payload")?;
    let frame_len = (body.len() as u32).to_be_bytes();
    send.write_all(&frame_len)
        .await
        .context("failed to write frame length")?;
    send.write_all(&body)
        .await
        .context("failed to write frame body")?;
    Ok(())
}

pub async fn read_json<T: DeserializeOwned>(recv: &mut quinn::RecvStream) -> Result<T> {
    let mut frame_len = [0_u8; 4];
    recv.read_exact(&mut frame_len)
        .await
        .context("failed to read frame length")?;
    let frame_len = u32::from_be_bytes(frame_len);
    let mut body = vec![0_u8; frame_len as usize];
    recv.read_exact(&mut body)
        .await
        .context("failed to read frame body")?;
    serde_json::from_slice(&body).context("failed to decode quic payload")
}

#[derive(Debug)]
struct SkipServerVerification {
    provider: Arc<rustls::crypto::CryptoProvider>,
}

impl SkipServerVerification {
    fn new() -> Self {
        Self {
            provider: Arc::new(default_provider()),
        }
    }
}

impl ServerCertVerifier for SkipServerVerification {
    fn verify_server_cert(
        &self,
        _end_entity: &CertificateDer<'_>,
        _intermediates: &[CertificateDer<'_>],
        _server_name: &ServerName<'_>,
        _ocsp_response: &[u8],
        _now: UnixTime,
    ) -> std::result::Result<ServerCertVerified, rustls::Error> {
        Ok(ServerCertVerified::assertion())
    }

    fn verify_tls12_signature(
        &self,
        message: &[u8],
        cert: &CertificateDer<'_>,
        dss: &DigitallySignedStruct,
    ) -> std::result::Result<HandshakeSignatureValid, rustls::Error> {
        verify_tls12_signature(
            message,
            cert,
            dss,
            &self.provider.signature_verification_algorithms,
        )
    }

    fn verify_tls13_signature(
        &self,
        message: &[u8],
        cert: &CertificateDer<'_>,
        dss: &DigitallySignedStruct,
    ) -> std::result::Result<HandshakeSignatureValid, rustls::Error> {
        verify_tls13_signature(
            message,
            cert,
            dss,
            &self.provider.signature_verification_algorithms,
        )
    }

    fn supported_verify_schemes(&self) -> Vec<SignatureScheme> {
        self.provider
            .signature_verification_algorithms
            .supported_schemes()
    }
}
