# Homebrew Install For Gorz

Gorz can be distributed through a third-party Homebrew tap as a small CLI launcher. The formula
installs `gorz`; the launcher manages a local Gozar checkout under `~/.gorz/gozar` and starts the
local Docker Compose prototype.

Gorz is local-first, demo-only, not production secure, and not for real sensitive communication.

## Create The Tap Repository

Create a GitHub repository:

```text
pirbod/homebrew-tap
```

Use this directory structure:

```text
homebrew-tap/
`- Formula/
   `- gorz.rb
```

Homebrew will install the formula as `pirbod/tap/gorz`.

## Create A Gozar Release

From the main Gozar repository:

```bash
git tag v0.1.0
git push origin main --tags
```

Download the release tarball and compute its SHA-256 checksum:

```bash
curl -L -o gozar-v0.1.0.tar.gz https://github.com/pirbod/gozar/archive/refs/tags/v0.1.0.tar.gz
shasum -a 256 gozar-v0.1.0.tar.gz
```

## Publish The Formula

Copy the formula template from the Gozar repository:

```bash
cp packaging/homebrew/Formula/gorz.rb ../homebrew-tap/Formula/gorz.rb
```

In `homebrew-tap/Formula/gorz.rb`, replace:

```text
REPLACE_WITH_RELEASE_TARBALL_SHA256
```

with the SHA-256 checksum from `shasum`.

Then push the tap:

```bash
cd ../homebrew-tap
git add Formula/gorz.rb
git commit -m "Add gorz formula"
git push origin main
```

## Test Install

```bash
brew tap pirbod/tap
brew install gorz
gorz doctor
gorz demo
```

Direct install also works:

```bash
brew install pirbod/tap/gorz
```

After `gorz demo` starts the local stack:

```text
Web:      http://localhost:5174
API:      http://localhost:8090/api/gorz/health
API docs: http://localhost:8090/docs
```

## Upgrade

```bash
brew update
brew upgrade gorz
```

## Troubleshooting

If Docker is not running, start Docker Desktop or Docker Engine and run:

```bash
gorz doctor
```

If the Docker Compose plugin is missing, install Docker Compose v2. The launcher uses
`docker compose`, not legacy `docker-compose`.

If port `5174` is already used, stop the other local process or change the Gorz Docker Compose
configuration before running `gorz demo`.

If port `8090` is already used, stop the other local process or change the Gorz Docker Compose
configuration before running `gorz demo`.

If the checkout at `~/.gorz/gozar` is stale or broken, force a fresh checkout:

```bash
rm -rf ~/.gorz/gozar
gorz demo
```

## Safety

Gorz is a local-first demo launcher for the local prototype. It is not a production secure
messenger, not a circumvention tool, and not for real sensitive communication.
