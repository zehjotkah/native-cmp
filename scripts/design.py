"""Craft design system for Native CMP.

Generates `.temp/css-variables.json` (Global Root variables) and
`.temp/tokens.json` (composite Tokens) for the Webstudio CLI.
"""

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / ".temp"

MOBILE = "wo9drbbFIH79Dku8JwG2F"  # Mobile portrait (max-width: 479px)
TABLET = "Nsu1RuiYCCciGnEk0yW2O"  # Tablet (max-width: 991px)

# --------------------------------------------------------------- variables

THEME = {
    "--theme-background": "#ffffff",
    "--theme-surface": "#f3f4f6",
    "--theme-foreground": "#15171c",
    "--theme-foreground-muted": "#4d5461",
    "--theme-border": "#dde0e5",
    "--theme-control": "#6f7582",
    "--theme-accent": "#1d4ed8",
    "--theme-on-accent": "#ffffff",
    "--theme-warning": "#9a4a00",
}

SEMANTIC = {
    "--foreground-primary": "var(--theme-foreground)",
    "--foreground-secondary": "var(--theme-foreground-muted)",
    "--foreground-disabled": "var(--theme-foreground-muted)",
    "--foreground-accent": "var(--theme-accent)",
    "--foreground-on-accent": "var(--theme-on-accent)",
    "--foreground-warning": "var(--theme-warning)",
    "--background-primary": "var(--theme-background)",
    "--background-secondary": "var(--theme-surface)",
    "--background-disabled": "var(--theme-border)",
    "--background-accent": "var(--theme-accent)",
    "--background-control": "var(--theme-control)",
    "--border-default": "var(--theme-border)",
    "--border-control": "var(--theme-control)",
    "--border-focus": "var(--theme-accent)",
    "--background-inverse": "var(--theme-foreground)",
    "--foreground-inverse": "var(--theme-background)",
    "--overlay-scrim": "color-mix(in srgb, var(--theme-foreground) 55%, transparent)",
    "--overlay-interaction-hover": "color-mix(in srgb, var(--theme-foreground) 6%, transparent)",
    "--overlay-interaction-pressed": "color-mix(in srgb, var(--theme-foreground) 12%, transparent)",
    "--overlay-on-accent-hover": "color-mix(in srgb, var(--theme-on-accent) 14%, transparent)",
    "--overlay-on-accent-pressed": "color-mix(in srgb, var(--theme-on-accent) 24%, transparent)",
    "--gap-xs": "4px",
    "--gap-s": "8px",
    "--gap-m": "16px",
    "--gap-l": "24px",
    "--spacing-default": "24px",
    "--focus-width": "2px",
    "--focus-offset": "2px",
    "--duration-default": "180ms",
    "--easing-default": "cubic-bezier(0.2, 0, 0, 1)",
    # extensions (documented in docs/development.md)
    "--radius-small": "10px",
    "--radius-default": "16px",
    "--radius-full": "999px",
    "--shadow-overlay": "0 24px 64px -12px rgb(0 0 0 / 0.28)",
    "--layer-overlay": "2147483000",
    "--width-content": "1280px",
}

# ------------------------------------------------------------------ helpers


def border(side_width="1px", color="var(--border-default)", style="solid", sides=("top", "right", "bottom", "left")):
    out = {}
    for side in sides:
        out[f"border-{side}-width"] = side_width
        out[f"border-{side}-style"] = style
        out[f"border-{side}-color"] = color
    return out


def radius(value):
    return {
        "border-top-left-radius": value,
        "border-top-right-radius": value,
        "border-bottom-left-radius": value,
        "border-bottom-right-radius": value,
    }


def padding(block, inline=None):
    inline = block if inline is None else inline
    return {"padding-top": block, "padding-bottom": block, "padding-left": inline, "padding-right": inline}


def margin0():
    return {"margin-top": "0", "margin-right": "0", "margin-bottom": "0", "margin-left": "0"}


def focus_ring():
    return {
        "outline-width": "var(--focus-width)",
        "outline-style": "solid",
        "outline-color": "var(--border-focus)",
        "outline-offset": "var(--focus-offset)",
    }


def overlay(var):
    return {"background-image": f"linear-gradient(var({var}), var({var}))"}


def transition(props):
    return {
        "transition-property": ", ".join(props),
        "transition-duration": ", ".join("var(--duration-default)" for _ in props),
        "transition-timing-function": ", ".join("var(--easing-default)" for _ in props),
    }


# ------------------------------------------------------------------- tokens
# name -> { "base": {...}, ":state": {...}, "@mobile": {...} }

TOKENS = {
    "consent": {"base": {"display": "contents"}},
    # notice ---------------------------------------------------------------
    "consent-notice": {
        "base": {
            "position": "fixed",
            "left": "var(--gap-m)",
            "right": "var(--gap-m)",
            "bottom": "var(--gap-m)",
            "z-index": "var(--layer-overlay)",
            "display": "flex",
            "flex-wrap": "wrap",
            "align-items": "flex-end",
            "justify-content": "space-between",
            "row-gap": "var(--gap-m)",
            "column-gap": "var(--gap-l)",
            "max-width": "1040px",
            "margin-left": "auto",
            "margin-right": "auto",
            **padding("20px", "var(--spacing-default)"),
            "background-color": "var(--background-primary)",
            "color": "var(--foreground-primary)",
            **border(),
            **radius("var(--radius-default)"),
            "box-shadow": "var(--shadow-overlay)",
            "font-size": "15px",
            "line-height": "1.5",
        },
        "@mobile": {
            "left": "var(--gap-s)",
            "right": "var(--gap-s)",
            "bottom": "var(--gap-s)",
            **padding("var(--gap-m)"),
        },
    },
    "consent-notice-body": {
        "base": {"flex-grow": "1", "flex-shrink": "1", "flex-basis": "380px", "display": "grid", "row-gap": "var(--gap-s)"}
    },
    "consent-notice-title": {
        "base": {**margin0(), "font-size": "17px", "font-weight": "600", "line-height": "1.3"}
    },
    "consent-notice-text": {"base": {**margin0(), "color": "var(--foreground-secondary)"}},
    "consent-notice-changes": {
        "base": {**margin0(), "font-size": "14px", "font-weight": "500", "color": "var(--foreground-warning)"}
    },
    "consent-notice-actions": {
        "base": {"display": "flex", "flex-wrap": "wrap", "align-items": "center", "column-gap": "var(--gap-s)", "row-gap": "var(--gap-s)"},
        "@mobile": {"width": "100%"},
    },
    # buttons & links -----------------------------------------------------
    "consent-button": {
        "base": {
            "display": "inline-flex",
            "align-items": "center",
            "justify-content": "center",
            "column-gap": "var(--gap-s)",
            "min-height": "44px",
            **padding("10px", "20px"),
            **border("1px", "transparent"),
            **radius("var(--radius-full)"),
            "background-color": "var(--background-secondary)",
            "color": "var(--foreground-primary)",
            "font-family": "inherit",
            "font-size": "15px",
            "font-weight": "600",
            "line-height": "1.2",
            "text-align": "center",
            "text-decoration-line": "none",
            "white-space": "nowrap",
            "cursor": "pointer",
            **transition(["background-color", "color", "border-color"]),
        },
        ":hover": overlay("--overlay-interaction-hover"),
        ":active": overlay("--overlay-interaction-pressed"),
        ":focus-visible": focus_ring(),
        ":disabled": {"cursor": "not-allowed", "color": "var(--foreground-disabled)"},
        "@mobile": {"flex-grow": "1", "flex-shrink": "1", "flex-basis": "auto"},
    },
    "is-consent-button-primary": {
        "base": {
            "background-color": "var(--background-accent)",
            "color": "var(--foreground-on-accent)",
            **border("1px", "var(--background-accent)"),
        },
        ":hover": overlay("--overlay-on-accent-hover"),
        ":active": overlay("--overlay-on-accent-pressed"),
    },
    "is-consent-button-secondary": {
        "base": {
            "background-color": "var(--background-primary)",
            "color": "var(--foreground-primary)",
            **border("1px", "var(--border-control)"),
        }
    },
    "is-consent-button-ghost": {
        "base": {
            "background-color": "transparent",
            "color": "var(--foreground-primary)",
            "text-decoration-line": "underline",
            "text-underline-offset": "3px",
            "padding-left": "12px",
            "padding-right": "12px",
        }
    },
    "consent-link": {
        "base": {
            **padding("0"),
            **border("0", "transparent", "none"),
            "background-color": "transparent",
            "color": "var(--foreground-accent)",
            "font-family": "inherit",
            "font-size": "inherit",
            "font-weight": "inherit",
            "line-height": "inherit",
            "text-decoration-line": "underline",
            "text-underline-offset": "2px",
            "cursor": "pointer",
        },
        ":hover": {"text-decoration-thickness": "2px"},
        ":focus-visible": {**focus_ring(), **radius("2px")},
    },
    # modal ------------------------------------------------------------------
    "consent-modal": {
        "base": {
            "position": "fixed",
            "top": "0",
            "right": "0",
            "bottom": "0",
            "left": "0",
            "z-index": "var(--layer-overlay)",
            "display": "flex",
            "align-items": "center",
            "justify-content": "center",
            **padding("var(--gap-m)"),
        },
        "@mobile": {"align-items": "flex-end", **padding("0")},
    },
    "consent-modal-scrim": {
        "base": {"position": "absolute", "top": "0", "right": "0", "bottom": "0", "left": "0", "background-color": "var(--overlay-scrim)"}
    },
    "consent-modal-dialog": {
        "base": {
            "position": "relative",
            "display": "flex",
            "flex-direction": "column",
            "width": "100%",
            "max-width": "640px",
            "max-height": "calc(100dvh - 32px)",
            "overflow-x": "hidden",
            "overflow-y": "hidden",
            "background-color": "var(--background-primary)",
            "color": "var(--foreground-primary)",
            **radius("var(--radius-default)"),
            "box-shadow": "var(--shadow-overlay)",
            "font-size": "15px",
            "line-height": "1.5",
            "outline-style": "none",
        },
        "@mobile": {
            "max-width": "none",
            "max-height": "92dvh",
            "border-bottom-left-radius": "0",
            "border-bottom-right-radius": "0",
        },
    },
    "consent-modal-header": {
        "base": {
            "display": "grid",
            "grid-template-columns": "1fr auto",
            "column-gap": "var(--gap-m)",
            "row-gap": "var(--gap-s)",
            "padding-top": "var(--spacing-default)",
            "padding-right": "var(--spacing-default)",
            "padding-bottom": "var(--gap-m)",
            "padding-left": "var(--spacing-default)",
            **border(sides=("bottom",)),
        }
    },
    "consent-modal-title": {
        "base": {**margin0(), "align-self": "center", "font-size": "20px", "font-weight": "600", "line-height": "1.3"}
    },
    "consent-modal-close": {
        "base": {
            "grid-column-start": "2",
            "grid-row-start": "1",
            "display": "grid",
            "place-items": "center",
            "width": "44px",
            "height": "44px",
            "margin-top": "-6px",
            "margin-inline-end": "-10px",
            **padding("0"),
            **border("0", "transparent", "none"),
            **radius("var(--radius-full)"),
            "background-color": "transparent",
            "color": "var(--foreground-secondary)",
            "cursor": "pointer",
        },
        ":hover": overlay("--overlay-interaction-hover"),
        ":active": overlay("--overlay-interaction-pressed"),
        ":focus-visible": focus_ring(),
    },
    "consent-modal-text": {
        "base": {**margin0(), "grid-column-start": "1", "grid-column-end": "-1", "font-size": "14px", "color": "var(--foreground-secondary)"}
    },
    "consent-modal-body": {
        "base": {
            "flex-grow": "1",
            "flex-shrink": "1",
            "flex-basis": "auto",
            "min-height": "0",
            "overflow-y": "auto",
            "overscroll-behavior-y": "contain",
            "padding-top": "var(--gap-xs)",
            "padding-bottom": "var(--gap-xs)",
            "padding-left": "var(--spacing-default)",
            "padding-right": "var(--spacing-default)",
        }
    },
    "consent-modal-footer": {
        "base": {
            "display": "flex",
            "flex-wrap": "wrap",
            "justify-content": "flex-end",
            "column-gap": "var(--gap-s)",
            "row-gap": "var(--gap-s)",
            **padding("var(--gap-m)", "var(--spacing-default)"),
            **border(sides=("top",)),
            "background-color": "var(--background-secondary)",
        }
    },
    # consent ID: proof of consent, shown in the dialog once a decision was made
    "consent-id": {
        "base": {
            **margin0(),
            "flex-grow": "1",
            "flex-shrink": "1",
            "flex-basis": "100%",
            "display": "flex",
            "flex-wrap": "wrap",
            "align-items": "baseline",
            "column-gap": "var(--gap-xs)",
            "font-size": "12px",
            "color": "var(--foreground-secondary)",
        }
    },
    "consent-id-value": {"base": {"font-family": "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace", "font-size": "11px", "word-break": "break-all"}},
    # purposes & services ------------------------------------------------------
    "consent-purposes": {"base": {**margin0(), **padding("0"), "list-style-type": "none", "display": "grid"}},
    "consent-purpose": {
        "base": {"display": "grid", "row-gap": "6px", **padding("var(--gap-m)", "0"), **border(sides=("bottom",))}
    },
    "is-consent-purpose-all": {"base": {"border-bottom-style": "none", "border-bottom-width": "0"}},
    "consent-purpose-header": {
        "base": {"display": "flex", "align-items": "center", "justify-content": "space-between", "column-gap": "var(--gap-m)"}
    },
    "consent-purpose-label": {
        "base": {
            "display": "flex",
            "flex-wrap": "wrap",
            "align-items": "center",
            "column-gap": "var(--gap-s)",
            "row-gap": "var(--gap-xs)",
            "font-size": "16px",
            "font-weight": "600",
            "cursor": "pointer",
        }
    },
    "consent-purpose-description": {"base": {**margin0(), "font-size": "14px", "color": "var(--foreground-secondary)"}},
    "consent-purpose-services": {"base": {"margin-top": "var(--gap-xs)"}},
    "consent-purpose-summary": {
        "base": {
            "width": "fit-content",
            **padding("4px", "0"),
            "font-size": "14px",
            "font-weight": "600",
            "color": "var(--foreground-accent)",
            "cursor": "pointer",
            **radius("4px"),
        },
        ":hover": {"text-decoration-line": "underline"},
        ":focus-visible": focus_ring(),
    },
    "consent-services": {
        "base": {
            "margin-top": "var(--gap-s)",
            "margin-right": "0",
            "margin-bottom": "0",
            "margin-left": "0",
            **padding("0"),
            "list-style-type": "none",
            "display": "grid",
            "row-gap": "var(--gap-s)",
        }
    },
    "consent-service": {
        "base": {
            "display": "grid",
            "row-gap": "var(--gap-xs)",
            **padding("12px", "var(--gap-m)"),
            **radius("var(--radius-small)"),
            "background-color": "var(--background-secondary)",
        }
    },
    "consent-service-header": {
        "base": {"display": "flex", "align-items": "center", "justify-content": "space-between", "column-gap": "var(--gap-m)"}
    },
    "consent-service-label": {
        "base": {
            "display": "flex",
            "flex-wrap": "wrap",
            "align-items": "center",
            "column-gap": "var(--gap-s)",
            "row-gap": "var(--gap-xs)",
            "font-size": "15px",
            "font-weight": "600",
            "cursor": "pointer",
        }
    },
    "consent-service-description": {"base": {**margin0(), "font-size": "14px", "color": "var(--foreground-secondary)"}},
    "consent-badge": {
        "base": {
            "display": "inline-flex",
            "align-items": "center",
            **padding("1px", "8px"),
            **border(),
            **radius("var(--radius-full)"),
            "background-color": "var(--background-primary)",
            "color": "var(--foreground-secondary)",
            "font-size": "12px",
            "font-weight": "600",
            "line-height": "1.5",
            "white-space": "nowrap",
        }
    },
    "consent-switch": {
        "base": {
            "appearance": "none",
            "position": "relative",
            "flex-shrink": "0",
            "width": "44px",
            "height": "24px",
            **margin0(),
            **radius("var(--radius-full)"),
            **border("0", "transparent", "none"),
            "background-color": "var(--background-control)",
            "cursor": "pointer",
            **transition(["background-color"]),
        },
        "::before": {
            "content": '""',
            "position": "absolute",
            "top": "3px",
            "left": "3px",
            "width": "18px",
            "height": "18px",
            **radius("var(--radius-full)"),
            "background-color": "var(--background-primary)",
            "box-shadow": "0 1px 2px rgb(0 0 0 / 0.3)",
            **transition(["translate"]),
        },
        ":checked": {"background-color": "var(--background-accent)"},
        ":checked::before": {"translate": "20px 0"},
        ":indeterminate": {"background-color": "var(--background-accent)"},
        ":indeterminate::before": {"translate": "10px 0"},
        ":disabled": {"cursor": "not-allowed", "opacity": "0.6"},
        ":focus-visible": focus_ring(),
        ":dir(rtl)": {"scale": "-1 1"},
    },
    # contextual consent gate ---------------------------------------------------
    "consent-gate": {
        "base": {"position": "relative", "display": "grid", **radius("var(--radius-default)"), "overflow-x": "hidden", "overflow-y": "hidden"},
        # interaction mode: leave room for the notice while it overlays the player
        "[data-cmp-requested]": {"min-height": "300px"},
    },
    "consent-gate-notice": {
        "base": {
            "display": "grid",
            "justify-items": "center",
            "align-content": "center",
            "row-gap": "var(--gap-s)",
            "min-height": "280px",
            **padding("var(--spacing-default)"),
            "text-align": "center",
            "background-color": "var(--background-secondary)",
            "color": "var(--foreground-primary)",
            **border(),
            **radius("var(--radius-default)"),
        }
    },
    "consent-gate-title": {"base": {**margin0(), "font-size": "17px", "font-weight": "600", "line-height": "1.3"}},
    "consent-gate-text": {"base": {**margin0(), "max-width": "52ch", "font-size": "14px", "color": "var(--foreground-secondary)"}},
    "consent-gate-actions": {
        "base": {"display": "flex", "flex-wrap": "wrap", "justify-content": "center", "column-gap": "var(--gap-s)", "row-gap": "var(--gap-s)", "margin-top": "var(--gap-xs)"}
    },
    "consent-gate-content": {"base": {"display": "block"}},
    # design preview frames --------------------------------------------------------
    "consent-preview": {
        "base": {
            "position": "relative",
            "transform": "translateZ(0)",
            "min-height": "360px",
            "overflow-x": "hidden",
            "overflow-y": "hidden",
            **border("1px", "var(--border-control)", "dashed"),
            **radius("var(--radius-default)"),
            "background-color": "var(--background-secondary)",
        }
    },
    "is-consent-preview-modal": {"base": {"min-height": "860px"}},
}


MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

TOKENS_V2 = {
    "consent-language": {"base": {"display": "contents"}},
    "consent-status": {
        "base": {
            "display": "flex",
            "align-items": "center",
            "justify-content": "space-between",
            "column-gap": "var(--gap-s)",
            **padding("12px", "var(--gap-m)"),
            **border(),
            **radius("var(--radius-small)"),
            "background-color": "var(--background-primary)",
            "font-size": "15px",
            "font-weight": "600",
            **transition(["border-color"]),
        },
        '[data-cmp-state="granted"]': {"border-top-color": "var(--background-accent)", "border-right-color": "var(--background-accent)", "border-bottom-color": "var(--background-accent)", "border-left-color": "var(--background-accent)"},
    },
    "consent-status-label": {
        "base": {
            **padding("2px", "10px"),
            **radius("var(--radius-full)"),
            "font-size": "12px",
            "font-weight": "700",
            "letter-spacing": "0.04em",
            "text-transform": "uppercase",
            "white-space": "nowrap",
            "background-color": "var(--background-secondary)",
            "color": "var(--foreground-secondary)",
        }
    },
    "is-consent-status-label-granted": {"base": {"background-color": "var(--background-accent)", "color": "var(--foreground-on-accent)"}},
    # marketing site ---------------------------------------------------------
    "site-header": {
        "base": {
            "position": "sticky",
            "top": "0",
            "z-index": "10",
            "background-color": "var(--background-primary)",
            **border(sides=("bottom",)),
        }
    },
    "site-header-inner": {
        "base": {
            "display": "flex",
            "align-items": "center",
            "justify-content": "space-between",
            "column-gap": "var(--gap-l)",
            "flex-wrap": "wrap",
            "row-gap": "var(--gap-s)",
            "max-width": "calc(var(--width-content) + 2 * var(--spacing-default))",
            "margin-left": "auto",
            "margin-right": "auto",
            **padding("14px", "var(--spacing-default)"),
        }
    },
    "site-brand": {
        "base": {"display": "inline-flex", "align-items": "center", "font-size": "17px", "font-weight": "700", "letter-spacing": "-0.01em", "color": "var(--foreground-primary)", "text-decoration-line": "none", **radius("4px")},
        ":focus-visible": focus_ring(),
    },
    "site-logo": {
        "base": {"display": "block", "width": "auto", "height": "48px", "max-width": "100%"},
        "@mobile": {"height": "40px"},
    },
    "site-nav": {
        "base": {"display": "flex", "flex-wrap": "wrap", "align-items": "center", "column-gap": "var(--gap-l)", "row-gap": "var(--gap-xs)", "font-size": "14px", "margin-inline-start": "auto"},
        "@tablet": {"display": "none"},
    },
    "site-nav-link": {
        "base": {"color": "var(--foreground-secondary)", "text-decoration-line": "none", "font-weight": "500"},
        ":hover": {"color": "var(--foreground-primary)"},
        ":focus-visible": {**focus_ring(), **radius("4px")},
        '[aria-current="page"]': {
            "color": "var(--foreground-primary)",
            "font-weight": "600",
            "text-decoration-line": "underline",
            "text-decoration-color": "var(--border-focus)",
            "text-decoration-thickness": "2px",
            "text-underline-offset": "6px",
        },
    },
    "site-section": {
        "base": {**padding("96px", "var(--spacing-default)"), "scroll-margin-top": "64px"},
        "@mobile": {"padding-top": "64px", "padding-bottom": "64px"},
    },
    "is-site-section-muted": {"base": {"background-color": "var(--background-secondary)"}},
    "site-container": {
        "base": {"display": "grid", "row-gap": "var(--gap-l)", "width": "100%", "max-width": "var(--width-content)", "margin-left": "auto", "margin-right": "auto"}
    },
    "site-split": {
        "base": {"display": "grid", "grid-template-columns": "minmax(0, 1.15fr) minmax(0, 0.85fr)", "column-gap": "56px", "row-gap": "var(--gap-l)", "align-items": "center"},
        "@tablet": {"grid-template-columns": "minmax(0, 1fr)"},
    },
    "site-stack": {"base": {"display": "grid", "row-gap": "var(--gap-m)", "align-content": "start", "justify-items": "start"}},
    "site-eyebrow": {
        "base": {**margin0(), "font-size": "13px", "font-weight": "700", "letter-spacing": "0.08em", "text-transform": "uppercase", "color": "var(--foreground-accent)"}
    },
    "site-heading-hero": {
        "base": {**margin0(), "max-width": "15ch", "font-size": "64px", "line-height": "1.04", "letter-spacing": "-0.035em", "font-weight": "750"},
        "@tablet": {"font-size": "52px"},
        "@mobile": {"font-size": "40px"},
    },
    "site-heading": {
        "base": {**margin0(), "max-width": "24ch", "font-size": "42px", "line-height": "1.1", "letter-spacing": "-0.025em", "font-weight": "700"},
        "@mobile": {"font-size": "32px"},
    },
    "site-heading-small": {"base": {**margin0(), "font-size": "18px", "line-height": "1.3", "font-weight": "650"}},
    "site-lead": {
        "base": {**margin0(), "max-width": "62ch", "font-size": "20px", "line-height": "1.55", "color": "var(--foreground-secondary)"},
        "@mobile": {"font-size": "18px"},
    },
    "site-text": {"base": {**margin0(), "font-size": "15px", "line-height": "1.6", "color": "var(--foreground-secondary)"}},
    "site-actions": {"base": {"display": "flex", "flex-wrap": "wrap", "align-items": "center", "column-gap": "var(--gap-s)", "row-gap": "var(--gap-s)"}},
    "site-badge": {
        "base": {
            "display": "inline-flex",
            "align-items": "center",
            **padding("6px", "12px"),
            **border(),
            **radius("var(--radius-full)"),
            "background-color": "var(--background-primary)",
            "color": "var(--foreground-primary)",
            "font-size": "13px",
            "font-weight": "600",
        }
    },
    "site-grid": {
        "base": {"display": "grid", "grid-template-columns": "repeat(auto-fit, minmax(min(100%, 250px), 1fr))", "column-gap": "var(--gap-m)", "row-gap": "var(--gap-m)"}
    },
    "is-site-grid-wide": {"base": {"grid-template-columns": "repeat(auto-fit, minmax(min(100%, 420px), 1fr))"}},
    "site-card": {
        "base": {
            "display": "grid",
            "align-content": "start",
            "row-gap": "var(--gap-s)",
            **padding("var(--spacing-default)"),
            **border(),
            **radius("var(--radius-default)"),
            "background-color": "var(--background-primary)",
            "min-width": "0",
        }
    },
    "site-card-number": {
        "base": {
            "display": "grid",
            "place-items": "center",
            "width": "36px",
            "height": "36px",
            **radius("var(--radius-full)"),
            "background-color": "var(--background-accent)",
            "color": "var(--foreground-on-accent)",
            "font-size": "15px",
            "font-weight": "700",
        }
    },
    "site-panel": {
        "base": {
            "display": "grid",
            "row-gap": "var(--gap-s)",
            **padding("var(--spacing-default)"),
            **radius("var(--radius-default)"),
            "background-color": "var(--background-secondary)",
            **border(),
            "box-shadow": "var(--shadow-overlay)",
        }
    },
    "site-code": {
        "base": {
            **margin0(),
            **padding("18px", "20px"),
            **radius("var(--radius-small)"),
            "background-color": "var(--background-inverse)",
            "color": "var(--foreground-inverse)",
            "font-family": MONO,
            "font-size": "13px",
            "line-height": "1.65",
            "white-space": "nowrap",
            "white-space-collapse": "preserve",
            "overflow-x": "auto",
            "tab-size": "2",
        }
    },
    "site-code-content": {"base": {"display": "block", "width": "max-content", "min-width": "100%"}},
    "site-inline-code": {
        "base": {
            **padding("1px", "6px"),
            **radius("6px"),
            "background-color": "var(--background-secondary)",
            "font-family": MONO,
            "font-size": "0.9em",
        }
    },
    "site-faq": {"base": {"display": "grid", "row-gap": "var(--gap-s)", **padding("var(--gap-m)", "0"), **border(sides=("bottom",))}},
    "site-faq-question": {
        "base": {"font-size": "17px", "font-weight": "650", "cursor": "pointer", **radius("4px")},
        ":focus-visible": focus_ring(),
    },
    "site-footer": {
        "base": {
            "display": "flex",
            "flex-wrap": "wrap",
            "align-items": "center",
            "justify-content": "space-between",
            "column-gap": "var(--gap-l)",
            "row-gap": "var(--gap-s)",
            "width": "100%",
            "max-width": "calc(var(--width-content) + 2 * var(--spacing-default))",
            "margin-left": "auto",
            "margin-right": "auto",
            **padding("40px", "var(--spacing-default)"),
            "font-size": "14px",
            "color": "var(--foreground-secondary)",
        }
    },
}


TOKENS_V3 = {
    "site-docs-layout": {
        "base": {
            "display": "grid",
            "grid-template-columns": "220px minmax(0, 1fr)",
            "column-gap": "56px",
            "row-gap": "var(--gap-l)",
            "max-width": "calc(var(--width-content) + 2 * var(--spacing-default))",
            "margin-left": "auto",
            "margin-right": "auto",
            "padding-top": "48px",
            "padding-bottom": "120px",
            "padding-left": "var(--spacing-default)",
            "padding-right": "var(--spacing-default)",
        },
        "@tablet": {"grid-template-columns": "minmax(0, 1fr)"},
    },
    "site-docs-sidebar": {
        "base": {
            "position": "sticky",
            "top": "88px",
            "align-self": "start",
            "max-height": "calc(100vh - 120px)",
            "overflow-y": "auto",
            "display": "grid",
            "row-gap": "var(--gap-s)",
        },
        "@tablet": {"position": "static", "max-height": "none", **padding("var(--gap-m)"), **border(), **radius("var(--radius-small)")},
    },
    "site-docs-nav-title": {
        "base": {**margin0(), "font-size": "12px", "font-weight": "700", "letter-spacing": "0.08em", "text-transform": "uppercase", "color": "var(--foreground-secondary)"}
    },
    "site-docs-nav": {
        "base": {"display": "grid", "row-gap": "2px"},
        "@tablet": {"display": "flex", "flex-wrap": "wrap", "column-gap": "var(--gap-m)", "row-gap": "var(--gap-xs)"},
    },
    "site-docs-nav-link": {
        "base": {"display": "block", **padding("5px", "0"), "font-size": "14px", "line-height": "1.35", "color": "var(--foreground-secondary)", "text-decoration-line": "none"},
        ":hover": {"color": "var(--foreground-primary)"},
        ":focus-visible": {**focus_ring(), **radius("4px")},
    },
    "site-docs-content": {"base": {"display": "grid", "row-gap": "64px", "min-width": "0", "align-content": "start"}},
    "site-docs-section": {"base": {"display": "grid", "row-gap": "var(--gap-m)", "align-content": "start", "scroll-margin-top": "88px", "min-width": "0"}},
    "site-docs-heading": {"base": {**margin0(), "font-size": "30px", "line-height": "1.2", "letter-spacing": "-0.02em", "font-weight": "700"}},
    "site-docs-subheading": {"base": {**margin0(), "margin-top": "var(--gap-s)", "font-size": "19px", "line-height": "1.3", "font-weight": "650", "scroll-margin-top": "88px"}},
    "site-body-text": {"base": {**margin0(), "font-size": "16px", "line-height": "1.7", "color": "var(--foreground-secondary)"}},
    "site-list": {
        "base": {**margin0(), "padding-left": "22px", "display": "grid", "row-gap": "6px", "font-size": "16px", "line-height": "1.65", "color": "var(--foreground-secondary)"}
    },
    "site-callout": {
        "base": {
            **margin0(),
            **padding("14px", "18px"),
            **radius("var(--radius-small)"),
            "background-color": "var(--background-secondary)",
            "border-left-width": "3px",
            "border-left-style": "solid",
            "border-left-color": "var(--border-focus)",
            "font-size": "15px",
            "line-height": "1.65",
            "color": "var(--foreground-primary)",
        }
    },
    "site-table-wrapper": {"base": {"overflow-x": "auto", **border(), **radius("var(--radius-small)")}},
    "site-table": {"base": {"width": "100%", "border-collapse": "collapse", "font-size": "14px", "line-height": "1.55"}, "@tablet": {"min-width": "640px"}},
    "site-table-header": {
        "base": {**padding("10px", "14px"), "text-align": "left", "vertical-align": "bottom", "font-weight": "650", "background-color": "var(--background-secondary)", **border(sides=("bottom",))}
    },
    "site-table-cell": {
        "base": {**padding("10px", "14px"), "text-align": "left", "vertical-align": "top", "color": "var(--foreground-secondary)", **border(sides=("bottom",))}
    },
    "site-example": {
        "base": {
            "display": "grid",
            "grid-template-columns": "minmax(0, 1fr) minmax(0, 1.35fr)",
            "column-gap": "32px",
            "row-gap": "var(--gap-m)",
            **padding("var(--spacing-default)"),
            **border(),
            **radius("var(--radius-default)"),
            "background-color": "var(--background-primary)",
            "scroll-margin-top": "88px",
        },
        "@tablet": {"grid-template-columns": "minmax(0, 1fr)"},
    },
    "site-example-column": {"base": {"display": "grid", "row-gap": "var(--gap-s)", "align-content": "start", "justify-items": "start", "min-width": "0"}},
    "site-code-label": {
        "base": {**margin0(), "margin-top": "var(--gap-xs)", "font-size": "12px", "font-weight": "700", "letter-spacing": "0.06em", "text-transform": "uppercase", "color": "var(--foreground-secondary)"}
    },
    "is-site-code-full": {"base": {"justify-self": "stretch"}},
    "is-site-inline-code-contrast": {"base": {"background-color": "var(--background-primary)"}},
}


TOKENS_V4 = {
    "site-generator-layout": {
        "base": {
            "display": "grid",
            "grid-template-columns": "minmax(0, 1fr) minmax(0, 1fr)",
            "column-gap": "32px",
            "row-gap": "var(--gap-l)",
            "align-items": "start",
            "max-width": "calc(var(--width-content) + 2 * var(--spacing-default))",
            "margin-left": "auto",
            "margin-right": "auto",
            "padding-top": "8px",
            "padding-bottom": "120px",
            "padding-left": "var(--spacing-default)",
            "padding-right": "var(--spacing-default)",
        },
        "@tablet": {"grid-template-columns": "minmax(0, 1fr)"},
    },
    "site-generator-steps": {"base": {"display": "grid", "row-gap": "var(--gap-l)", "min-width": "0"}},
    "site-generator-output": {
        "base": {
            "position": "sticky",
            "top": "88px",
            "display": "grid",
            "row-gap": "var(--gap-m)",
            "max-height": "calc(100vh - 104px)",
            "overflow-y": "auto",
            "min-width": "0",
            **padding("var(--spacing-default)"),
            **border(),
            **radius("var(--radius-default)"),
            "background-color": "var(--background-secondary)",
        },
        "@tablet": {"position": "static", "max-height": "none"},
    },
    "site-fieldset": {
        "base": {
            **margin0(),
            "display": "grid",
            "row-gap": "var(--gap-m)",
            "min-width": "0",
            **padding("var(--spacing-default)"),
            **border(),
            **radius("var(--radius-default)"),
            "background-color": "var(--background-primary)",
        }
    },
    "site-legend": {"base": {**padding("0"), "float": "left", "width": "100%", "font-size": "20px", "font-weight": "700", "line-height": "1.3", "letter-spacing": "-0.01em"}},
    "site-help": {"base": {**margin0(), "font-size": "14px", "line-height": "1.55", "color": "var(--foreground-secondary)"}},
    "site-form-grid": {
        "base": {"display": "grid", "grid-template-columns": "repeat(auto-fit, minmax(min(100%, 200px), 1fr))", "column-gap": "var(--gap-m)", "row-gap": "var(--gap-m)", "align-items": "start"}
    },
    "site-field": {"base": {"display": "grid", "row-gap": "6px", "min-width": "0", "align-content": "start"}},
    "site-label": {"base": {"font-size": "14px", "font-weight": "600", "color": "var(--foreground-primary)"}},
    "site-input": {
        "base": {
            "width": "100%",
            "min-height": "42px",
            **margin0(),
            **padding("8px", "12px"),
            **border("1px", "var(--border-control)"),
            **radius("var(--radius-small)"),
            "background-color": "var(--background-primary)",
            "color": "var(--foreground-primary)",
            "font-family": "inherit",
            "font-size": "15px",
            "line-height": "1.4",
        },
        ":focus-visible": {**focus_ring(), "outline-offset": "0"},
    },
    "is-site-input-code": {"base": {"min-height": "180px", "font-family": MONO, "font-size": "13px", "resize": "vertical"}},
    "site-purpose-group": {"base": {"display": "grid", "row-gap": "var(--gap-s)"}},
    "site-option": {
        "base": {
            "display": "grid",
            "row-gap": "var(--gap-s)",
            **padding("12px", "14px"),
            **border(),
            **radius("var(--radius-small)"),
            "background-color": "var(--background-primary)",
            **transition(["border-color", "background-color"]),
        },
        "[data-gen-selected]": {
            "border-top-color": "var(--background-accent)",
            "border-right-color": "var(--background-accent)",
            "border-bottom-color": "var(--background-accent)",
            "border-left-color": "var(--background-accent)",
            "background-color": "var(--background-secondary)",
        },
    },
    "site-option-label": {
        "base": {"display": "grid", "grid-template-columns": "auto minmax(0, 1fr)", "column-gap": "12px", "align-items": "start", "cursor": "pointer"}
    },
    "site-option-text": {"base": {"display": "grid", "row-gap": "2px"}},
    "site-checkbox": {
        "base": {"width": "18px", "height": "18px", "margin-top": "2px", "margin-right": "0", "margin-bottom": "0", "margin-left": "0", "accent-color": "var(--background-accent)", "cursor": "pointer"},
        ":focus-visible": focus_ring(),
    },
    "site-option-fields": {"base": {"display": "grid", "grid-template-columns": "repeat(auto-fit, minmax(min(100%, 200px), 1fr))", "column-gap": "var(--gap-s)", "row-gap": "var(--gap-s)", "padding-left": "30px"}},
    "site-output-block": {"base": {"display": "grid", "grid-template-columns": "minmax(0, 1fr)", "row-gap": "var(--gap-s)", "min-width": "0"}},
    "site-output-header": {"base": {"display": "flex", "flex-wrap": "wrap", "align-items": "center", "justify-content": "space-between", "column-gap": "var(--gap-s)", "row-gap": "var(--gap-xs)"}},
    "is-site-code-scroll": {"base": {"max-height": "300px", "overflow-y": "auto"}},
    "site-status-text": {"base": {"font-size": "13px", "font-weight": "600", "color": "var(--foreground-accent)"}},
}


TOKENS_V5 = {
    "is-consent-gate-overlay": {
        "base": {
            "position": "absolute",
            "top": "0",
            "right": "0",
            "bottom": "0",
            "left": "0",
            "z-index": "2",
            "min-height": "0",
            "overflow-y": "auto",
            "background-color": "color-mix(in srgb, var(--background-secondary) 96%, transparent)",
        }
    },
    "consent-video": {
        "base": {
            "position": "relative",
            "display": "block",
            "width": "100%",
            "aspect-ratio": "16 / 9",
            "overflow-x": "hidden",
            "overflow-y": "hidden",
            **radius("var(--radius-default)"),
            "background-color": "var(--background-inverse)",
        }
    },
}


TOKENS_V6 = {
    "site-form": {"base": {"display": "grid", "row-gap": "var(--gap-m)", "min-width": "0"}},
    "is-site-split-top": {"base": {"align-items": "start"}},
    "is-site-input-textarea": {"base": {"min-height": "160px", "resize": "vertical"}},
    "site-form-message": {
        "base": {
            **margin0(),
            **padding("12px", "16px"),
            **radius("var(--radius-small)"),
            "font-size": "15px",
            "line-height": "1.5",
            "color": "var(--foreground-primary)",
            "background-color": "color-mix(in srgb, var(--foreground-accent) 10%, var(--background-primary))",
        }
    },
    "is-site-form-message-error": {
        "base": {"background-color": "color-mix(in srgb, var(--foreground-warning) 12%, var(--background-primary))"}
    },
}


TOKENS_V7 = {
    "site-visually-hidden": {
        "base": {
            "position": "absolute", "width": "1px", "height": "1px", **padding("0"), **{f"margin-{side}": "-1px" for side in ("top", "right", "bottom", "left")},
            "overflow-x": "hidden", "overflow-y": "hidden", "clip-path": "inset(50%)", "white-space": "nowrap", **border("0"),
        }
    },
    "is-site-desktop-only": {"base": {"display": "inline-flex"}, "@tablet": {"display": "none"}},
    "site-menu-button": {
        "base": {
            "display": "none", "align-items": "center", "justify-content": "center", "flex-shrink": "0",
            "width": "44px", "height": "44px", **padding("0"), "margin-inline-start": "auto",
            **border("1px", "var(--border-control)"), **radius("var(--radius-full)"),
            "background-color": "transparent", "color": "var(--foreground-primary)", "cursor": "pointer",
            **transition(["background-color"]),
        },
        "@tablet": {"display": "inline-flex"},
        ":hover": {"background-color": "var(--overlay-interaction-hover)"},
        ":focus-visible": focus_ring(),
    },
    "site-menu-icon": {"base": {"display": "block", "width": "22px", "height": "22px"}},
    "site-menu-overlay": {
        "base": {"position": "fixed", "top": "0", "right": "0", "bottom": "0", "left": "0", "z-index": "100", "background-color": "var(--overlay-scrim)"}
    },
    "site-menu-sheet": {
        "base": {
            "position": "fixed", "top": "0", "bottom": "0", "inset-inline-end": "0", "z-index": "101",
            "display": "grid", "align-content": "start", "row-gap": "var(--gap-l)",
            "width": "min(360px, 100%)", **padding("20px", "var(--spacing-default)"),
            "overflow-y": "auto", "background-color": "var(--background-primary)", "box-shadow": "var(--shadow-overlay)",
            "outline-style": "none",
        }
    },
    "site-menu-header": {"base": {"display": "flex", "align-items": "center", "justify-content": "space-between", "column-gap": "var(--gap-m)"}},
    "site-menu-title": {"base": {**margin0(), "font-size": "18px", "font-weight": "650", "line-height": "1.3"}},
    "site-menu-close": {
        "base": {
            "display": "inline-flex", "align-items": "center", "justify-content": "center", "width": "44px", "height": "44px", **padding("0"),
            **border("0"), **radius("var(--radius-full)"), "background-color": "transparent", "color": "var(--foreground-primary)", "cursor": "pointer",
            "margin-inline-end": "-10px",
        },
        ":hover": {"background-color": "var(--overlay-interaction-hover)"},
        ":focus-visible": focus_ring(),
    },
    "site-menu-nav": {"base": {"display": "grid"}},
    "site-menu-link": {
        "base": {
            "display": "block", **padding("14px", "0"), **border(sides=("bottom",)),
            "font-size": "18px", "font-weight": "500", "color": "var(--foreground-primary)", "text-decoration-line": "none",
        },
        ":hover": {"color": "var(--foreground-accent)"},
        ":focus-visible": {**focus_ring(), "outline-offset": "-2px", **radius("4px")},
        '[aria-current="page"]': {"color": "var(--foreground-accent)", "font-weight": "650"},
    },
    "is-consent-button-block": {"base": {"width": "100%"}},
}



TOKENS_V8 = {
    "site-prompt": {
        "base": {
            **margin0(),
            **padding("18px", "20px"),
            **radius("var(--radius-small)"),
            "background-color": "var(--background-inverse)",
            "color": "var(--foreground-inverse)",
            "font-family": MONO,
            "font-size": "14px",
            "line-height": "1.65",
            "overflow-wrap": "anywhere",
        }
    },
    "is-site-card-link": {
        "base": {"color": "inherit", "text-decoration-line": "none", **transition(["border-color", "background-color"])},
        ":hover": border("1px", "var(--border-focus)"),
        ":focus-visible": focus_ring(),
    },
    "is-site-badge-start": {"base": {"justify-self": "start"}},
    "is-site-card-featured": {
        "base": {**border("2px", "var(--border-focus)"), "background-color": "var(--background-primary)"},
    },
    # full-row card, e.g. the starter project as the fifth install way
    "is-site-card-wide": {"base": {"grid-column-start": "1", "grid-column-end": "-1"}},
}

# "Used by" logo marquee on Home. Two identical lists scroll by their own width plus the gap,
# so the loop is seamless. Keyframes, pause on hover/focus and reduced motion live in the
# section's "Marquee Motion" embed (onepager.USED_BY_MOTION).
TOKENS_V9 = {
    "is-site-section-compact": {
        "base": {"padding-top": "48px", "padding-bottom": "48px"},
        "@mobile": {"padding-top": "40px", "padding-bottom": "40px"},
    },
    "site-marquee": {
        "base": {
            "display": "flex",
            "column-gap": "var(--gap-l)",
            "overflow-x": "hidden",
            "overflow-y": "hidden",
            "mask-image": "linear-gradient(to right, transparent, black 10%, black 90%, transparent)",
        }
    },
    "site-marquee-list": {
        "base": {
            **margin0(),
            **padding("0"),
            "display": "flex",
            "flex-shrink": "0",
            "align-items": "center",
            "justify-content": "space-around",
            "column-gap": "var(--gap-l)",
            "min-width": "100%",
            "list-style-type": "none",
            "animation-name": "site-marquee",
            "animation-duration": "40s",
            "animation-timing-function": "linear",
            "animation-iteration-count": "infinite",
        },
        "@mobile": {"animation-duration": "16s"},
    },
    "site-marquee-item": {"base": {"flex-shrink": "0"}},
    "site-used-by-link": {
        "base": {
            "display": "block",
            **padding("8px"),
            **radius("var(--radius-small)"),
            "filter": "grayscale(1)",
            **transition(["filter"]),
        },
        ":hover": {"filter": "none"},
        ":focus-visible": {**focus_ring(), "filter": "none"},
    },
    "site-used-by-logo": {
        "base": {"display": "block", "width": "auto", "height": "56px", "max-width": "240px", "object-fit": "contain"},
        "@mobile": {"height": "44px", "max-width": "180px"},
    },
}


def _apply_cmp_theme():
    """consent-* / is-consent-* tokens only use the namespaced --cmp-* variables (see theme.py)."""
    import re
    import theme

    def rename(value):
        return re.sub(r"var\((--[a-z0-9-]+)", lambda m: "var(" + theme.RENAME.get(m.group(1), m.group(1)), value)

    for tokens in (TOKENS, TOKENS_V2, TOKENS_V3, TOKENS_V4, TOKENS_V5, TOKENS_V6, TOKENS_V7, TOKENS_V8, TOKENS_V9):
        for name, groups in tokens.items():
            if not name.startswith(("consent-", "is-consent-")):
                continue
            for group, styles in groups.items():
                for prop in list(styles):
                    if isinstance(styles[prop], str):
                        styles[prop] = rename(styles[prop])
            base = groups.setdefault("base", {})
            if name in theme.HEADING_TOKENS:
                base["font-weight"] = f"var(--cmp-heading-weight, {base.get('font-weight', '600')})"
                base["font-family"] = "var(--cmp-heading-font, inherit)"
                base["text-transform"] = "var(--cmp-heading-transform, none)"
                base["letter-spacing"] = "var(--cmp-heading-letter-spacing, normal)"
            if name in theme.BUTTON_TOKENS:
                base["font-weight"] = f"var(--cmp-button-weight, {base.get('font-weight', '600')})"
                base["font-family"] = "var(--cmp-button-font, inherit)"
                base["text-transform"] = "var(--cmp-button-transform, none)"
                base["letter-spacing"] = "var(--cmp-button-letter-spacing, normal)"
                for corner in ("top-left", "top-right", "bottom-left", "bottom-right"):
                    base[f"border-{corner}-radius"] = "var(--cmp-button-radius)"
            if name in theme.BUTTON_BORDER_TOKENS:
                for side in ("top", "right", "bottom", "left"):
                    key = f"border-{side}-width"
                    if key in base and not base[key].startswith("var("):
                        base[key] = f"var(--cmp-button-border-width, {base[key]})"


_apply_cmp_theme()


def token_payload(tokens_dict=None):
    tokens = []
    for name, groups in (tokens_dict or TOKENS).items():
        declarations = []
        for group, styles in groups.items():
            for prop, value in styles.items():
                decl = {"property": prop, "value": value}
                if group == "@mobile":
                    decl["breakpoint"] = MOBILE
                elif group == "@tablet":
                    decl["breakpoint"] = TABLET
                elif group != "base":
                    decl["state"] = group
                declarations.append(decl)
        tokens.append({"name": name, "declarations": declarations})
    return {"tokens": tokens}


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    (OUT / "css-variables.json").write_text(json.dumps({"vars": {**THEME, **SEMANTIC}, "overwrite": True}, indent=1))
    (OUT / "tokens.json").write_text(json.dumps(token_payload(), indent=1))
    (OUT / "tokens-v2.json").write_text(json.dumps(token_payload(TOKENS_V2), indent=1))
    (OUT / "tokens-v3.json").write_text(json.dumps(token_payload(TOKENS_V3), indent=1))
    (OUT / "tokens-v4.json").write_text(json.dumps(token_payload(TOKENS_V4), indent=1))
    (OUT / "tokens-v5.json").write_text(json.dumps(token_payload(TOKENS_V5), indent=1))
    (OUT / "tokens-v6.json").write_text(json.dumps(token_payload(TOKENS_V6), indent=1))
    (OUT / "tokens-v7.json").write_text(json.dumps(token_payload(TOKENS_V7), indent=1))
    (OUT / "tokens-v8.json").write_text(json.dumps(token_payload(TOKENS_V8), indent=1))
    (OUT / "tokens-v9.json").write_text(json.dumps(token_payload(TOKENS_V9), indent=1))
    print("tokens:", len(TOKENS) + len(TOKENS_V2), "variables:", len(THEME) + len(SEMANTIC))
