---
name: AvatarOS Light Theme
description: Design specification and tokens for AvatarOS Autonomous Digital Human Platform
colors:
  primary: "#1A73E8"
  primary-container: "#E8F0FE"
  on-primary: "#FFFFFF"
  secondary: "#137333"
  tertiary: "#B06000"
  neutral: "#202124"
  error: "#C5221F"
  background: "#FFFFFF"
  surface: "#F8F9FA"
  surface-variant: "#F1F3F4"
  surface-elevated: "#FFFFFF"
  outline: "#DADCE0"
  google-blue: "#1A73E8"
  google-red: "#D93025"
  google-yellow: "#B06000"
  google-green: "#137333"
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
    textColor: "{colors.on-primary}"
    rounded: "{rounded.full}"
    padding: 4px 10px
  badge-yellow:
    backgroundColor: "{colors.tertiary}"
    textColor: "{colors.on-primary}"
    rounded: "{rounded.full}"
    padding: 4px 10px
  badge-red:
    backgroundColor: "{colors.error}"
    textColor: "{colors.on-primary}"
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
    textColor: "{colors.on-primary}"
    rounded: "{rounded.sm}"
    padding: 4px
  brand-red-accent:
    backgroundColor: "{colors.google-red}"
    textColor: "{colors.on-primary}"
    rounded: "{rounded.sm}"
    padding: 4px
  brand-yellow-accent:
    backgroundColor: "{colors.google-yellow}"
    textColor: "{colors.on-primary}"
    rounded: "{rounded.sm}"
    padding: 4px
  brand-green-accent:
    backgroundColor: "{colors.google-green}"
    textColor: "{colors.on-primary}"
    rounded: "{rounded.sm}"
    padding: 4px
---

## Overview

AvatarOS adopts the official Google Light Design System, embodying the clean aesthetic of Google Search, Google Workspace, Google Cloud Console, and Google DeepMind. The canvas transitions from dark tones to crisp pure white (`#FFFFFF`) and warm off-white surface foundations (`#F8F9FA`), paired with Google's signature four-color identity: Google Blue (`#1A73E8`), Google Red (`#D93025`), Google Yellow (`#B06000`), and Google Green (`#137333`).

## Colors

The light color palette is engineered for executive readability, high-trust safety audits, and full WCAG AAA accessibility:

- **Primary (`#1A73E8`):** Official Google Blue 600, used for primary actions, navigation indicators, and focused elements.
- **Primary Container (`#E8F0FE`):** Soft blue surface tint for active tabs and selected cards.
- **On Primary (`#FFFFFF`):** Pure white ink ensuring maximum contrast against primary button fills.
- **Secondary (`#137333`):** Official Google Green 700, representing verified rights, approved safety checks, and healthy ClickHouse telemetry.
- **Tertiary (`#B06000`):** Google Amber 800, communicating advisory notices, in-progress reviews, and latency gauges with strict contrast compliance.
- **Error (`#C5221F`):** Google Red 700, highlighting hallucinated claims, unauthorized likeness requests, and blocked gates.
- **Background (`#FFFFFF`):** Crisp pure white canvas foundation.
- **Surface (`#F8F9FA`):** Google off-white elevation layer for cards, sidebars, and workspaces.
- **Surface Elevated (`#FFFFFF`):** High-elevation modals, floating toolbars, and search prompts with subtle drop shadows.
- **Outline (`#DADCE0`):** Official Google border divider line for clean structural separation.

## Typography

- **Google Sans / Display:** Applied to primary view titles, modal headings, and brand mastheads.
- **Roboto / Body:** Applied to conversational speech bubbles, character descriptions, and telemetry metrics.
- **Roboto Mono / Code:** Applied to SHA-256 hashes, C2PA manifest identifiers, MCP JSON payloads, and ClickHouse SQL queries.

## Layout

- **Top Application Bar:** 56px fixed height with Google 4-color micro-bar, pill navigation switcher, and Cinematic Judge Mode launcher.
- **Google Search Command Bar:** Pure white pill container with embedded language and register selectors.
- **Three-Column Autonomous Studio:** Left Cast roster (280px), Center Live Stage (Flex 1), Right Vertex AI DAG trace (400px).
- **Cinematic Judge Mode Overlay:** Fullscreen theater presentation with chapter navigation, audio-visual narrative, and interactive demonstration triggers.

## Elevation & Depth

Material Design 3 light elevation shadows:
- **Level 1 (Cards):** `0 1px 2px 0 rgba(60,64,67,0.3), 0 1px 3px 1px rgba(60,64,67,0.15)`.
- **Level 2 (Hover/Active):** `0 1px 3px 0 rgba(60,64,67,0.3), 0 4px 8px 3px rgba(60,64,67,0.15)`.
- **Level 3 (Modals/Overlays):** `0 8px 24px rgba(60,64,67,0.2)`.

## Shapes

- Pill-shaped geometry (`rounded: full` / `9999px`) for buttons, search bars, and status indicators.
- Friendly `16px` radius (`rounded: lg`) for cards, viewports, and modals.

## Components

- **Cinematic Judge Mode:** 6-chapter widescreen interactive theater presentation with live action triggers.
- **Google Labs 3D Canvas:** Three.js WebGL holographic core rendered with alpha transparency on white background.
- **Looker Studio Metric Cards:** Clean KPI scorecards displaying ClickHouse query duration, cache hit rates, and ingestion throughput.
- **Vertex AI DAG Pipeline:** Staggered execution cards with Google Material badges.

## Do's and Don'ts

### Do's
- **Do** maintain crisp white `#FFFFFF` and off-white `#F8F9FA` foundations with high contrast dark charcoal text (`#202124`).
- **Do** use pill-shaped containers (`border-radius: 9999px`) for search bars, action buttons, and status badges.
- **Do** provide hackathon judges with one-click access to Cinematic Judge Mode.

### Don'ts
- **Don't** use dark or muddy backgrounds.
- **Don't** use uncurated light text that fails contrast checks against white surfaces.
