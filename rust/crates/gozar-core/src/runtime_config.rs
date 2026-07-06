use std::env;

use anyhow::{anyhow, Result};

pub const DEMO_CONTROL_SECRET: &str = "gozar-local-shared-secret";
pub const ALLOW_INSECURE_DEV_DEFAULTS_ENV: &str = "GOZAR_ALLOW_INSECURE_DEV_DEFAULTS";

pub fn control_secret_from_env() -> Result<String> {
    required_secret_from_env("GOZAR_CONTROL_SECRET", DEMO_CONTROL_SECRET)
}

pub fn required_secret_from_env(key: &str, demo_value: &str) -> Result<String> {
    let allow_insecure_dev_defaults = allow_insecure_dev_defaults();
    match env::var(key) {
        Ok(value) if !value.trim().is_empty() => {
            if value == demo_value && !allow_insecure_dev_defaults {
                return Err(anyhow!(
                    "{key} is set to the local demo value; use a real secret or set {ALLOW_INSECURE_DEV_DEFAULTS_ENV}=true for the local demo"
                ));
            }
            Ok(value)
        }
        _ if allow_insecure_dev_defaults => Ok(demo_value.to_string()),
        _ => Err(anyhow!(
            "{key} is required; set {key} or set {ALLOW_INSECURE_DEV_DEFAULTS_ENV}=true for the local demo"
        )),
    }
}

pub fn allow_insecure_dev_defaults() -> bool {
    env::var(ALLOW_INSECURE_DEV_DEFAULTS_ENV)
        .map(|value| matches!(value.as_str(), "true" | "1" | "yes"))
        .unwrap_or(false)
}

#[cfg(test)]
mod tests {
    use super::{required_secret_from_env, ALLOW_INSECURE_DEV_DEFAULTS_ENV, DEMO_CONTROL_SECRET};
    use std::env;
    use std::sync::{Mutex, OnceLock};

    fn env_lock() -> &'static Mutex<()> {
        static LOCK: OnceLock<Mutex<()>> = OnceLock::new();
        LOCK.get_or_init(|| Mutex::new(()))
    }

    #[test]
    fn rejects_missing_secret_by_default() {
        let _guard = env_lock().lock().expect("env lock");
        env::remove_var("GOZAR_TEST_SECRET");
        env::remove_var(ALLOW_INSECURE_DEV_DEFAULTS_ENV);

        let err = required_secret_from_env("GOZAR_TEST_SECRET", DEMO_CONTROL_SECRET)
            .expect_err("missing secret should fail");
        assert!(err.to_string().contains("GOZAR_TEST_SECRET is required"));
    }

    #[test]
    fn rejects_demo_secret_without_dev_flag() {
        let _guard = env_lock().lock().expect("env lock");
        env::set_var("GOZAR_TEST_SECRET", DEMO_CONTROL_SECRET);
        env::remove_var(ALLOW_INSECURE_DEV_DEFAULTS_ENV);

        let err = required_secret_from_env("GOZAR_TEST_SECRET", DEMO_CONTROL_SECRET)
            .expect_err("demo secret should fail");
        assert!(err.to_string().contains("local demo value"));
        env::remove_var("GOZAR_TEST_SECRET");
    }

    #[test]
    fn permits_demo_secret_with_dev_flag() {
        let _guard = env_lock().lock().expect("env lock");
        env::set_var("GOZAR_TEST_SECRET", DEMO_CONTROL_SECRET);
        env::set_var(ALLOW_INSECURE_DEV_DEFAULTS_ENV, "true");

        let secret = required_secret_from_env("GOZAR_TEST_SECRET", DEMO_CONTROL_SECRET)
            .expect("demo secret should be accepted in explicit dev mode");
        assert_eq!(secret, DEMO_CONTROL_SECRET);
        env::remove_var("GOZAR_TEST_SECRET");
        env::remove_var(ALLOW_INSECURE_DEV_DEFAULTS_ENV);
    }
}
