# SYSTEM V1.2 — Invocation-Only Agent Architecture

## Purpose
This repository bootstraps a human-orchestrated, invocation-only operating system for LLM-assisted work.
It prevents autonomy creep, preserves auditability, and keeps authority and execution strictly separated.

## Non-negotiables
- Nothing runs unless explicitly invoked by a human
- Documentation is the source of truth for authority
- Plans define execution scope
- Tests define correctness

## Template
Copy into a project and fill in. Do not edit templates in-place.

# OBSIDIAN VAULT SETUP

## Authority
This document does not grant authority.

Note: Obsidian is a recommended documentation interface, not a system requirement.
All authority derives from repository files, not tooling.

---

## Overview

Each project directory can serve as an Obsidian vault for documentation purposes. This template describes how to set up the vault with authority-aware color coding.

## Directory Structure

```
projects/<project>/
├── .obsidian/
│   ├── app.json
│   ├── appearance.json
│   ├── core-plugins.json
│   ├── graph.json
│   ├── snippets/
│   │   └── authority-colors.css
│   ├── templates/
│   └── workspace.json
├── assets/                    # Attachments folder
├── authority/                 # Authority-granting documents
│   ├── INVARIANTS.md
│   └── DECISIONS.md
├── docs/                      # Non-authority documents
│   ├── ARCHITECTURE.md
│   └── PIPELINE.md
├── plans/
│   ├── active/               # Active plans (grant authority)
│   └── archive/              # Archived plans
├── AUTHORITY.md              # Authority index
└── README.md
```

## Setup Steps

### 1. Create Obsidian Configuration

Create `.obsidian/` directory with the following files:

**app.json**
```json
{
  "alwaysUpdateLinks": true,
  "newFileLocation": "folder",
  "newFileFolderPath": "docs",
  "attachmentFolderPath": "assets",
  "showLineNumber": true,
  "strictLineBreaks": false,
  "readableLineLength": true
}
```

**appearance.json**
```json
{
  "accentColor": "",
  "baseFontSize": 16
}
```

**core-plugins.json**
```json
{
  "file-explorer": true,
  "global-search": true,
  "switcher": true,
  "graph": true,
  "backlink": true,
  "outgoing-link": true,
  "tag-pane": true,
  "page-preview": true,
  "templates": true,
  "command-palette": true,
  "outline": true,
  "file-recovery": true
}
```

### 2. Configure Graph View Colors

Create `.obsidian/graph.json`:

```json
{
  "colorGroups": [
    {
      "query": "path:authority/",
      "color": { "a": 1, "rgb": 16729156 }
    },
    {
      "query": "path:plans/active/",
      "color": { "a": 1, "rgb": 5025616 }
    },
    {
      "query": "path:docs/",
      "color": { "a": 1, "rgb": 8421504 }
    }
  ],
  "showArrow": true,
  "nodeSizeMultiplier": 1.2
}
```

**Color meanings:**
- Red (`16729156`) — Authority documents
- Green (`5025616`) — Active plans
- Gray (`8421504`) — Non-authority docs

### 3. Create Authority Color CSS Snippet

Create `.obsidian/snippets/authority-colors.css`:

```css
/* Authority Color Coding for File Explorer */

/* Authority folder and files - Red accent */
.nav-folder-title[data-path="authority"],
.nav-folder-title[data-path="authority"] .nav-folder-title-content {
  color: #ff6b6b !important;
  font-weight: 600;
}

.nav-file-title[data-path^="authority/"] {
  color: #ff6b6b !important;
}

.nav-file-title[data-path^="authority/"]::before {
  content: "◆ ";
  color: #ff6b6b;
}

/* Active plans - Green accent */
.nav-folder-title[data-path="plans/active"],
.nav-folder-title[data-path="plans/active"] .nav-folder-title-content {
  color: #51cf66 !important;
  font-weight: 600;
}

.nav-file-title[data-path^="plans/active/"] {
  color: #51cf66 !important;
}

.nav-file-title[data-path^="plans/active/"]::before {
  content: "▶ ";
  color: #51cf66;
}

/* Archived plans - Dimmed */
.nav-folder-title[data-path="plans/archive"],
.nav-folder-title[data-path="plans/archive"] .nav-folder-title-content {
  color: #868e96 !important;
  opacity: 0.7;
}

.nav-file-title[data-path^="plans/archive/"] {
  color: #868e96 !important;
  opacity: 0.7;
}

/* Docs folder - Gray/neutral */
.nav-folder-title[data-path="docs"],
.nav-folder-title[data-path="docs"] .nav-folder-title-content {
  color: #adb5bd !important;
}

.nav-file-title[data-path^="docs/"] {
  color: #adb5bd !important;
}

/* AUTHORITY.md at root - Special styling */
.nav-file-title[data-path="AUTHORITY.md"] {
  color: #ffd43b !important;
  font-weight: 600;
}

.nav-file-title[data-path="AUTHORITY.md"]::before {
  content: "★ ";
  color: #ffd43b;
}

/* Plans folder header */
.nav-folder-title[data-path="plans"],
.nav-folder-title[data-path="plans"] .nav-folder-title-content {
  color: #69db7c !important;
}
```

### 4. Enable the CSS Snippet

1. Open Obsidian Settings
2. Navigate to **Appearance** → **CSS snippets**
3. Click refresh icon to detect new snippets
4. Toggle **authority-colors** ON

## Color Legend

| Element | Color | Symbol | Meaning |
|---------|-------|--------|---------|
| `authority/` | Red | ◆ | Grants authority |
| `plans/active/` | Green | ▶ | Active execution authority |
| `plans/archive/` | Gray (dim) | — | Historical reference |
| `docs/` | Gray | — | Non-authority |
| `AUTHORITY.md` | Yellow | ★ | Authority index |

## Opening the Vault

1. In Obsidian: **Open folder as vault**
2. Select the project directory (e.g., `projects/notion-obligations/`)
3. Enable the CSS snippet as described above
4. Press `Cmd+G` to view the authority graph
