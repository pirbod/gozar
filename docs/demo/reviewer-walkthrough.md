# Reviewer Walkthrough

## 1. Safety boundary

Read README Safety Disclaimer.

## 2. Four-phase roadmap

Open `docs/product/four-phase-roadmap.md`.

## 3. Run readiness check

```bash
make production-readiness-check
```

Expected:

- Controlled release readiness: `PASS` or `PARTIAL`
- Production readiness: `READY`
- Production-ready for real use: `NO`

## 4. Android demo

Open `android/gorz` in Android Studio.

Run emulator.

Validate offline demo.

## 5. Route safety

Open Route Policy screen.

Confirm:

- Applied route: `10.77.0.0/24`

## 6. Evidence

Generate Evidence Package V2.

Confirm:

- Redaction summary
- Integrity checksum
- No raw sensitive identifiers

## 7. Platform layer

```bash
make terraform-check
make k8s-check
make observability-check
```

## 8. Detection layer

```bash
make detection-check
```

## 9. Incident summary

```bash
make incident-summary-demo
```

## 10. Final validation

Open `docs/vpn-product/phase-4-final-validation-report.md`.

## 11. Demo video

Open `docs/demo/demo-video-link.md`.

## 12. Final conclusion

Gozar/Gorz is a controlled local-first prototype release candidate, not a production VPN.
