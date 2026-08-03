# AWS Evidence Design System

Version: **1.0.0**  
Last reviewed: **August 3, 2026**

The AWS Evidence Design System is the visual and content framework for the public AWS Serverless Metadata Workflow site. It is designed for a high-trust technical portfolio where recruiters, engineers, and automated search systems need to understand the project quickly without encountering inflated claims or decorative noise.

## 1. Design principles

### Verified before impressive

The design should make evidence easy to reach. Architecture graphics, source links, implementation excerpts, official documentation, and claim boundaries are more important than animation or visual novelty.

### Operational, not fictional

Visuals should resemble dashboards, event flows, runbooks, data contracts, and system diagrams. Do not use generic futuristic clouds or fake terminal screenshots that imply a running environment when one has not been verified.

### Plain language with technical depth

Headlines should be understandable to recruiters. Supporting text, code excerpts, and linked documentation should provide enough detail for engineers.

### Accessible by default

Keyboard access, logical headings, strong contrast, descriptive alternative text, reduced-motion handling, responsive layouts, and readable line lengths are part of the design system, not later cleanup work.

### Scope is a component

Truthful boundaries are displayed with the same visual importance as positive proof. Warning cards and scope callouts are not apology text; they are trust-building interface elements.

## 2. Brand vocabulary

The site uses these recurring terms:

- **Workflow** — the S3 to Lambda to DynamoDB processing path
- **Proof** — repositories, tests, credentials, source writing, and live demonstrations
- **Verified source** — current official AWS documentation
- **Public reconstruction** — the deployable public version built from the original internship architecture without confidential material
- **Scope boundary** — what the work did not include or does not claim
- **Operational signal** — logs, alarms, retries, queue depth, test results, or other observable evidence

Avoid vague language such as:

- innovative cloud solution
- cutting-edge architecture
- enterprise-grade without evidence
- production-ready when deployment and load behavior have not been verified
- expert, guru, ninja, rockstar, or 10x

## 3. Color tokens

The CSS custom properties in `styles.css` are the source of truth.

| Token | Value | Role |
|---|---|---|
| `--navy-950` | `#071426` | Primary dark background, code surfaces, hero foundation |
| `--navy-900` | `#0a1d35` | Secondary dark background |
| `--navy-800` | `#12345c` | Elevated dark panels |
| `--blue-700` | `#175cd3` | Primary interactive color and section kicker |
| `--blue-600` | `#2474e5` | Infrastructure nodes and active states |
| `--blue-100` | `#dcecff` | Light text and information surfaces |
| `--blue-50` | `#eff7ff` | Information background |
| `--slate-950` | `#0f172a` | Primary body text |
| `--slate-600` | `#475569` | Secondary body text |
| `--slate-200` | `#e2e8f0` | Borders and dividers |
| `--slate-50` | `#f8fafc` | Page background |
| `--green-700` | `#047857` | Verified and successful states |
| `--green-50` | `#ecfdf5` | Verified-state background |
| `--orange-700` | `#c2410c` | Warning text |
| `--orange-50` | `#fff7ed` | Scope and cleanup warnings |
| AWS-style accent | `#ff9900` | Illustration accent only, not a claim of AWS brand ownership |

### Color-use rules

- Do not use color alone to communicate status.
- Verified states include a check mark and text label.
- Warning states include a heading and explicit explanation.
- Interactive links remain underlined or have a visible bordered-button treatment.
- The orange accent is used sparingly in diagrams and data emphasis.

## 4. Typography

### Font stack

```css
font-family: Inter, ui-sans-serif, system-ui, -apple-system,
  BlinkMacSystemFont, "Segoe UI", sans-serif;
```

No external font request is required. The system stack keeps the site fast and avoids layout shifts caused by font loading.

### Type scale

| Role | Responsive size |
|---|---|
| Primary hero | `clamp(2.8rem, 6.4vw, 5.7rem)` |
| Subpage hero | `clamp(2.4rem, 6vw, 4.8rem)` |
| Section heading | `clamp(2rem, 4.5vw, 3.45rem)` |
| Feature heading | `clamp(1.9rem, 3.5vw, 3rem)` |
| Card heading | approximately `1.08rem–1.22rem` |
| Body | `1rem`, line height `1.65` |
| Lead copy | `clamp(1.06rem, 1.5vw, 1.24rem)` |
| Metadata | `0.75rem–0.86rem` |
| Code | approximately `0.86rem`, line height `1.7` |

### Heading rules

- One visible `h1` per page.
- Section headings use `h2`.
- Cards use `h3`.
- Do not skip heading levels for visual size.
- Headings use concise claims; paragraphs carry qualifications.

## 5. Spacing and layout

### Base scale

Use a four-pixel base rhythm:

`4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80`

### Content width

```css
--content: 1160px;
```

The default container width is the smaller of the content token or the viewport minus 36 pixels.

### Section spacing

- Desktop sections: approximately 82 pixels vertically.
- Mobile sections: approximately 64 pixels vertically.
- Major components use 20–24 pixel gaps.
- Text columns should remain narrow enough for comfortable reading.

### Grid behavior

- Three-column cards collapse to two columns below 980 pixels.
- All multi-column layouts collapse to one column below 720 pixels.
- Navigation may scroll horizontally on small screens rather than wrap into an unusable stack.

## 6. Shape and elevation

| Token | Value | Use |
|---|---|---|
| `--radius-sm` | `10px` | Small callouts and controls |
| `--radius-md` | `18px` | Cards, code panels, tables |
| `--radius-lg` | `28px` | Hero panels and major feature containers |
| `--shadow-sm` | subtle 8/24 shadow | Standard cards |
| `--shadow-lg` | stronger 24/70 shadow | Hero and primary feature panels |

Shadows support hierarchy but never replace borders. Every elevated card also has a visible border for high-contrast and forced-colors environments.

## 7. Core components

### Hero

Purpose: state the project, scope, and next action immediately.

Required content:

- eyebrow describing the project context
- one clear `h1`
- plain-language lead
- status pills or proof summary
- primary repository link
- scope callout

### Trust strip

Purpose: provide four compact facts directly below a hero.

Examples:

- implementation scope
- verification state
- credential state
- public-safety boundary

### Article feature and article cards

Purpose: link to canonical writing without duplicating full articles.

Required content:

- unique relevant illustration
- source date from canonical frontmatter
- title
- short teaser
- tags
- explicit destination

### Proof card

Purpose: explain what a repository or credential verifies and what role it plays in the overall evidence map.

### Reference card

Purpose: connect a design decision to a primary official source and the local implementation.

### Code panel

Purpose: show a small, load-bearing implementation excerpt or command sequence.

Rules:

- do not paste entire files
- label the purpose
- link to the full source
- allow horizontal scrolling
- maintain readable contrast

### Verified card

Uses green surface and explicit check language for confirmed behavior.

### Warning card

Uses orange surface and explicit scope, cleanup, or uncertainty language.

### FAQ disclosure

Uses native `details` and `summary` elements to preserve keyboard and screen-reader behavior without JavaScript.

## 8. Illustration system

All first-party illustrations follow these rules:

- dark navy technical environment
- blue infrastructure and information lines
- green for verified outcomes
- orange for costs, warnings, or AWS-associated emphasis
- no copied AWS service logos
- no fake screenshots of unverified live accounts
- no text smaller than 14 pixels inside SVGs
- meaningful `<title>` and `<desc>` elements inside SVGs
- full explanatory alternative text in the embedding HTML
- surrounding text must communicate the same concept without requiring the image

Current illustration set:

- architecture overview
- processing flow
- data model
- security boundary
- cost drivers
- internship troubleshooting console
- cost radar
- multi-cloud comparison
- Cognito authentication flow
- ProjectHub grounded-answer pipeline
- certification roadmap
- medic-to-engineer bridge

## 9. Motion

The site does not depend on animation. Hover movement is limited to small card elevation and image scale changes.

For `prefers-reduced-motion: reduce`:

- smooth scrolling is disabled
- transitions are effectively removed
- content and navigation remain fully usable

## 10. Accessibility acceptance criteria

A release should meet all of the following:

- skip link reaches the main landmark
- every page has a unique title, description, canonical URL, and visible `h1`
- every meaningful image has descriptive alternative text
- decorative graphics are hidden from assistive technology
- heading levels are logical
- all functions work with keyboard only
- focus styles remain visible
- links are distinguishable without color alone
- content remains usable at 200% zoom
- layouts do not require horizontal page scrolling at common mobile widths
- code blocks may scroll internally
- forced-colors mode preserves borders and controls
- no auto-playing or time-limited content

## 11. SEO and answer-engine requirements

Each public page should include:

- unique `<title>`
- concise meta description
- canonical URL
- Open Graph title, description, URL, and image
- Twitter summary-large-image card
- appropriate JSON-LD type
- internal links to workflow, writing, proof, and verified sources
- sitemap entry
- descriptive heading hierarchy

The site also provides:

- `robots.txt`
- `sitemap.xml`
- `rss.xml`
- `llms.txt`
- `site.webmanifest`
- a custom 404 page

## 12. Content governance

### Canonical article metadata

Article titles, dates, descriptions, and slugs must come from the MDX frontmatter in the public blog repository. Search-result display dates are not authoritative when they conflict with source frontmatter.

### Technical verification

Service behavior should be checked against current official AWS documentation. Secondary tutorials can inspire future improvements but should not be the authority for a production claim.

### Claim changes

Any change that expands the internship claim must include evidence. Do not quietly change “training environment” into “production environment,” “guided troubleshooting” into “owned incidents,” or “public reconstruction” into “original internal repository.”

## 13. Release governance

A production update should pass:

- Python unit tests
- coverage threshold
- Python linting
- AWS SAM validation and build
- static site validation
- JSON-LD parsing
- local asset and link checks
- sitemap and robots validation
- live GitHub Pages health check after publication

The design system version should change when tokens, component contracts, or content-governance rules change materially.
