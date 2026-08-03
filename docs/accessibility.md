# Accessibility Notes

## Goal

The public site is meant to explain a technical system without requiring specialized tools, perfect vision, or mouse-only interaction.

## Current accessibility choices

- semantic headings follow a logical hierarchy
- navigation uses standard links
- diagrams include descriptive alternative text in the HTML
- SVG diagrams include `<title>` and `<desc>` elements
- text and interface elements use strong color contrast
- content does not depend on color alone
- layouts collapse to one column on smaller screens
- links remain visibly distinguishable from body text
- the site does not use autoplay, animation, or time-limited interaction

## Diagram accessibility

Each architecture graphic has two layers of explanation:

1. a visual SVG for quick understanding
2. surrounding written documentation that explains the same flow in text

A reader who cannot see the diagram can still understand the architecture from the page and linked Markdown documents.

## Keyboard behavior

The site uses native links and does not replace browser controls with custom JavaScript widgets. Standard Tab, Shift+Tab, Enter, and browser navigation behavior should work without additional scripting.

## Reduced motion

No required animations are used. The only motion-like effect is native smooth scrolling, which does not block navigation or content access.

## Future accessibility checks

A mature release should add automated and manual checks such as:

- Lighthouse accessibility review
- axe-core or Pa11y scan
- keyboard-only walkthrough
- screen-reader heading and landmark review
- zoom testing at 200% and 400%
- high-contrast and forced-colors review

## Writing style

The documentation prefers short sections, direct explanations, expanded service names, and explicit claim boundaries. Accessibility includes cognitive clarity, not only markup compliance.
