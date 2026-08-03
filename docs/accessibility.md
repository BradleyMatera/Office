# Accessibility Notes

## Goal

The AWS Serverless Metadata Workflow site should be understandable and navigable without requiring perfect vision, precise pointer control, animation tolerance, a large screen, or prior AWS knowledge.

Accessibility includes semantic structure, keyboard access, visual contrast, responsive behavior, image explanation, and cognitive clarity.

## Current implementation

### Page structure

- every public page declares `lang="en"`
- every page has a unique title and one visible `h1`
- headings follow a logical hierarchy
- each page contains one `main` landmark
- a skip link moves keyboard users directly to the main content
- navigation uses standard links rather than custom JavaScript controls
- the main project page uses an application header and section navigation

### Keyboard access

The site has no required JavaScript interaction.

Standard browser behavior supports:

- Tab and Shift+Tab navigation
- Enter to activate links
- browser back and forward navigation
- direct URL access to every public page

Focus indicators use a visible blue outline with offset. Sticky navigation should never obscure the focused element.

### Images and diagrams

Meaningful images include descriptive `alt` text in the HTML.

First-party SVG diagrams also include:

- an internal `<title>`
- an internal `<desc>`
- a written explanation near the image
- equivalent text explaining the same architecture

A visitor does not need to perceive the diagram to understand the workflow.

### Color and contrast

The interface follows Cloudscape-style color roles:

- dark text on white or light-gray surfaces
- white text in the dark application header
- blue links and primary actions
- green success indicators with text labels
- informational alerts with an icon, heading, and explanation
- borders on containers in addition to shadows

Color is never the only indicator of meaning.

### Responsive behavior

- the desktop side navigation becomes a horizontally scrollable section bar below 980 pixels
- three-column layouts become two columns below 980 pixels
- multi-column layouts become one column below 700 pixels
- action groups stack vertically on narrow screens
- code and tables scroll internally when needed
- the page should not require horizontal scrolling at common mobile widths

### Typography

The site uses Open Sans with Helvetica and Arial fallbacks. Body text is intentionally compact but remains at a readable 14-pixel base with a 1.5 line height.

External font loading is not required for content to render. The fallback stack preserves the layout when Google Fonts is unavailable.

### Reduced motion

No essential content depends on animation.

When `prefers-reduced-motion: reduce` is active:

- smooth scrolling is disabled
- the site remains fully usable without transition effects

### Cognitive clarity

The site explains the project through normal technical sections:

- Overview
- Architecture
- What I built during the internship
- Public implementation
- Reliability and operations
- Evidence
- Related AWS writing
- Project scope

The interface does not include instructions about how recruiters should read the page. The content order communicates the relationship between the original capstone, the public implementation, verification, and scope.

## Static validation

`scripts/validate_site.py` checks repository-level requirements that can be verified without a browser:

- page language
- title and description presence
- one visible `h1`
- one main landmark
- skip link presence
- duplicate IDs
- image `alt` attributes
- local asset existence
- local fragment targets
- SVG title and description elements
- JSON-LD syntax
- sitemap, RSS, manifest, and required production files

This is not a complete WCAG audit. It catches common regressions before publication.

## Manual release checks

### Keyboard-only review

- enter through the skip link
- reach every application-header and section-navigation link
- activate every major action
- confirm focus remains visible around sticky navigation

### Zoom and reflow

- review at 200% browser zoom
- review at 400% where practical
- check narrow mobile viewport behavior
- confirm diagrams and code blocks remain usable
- confirm no text is clipped in containers, tables, status indicators, or buttons

### Screen-reader structure

- review the page-title announcement
- inspect heading order
- verify main and navigation landmarks
- confirm image descriptions are useful but not repetitive
- confirm decorative content is not announced as important information

### Contrast and alternate display modes

- check text, links, focus rings, containers, status indicators, and alerts
- inspect forced-colors or high-contrast mode
- verify meaning remains available without color

### Automated browser tools

Useful checks include:

- Lighthouse accessibility audit
- axe-core or Pa11y scan
- browser accessibility-tree inspection
- HTML validation

Automated scores do not prove that the technical explanation is understandable or that the keyboard path is good. Review the rendered pages manually.

## External links

The site links to personal articles, GitHub source files, the recruiter portfolio, LinkedIn, and official AWS documentation. Links use descriptive text and are not forced into new tabs.

## Interface relationship

The applied visual and interaction rules are documented in [Cloudscape Interface Notes](design-system.md).

There is no public design-system page. Changes to typography, color roles, spacing, controls, navigation, motion, or content structure should update `styles.css`, `hub.css`, the interface notes, and this accessibility document together.

## Known limitations

The repository-level validator does not currently:

- execute a screen reader
- calculate rendered color contrast
- test browser zoom visually
- inspect focus order in a rendered browser
- run axe-core or Lighthouse
- verify accessibility of external websites

The site should not claim formal WCAG conformance without completing and recording an appropriate audit.
