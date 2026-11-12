# Design pass awaiting screenshot review

Part of #103 · design pass

The baseline is PR #114 at `47011df032e3c137f7e485336d11877623207b6e`. The candidate source is `c5124e485a9abd3a7f6913354140bde3ed1faeed`. The later evidence commit does not change the site. Pascal reviews these screenshots before any merge, signoff, or deployment.

## Observed problems

| Problem | Before | Change |
| --- | --- | --- |
| The collapsed mobile menu accepts keyboard focus | [Recorded invisible Blog focus](closed-menu-before.json) | CSS visibility follows the existing `aria-expanded` state |
| The backdrop covers the close button | [639 px light](screenshots/menu-639-light-before.png), [dark](screenshots/menu-639-dark-before.png) | Place the button above the backdrop |
| Tag counts are faint in both themes | [Mobile light](screenshots/tags-390-light-before.png), [dark](screenshots/tags-390-dark-before.png) | Inherit the readable foreground color |
| Prose links have faint underlines | [Mobile light](screenshots/prose-390-light-before.png), [dark](screenshots/prose-390-dark-before.png) | Use primary underlines at rest and on hover, with foreground text |
| Small orange titles lose contrast in light mode | [Desktop list](screenshots/archive-1280-light-before.png), [mobile tags](screenshots/tags-390-light-before.png) | Use foreground text for page titles and underlined list links |

## Compare both themes and widths

| Page and viewport | Light before | Light after | Dark before | Dark after |
| --- | --- | --- | --- | --- |
| Tags, desktop 1280 px | [Before](screenshots/tags-1280-light-before.png) | [After](screenshots/tags-1280-light-after.png) | [Before](screenshots/tags-1280-dark-before.png) | [After](screenshots/tags-1280-dark-after.png) |
| Tags, mobile 390 px | [Before](screenshots/tags-390-light-before.png) | [After](screenshots/tags-390-light-after.png) | [Before](screenshots/tags-390-dark-before.png) | [After](screenshots/tags-390-dark-after.png) |
| Blog list, desktop 1280 px | [Before](screenshots/archive-1280-light-before.png) | [After](screenshots/archive-1280-light-after.png) | [Before](screenshots/archive-1280-dark-before.png) | [After](screenshots/archive-1280-dark-after.png) |
| Blog list, mobile 390 px | [Before](screenshots/archive-390-light-before.png) | [After](screenshots/archive-390-light-after.png) | [Before](screenshots/archive-390-dark-before.png) | [After](screenshots/archive-390-dark-after.png) |
| French prose, desktop 1280 px | [Before](screenshots/prose-1280-light-before.png) | [After](screenshots/prose-1280-light-after.png) | [Before](screenshots/prose-1280-dark-before.png) | [After](screenshots/prose-1280-dark-after.png) |
| French prose, mobile 390 px | [Before](screenshots/prose-390-light-before.png) | [After](screenshots/prose-390-light-after.png) | [Before](screenshots/prose-390-dark-before.png) | [After](screenshots/prose-390-dark-after.png) |
| Open menu, 639 px | [Before](screenshots/menu-639-light-before.png) | [After](screenshots/menu-639-light-after.png) | [Before](screenshots/menu-639-dark-before.png) | [After](screenshots/menu-639-dark-after.png) |

## Verification

`just check` passes after `just fresh`. `just signoff-check` confirms that main requires signoff. Neither command signs off the head. The full verify-blog matrix captured 44 screenshots before and 44 after without capture failures. The [pixel comparison](shots-diff.json) reports 30 changed shots and 14 identical shots. A pixel-exact diff is expected to fail for this design change. No runtime or selected-image differences were reported. All four home screenshots are identical.

The [reader-path result](reader-path.json) covers keyboard opening, visible link focus, pointer closing, overlay closing, resizing from 639 to 640 and back, and theme persistence through reload and navigation. Separate keyboard sequences cover 390, 639, 640, and 1280 px in both themes. Collapsed mobile links leave the Tab order; desktop links remain reachable. Inspected tag and French prose pages have no horizontal overflow at these widths.

The [before](contrast-before.json) and [after](contrast-after.json) measurements convert browser-computed colors to sRGB through a canvas and use the WCAG relative-luminance formula. Alpha text is composited against the actual chip background. Tag-count contrast changes from 1.96:1 to 10.32:1 in light mode and from 3.33:1 to 7.26:1 in dark mode. Prose underline contrast changes from 1.39:1 to 3.70:1 in light mode and from 1.90:1 to 4.86:1 in dark mode. These readings cover the sampled elements, not every color and interaction on the site.

Fresh builds use the same font cache. `just parity BASE_DIST CANDIDATE_DIST --accept dev_notes/design-pass/parity-accept.json` accepts only [453 exact fingerprints](parity-accept.json). They cover 222 stylesheet bindings, 222 attribute findings, the compiled stylesheet, and eight formatter-only heading whitespace changes. All seven changed attribute pairs were checked across all 222 pages against the component diff. Routes, text, inline text, headings, IDs, links, scripts, images, feeds, Pagefind content, fonts, and OG pixels remain identical. Fingerprint acceptance records the author's intended changes. Pascal's visual review remains open.

## Preserved choices and limits

The existing JetBrains Mono family, type scale, article line height, reading width, mobile gutters, section spacing, theme values, banner format, and header layout remain. The inspected layout did not justify a redesign. No nontrivial visual change or mockup selection is proposed. Home featured-post choices and other pending editorial decisions remain with Pascal.

Experience First selected the reader-visible contrast and navigation fixes. Laziness Protocol kept the implementation to existing class lists and semantic tokens. Model the Domain kept `aria-expanded` as the one menu state. Sequence Work into Verifiable Units separated the navigation and contrast commits. Prove It Works required browser interaction and before-and-after artifacts.

This is Chromium proof on om1. Mobile Safari is not confirmed. No subagents or independent reviewer were used, as requested. No production or deployment verification is claimed.
