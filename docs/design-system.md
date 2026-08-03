# Cloudscape Interface Notes

Last reviewed: **August 3, 2026**

The public project site follows the visual foundation and information-architecture patterns of the open-source **Cloudscape Design System**, which was created for and is used by AWS products.

This repository is a static HTML and CSS site. It does not import Cloudscape's React component package. Instead, it applies the relevant foundation and patterns directly:

- Open Sans typography
- AWS-style application header
- gray application canvas and white bordered containers
- compact spacing and information density
- blue primary actions and links
- status indicators with text and icons
- key-value panels
- side navigation on larger screens
- horizontal section navigation on smaller screens
- alerts, tables, cards, and compact action groups

The project is not an AWS product and does not imply endorsement by AWS.

## Why Cloudscape fits this project

The site explains AWS infrastructure, service relationships, operational behavior, tests, and documentation. A system designed for cloud-management interfaces is a better fit than a marketing-site or portfolio-gallery style.

The interface should feel like technical project documentation:

- the project name and behavior appear first
- architecture follows the system flow
- implementation links sit beside the claims they support
- operational behavior is grouped as a sequence
- test results use compact status and metric treatment
- scope is presented as an informational alert
- related articles appear after the project explanation

The interface must not include sections that explain how recruiters are expected to read the page. The page structure should make the sequence clear without narrating the audience's behavior.

## Source files

- `styles.css` contains the shared tokens, layout, controls, containers, status treatment, and responsive behavior.
- `hub.css` contains the secondary-page extensions for articles, evidence, and AWS references.
- `index.html` is the primary project page.
- `writing.html`, `proof.html`, and `sources.html` use the same interface system.

There is no public design-system page. The design system is visible through the pages themselves.

## Typography

The site uses Open Sans, matching Cloudscape's typography foundation.

Fallback stack:

```css
font-family: "Open Sans", Helvetica, Arial, sans-serif;
```

Text hierarchy is intentionally compact:

- page title: responsive `2rem` to `2.625rem`
- section heading: `1.5rem`
- container heading: `1.125rem`
- body: `14px` with `1.5` line height
- labels and metadata: approximately `0.75rem` to `0.85rem`

## Color foundation

The main CSS tokens follow Cloudscape-style roles rather than decorative branding names:

- `--color-background-layout`
- `--color-background-container`
- `--color-background-header`
- `--color-background-button-primary`
- `--color-border-container`
- `--color-border-divider`
- `--color-text-heading`
- `--color-text-body`
- `--color-text-secondary`
- `--color-text-link`
- `--color-text-status-success`

Rules:

- color never communicates status alone
- links remain visibly interactive
- white containers retain borders even when shadows are unavailable
- orange is limited to the small AWS text mark and diagrams
- green is used only for verified or successful states

## Layout

Desktop layout:

```text
Application header
+----------------------+----------------------------------+
| Section navigation   | Main project content             |
|                      | Page header                      |
|                      | Containers and diagrams          |
+----------------------+----------------------------------+
```

Below 980 pixels, the side navigation becomes a horizontally scrollable section bar. Below 700 pixels, multi-column layouts become one column and action groups stack vertically.

## Components used

### Application header

Provides the project identity and only three global destinations: AWS writing, GitHub, and portfolio.

### Side navigation

Lists the actual project sections. It does not describe an audience or reading duration.

### Page header

Contains:

- project context
- project name
- one-sentence system behavior
- primary source and article actions
- key project facts
- verification status

### Container

The default surface for architecture explanations, implementation details, documentation, and related content.

### Key-value panel

Summarizes core services, architecture type, original environment, and public implementation without a large decorative hero card.

### Status indicator

Shows tested implementation, unit-test count, and coverage. Status includes text and a visible dot.

### Alert

Explains the separation between the original internship project and the public reconstruction.

### Metric cards

Display test and coverage results. They are used only for measurable values.

### Article cards

Link to original writing with a title, publication date, summary, and relevant first-party artwork.

## Content rules

### Explain the project directly

Good:

> When a file is uploaded to Amazon S3, AWS Lambda reads its object metadata, converts it into a consistent record, and stores that record in Amazon DynamoDB.

Avoid:

> This page is the fastest way for a recruiter to understand what I built.

### Use normal technical labels

Use:

- Overview
- Architecture
- Public implementation
- Reliability and operations
- Evidence
- Project scope

Avoid invented navigation labels such as:

- Proof map
- Trust layer
- Recruiter path
- Verified-source experience
- What the reader will see

### Keep scope close to the claim

The site must clearly separate:

- the original internship capstone
- the later public reconstruction
- local and CI verification
- a real deployed AWS integration

The public code must never be described as an exact internal Amazon repository.

## Accessibility requirements

- one visible `h1` per page
- one `main` landmark per page
- a skip link
- logical heading order
- keyboard-visible focus styles
- descriptive image alternative text
- `<title>` and `<desc>` in first-party SVGs
- no essential animation
- reduced-motion support
- responsive reflow without horizontal page scrolling
- status meaning available without color
- controls at least 36 pixels high, with primary actions generally 44 pixels or larger on touch layouts

## Release checks

Run:

```bash
make check
```

A public-interface change should also be reviewed for:

- desktop and mobile layout
- keyboard navigation
- 200% zoom
- focus visibility around the sticky header and navigation
- readable diagram scaling
- accurate local links and metadata
- consistent wording between the site, README, resume reference, and generated resumes

Material visual or interaction changes should update this document, `styles.css`, `hub.css`, and the accessibility notes together.
