# CLAUDE.md - AI Assistant Guide for ISAO

## Project Overview

ISAO is a **Progressive Web App (PWA) timecard/attendance management system** (勤務管理タイムカード) built with vanilla HTML, CSS, and JavaScript. It enables shared team attendance tracking where multiple users/devices can record clock-in/clock-out times with automatic synchronization across all connected devices.

**Repository:** `kosshy130/isao`

## File Structure

```
/
├── index.html              # Main app - shared/multi-device timecard (v2.0, 1126 lines)
├── index.html.html         # Duplicate of the v1.0 single-device version
├── timecard_app (4).html   # Original single-device timecard app (v1.0, 789 lines)
└── CLAUDE.md               # This file
```

### File Descriptions

- **`index.html`** — The primary production file. Multi-device shared timecard with 30-second auto-sync, device tracking, 5 tabs (punch, history, report, employee management, admin). This is the active version.
- **`timecard_app (4).html`** — Earlier single-device version (v1.0). 4 tabs, local storage only, no sync capabilities.
- **`index.html.html`** — Appears to be a duplicate of the v1.0 file. Likely a backup.

## Tech Stack

| Category | Technology |
|----------|-----------|
| Language | JavaScript (ES6+), HTML5, CSS3 |
| Framework | None (vanilla JS) |
| Storage | Custom `window.storage` API with shared sync support |
| PWA | Web App Manifest (inline base64), standalone mode |
| Geolocation | Browser Geolocation API for GPS tracking on clock events |
| UI Locale | Japanese (`ja-JP`) |

## Architecture

This is a **single-file web application** with no build system, no package manager, and no external dependencies. All HTML, CSS, and JavaScript are contained within each `.html` file.

### Storage API

The app uses a proprietary `window.storage` API (provided by the hosting environment):

```javascript
// Read data (async)
await window.storage.get('key')           // local storage
await window.storage.get('key', true)     // shared/synced storage

// Write data (async)
await window.storage.set('key', value)           // local storage
await window.storage.set('key', value, true)     // shared/synced storage
```

**Storage keys used (shared):**
- `timecard_shared_users` — Array of user/employee objects
- `timecard_shared_records` — Array of clock-in/clock-out records
- `timecard_shared_settings` — App settings and metadata

**Local storage keys:**
- `timecard_device_id` — Unique device identifier (persisted in localStorage)

### Data Models

**User:**
```javascript
{
  id: 'user_<timestamp>',
  name: string,
  createdAt: ISO8601,
  createdBy: deviceId
}
```

**Record:**
```javascript
{
  id: 'record_<timestamp>',
  userId: string,
  userName: string,
  clockIn: ISO8601,
  clockOut: ISO8601 | null,
  location: { lat, lng, accuracy },
  deviceId: string,
  clockOutLocation: { lat, lng, accuracy },  // optional
  clockOutDeviceId: string                    // optional
}
```

### Key Functions (index.html)

| Function | Purpose |
|----------|---------|
| `init()` | Application initialization, loads data, starts sync |
| `syncData()` | Fetches latest data from shared storage |
| `saveData()` | Persists data to shared storage |
| `clockIn()` | Records a clock-in event with GPS location |
| `clockOut()` | Records a clock-out event with GPS location |
| `generateReport()` | Generates monthly work hour statistics |
| `exportData()` / `importData()` | Data backup and restore |
| `switchTab(tabName)` | Tab-based navigation controller |

### Sync Behavior

- Auto-sync every **30 seconds** via `setInterval`
- Saves on `visibilitychange` (page hidden) and `beforeunload`
- Sync status shown via transient notification (3-second fade)
- Silent sync mode to avoid disrupting the user

## Development Workflow

### Running the App

No build step required. Either:
1. Open `index.html` directly in a modern browser
2. Serve via any HTTP server for full PWA capabilities

### Making Changes

Since all code is in single HTML files:
1. Edit the relevant `.html` file directly
2. Reload the browser to test changes
3. The primary file to modify is `index.html`

### No Build/Lint/Test Commands

- No `package.json`, `Makefile`, or build configuration exists
- No linting or formatting tools are configured
- No automated test suite exists
- All testing is manual/browser-based

## Code Conventions

### Naming
- **Functions/variables:** camelCase (`syncData`, `clockIn`, `deviceId`)
- **Storage keys:** snake_case with prefix (`timecard_shared_users`)
- **CSS classes:** kebab-case (`sync-status`, `tab-container`, `btn-clock-in`)

### Patterns
- All code in `<script>` tags within the HTML file (no external JS files)
- All styles in `<style>` tags within the HTML file (no external CSS files)
- `async/await` for all storage operations
- Tab-based UI navigation using `classList` manipulation
- Array methods (`filter`, `map`, `sort`, `find`) for data manipulation
- Event-driven UI with `onclick` handlers

### UI/UX
- Purple/pink gradient theme (`#667eea` to `#764ba2`)
- Card-based layout with rounded corners (16px border-radius)
- Responsive, mobile-first design (max-width 600px container)
- Japanese language UI throughout
- Status indicators: green = working, red = off duty
- 3-second transient alert messages

## Important Notes for AI Assistants

1. **Single-file architecture** — Do not split the code into separate JS/CSS files unless explicitly requested. The self-contained design is intentional for deployment simplicity.

2. **Custom storage API** — `window.storage` is not a standard browser API. It's provided by the hosting environment. Do not replace it with `localStorage` or `IndexedDB`.

3. **Japanese locale** — All user-facing strings are in Japanese. Maintain this convention when adding or modifying UI text.

4. **No dependencies** — Do not introduce npm packages, CDN libraries, or external dependencies without explicit request.

5. **The v1.0 files are legacy** — Focus changes on `index.html` (the shared/v2.0 version) unless specifically asked to modify the older versions.

6. **GPS/Geolocation** — Clock-in and clock-out events capture the user's location. Handle geolocation failures gracefully (the app already falls back if location is unavailable).

7. **Data integrity** — Records and users are synced across devices. When modifying data operations, ensure changes are saved to shared storage (`shared: true` flag) to maintain sync.
