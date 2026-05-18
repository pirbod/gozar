# Gorz Demo Script

1. Run `make gorz-demo`.
2. Open `http://localhost:5174`.
3. Create a demo identity named `Ari Local`.
4. Create a second demo identity named `Blair Demo`.
5. Create a local conversation.
6. Select `direct_ok` and send a message.
7. Review the high confidence score and evidence.
8. Select `degraded` and send a message.
9. Compare the lower mandatory and support scores.
10. Select `blocked` and send a message.
11. Generate an incident package from the blocked message.
12. Open Evidence and download the redacted JSON.
13. Open Safety and review the audit trail.
14. Enable emergency pause.
15. Return to Messenger and verify a new send is blocked.
16. Resume demo sends.

Expected URLs:

- Gorz Web: `http://localhost:5174`
- Gorz API: `http://localhost:8090/api/gorz/health`
- API Docs: `http://localhost:8090/docs`

