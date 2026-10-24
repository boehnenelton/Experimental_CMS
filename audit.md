# EXPERIMENTAL CMS — FULL SECURITY AUDIT & REMEDIATION GUIDE
**Scope:** Experimental_CMS v3.11.0 (PKG29) + Lib_PY canonical library comparison
**Auditor:** Qwen3.8
**Date:** 2026-09-25

---

## EXECUTIVE SUMMARY

The Experimental CMS is a Flask-based admin dashboard + static-site builder backed by BEJSON/MFDB multi-file databases. The codebase shows evidence of prior security hardening (path traversal guards, autoescape, secure_filename). However, **three critical/high-severity authentication and network-exposure issues remain unremediated**, and the library set inside the CMS has **diverged from the canonical Lib_PY** in ways that require attention.

**Overall risk rating: HIGH**

| Severity | Count | Summary |
|---|---|---|
| CRITICAL | 2 | No authentication; debug-mode RCE potential |
| HIGH | 3 | Preview server LAN exposure; no CSRF; XSS via `|safe` |
| MEDIUM | 4 | Legacy CMS lib folder; extra HTML libs; no rate limiting; weak secret |
| LOW | 3 | Missing new canonical families; stale doc references; dead code |

---

## SECTION 1 — SECURITY AUDIT FINDINGS

---

### CRITICAL-1 — No authentication on any route

**File:** `EXPCMS.py`
**Location:** All `@app.route(...)` decorators

Every route in the Flask application is accessible without any form of authentication. There is no login, no session token, no API key check, no HTTP Basic Auth. Any user who can reach the port can create, edit, delete pages, upload files, trigger builds, restore backups, and factory-reset the entire database.

The prior audit acknowledged this ("H1: app.run(host='0.0.0.0', debug=True) … no authentication") and fixed the binding and debug mode, but **authentication itself was never added**.

**Risk:** Full CMS compromise by any network-reachable client.

---

### CRITICAL-2 — Debug mode RCE potential via env var

**File:** `EXPCMS.py`, lines near `app.run(...)`

```python
_run_debug_env = os.environ.get("EXPCMS_DEBUG")
if _run_debug_env is not None:
    _run_debug = _run_debug_env.strip().lower() in ("1", "true", "yes")
else:
    _run_debug = _run_host in ("127.0.0.1", "localhost", "::1")
```

If `EXPCMS_DEBUG` is set to `true` while `EXPCMS_HOST` is set to a non-loopback address, the Werkzeug interactive debugger is exposed. This is a known RCE vector. The code prints a warning but **does not block it**.

**Risk:** Remote code execution if both env vars are misconfigured.

---

### HIGH-1 — Preview server binds to 0.0.0.0 by default

**File:** `EXPCMS.py`, `srv_start()`

```python
_preview_host = os.environ.get("EXPCMS_PREVIEW_HOST", "")
```

When `EXPCMS_PREVIEW_HOST` is not set, the preview server binds to `""` which resolves to `0.0.0.0`. The code prints a warning when overridden to non-loopback, but the default itself is all-interfaces.

**Risk:** The built static site and hosted apps are exposed to the LAN without authentication.

---

### HIGH-2 — No CSRF protection

**File:** `EXPCMS.py`

The application uses Flask's session-based flash messages but does not use `flask-wtf` or any CSRF protection middleware. State-changing operations (page create, delete, backup restore, factory reset) are triggered via form POST without CSRF tokens.

The prior audit noted this ("M4: all destructive routes converted from GET links to POST-only") but CSRF tokens were never added.

**Risk:** Cross-site request forgery against any authenticated browser session (if auth were added).

---

### HIGH-3 — XSS via `|safe` rendering of `html_body`

**File:** `EXPCMS_Builder.py`, page rendering templates

In the `Article_Skeleton.html` template and the builder's `_build_page()` method, user-authored page body HTML is rendered with Jinja2's `|safe` filter:

```
{{ html_body | safe }}
```

While the CMS sanitizes HTML imports via BeautifulSoup (`_sanitize_imported_html`), **direct HTML editing in the page editor can inject arbitrary scripts**. There is no server-side sanitization of the `html_body` field on save.

**Risk:** Stored XSS on any built page if an attacker gains CMS access.

---

### MEDIUM-1 — Legacy `Lib_PY/CMS/` folder contains unused code

**File:** `Lib_PY/CMS/`

The CMS project contains a `Lib_PY/CMS/` folder with three files:
- `lib_bejson_CMS_cms_config.py` (v2.0.1)
- `lib_bejson_CMS_cms_core.py` (v2.1.3)
- `lib_bejson_CMS_cms_mfdb.py` (v2.1.6)

The active CMS code imports from `Lib_PY/ExpCMS/`, not `Lib_PY/CMS/`. The `Lib_PY/CMS/` folder is **dead code** that is never imported by any route or builder.

**Risk:** Dead code increases attack surface and maintenance burden. A future developer might accidentally import from it.

---

### MEDIUM-2 — Extra HTML diagram libraries not in canonical Lib_PY

**File:** `Lib_PY/HTML/` in CMS

The CMS's `Lib_PY/HTML/` folder contains three diagram-related libraries that do **not exist** in the canonical `Lib_PY/HTML/`:

- `lib_bejson_HTML_bejson_diagram_core.py`
- `lib_bejson_HTML_bejson_diagram_html.py`
- `lib_bejson_HTML_bejson_diagram_validator.py`

These libraries are present in the CMS but absent from the canonical library set. This means:
1. The CMS has diverged from canonical.
2. These libraries are not tracked in the canonical library manifest.
3. A library sync from canonical would silently delete them.

**Risk:** Library divergence; potential for silent breakage on sync.

---

### MEDIUM-3 — No rate limiting on any endpoint

**File:** `EXPCMS.py`

No rate limiting is applied to any endpoint. File uploads, page saves, backup restores, and build triggers can be called in rapid succession without throttling.

**Risk:** Denial of service; resource exhaustion via rapid backup/restore cycles.

---

### MEDIUM-4 — Weak secret key fallback

**File:** `EXPCMS.py`

```python
app.secret_key = os.environ.get("EXPCMS_SECRET_KEY") or uuid.uuid4().hex
```

If `EXPCMS_SECRET_KEY` is not set, a random per-process key is generated. This means session cookies become invalid across process restarts. While this is safer than a hardcoded key, it means sessions are not persistent, which is a usability issue that might lead operators to set a weak key.

**Risk:** Low direct security risk, but poor operational security posture.

---

### LOW-1 — New canonical families absent from CMS

The canonical `Lib_PY` contains several families that are **not present** in the CMS:

- `AI/` — AI integration libraries (Gemini, Grok, HuggingFace, OpenRouter)
- `Core_Nesting/` — nesting extension
- `Core_Extension/` — new family (`lib_bejson_markdown`)
- `MD/` — markdown library
- `System/` — system utilities
- `Utility/` — utility libraries

This is expected since these are new additions to the canonical library set. However, the CMS should be aware of them.

**Risk:** Low. Expected divergence.

---

### LOW-2 — Stale documentation references

**File:** `docs/usage-guide.md`, `docs/architecture.md`

Some documentation references `Lib_PY/CMS/` paths that are no longer used. The architecture doc correctly describes the `Lib_PY/ExpCMS/` structure but some older sections reference the legacy CMS family.

**Risk:** Low. Confusing for developers.

---

### LOW-3 — Dead code in `lib_bejson_HTML_html_firebase.py`

**File:** `Lib_PY/HTML/lib_bejson_HTML_html_firebase.py`

This file contains hardcoded Firebase configuration with a comment saying "SECURITY: Hardcoded credentials removed." However, the file still contains the structure for Firebase config, and the `validate_firebase_config` function raises on missing keys. This file appears to be a stub or dead code since the CMS does not use Firebase.

**Risk:** Low. Dead code.

---

## SECTION 2 — LIBRARY ASSESSMENT: CMS vs CANONICAL Lib_PY

---

### Core Libraries

| Library | CMS Version | Canonical Version | Status |
|---|---|---|---|
| `lib_bejson_Core_bejson_core.py` | 2.0.5 | 2.0.5 | ✅ In sync |
| `lib_bejson_Core_bejson_env.py` | 2.2.0 | 2.2.0 | ✅ In sync |
| `lib_bejson_Core_bejson_errors.py` | 2.4.0 | 2.4.0 | ✅ In sync |
| `lib_bejson_Core_bejson_validator.py` | 2.2.1 | 2.2.1 | ✅ In sync |
| `lib_bejson_Core_bejson_path_guard.py` | 1.1.0 | 1.1.0 | ✅ In sync |
| `lib_bejson_Core_bejson_chunking.py` | 1.9.0 | 1.9.0 | ✅ In sync |
| `lib_bejson_Core_bejson_parse.py` | 2.1.0 | 2.1.0 | ✅ In sync |
| `lib_bejson_Core_bejson_provider.py` | 2.1.1 | 2.1.1 | ✅ In sync |
| `lib_bejson_Core_bejson_schema.py` | 2.3.0 | 2.3.0 | ✅ In sync |
| `lib_bejson_Core_bejson_state_management.py` | 2.0.1 | 2.0.1 | ✅ In sync |
| `lib_bejson_Core_bejson_static_backend.py` | 2.1.0 | 2.1.0 | ✅ In sync |
| `lib_bejson_Core_bejson_list_validator.py` | 1.3.1 | 1.3.1 | ✅ In sync |
| `lib_bejson_Core_bejson_104db_parser.py` | 1.0.0 | 1.0.0 | ✅ In sync |
| `lib_bejson_Core_mfdb_core.py` | 2.3.0 | 2.3.0 | ✅ In sync |
| `lib_bejson_Core_mfdb_validator.py` | 2.2.0 | 2.2.0 | ✅ In sync |

**Core library assessment:** All Core libraries are in sync with canonical. No outdated Core libraries detected.

---

### HTML Libraries

| Library | CMS Version | Canonical Version | Status |
|---|---|---|---|
| `lib_bejson_HTML_bejson_html3_component_css.py` | 3.0.4 | 3.0.4 | ✅ In sync |
| `lib_bejson_HTML_bejson_html3_skeletons.py` | 3.0.2 | 3.0.2 | ✅ In sync |
| `lib_bejson_HTML_bejson_to_html.py` | 3.0.0 | 3.0.0 | ✅ In sync |
| `lib_bejson_HTML_bejson_validator_diagram.py` | 3.0.0 | 3.0.0 | ✅ In sync |
| `lib_bejson_HTML_bejson_errors.py` | 1.0.0 | 1.0.0 | ✅ In sync |
| `lib_bejson_HTML_html3_animations.py` | 3.0.0 | 3.0.0 | ✅ In sync |
| `lib_bejson_HTML_html3_app_layout.py` | 3.0.1 | 3.0.1 | ✅ In sync |
| `lib_bejson_HTML_html3_bejson_renderer.py` | 3.1.2 | 3.1.2 | ✅ In sync |
| `lib_bejson_HTML_html3_body.py` | 3.0.0 | 3.0.0 | ✅ In sync |
| `lib_bejson_HTML_html3_charts.py` | 3.0.0 | 3.0.0 | ✅ In sync |
| `lib_bejson_HTML_html3_clipboard.py` | 3.0.0 | 3.0.0 | ✅ In sync |
| `lib_bejson_HTML_html3_dev_tools.py` | 3.0.0 | 3.0.0 | ✅ In sync |
| `lib_bejson_HTML_html3_error_pages.py` | 3.0.0 | 3.0.0 | ✅ In sync |
| `lib_bejson_HTML_html3_feed_templates.py` | 3.0.0 | 3.0.0 | ✅ In sync |
| `lib_bejson_HTML_html3_flask.py` | 3.1.0 | 3.1.0 | ✅ In sync |
| `lib_bejson_HTML_html3_forms.py` | 3.0.0 | 3.0.0 | ✅ In sync |
| `lib_bejson_HTML_html3_list_renderer.py` | 2.1.2 | 2.1.2 | ✅ In sync |
| `lib_bejson_HTML_html3_metrics.py` | 3.0.0 | 3.0.0 | ✅ In sync |
| `lib_bejson_HTML_html3_page_templates.py` | 3.0.0 | 3.0.0 | ✅ In sync |
| `lib_bejson_HTML_html3_pagination.py` | 3.0.0 | 3.0.0 | ✅ In sync |
| `lib_bejson_HTML_html3_showcase.py` | 3.1.1 | 3.1.1 | ✅ In sync |
| `lib_bejson_HTML_html3_sidemenu.py` | 3.0.0 | 3.0.0 | ✅ In sync |
| `lib_bejson_HTML_html3_tables.py` | 3.1.0 | 3.1.0 | ✅ In sync |
| `lib_bejson_HTML_html3_text.py` | 3.0.0 | 3.0.0 | ✅ In sync |
| `lib_bejson_HTML_html3_version.py` | 3.0.0 | 3.0.0 | ✅ In sync |
| `lib_bejson_HTML_html3_widgets.py` | 3.0.1 | 3.0.1 | ✅ In sync |
| `lib_bejson_HTML_html_firebase.py` | 2.0.1 | 2.0.1 | ✅ In sync |
| `lib_bejson_HTML_bejson_diagram_core.py` | 1.2.0 | **ABSENT** | ⚠️ CMS-only |
| `lib_bejson_HTML_bejson_diagram_html.py` | 1.0.0 | **ABSENT** | ⚠️ CMS-only |
| `lib_bejson_HTML_bejson_diagram_validator.py` | 1.0.1 | **ABSENT** | ⚠️ CMS-only |

**HTML library assessment:** All shared HTML libraries are in sync. However, **three diagram libraries exist only in the CMS and are absent from canonical**. These must be either promoted to canonical or removed from the CMS.

---

### ExpCMS Libraries (CMS-specific, not in canonical)

| Library | Version | Status |
|---|---|---|
| `lib_bejson_ExpCMS_cms_mfdb.py` | 2.5.1 | CMS-specific, expected |
| `lib_bejson_ExpCMS_mfdb_chunker_v6.py` | 6.2.0 | CMS-specific, expected |
| `lib_bejson_ExpCMS_chunker_wrapper.py` | 1.0.1 | CMS-specific, expected |
| `lib_bejson_ExpCMS_widgets.py` | 1.1.0 | CMS-specific, expected |

**ExpCMS library assessment:** These are CMS-specific and expected to be absent from canonical. No issues detected.

---

### CMS Legacy Libraries (present in CMS, absent from canonical)

| Library | Version | Status |
|---|---|---|
| `lib_bejson_CMS_cms_config.py` | 2.0.1 | ⚠️ Dead code, not imported |
| `lib_bejson_CMS_cms_core.py` | 2.1.3 | ⚠️ Dead code, not imported |
| `lib_bejson_CMS_cms_mfdb.py` | 2.1.6 | ⚠️ Dead code, not imported |

**CMS legacy library assessment:** The `Lib_PY/CMS/` folder contains three files that are **never imported** by any route, builder, or library in the active CMS. This is dead code that should be removed.

---

### New Canonical Families Absent from CMS

| Family | Libraries | Status |
|---|---|---|
| `AI/` | bejson_gemini, bejson_grok, bejson_huggingface, bejson_openrouter, etc. | Not in CMS (expected) |
| `Core_Nesting/` | lib_bejson_CoreNesting_bejson_core_nesting.py | Not in CMS (expected) |
| `Core_Extension/` | lib_bejson_markdown (md_indexer, md_ops, md_db, md_errors) | Not in CMS (expected) |
| `MD/` | lib_bejson_MD_md_indexer, md_ops, md_db, md_errors | Not in CMS (expected) |
| `System/` | lib_bejson_System_av_manager, be_core, bejson_errors | Not in CMS (expected) |
| `Utility/` | lib_bejson_Utility_bejson_utility, bejson_errors | Not in CMS (expected) |

**New families assessment:** These are new additions to the canonical library set. Their absence from the CMS is expected but should be documented.

---

## SECTION 3 — REMEDIATION GUIDE

---

### PRIORITY 1 — CRITICAL (Remediate immediately)

---

#### R-1.1 — Add authentication middleware

**Target:** `EXPCMS.py`
**Action:** Add authentication to all routes.

**Option A (recommended for internal tools):** HTTP Basic Auth with bcrypt-hashed credentials.

```python
import bcrypt
from functools import wraps

AUTH_USERS = {
    "admin": bcrypt.hashpw(b"CHANGE_ME", bcrypt.gensalt()).decode()
}

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return Response("Authentication required", 401,
                           {"WWW-Authenticate": 'Basic realm="ExpCMS"'})
        return f(*args, **kwargs)
    return decorated

def check_auth(username, password):
    if username not in AUTH_USERS:
        return False
    return bcrypt.checkpw(password.encode(), AUTH_USERS[username].encode())

# Apply to all routes
app.before_request(lambda: require_auth(lambda: None)())
```

**Option B (for production):** Flask-Login with session-based auth.

**Verification:** All routes return 401 without credentials; return 200 with valid credentials.

---

#### R-1.2 — Hard-block debug mode on non-loopback

**Target:** `EXPCMS.py`, near `app.run(...)`
**Action:** Hard-block debug mode when host is non-loopback.

```python
_run_host = os.environ.get("EXPCMS_HOST", "127.0.0.1")
_run_debug = os.environ.get("EXPCMS_DEBUG", "").strip().lower() in ("1", "true", "yes")

if _run_host not in ("127.0.0.1", "localhost", "::1") and _run_debug:
    raise RuntimeError(
        "EXPCMS_DEBUG=1 with non-loopback EXPCMS_HOST is BLOCKED. "
        "The Werkzeug debugger exposes arbitrary code execution to the network. "
        "Set EXPCMS_HOST to 127.0.0.1 or unset EXPCMS_DEBUG."
    )

app.run(host=_run_host, port=_run_port, debug=_run_debug)
```

**Verification:** Setting `EXPCMS_DEBUG=1` with `EXPCMS_HOST=0.0.0.0` raises RuntimeError.

---

### PRIORITY 2 — HIGH (Remediate within 1 week)

---

#### R-2.1 — Bind preview server to loopback by default

**Target:** `EXPCMS.py`, `srv_start()`
**Action:** Change default bind from `""` to `"127.0.0.1"`.

```python
_preview_host = os.environ.get("EXPCMS_PREVIEW_HOST", "127.0.0.1")
```

**Verification:** Preview server binds to 127.0.0.1 by default.

---

#### R-2.2 — Add CSRF protection

**Target:** `EXPCMS.py`
**Action:** Add Flask-WTF CSRF protection.

```python
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)

# In app config
app.config["WTF_CSRF_TIME_LIMIT"] = None  # or a reasonable TTL
```

All form POSTs must include `{{ csrf_token() }}` in templates.

**Verification:** POST without CSRF token returns 400.

---

#### R-2.3 — Sanitize `html_body` on save

**Target:** `EXPCMS.py`, `save_page()`
**Action:** Sanitize `html_body` before saving, or add a content-security-policy header to built pages.

**Option A (recommended):** Sanitize on save using the existing `_sanitize_imported_html` logic from `lib_bejson_ExpCMS_cms_mfdb.py`.

```python
from lib_bejson_ExpCMS_cms_mfdb import MFDB_CMS_Manager

# In save_page(), before saving:
html_body = MFDB_CMS_Manager._sanitize_imported_html(html_body)
```

**Option B:** Add CSP headers to built pages to prevent inline script execution.

**Verification:** A page saved with `<script>alert(1)</script>` in html_body does not execute the script on the built page.

---

### PRIORITY 3 — MEDIUM (Remediate within 1 month)

---

#### R-3.1 — Remove `Lib_PY/CMS/` folder

**Target:** `Lib_PY/CMS/`
**Action:** Delete the entire `Lib_PY/CMS/` folder.

**Verification:** No imports reference `Lib_PY/CMS/`. Application runs without it.

---

#### R-3.2 — Resolve HTML diagram library divergence

**Target:** `Lib_PY/HTML/` in CMS
**Action:** Either:
- **Option A:** Promote the three diagram libraries to canonical `Lib_PY/HTML/`.
- **Option B:** Remove them from the CMS if they are unused.

**Verification:** Library set is consistent between CMS and canonical.

---

#### R-3.3 — Add rate limiting

**Target:** `EXPCMS.py`
**Action:** Add Flask-Limiter rate limiting.

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["100 per hour"],
    storage_uri="memory://",
)

# Apply stricter limits to sensitive endpoints
@app.route("/backup/create", methods=["POST"])
@limiter.limit("5 per hour")
def backup_create():
    ...
```

**Verification:** Rapid backup/restore calls return 429.

---

#### R-3.4 — Document secret key requirement

**Target:** `docs/usage-guide.md`
**Action:** Add a section documenting the requirement to set `EXPCMS_SECRET_KEY` in production.

**Verification:** Documentation includes the requirement.

---

### PRIORITY 4 — LOW (Remediate within 1 quarter)

---

#### R-4.1 — Document new canonical families

**Target:** `docs/architecture.md`
**Action:** Add a section documenting the new canonical library families (AI, Core_Nesting, Core_Extension, MD, System, Utility) and their absence from the CMS.

**Verification:** Documentation includes the new families.

---

#### R-4.2 — Update stale documentation references

**Target:** `docs/usage-guide.md`, `docs/architecture.md`
**Action:** Update all references to `Lib_PY/CMS/` to reference `Lib_PY/ExpCMS/`.

**Verification:** No documentation references `Lib_PY/CMS/`.

---

#### R-4.3 — Remove dead Firebase code

**Target:** `Lib_PY/HTML/lib_bejson_HTML_html_firebase.py`
**Action:** Remove the file if Firebase is not used, or document its purpose.

**Verification:** No references to Firebase in the codebase.

---

## SECTION 4 — LIBRARY SYNC CHECKLIST

Use this checklist to verify library sync after any library update:

| Check | Status |
|---|---|
| All Core library versions match canonical | ⬜ |
| All HTML library versions match canonical | ⬜ |
| No CMS-only HTML libraries without canonical tracking | ⬜ |
| `Lib_PY/CMS/` folder removed | ⬜ |
| No imports reference `Lib_PY/CMS/` | ⬜ |
| ExpCMS libraries present and current | ⬜ |
| New canonical families documented | ⬜ |
| No stale documentation references | ⬜ |

---

## APPENDIX — FINDINGS CROSS-REFERENCE

| Finding | Severity | File | Line(s) | Prior Audit Ref |
|---|---|---|---|---|
| CRITICAL-1: No auth | CRITICAL | EXPCMS.py | All routes | H1 (partial) |
| CRITICAL-2: Debug RCE | CRITICAL | EXPCMS.py | ~app.run | H1 (partial) |
| HIGH-1: Preview 0.0.0.0 | HIGH | EXPCMS.py | srv_start | NEW |
| HIGH-2: No CSRF | HIGH | EXPCMS.py | All POST routes | M4 (partial) |
| HIGH-3: XSS via |safe | HIGH | EXPCMS_Builder.py | Templates | NEW |
| MEDIUM-1: Legacy CMS folder | MEDIUM | Lib_PY/CMS/ | All | NEW |
| MEDIUM-2: Extra HTML libs | MEDIUM | Lib_PY/HTML/ | Diagram libs | NEW |
| MEDIUM-3: No rate limiting | MEDIUM | EXPCMS.py | All routes | NEW |
| MEDIUM-4: Weak secret | MEDIUM | EXPCMS.py | Secret key | L1 (partial) |
| LOW-1: New families absent | LOW | Lib_PY/ | Multiple | NEW |
| LOW-2: Stale docs | LOW | docs/ | Multiple | NEW |
| LOW-3: Dead Firebase code | LOW | Lib_PY/HTML/ | html_firebase | NEW |

---

*End of audit. All findings are based on static analysis of the provided BEJSON chunked files. No runtime testing was performed.*