# Gorz Demo Walkthrough

1. Run `make gorz-demo`.
2. Open `http://localhost:5174`.
3. Create two local demo identities.
4. Create a local demo conversation.
5. Send a `direct_ok` message and review confirmed delivery evidence.
6. Send a `degraded` message and compare the lower confidence score.
7. Send a `blocked` message and inspect the bottleneck evidence.
8. Generate an incident package from the blocked message.
9. Open Evidence and download the redacted JSON.
10. Open Safety and review the audit trail.
11. Enable emergency pause and confirm a new send is blocked.
12. Resume demo sends.

