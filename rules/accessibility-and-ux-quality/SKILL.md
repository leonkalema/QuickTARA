---
name: accessibility-and-ux-quality
description: Enforces inclusive, WCAG-compliant UX: semantic HTML, keyboard navigation, color contrast, ARIA, motion sensitivity, forms, media, and automated checks. Use when building/reviewing UI or preventing regressions in CI.
license: Complete terms in LICENSE.txt
---

# Accessibility and UX Quality

## Principles
- POUR: Perceivable, Operable, Understandable, Robust.
- Keyboard-first: everything reachable and usable without a mouse.
- Prefer native elements; add ARIA only to enhance semantics.
- Visible focus, logical order, and respectful motion.

## Instructions

### Step 1: Semantics and structure
- Proper landmarks: header, nav, main, aside, footer.
- Heading hierarchy (h1…h6) reflects document outline.
- Lists, tables, and buttons/links used correctly; no div-spans for controls.

### Step 2: Keyboard and focus
- Tab order matches visual order; first focus is meaningful.
- Manage focus on route changes and dialogs (focus trap, return focus).
- Provide skip links; Escape closes modals/menus.

### Step 3: Forms
- Label every control; associate with `for`/`id` or wrap.
- Use `aria-describedby` for errors/help; indicate required fields.
- Proper input types and `autocomplete` tokens.

### Step 4: ARIA and dynamic content
- Only add roles/states when native semantics are insufficient.
- Use `aria-live` for asynchronous updates; announce state changes.
- Roving tabindex for menus/toolbars; single tab stop + arrow keys.

### Step 5: Color, contrast, and states
- Text contrast ≥ 4.5:1 (3:1 for large text); verify with tooling.
- Don’t rely on color alone; add icons, text, or patterns.
- Clear focus styles; hover ≠ focus; disabled vs. read-only distinct.

### Step 6: Motion and media
- Respect `prefers-reduced-motion`; provide non-animated alternatives.
- Avoid parallax/strobing; limit animation duration and distance.
- Captions for video, transcripts for audio; accessible media controls.

### Step 7: Screen reader testing
- Test with VoiceOver/NVDA; ensure logical reading order.
- Elements have accessible names; announce role, state, value.

### Step 8: Automation and CI
- Run axe and Lighthouse a11y audits in CI; fail on critical issues.
- Add Playwright/Cypress + axe checks for key flows.

## Checklists
- Landmarks/headings/semantics correct.
- Keyboard access and focus management verified.
- Forms labeled, errors announced, input types set.
- Contrast passes; non-color indicators present.
- Motion respects preferences; media accessible.
- Automated audits configured in CI.

## Patterns
- Dialog: focus trap, `aria-modal="true"`, `role="dialog"`, labeled by title.
- Combobox: input + listbox with active descendant pattern.
- Menu button: button toggles menu; roving tabindex for items.

## Troubleshooting
- Keyboard trap: ensure Escape closes; remove `tabindex=-1` from focusable items.
- Screen reader announces wrong role: remove conflicting ARIA.
- Low contrast: adjust tokens; verify against design system scales.
