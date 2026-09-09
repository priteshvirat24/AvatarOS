---
name: Google DeepMind AvatarOS
description: Official Google Design Language specification and tokens for AvatarOS Autonomous Digital Human Studio
colors:
  primary: "#8AB4F8"
  primary-container: "#1A73E8"
  on-primary: "#041E49"
  secondary: "#81C995"
  tertiary: "#FDD663"
  neutral: "#E8EAED"
  error: "#F28B82"
  background: "#131314"
  surface: "#1E1F22"
  surface-variant: "#282A2C"
  surface-elevated: "#303134"
  outline: "#3C4043"
  google-blue: "#4285F4"
  google-red: "#EA4335"
  google-yellow: "#FBBC04"
  google-green: "#34A853"
typography:
  h1:
    fontFamily: Google Sans
    fontSize: 2.25rem
  h2:
    fontFamily: Google Sans
    fontSize: 1.5rem
  h3:
    fontFamily: Google Sans
    fontSize: 1.125rem
  body-md:
    fontFamily: Roboto
    fontSize: 0.875rem
  code:
    fontFamily: Roboto Mono
    fontSize: 0.8125rem
rounded:
  sm: 4px
  md: 8px
  lg: 16px
  full: 9999px
spacing:
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    rounded: "{rounded.full}"
    padding: 10px 24px
  button-secondary:
    backgroundColor: "{colors.surface-variant}"
    textColor: "{colors.neutral}"
    rounded: "{rounded.full}"
    padding: 8px 16px
  card-surface:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.neutral}"
    rounded: "{rounded.lg}"
    padding: 16px
  card-elevated:
    backgroundColor: "{colors.surface-elevated}"
    textColor: "{colors.neutral}"
    rounded: "{rounded.lg}"
    padding: 20px
  badge-blue:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    rounded: "{rounded.full}"
    padding: 4px 10px
  badge-green:
    backgroundColor: "{colors.secondary}"
    textColor: "{colors.surface}"
    rounded: "{rounded.full}"
    padding: 4px 10px
  badge-yellow:
    backgroundColor: "{colors.tertiary}"
    textColor: "{colors.surface}"
    rounded: "{rounded.full}"
    padding: 4px 10px
  badge-red:
    backgroundColor: "{colors.error}"
    textColor: "{colors.surface}"
    rounded: "{rounded.full}"
    padding: 4px 10px
  workspace-canvas:
    backgroundColor: "{colors.background}"
    textColor: "{colors.neutral}"
    rounded: "{rounded.sm}"
    padding: 24px
  outline-separator:
    backgroundColor: "{colors.outline}"
    textColor: "{colors.neutral}"
    rounded: "{rounded.sm}"
    padding: 1px
  brand-blue-accent:
    backgroundColor: "{colors.google-blue}"
    textColor: "{colors.surface}"
    rounded: "{rounded.sm}"
    padding: 4px
  brand-red-accent:
    backgroundColor: "{colors.google-red}"
    textColor: "{colors.background}"
    rounded: "{rounded.sm}"
    padding: 4px
  brand-yellow-accent:
    backgroundColor: "{colors.google-yellow}"
    textColor: "{colors.surface}"
    rounded: "{rounded.sm}"
    padding: 4px
  brand-green-accent:
    backgroundColor: "{colors.google-green}"
    textColor: "{colors.surface}"
    rounded: "{rounded.sm}"
    padding: 4px
---

## Overview

AvatarOS adopts the official Google Design System, blending the visual clarity of Google Material You (M3), the precision of Google Cloud Platform & Vertex AI, and the futuristic elegance of Google DeepMind and Google Labs. 

The user interface delivers a high-trust, responsive control plane for autonomous digital human orchestration. Every surface adheres to Google's signature dark aesthetic (`#131314`), accented by the iconic Google four-color harmony: Google Blue (`#4285F4`), Google Red (`#EA4335`), Google Yellow (`#FBBC04`), and Google Green (`#34A853`).

## Colors

The color system is calibrated for deep focus, accessibility, and recognizable Google identity:

- **Primary (`#8AB4F8`):** Google Blue 300, used for active navigational elements, key action targets, and focused states in dark theme.
- **Primary Container (`#1A73E8`):** Google Blue 600, used for interactive badges, elevated buttons, and primary indicator fills.
- **On Primary (`#041E49`):** High-contrast dark ink ensuring WCAG AAA compliant text contrast against primary buttons.
- **Secondary (`#81C995`):** Google Green 300, representing verified safety gates, published media, healthy ClickHouse telemetry, and passed evaluations.
- **Tertiary (`#FDD663`):** Google Yellow 300, reserved for pending reviews, advisory notices, active audio processing, and latency gauges.
- **Error (`#F28B82`):** Google Red 300, communicating safety blocks, rights violations, and unverified factual claims.
- **Background (`#131314`):** Official Google standard dark canvas foundation.
- **Surface (`#1E1F22`):** First elevation layer for workspace cards, sidebars, and control panels.
- **Surface Elevated (`#303134`):** Modal dialogs, dropdowns, and floating command bars.
- **Outline (`#3C4043`):** Subtle Google divider borders maintaining structural definition without visual clutter.

## Typography

Typography prioritizes geometric clarity, editorial elegance, and instant legibility across complex DAG traces and conversational transcripts:

- **Google Sans / Display:** Applied to primary view titles, modal headings, and brand mastheads.
- **Roboto / Body:** Applied to conversational speech bubbles, character descriptions, and telemetry metrics.
- **Roboto Mono / Code:** Applied to SHA-256 hashes, C2PA manifest identifiers, MCP JSON payloads, and ClickHouse SQL queries.

## Layout

Layout follows Google's 8pt grid system with full responsive fluid scaling:

- **Top Application Bar:** 56px fixed height with Google 4-color accent micro-bar, pill navigation switcher, and provider status indicators.
- **Single-Action Command Bar:** Google Search-style pill container with embedded language and register selectors.
- **Three-Column Autonomous Studio:**
  - Left Column (280px): Digital Cast & Persistent Identity Roster.
  - Center Column (Flex 1): Live Stage with Three.js 3D Holographic Core & Master Video Player.
  - Right Column (420px): Vertex AI Agent Execution Graph & DAG Trace Inspector.
- **Bottom Timeline:** Fixed 72px production timeline scrubber.

## Elevation & Depth

Surfaces employ tonal elevation rather than heavy drop shadows, consistent with Google Material 3:

- **Level 0 (Canvas):** `#131314` flat background.
- **Level 1 (Cards):** `#1E1F22` with 1px `#3C4043` border.
- **Level 2 (Hover/Active):** `#282A2C` with subtle glow (`rgba(138, 180, 248, 0.12)`).
- **Level 3 (Modals/Overlays):** `#303134` with 24px backdrop blur and soft ambient shadow.

## Shapes

Shape language is defined by rounded pills and friendly radii:

- **Buttons & Chips:** Pill shaped (`rounded: full` / `9999px`) for actions and filters.
- **Cards & Viewports:** Smooth `16px` radius (`rounded: lg`).
- **Input Fields & Form Elements:** `8px` radius (`rounded: md`).

## Components

- **Pill Navigation Switcher:** Segmented control with smooth sliding pill indicator for Studio, Live, Evolution, and Knowledge modes.
- **Google Labs 3D Canvas:** Interactive Three.js WebGL holographic avatar core with audio reactivity and orbit damping.
- **Agent Pipeline Trace:** Vertex AI style DAG nodes showing Research, Claims, Script, Director, Performance, Guardian, and Publisher states.
- **Looker Studio Metric Cards:** Real-time KPI scorecards displaying ClickHouse query duration, cache hit rates, and ingestion throughput.

## Do's and Don'ts

### Do's
- **Do** use the Google 4-color gradient (`#4285F4`, `#EA4335`, `#FBBC04`, `#34A853`) as a subtle micro-accent or indicator, not as a dominating background fill.
- **Do** use pill-shaped containers (`border-radius: 9999px`) for search bars, status badges, and primary action buttons.
- **Do** ensure all text maintains at least 4.5:1 contrast against its immediate background.
- **Do** apply smooth spring physics via Framer Motion for modal transitions and view switches.

### Don'ts
- **Don't** use generic oversaturated neon glows or uncurated color schemes.
- **Don't** use sharp rectangular 0px borders for interactive buttons.
- **Don't** mix inconsistent font families; strictly stick to Google Sans, Roboto, and Roboto Mono.
