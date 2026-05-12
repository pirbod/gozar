# Gorz Local Run

Gorz is a Vite React app in `ts/apps/gorz-web`.

## Install

```bash
npm install
```

## Run

```bash
npm run dev:gorz
```

Vite prints the local URL. The app opens to the Sara conversation, with Safety mode enabled and the network confidence panel available on desktop.

## Build

```bash
npm run build --workspace gorz-web
```

## Test

```bash
npm run test --workspace gorz-web
```

The tests cover confidence classification, incident record redaction, mock encryption round trip, and delivery-state mapping by diagnostic scenario.

## Demo Checklist

1. Select a conversation.
2. Send a mock message.
3. Change the diagnostic scenario.
4. Confirm delivery state updates.
5. Open Network Confidence.
6. Open Safety Mode.
7. Open Incident Record and review the JSON.

## Limits

The app does not make external network requests, run live probes, or perform production cryptography. It is a local proof of concept only.
