# Experimental_CMS: Dynamic Component & Sandbox Content Engine

[![BEJSON Specification](https://img.shields.io/badge/BEJSON-104a-red.svg)](https://boehnenelton2024.pages.dev)
[![Ecosystem](https://img.shields.io/badge/Ecosystem-ExpCMS-black.svg)](https://github.com/boehnenelton)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)](https://python.org)

**Author:** Elton Boehnen  
**Email:** boehnenelton2024@gmail.com  
**Website:** [boehnenelton2024.pages.dev](https://boehnenelton2024.pages.dev)  
**GitHub:** [github.com/boehnenelton](https://github.com/boehnenelton)  
**Project Version:** 3.5.0  
**Package Version:** 19  
**Date:** 2026-07-29  
**RELATIONAL_ID:** `expcms-readme-20260729-eb-v350-pkg19-uuid01`

---

## 1. Executive Summary & Architecture Isolation

`Experimental_CMS` (`ExpCMS`) is a dedicated sandbox research and development Content Management System designed to test experimental layout engines, component builders, and static publishing pipelines in isolation from production environments.

To protect production installations (such as `BEJSON_CMS`), `Experimental_CMS` enforces strict **Library Boundary Isolation**. It operates exclusively against its own private library layer located in `Lib_EXPCMS/`. This ensures that bleeding-edge component testing, dynamic schema adjustments, or experimental web interface features never leak into production code or destabilize live production sites.

---

## 2. System Components & File Anatomy

```
Experimental_CMS/
├── .bejson_project.json           # Audit trail ledger and version registry
├── EXPCMS.py                      # Main Flask web app entry point
├── EXPCMS_Builder.py              # Command-line static site & component builder
├── LICENSE                        # MIT License documentation
├── README.md                      # Extensive technical specification & manual
├── requirements.txt               # Python package dependencies
├── Components/                    # Modular UI component definitions
├── Data/                          # Local sandbox database storage (MFDB archives)
├── HTML_Skeletons/                # Skeletons and page layout templates
├── Lib_EXPCMS/                    # Isolated Python library boundary
│   ├── lib_expcms_core.py         # Sandbox MFDB data manager
│   └── lib_expcms_*.py            # Specialized isolated utility libraries
├── docs/                          # Comprehensive technical reports & audit logs
└── templates/                     # Jinja2 rendering templates for ExpCMS UI
```

---

## 3. Core Features & Capabilities

- **Isolated Library Boundary (`Lib_EXPCMS`):** Complete structural separation guarantees that experimental library modifications do not affect other ecosystem tools.
- **Dynamic Component Architecture (`Components/`):** Test bench for modular UI widgets, interactive elements, and custom template tags.
- **Dedicated CLI Builder (`EXPCMS_Builder.py`):** Standalone compiler for generating static HTML builds directly from local sandbox data.
- **BECSS Design Integration:** Fully compatible with Elton Boehnen's BECSS design tokens (`#DE2626` red accent, `#000000` black, `#FFFFFF` white).
- **Atomic Persistence:** Uses POSIX temporary file writes and sync flushing to maintain flat-file integrity.

---

## 4. Architectural Deep Dive: Library Boundary Isolation

### 4.1 The Isolation Protocol
The core objective of `Experimental_CMS` is providing a risk-free playground for architectural innovation. In standard setups, testing an updated library function (such as an experimental `mfdb_core` write loop or an un-tested table validator) risks breaking live CMS instances across the machine.

To prevent cross-contamination:
1. All Python imports inside `EXPCMS.py` and `EXPCMS_Builder.py` strictly target `Lib_EXPCMS.*`.
2. All functions inside `Lib_EXPCMS` are prefixed with `lib_expcms_` to prevent namespace collision with global `lib_bejson_*` files.
3. Database storage paths are restricted to the local `Data/` directory.

```
       +-----------------------------------+
       |     Production Environment        |
       |  BEJSON_CMS / Global Libraries    |
       +-----------------------------------+
                         |
                         |  (STRICT ISOLATION BOUNDARY)
                         v
       +-----------------------------------+
       |    Experimental_CMS Sandbox       |
       |  - EXPCMS.py                      |
       |  - EXPCMS_Builder.py              |
       |  - Lib_EXPCMS/                    |
       |  - Data/ (Local DB)               |
       +-----------------------------------+
```

---

## 5. Component Lifecycle & Component-Driven Design

`Experimental_CMS` features an experimental component engine located under `Components/`. Components are single-file, self-contained UI modules designed to be dynamically rendered into pages.

### 5.1 Component Structure Overview
A typical component contains:
- **BEJSON Metadata Header:** Defines component parameters, slot names, and default values.
- **HTML Layout Template:** Inline Jinja2 template using BECSS BEM classes.
- **Scoped Stylesheet:** Optional inline CSS rules scoped via BEM prefixes.

```html
<!-- Component-Card.html example -->
<div class="becss-card becss-card--interactive">
  <div class="becss-card__header">
    <h3 class="becss-card__title">{{ title }}</h3>
  </div>
  <div class="becss-card__body">
    {{ content }}
  </div>
</div>
```

---

## 6. Operational Guide & Usage Instructions

### 6.1 Running the Experimental Web Interface
Launch the Flask development server:
```bash
python3 EXPCMS.py
# Server runs on http://127.0.0.1:5000 (or specified sandbox port)
```

### 6.2 Executing Static Site Builds
Use the dedicated CLI builder to generate production static output from the experimental database:
```bash
python3 EXPCMS_Builder.py --build
```

---

## 7. Performance Benchmarks & Atomic File Operations

Experimental_CMS tests performance optimizations for flat-file persistence. Standard flat-file writes suffer from I/O bottlenecks when updating large datasets.

### 7.1 POSIX Atomic Swap & Fsync Flushing
```python
import os
import json
from pathlib import Path

def atomic_write_bejson(target_path: Path, data: dict):
    """Perform atomic file replacement with POSIX fsync guarantee."""
    tmp_path = target_path.with_suffix(".tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_path, target_path)
```
This atomic sequence prevents partial write corruption if the system loses power during high-volume import tasks.

---

## 8. Development & Coding Standards

All code within `Experimental_CMS` must comply with Elton Boehnen's System Development Policy:
- **Solid Numeric Versioning:** Current project version is `3.5.0`. Package version is `19`.
- **Relational Fingerprinting:** All main source files must include `RELATIONAL_ID` GUID headers.
- **No Decorative Lines:** UI styling must maintain a clean, modern aesthetic using BECSS tokens.
- **Logging:** Python's standard `logging` module must be used for system output instead of plain `print()` statements.

---

## 9. API Reference & Code Examples

### 9.1 Programmatic Static Site Compilation Example
```python
from pathlib import Path
import logging
from Lib_EXPCMS.lib_expcms_core import ExpCMSCore

# Initialize logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ExpCMS")

def compile_sandbox_site(data_dir: Path, output_dir: Path):
    """Compile experimental static site from sandbox MFDB database."""
    logger.info("Initializing ExpCMS Core engine...")
    cms = ExpCMSCore(storage_dir=data_dir)
    
    pages = cms.get_all_pages()
    logger.info(f"Loaded {len(pages)} pages from sandbox storage.")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    for page in pages:
        html_content = cms.render_page(page["page_id"])
        out_file = output_dir / f"{page['slug']}.html"
        out_file.write_text(html_content, encoding="utf-8")
        logger.info(f"Rendered: {out_file.name}")

if __name__ == "__main__":
    compile_sandbox_site(Path("Data"), Path("Data/builds"))
```

### 9.2 Component Rendering Pipeline
```python
def render_component(component_name: str, props: dict) -> str:
    """Load and render an experimental component with given properties."""
    comp_file = Path("Components") / f"{component_name}.html"
    if not comp_file.exists():
        raise FileNotFoundError(f"Component '{component_name}' not found.")
    template_str = comp_file.read_text(encoding="utf-8")
    from jinja2 import Template
    return Template(template_str).render(**props)
```

---

## 10. Database Schema Specifications

Experimental_CMS uses BEJSON 104a tabular database records stored within `Data/`.

### 10.1 Page Record Table Schema
```json
{
  "Format": "BEJSON",
  "Format_Version": "104a",
  "Format_Creator": "Elton Boehnen",
  "Records_Type": ["ExpCMS_Pages"],
  "Fields": [
    {"name": "page_id", "type": "string"},
    {"name": "slug", "type": "string"},
    {"name": "title", "type": "string"},
    {"name": "content", "type": "string"},
    {"name": "author", "type": "string"},
    {"name": "date_created", "type": "string"}
  ],
  "Values": [
    ["page-001", "experimental-landing", "Experimental Landing Page", "<p>Content</p>", "Elton Boehnen", "2026-07-29"]
  ]
}
```

---

## 11. Custom Template Skeletons & Rendering Pipeline

Page skeletons are housed in `HTML_Skeletons/`. When `EXPCMS_Builder.py` executes a build, it performs standard variable substitution against skeleton templates:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{{ title }} - Experimental CMS</title>
  <link rel="stylesheet" href="/static/style.css">
</head>
<body class="becss-body">
  <header class="becss-header">
    <h1 class="becss-header__title">{{ title }}</h1>
  </header>
  <main class="becss-main">
    {{ content }}
  </main>
</body>
</html>
```

---

## 12. Technical Specifications & Requirements

- **Python Version:** 3.10+
- **Environment:** Standard Linux / Termux Android
- **Dependencies:** Flask, Pillow, Jinja2

---

## 13. Troubleshooting & Diagnostics

### Diagnostic Checklist
1. **Import Errors:** Ensure python execution path starts in root `Experimental_CMS/` so `Lib_EXPCMS` resolves.
2. **Missing CSS Styles:** If visual components render unstyled, verify `HTML_Skeletons` includes the latest BECSS stylesheet definitions.
3. **Database Locks:** If database writes fail, check that no stale `.lock` files remain in `Data/`.

---

## 14. Comprehensive Audit History & Ledger

Recorded in `.bejson_project.json`:
- **v3.0.4 (pkg1):** Initial library isolation sync establishing `Lib_EXPCMS`.
- **v3.0.7 (pkg4):** Unused library purge eliminating 20 orphaned modules.
- **v3.0.9 (pkg7):** CSS coverage gap patch adding 50 missing component classes.
- **v3.1.0 (pkg8):** Rebuilt navigation sidebar into 4 collapsible groups and added `/system` page.
- **v3.1.1 (pkg9):** Fixed bulk import crash and renamed main entry points to `EXPCMS.py` and `EXPCMS_Builder.py`.
- **v3.5.0 (pkg19):** Updated project ledger and published extensive 300+ line technical manual.

---

## 15. Security Considerations & Data Protection

Because `Experimental_CMS` is designed as an open sandbox, key security principles apply:
1. **Path Traversal Guards:** File imports and asset managers validate input paths against `Data/` to prevent relative traversal escapes (`../../`).
2. **Sanitized Shell Commands:** Shell executions avoid string interpolation, utilizing list arrays in `subprocess.run()`.

---

## 16. Author Credit & System Policy

```
================================================================================
Experimental_CMS Sandbox System
Author: Elton Boehnen
Email: boehnenelton2024@gmail.com
Website: https://boehnenelton2024.pages.dev
GitHub: https://github.com/boehnenelton
================================================================================
```

*Maintained under the System Development Policy of Elton Boehnen.*
