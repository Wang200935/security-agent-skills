# Finding API/CDN URLs by reading application source code

When docs and web searches fail to give a working URL for an internal API (e.g. firmware CDN, telemetry endpoint, update feed), the **last resort that always works** is to find the URL hardcoded in the official client app's source.

## The technique

1. **Identify the official client** that already talks to the mystery server.
   - For Flipper Zero firmware: `qFlipper` (the GUI app).
   - For VS Code extensions: `code` CLI / bundled extension host.
   - For npm packages: check `node_modules/<pkg>/dist/`.
   - For Android apps: decompile APK with jadx.

2. **Search GitHub for the client source**.
   ```
   curl -sL "https://api.github.com/repos/<org>/<client>/contents/<dir>"
   ```
   List all files recursively:
   ```
   curl -sL "https://api.github.com/repos/<org>/<client>/git/trees/<branch>?recursive=1"
   ```

3. **Grep for URL/host/domain keywords** in candidate source files:
   ```
   "flipperzero" | "directory.json" | "http" | "firmware"
   "url" | "endpoint" | "baseUrl" | "api.*\.com" | "cdn"
   ```
   Useful files are usually named: `*registry*.cpp`, `*updater*.cpp`, `*client*.js`, `*config*.yaml`, `*api*.py`.

4. **For compiled/minified JS** (e.g. webpack/vite bundles), grep for host patterns directly:
   ```
   grep -oE 'https?://[^"'\'']+\.(tgz|json|dfu|bin)' bundle.js
   ```
   The URL string will appear verbatim even after minification.

5. **Verify the URL works**:
   ```
   curl -sIL <url>   # HEAD — some servers return 405 for HEAD
   curl -sL  <url>   # GET — usually the real test
   ```
   Always use `-sL` (silent + follow redirects). Try both HEAD and GET — some CDNs allow GET but reject HEAD.

## Worked example — Flipper Zero firmware CDN

Goal: find the URL to download the latest official Flipper Zero firmware.

Steps:
1. Client: `flipperdevices/qFlipper` on GitHub.
2. `GET /repos/flipperdevices/qFlipper/contents/backend` → list files.
3. Grep `applicationbackend.cpp` for `FirmwareUpdateRegistry` constructor:
   ```
   m_firmwareUpdateRegistry(new FirmwareUpdateRegistry(
     "https://update.flipperzero.one/firmware/directory.json", this))
   ```
4. Fetch the directory:
   ```
   curl -sL https://update.flipperzero.one/firmware/directory.json
   ```
   Returns JSON listing channels (release / dev / rc) with version, timestamp, files[].
5. Parse for `target==f7 type==update_tgz` (for normal update) or `type==full_dfu` (for recovery).
6. Download those URLs.

## Pitfalls

- **`curl -I` / `curl -sIL` returns 405 for some CDNs** (e.g. `update.flipperzero.one`). Always retry with plain `curl -sL` (GET).
- **The CLI tool name might not match the GitHub repo name**. E.g. `qFlipper-cli` on macOS is the CLI from `flipperdevices/qFlipper` repo. The binary name capitalization matters.
- **URL might be parameterized in source** — look for `QStringLiteral("...")` wrapping or `.arg(version)` if the URL is built from a template.
- **Source might point to localhost or staging** — verify the URL is the production one (look for `-prod`, `-release`, `https://` vs `http://`, or comments).
- **The URL might be split across multiple files** — config + client + helper. Search broadly.

## When this technique applies

- Firmware update URLs
- Telemetry / crash report endpoints
- License server URLs
- OAuth/OIDC discovery endpoints
- App update feeds (different from firmware feeds — see `flipper-zero-backupup` pitfall about confusing qFlipper APP URL with firmware URL)

## When it does NOT apply

- Pure local file operations (no network)
- Cryptographic operations with no remote counterpart
- When the source isn't published (closed-source commercial software without SDK)