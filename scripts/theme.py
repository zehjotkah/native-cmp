"""Native CMP theme API: namespaced --cmp-* variables used by every consent-* / is-consent-* token.

Each variable falls back to the matching Craft variable when a project defines it, otherwise to a
neutral default. Projects restyle the consent UI by overriding --cmp-* variables (see install.txt).
"""

# name: (craft variable or None, default, role)
CMP_VARIABLES = {
    # colors
    "--cmp-background": ("--background-primary", "#ffffff", "Notice, dialog and gate background"),
    "--cmp-surface": ("--background-secondary", "#f3f4f6", "Purpose and service rows, gate placeholder, button hover base"),
    "--cmp-text": ("--foreground-primary", "#15171c", "Text"),
    "--cmp-text-muted": ("--foreground-secondary", "#4d5461", "Descriptions and secondary text"),
    "--cmp-border": ("--border-default", "#dde0e5", "Dividers and badges"),
    "--cmp-control": ("--border-control", "#6f7582", "Switch track when off, outlined button border"),
    "--cmp-accent": ("--background-accent", "#1d4ed8", "Primary button, switch when on, links"),
    "--cmp-on-accent": ("--foreground-on-accent", "#ffffff", "Text on the primary button"),
    "--cmp-focus": ("--border-focus", "var(--cmp-accent)", "Focus ring"),
    "--cmp-warning": ("--foreground-warning", "#9a4a00", "“Services changed” note"),
    "--cmp-disabled": ("--foreground-disabled", "var(--cmp-text-muted)", "Disabled text"),
    "--cmp-inverse": ("--background-inverse", "var(--cmp-text)", "Video placeholder background"),
    "--cmp-scrim": ("--overlay-scrim", "color-mix(in srgb, var(--cmp-text) 55%, transparent)", "Backdrop behind the dialog"),
    "--cmp-hover": ("--overlay-interaction-hover", "color-mix(in srgb, var(--cmp-text) 6%, transparent)", "Hover tint on buttons"),
    "--cmp-pressed": ("--overlay-interaction-pressed", "color-mix(in srgb, var(--cmp-text) 12%, transparent)", "Pressed tint on buttons"),
    "--cmp-on-accent-hover": ("--overlay-on-accent-hover", "color-mix(in srgb, var(--cmp-on-accent) 14%, transparent)", "Hover tint on the primary button"),
    "--cmp-on-accent-pressed": ("--overlay-on-accent-pressed", "color-mix(in srgb, var(--cmp-on-accent) 24%, transparent)", "Pressed tint on the primary button"),
    # shape
    "--cmp-radius": ("--radius-default", "16px", "Notice, dialog and gate corners"),
    "--cmp-radius-small": ("--radius-small", "10px", "Small corners (rows, placeholders)"),
    "--cmp-radius-full": ("--radius-full", "999px", "Switches, badges and the close button"),
    "--cmp-button-radius": (None, "var(--cmp-radius-full)", "Button corners (set 0 for square buttons, switches keep --cmp-radius-full)"),
    "--cmp-button-border-width": (None, "1px", "Button border width"),
    "--cmp-shadow": ("--shadow-overlay", "0 24px 64px -12px rgb(0 0 0 / 0.28)", "Notice and dialog shadow"),
    # typography
    "--cmp-heading-font": (None, "inherit", "Font of titles and purpose/service labels (inherit = page font)"),
    "--cmp-heading-weight": (None, "600", "Weight of titles and labels"),
    "--cmp-heading-transform": (None, "none", "Letter case of titles and labels, e.g. uppercase"),
    "--cmp-heading-letter-spacing": (None, "normal", "Letter spacing of titles and labels"),
    "--cmp-button-font": (None, "inherit", "Button font"),
    "--cmp-button-weight": (None, "600", "Button weight"),
    "--cmp-button-transform": (None, "none", "Button letter case"),
    "--cmp-button-letter-spacing": (None, "normal", "Button letter spacing"),
    # spacing, motion, layers
    "--cmp-gap-xs": ("--gap-xs", "4px", "Spacing"),
    "--cmp-gap-s": ("--gap-s", "8px", "Spacing"),
    "--cmp-gap-m": ("--gap-m", "16px", "Spacing"),
    "--cmp-gap-l": ("--gap-l", "24px", "Spacing"),
    "--cmp-spacing": ("--spacing-default", "24px", "Inner padding of notice and dialog"),
    "--cmp-focus-width": ("--focus-width", "2px", "Focus ring width"),
    "--cmp-focus-offset": ("--focus-offset", "2px", "Focus ring offset"),
    "--cmp-duration": ("--duration-default", "180ms", "Transition duration"),
    "--cmp-easing": ("--easing-default", "cubic-bezier(0.2, 0, 0, 1)", "Transition easing"),
    "--cmp-layer": ("--layer-overlay", "2147483000", "z-index of notice and dialog"),
}


def css_value(name):
    craft, default, _ = CMP_VARIABLES[name]
    return f"var({craft}, {default})" if craft else default


def definitions():
    return {name: css_value(name) for name in CMP_VARIABLES}


# old generic variable -> namespaced variable
RENAME = {craft: name for name, (craft, _, _) in CMP_VARIABLES.items() if craft}
RENAME.update({"--background-control": "--cmp-control", "--foreground-accent": "--cmp-accent"})

HEADING_TOKENS = ["consent-notice-title", "consent-modal-title", "consent-gate-title", "consent-purpose-label", "consent-service-label"]
BUTTON_TOKENS = ["consent-button"]
BUTTON_BORDER_TOKENS = ["consent-button", "is-consent-button-primary", "is-consent-button-secondary"]
