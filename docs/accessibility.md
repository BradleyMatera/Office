# Accessibility Notes

## Goal

The public AWS hub is intended to work as a resume link, technical walkthrough, writing directory, proof map, and source library. A visitor should be able to understand and navigate it without requiring perfect vision, precise pointer control, animation tolerance, a large screen, or prior AWS knowledge.

Accessibility includes markup, interaction, visual contrast, responsive behavior, image explanation, and cognitive clarity.

## Current implementation

### Page structure

- every public page declares `lang="en"`
- every page has a unique title and visible `h1`
- headings follow a logical hierarchy
- each page contains one `main` landmark
- a skip link moves keyboard users directly to the main content
- navigation uses standard links rather than custom JavaScript controls
- the FAQ uses native `details` and `summary`

### Keyboard access

The site has no required JavaScript interaction.

Standard browser behavior supports:

- Tab and Shift+Tab navigation
- Enter to activate links
- Space or Enter to operate native disclosures
- browser back and forward navigation
- direct URL access to every major page

Visible focus indicators use a high-contrast outline and offset.

### Images and diagrams

Meaningful images include descriptive `alt` text in the HTML.

First-party SVG diagrams also include:

- an internal `<title>`
- an internal `<desc>`
- a written explanation near the image
- a linked document or section that explains the same architecture in text

A visitor does not need to perceive the diagram to understand the workflow.

### Color and contrast

- primary text uses dark slate on light surfaces
- dark technical panels use light blue or white text
- verified states use text and a check indicator, not green alone
- warning states use headings and explicit wording, not orange alone
- links are underlined or use visible bordered-button treatments
- cards retain borders in addition to shadows
- forced-colors mode restores clear control and card borders

### Responsive behavior

- three-column card layouts collapse to two columns below 980 pixels
- multi-column layouts collapse to one column below 720 pixels
- navigation can scroll horizontally instead of compressing links into unreadable text
- code blocks scroll internally
- the full page should not require horizontal scrolling at common mobile widths
- system fonts prevent external font-loading delays and layout shifts

### Reduced motion

No essential content depends on animation.

When `prefers-reduced-motion: reduce` is active:

- smooth scrolling is disabled
- hover and transition durations are effectively removed
- all content remains visible and functional

### Cognitive accessibility

The site uses:

- plain-language section headings
- short paragraphs before detailed implementation blocks
- consistent terms such as workflow, proof, verified source, and scope boundary
- explicit distinctions between local tests, SAM validation, live Pages health, and deployed AWS integration
- visible explanations of what the internship did not include
- previews that link to full articles instead of duplicating long content into one page

## Static accessibility validation

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
- structured-data syntax

This is not a complete WCAG audit. It catches common regressions before publication.

## Manual release checks

A major release should include:

### Keyboard-only walkthrough

- enter through the skip link
- reach every primary navigation item
- open and close every FAQ disclosure
- activate every major call to action
- confirm focus never disappears behind sticky navigation

### Zoom and reflow

- review at 200% browser zoom
- review at 400% where practical
- check narrow mobile viewport behavior
- confirm code blocks scroll internally rather than widening the page
- confirm no text is clipped in cards, tables, or buttons

### Screen-reader structure

- review page title announcement
- inspect heading order
- verify main and navigation landmarks
- confirm image descriptions are meaningful but not repetitive
- confirm decorative content is not announced as important information

### Contrast and alternate display modes

- check light-mode contrast
- inspect forced-colors or high-contrast mode
- verify links and focus states remain distinguishable
- verify verified and warning states remain understandable without color

### Automated browser tools

Useful checks include:

- Lighthouse accessibility audit
- axe-core or Pa11y scan
- browser accessibility-tree inspection
- HTML validator

Automated results should be reviewed manually. A numeric score does not prove that the technical explanation is understandable or that the keyboard path is good.

## Tables

The proof and source pages use real HTML tables for claim mappings.

- header cells use `th`
- tables can scroll horizontally on small screens
- cell text remains plain and does not rely on icons alone
- complex architecture is not encoded only as a table

## External links

The site links to:

- canonical personal articles
- DEV editions
- GitHub repositories
- Credly badges
- official AWS documentation

Links use descriptive text rather than repeated “click here” labels. External links are not forced into new tabs, allowing the visitor to control navigation behavior.

## Writing and date accuracy

Accessibility includes avoiding confusing metadata.

Canonical article dates and slugs are taken from MDX frontmatter in the public blog source repository. When a search interface displays a conflicting date, the source metadata is treated as authoritative until the publishing system is corrected.

## Design-system relationship

The complete visual and interaction contract is documented in:

- [AWS Evidence Design System](design-system.md)
- [Visual Design System Page](../design-system.html)

Changes to color, spacing, typography, components, motion, or content-governance rules should update the design-system version and this accessibility document when behavior changes.

## Known limitations

The repository-level validator does not currently:

- execute a screen reader
- calculate rendered color contrast
- test browser zoom visually
- inspect focus order in a rendered browser
- run axe-core or Lighthouse
- verify accessibility of external websites

These remain manual or browser-based release checks. The site should not claim formal WCAG conformance without completing and recording an appropriate audit.
