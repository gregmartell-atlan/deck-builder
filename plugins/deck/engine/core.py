"""
Atlan Deck Engine v1.0 — Intelligent, Self-Healing Slide Builder

Usage in build scripts:
    import sys, os
    sys.path.insert(0, os.path.expanduser(
        '~/.claude/local-plugins/plugins/deck/engine'))
    from core import *

Sections:
    §1  Design Tokens          Colors, font, dimensions, spacing scale
    §2  Grid System             12-column layout, table column specs
    §3  Text Measurement        Width estimation, auto-font, overflow prediction
    §4  Request Buffer          Shape helpers, text-in-shape, standalone text
    §5  Native Tables           build_table() with col_type auto-sizing
    §6  Composite Helpers       pill, kpi_card, insight_card, phase_card, etc.
    §7  Storyboard Preview      Pre-build ASCII wireframe + pacing analysis
    §8  DEAL Reconciliation     Single source of truth for numbers
    §9  Validation Engine       Post-build checks (font, outline, overflow, etc.)
    §10 Self-Healing Loop       Auto-fix detected issues, retry, report
    §11 Build Infrastructure    Auth, flush, save_context, terminal output
"""

import re
import os
import sys
import json
import math
import time
import pickle
import subprocess
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple, Union


# ═══════════════════════════════════════════════════════════════════
# §1  DESIGN TOKENS
# ═══════════════════════════════════════════════════════════════════

# ── Primary ───────────────────────────────────────────────────────
BLUE   = {'red': 0.125, 'green': 0.149, 'blue': 0.824}   # #2026D2
CYAN   = {'red': 0.384, 'green': 0.882, 'blue': 0.988}   # #62E1FC
PINK   = {'red': 0.953, 'green': 0.302, 'blue': 0.467}   # #F34D77

# ── Text ──────────────────────────────────────────────────────────
DARK   = {'red': 0.169, 'green': 0.169, 'blue': 0.224}   # #2B2B39
GRAY   = {'red': 0.451, 'green': 0.451, 'blue': 0.588}   # #737396
WHITE  = {'red': 1.0,   'green': 1.0,   'blue': 1.0}

# ── Decorative / Background ──────────────────────────────────────
DKBLUE = {'red': 0.102, 'green': 0.122, 'blue': 0.710}
LTBG   = {'red': 0.957, 'green': 0.961, 'blue': 0.973}   # #F4F5F8
LTCYAN = {'red': 0.92,  'green': 0.97,  'blue': 0.99}
LTPINK = {'red': 1.0,   'green': 0.96,  'blue': 0.97}
LTGREEN= {'red': 0.93,  'green': 0.98,  'blue': 0.94}

# ── Status accents ────────────────────────────────────────────────
GREEN  = {'red': 0.086, 'green': 0.639, 'blue': 0.290}
ORANGE = {'red': 0.918, 'green': 0.345, 'blue': 0.047}

# ── Extended accent palette ───────────────────────────────────────
CORAL  = {'red': 1.0,   'green': 0.42,  'blue': 0.29}    # #FF6B4A
EMERALD= {'red': 0.0,   'green': 0.769, 'blue': 0.549}   # #00C48C
PURPLE = {'red': 0.608, 'green': 0.498, 'blue': 1.0}     # #9B7FFF
GOLD   = {'red': 1.0,   'green': 0.722, 'blue': 0.302}   # #FFB84D

# ── Color lookup (for validation) ─────────────────────────────────
BRAND_COLORS = {
    'BLUE': BLUE, 'CYAN': CYAN, 'PINK': PINK, 'DARK': DARK,
    'GRAY': GRAY, 'WHITE': WHITE, 'DKBLUE': DKBLUE, 'LTBG': LTBG,
    'LTCYAN': LTCYAN, 'LTPINK': LTPINK, 'LTGREEN': LTGREEN,
    'GREEN': GREEN, 'ORANGE': ORANGE, 'CORAL': CORAL,
    'EMERALD': EMERALD, 'PURPLE': PURPLE, 'GOLD': GOLD,
}


# ── Semantic Role Mapping ─────────────────────────────────────────
ROLE = {
    'ACTION':    BLUE,      # Primary calls to action, headers, solutions
    'HIGHLIGHT': CYAN,      # Secondary callouts, separators, key metrics
    'RISK':      CORAL,     # Risks, blockers, competitive threats
    'SUCCESS':   EMERALD,   # Outcomes, growth, achievements
    'AI':        PURPLE,    # AI/Innovation highlights
    'ATTENTION': GOLD,      # Notes, caveats, things needing focus
    'INFO':      GRAY,      # Secondary text, captions
    'ALERT':     PINK,      # High-priority warnings
    'NEUTRAL':   LTBG,      # Card backgrounds, subtle fills
}


def _color_key(rgb):
    """Round color components to 2 decimals for comparison."""
    if not rgb:
        return None
    return (round(rgb.get('red', 0), 2),
            round(rgb.get('green', 0), 2),
            round(rgb.get('blue', 0), 2))


NEUTRAL_COLORS = {
    _color_key(WHITE), _color_key(DARK),
    _color_key(GRAY), _color_key(LTBG),
}

# ── Typography ────────────────────────────────────────────────────
FONT = 'Space Grotesk'

TYPE_SCALE = {
    'slide_title':    20,
    'section_header': 28,
    'stat_number':    40,
    'subtitle':       12,
    'body':           11,
    'card_label':     10,
    'caption':        10,
    'pill':           10,
    'quote':          13,
    'table_header':   10,
    'table_body':     10,
}

# ── Dimensions ────────────────────────────────────────────────────
INCH = 914400
SW   = int(10.0 * INCH)
SH   = int(5.625 * INCH)

def emu(inches):
    """Convert inches to EMU."""
    return int(inches * INCH)

M = 0.5  # standard margin in inches

# ── Spacing Scale ─────────────────────────────────────────────────
SP = {
    'xs':  emu(0.08),    # tight internal padding
    'sm':  emu(0.15),    # card internal padding
    'md':  emu(0.225),   # gap between cards
    'lg':  emu(0.35),    # gap between groups
    'xl':  emu(0.5),     # margin
    '2xl': emu(0.75),    # section separation
    '3xl': emu(1.0),     # major vertical breaks
}


# ═══════════════════════════════════════════════════════════════════
# §2  GRID SYSTEM
# ═══════════════════════════════════════════════════════════════════

class Grid:
    """12-column, 8-row grid system for consistent slide layout.

    Usage:
        x, w = Grid.x(0, span=4)   # first 4 columns
        y, h = Grid.y(0, span=2)   # first 2 rows
        shape(oid, pid, x, y, w, h, BLUE)
    """
    COLS     = 12
    ROWS     = 8
    MARGIN_X = 0.5      # inches, left/right
    MARGIN_T = 1.0      # inches, top (below title area)
    MARGIN_B = 0.4      # inches, bottom
    GAP      = 0.225    # inches, between cells
    USABLE_W = 10.0 - 2 * 0.5                          # 9.0"
    USABLE_H = 5.625 - 1.0 - 0.4                       # 4.225"
    COL_W    = (USABLE_W - GAP * (COLS - 1)) / COLS    # ~0.5227"
    ROW_H    = (USABLE_H - GAP * (ROWS - 1)) / ROWS    # ~0.3344"

    @staticmethod
    def x(col, span=1):
        """Return (x_emu, width_emu) for grid column position."""
        x = Grid.MARGIN_X + col * (Grid.COL_W + Grid.GAP)
        w = span * Grid.COL_W + (span - 1) * Grid.GAP
        return emu(x), emu(w)

    @staticmethod
    def y(row, span=1):
        """Return (y_emu, height_emu) for grid row position."""
        y = Grid.MARGIN_T + row * (Grid.ROW_H + Grid.GAP)
        h = span * Grid.ROW_H + (span - 1) * Grid.GAP
        return emu(y), emu(h)

    @staticmethod
    def pos(col, row, col_span=1, row_span=1):
        """Return (x, y, w, h) in EMU for a grid cell."""
        x, w = Grid.x(col, col_span)
        y, h = Grid.y(row, row_span)
        return x, y, w, h

    @staticmethod
    def equal_cards(n, total_cols=12, start_col=0):
        """Return list of (x, w) tuples for n equal-width cards."""
        span = total_cols // n
        return [Grid.x(start_col + i * span, span) for i in range(n)]

    @staticmethod
    def title_area():
        """Return (x, y, w, h) for the standard title position."""
        return emu(M), emu(0.35), emu(9.0), emu(0.5)

    @staticmethod
    def subtitle_area():
        """Return (x, y, w, h) for the standard subtitle position."""
        return emu(M), emu(0.7), emu(9.0), emu(0.25)


# ═══════════════════════════════════════════════════════════════════
# §2b  LAYOUT ENGINE (Relative Positioning)
# ═══════════════════════════════════════════════════════════════════

class Layout:
    """Smart positioning helpers for relative stacks and groups.

    Usage:
        cards = Layout.distribute(3, emu(9.0), SP['md'], emu(M))
        x1, w1, x2, w2 = Layout.flex_split(emu(9.0), ratio=0.4)
        cx = Layout.center(emu(2.0), emu(9.0), emu(M))
    """

    @staticmethod
    def distribute(n, total_w_emu, gap_emu, start_x_emu=0):
        """Return list of (x, w) tuples for N items evenly spaced."""
        if n < 1:
            return []
        w = (total_w_emu - (n - 1) * gap_emu) // n
        return [(start_x_emu + i * (w + gap_emu), w) for i in range(n)]

    @staticmethod
    def flex_split(total_w_emu, ratio=0.5, gap_emu=None):
        """Return (x1, w1, x2, w2) for a two-column split."""
        gap = gap_emu if gap_emu is not None else SP['md']
        w1 = int((total_w_emu - gap) * ratio)
        w2 = total_w_emu - gap - w1
        return 0, w1, w1 + gap, w2

    @staticmethod
    def center(item_w_emu, container_w_emu, container_x_emu=0):
        """Return x_emu to center item_w in container_w."""
        return container_x_emu + (container_w_emu - item_w_emu) // 2

    @staticmethod
    def v_stack(items_h_emu, gap_emu, start_y_emu=0):
        """Return list of y_emu for a vertical stack of items."""
        y = start_y_emu
        result = []
        for h in items_h_emu:
            result.append(y)
            y += h + gap_emu
        return result


def group_elements(gid, oids):
    """Logically group multiple objects so they move together in the UI."""
    if not oids:
        return
    reqs.append({'groupObjects': {
        'groupObjectId': gid,
        'childrenObjectIds': oids}})


def connector(oid, pid, start_oid, end_oid, start_idx=0, end_idx=0,
              category='STRAIGHT', color=None, weight=1.0):
    """Create a smart line that plugs into two existing shapes.

    Connection site indexes for RECTANGLE: 0=Bottom, 1=Left, 2=Top, 3=Right.
    The line auto-follows if shapes are moved in the UI.
    """
    color = color or GRAY
    reqs.append({'createLine': {
        'objectId': oid, 'lineCategory': category,
        'elementProperties': {
            'pageObjectId': pid,
            'size': {'width': {'magnitude': 1, 'unit': 'EMU'},
                     'height': {'magnitude': 1, 'unit': 'EMU'}},
            'transform': {'scaleX': 1, 'scaleY': 1,
                          'translateX': 0, 'translateY': 0,
                          'unit': 'EMU'}}}})
    reqs.append({'updateLineProperties': {
        'objectId': oid,
        'fields': 'lineFill.solidFill.color,weight,startConnection,endConnection',
        'lineProperties': {
            'lineFill': {'solidFill': {'color': {'rgbColor': color}}},
            'weight': {'magnitude': weight, 'unit': 'PT'},
            'startConnection': {
                'connectedObjectId': start_oid,
                'connectionSiteIndex': start_idx},
            'endConnection': {
                'connectedObjectId': end_oid,
                'connectionSiteIndex': end_idx}}}})


# ── Table Column Type Specs ───────────────────────────────────────

COL_SPECS = {
    'label':    {'min_in': 2.0, 'max_in': 3.5, 'weight': 3.0},
    'price':    {'min_in': 1.0, 'max_in': 1.8, 'weight': 1.5},
    'status':   {'min_in': 0.7, 'max_in': 1.2, 'weight': 1.0},
    'detail':   {'min_in': 1.5, 'max_in': 3.0, 'weight': 2.0},
    'number':   {'min_in': 0.5, 'max_in': 1.0, 'weight': 1.0},
    'feature':  {'min_in': 1.2, 'max_in': 2.5, 'weight': 2.0},
    'owner':    {'min_in': 0.8, 'max_in': 1.5, 'weight': 1.2},
    'narrow':   {'min_in': 0.5, 'max_in': 0.8, 'weight': 0.7},
    'wide':     {'min_in': 2.5, 'max_in': 4.0, 'weight': 3.5},
}

def auto_col_widths(col_types, total_width_in=9.0):
    """Calculate consistent column widths from type specs.

    Every table using ['label', 'price', 'price', 'status'] gets
    identical proportions regardless of which slide it's on.
    """
    specs = [COL_SPECS[c] for c in col_types]
    total_weight = sum(s['weight'] for s in specs)

    # First pass: distribute by weight
    raw = [s['weight'] / total_weight * total_width_in for s in specs]

    # Second pass: clamp to min/max
    clamped = [max(s['min_in'], min(s['max_in'], r))
               for s, r in zip(specs, raw)]

    # Third pass: normalize to exactly fill total_width
    actual = sum(clamped)
    scale = total_width_in / actual
    final = [c * scale for c in clamped]

    return [emu(w) for w in final]


# ═══════════════════════════════════════════════════════════════════
# §3  TEXT MEASUREMENT
# ═══════════════════════════════════════════════════════════════════

# Space Grotesk character width factors (width / font_size_pt).
# Measured empirically. Good enough to prevent blowouts, not pixel-perfect.
_CHAR_NARROW = set('iIlL1|!.,;:\'"()[]{}')
_CHAR_WIDE   = set('mMwWOQDG@%#&')
_CHAR_DIGIT  = set('0123456789')
_CHAR_SPACE  = set(' ')

_WIDTH_FACTORS = {
    'narrow':  0.38,
    'digit':   0.56,
    'normal':  0.55,
    'bold':    0.60,
    'wide':    0.72,
    'space':   0.28,
}


def text_width_emu(text, font_pt, bold=False):
    """Estimate rendered text width in EMU for Space Grotesk."""
    if not text:
        return 0
    width_pts = 0
    for ch in text:
        if ch in _CHAR_SPACE:
            factor = _WIDTH_FACTORS['space']
        elif ch in _CHAR_NARROW:
            factor = _WIDTH_FACTORS['narrow']
        elif ch in _CHAR_WIDE:
            factor = _WIDTH_FACTORS['wide']
        elif ch in _CHAR_DIGIT:
            factor = _WIDTH_FACTORS['digit']
        elif bold:
            factor = _WIDTH_FACTORS['bold']
        else:
            factor = _WIDTH_FACTORS['normal']
        width_pts += font_pt * factor
    return int(width_pts * 12700)  # 1 pt = 12700 EMU


def auto_font(text, container_w_emu, max_sz=12, min_sz=7, bold=False,
              fill_ratio=0.90):
    """Find the largest font size that fits text in container."""
    target = int(container_w_emu * fill_ratio)
    for sz in range(max_sz, min_sz - 1, -1):
        if text_width_emu(text, sz, bold) <= target:
            return sz
    return min_sz


def will_fit(text, container_w_emu, font_pt, bold=False, fill_ratio=0.90):
    """Check if text fits in container at given font size."""
    return text_width_emu(text, font_pt, bold) <= int(container_w_emu * fill_ratio)


def lines_needed(text, container_w_emu, font_pt, bold=False):
    """Estimate how many lines text will wrap to."""
    if not text:
        return 0
    usable = container_w_emu * 0.90
    if usable <= 0:
        return 1
    w = text_width_emu(text, font_pt, bold)
    return max(1, math.ceil(w / usable))


def text_height_emu(text, container_w_emu, font_pt, bold=False,
                    line_spacing=1.3):
    """Estimate total rendered text height in EMU, accounting for wrap."""
    n = lines_needed(text, container_w_emu, font_pt, bold)
    line_h = font_pt * line_spacing * 12700
    return int(n * line_h)


def auto_container_height(text, container_w_emu, font_pt, bold=False,
                          padding_emu=None, line_spacing=1.3):
    """Calculate minimum container height for text with padding."""
    if padding_emu is None:
        padding_emu = SP['sm'] * 2
    content_h = text_height_emu(text, container_w_emu, font_pt, bold,
                                line_spacing)
    return content_h + padding_emu



# ═══════════════════════════════════════════════════════════════════
# §3b  INTELLIGENT SYNTHESIS
# ═══════════════════════════════════════════════════════════════════

def synthesize(text, limit=60):
    """LLM hook for rewriting dense text into slide-ready bullets.

    Currently a heuristic fallback—returns first sentence if over limit.
    In production, this would call a remote LLM to rewrite for the medium.
    """
    if not text:
        return ""
    if len(text) <= limit:
        return text
    sentences = text.split('.')
    return sentences[0].strip() + "."


# ═══════════════════════════════════════════════════════════════════
# §4  REQUEST BUFFER & SHAPE HELPERS
# ═══════════════════════════════════════════════════════════════════

# Module-level request buffer. Build scripts append here, then flush().
reqs = []


def shape(oid, pid, l, t, w, h, fill, stype='RECTANGLE'):
    """Create shape with fill, outline removed, vertical middle alignment."""
    reqs.extend([
        {'createShape': {
            'objectId': oid, 'shapeType': stype,
            'elementProperties': {'pageObjectId': pid,
                'size': {'width': {'magnitude': w, 'unit': 'EMU'},
                         'height': {'magnitude': h, 'unit': 'EMU'}},
                'transform': {'scaleX': 1, 'scaleY': 1,
                    'translateX': l, 'translateY': t, 'unit': 'EMU'}}}},
        {'updateShapeProperties': {
            'objectId': oid,
            'fields': 'shapeBackgroundFill.solidFill.color,'
                      'outline.propertyState,contentAlignment',
            'shapeProperties': {
                'shapeBackgroundFill': {
                    'solidFill': {'color': {'rgbColor': fill}}},
                'outline': {'propertyState': 'NOT_RENDERED'},
                'contentAlignment': 'MIDDLE'}}},
    ])


def bordered(oid, pid, l, t, w, h, fill, border, bw=1.0,
             stype='RECTANGLE'):
    """Shape with solid border + fill, vertical middle alignment."""
    reqs.extend([
        {'createShape': {
            'objectId': oid, 'shapeType': stype,
            'elementProperties': {'pageObjectId': pid,
                'size': {'width': {'magnitude': w, 'unit': 'EMU'},
                         'height': {'magnitude': h, 'unit': 'EMU'}},
                'transform': {'scaleX': 1, 'scaleY': 1,
                    'translateX': l, 'translateY': t, 'unit': 'EMU'}}}},
        {'updateShapeProperties': {
            'objectId': oid,
            'fields': 'shapeBackgroundFill.solidFill.color,'
                      'outline.outlineFill.solidFill.color,'
                      'outline.weight,contentAlignment',
            'shapeProperties': {
                'shapeBackgroundFill': {
                    'solidFill': {'color': {'rgbColor': fill}}},
                'contentAlignment': 'MIDDLE',
                'outline': {
                    'outlineFill': {
                        'solidFill': {'color': {'rgbColor': border}}},
                    'weight': {'magnitude': bw, 'unit': 'PT'}}}}},
    ])


def dashed(oid, pid, l, t, w, h, fill, border, bw=1.5,
           stype='ROUND_RECTANGLE'):
    """Shape with dashed border + vertical middle alignment."""
    reqs.extend([
        {'createShape': {
            'objectId': oid, 'shapeType': stype,
            'elementProperties': {'pageObjectId': pid,
                'size': {'width': {'magnitude': w, 'unit': 'EMU'},
                         'height': {'magnitude': h, 'unit': 'EMU'}},
                'transform': {'scaleX': 1, 'scaleY': 1,
                    'translateX': l, 'translateY': t, 'unit': 'EMU'}}}},
        {'updateShapeProperties': {
            'objectId': oid,
            'fields': 'shapeBackgroundFill.solidFill.color,'
                      'outline.outlineFill.solidFill.color,'
                      'outline.weight,outline.dashStyle,contentAlignment',
            'shapeProperties': {
                'shapeBackgroundFill': {
                    'solidFill': {'color': {'rgbColor': fill}}},
                'contentAlignment': 'MIDDLE',
                'outline': {
                    'outlineFill': {
                        'solidFill': {'color': {'rgbColor': border}}},
                    'weight': {'magnitude': bw, 'unit': 'PT'},
                    'dashStyle': 'DASH'}}}},
    ])


def text_in(oid, text, sz=8, bold=False, color=None, align='CENTER'):
    """Insert single-run text directly into an existing shape."""
    if not text:
        return
    color = color or DARK
    reqs.extend([
        {'updateShapeProperties': {
            'objectId': oid,
            'fields': 'contentAlignment',
            'shapeProperties': {'contentAlignment': 'MIDDLE'}}},
        {'insertText': {'objectId': oid, 'text': text}},
        {'updateTextStyle': {
            'objectId': oid,
            'textRange': {'type': 'ALL'},
            'style': {
                'fontFamily': FONT,
                'fontSize': {'magnitude': sz, 'unit': 'PT'},
                'bold': bold,
                'foregroundColor': {'opaqueColor': {'rgbColor': color}}},
            'fields': 'fontFamily,fontSize,bold,foregroundColor'}},
        {'updateParagraphStyle': {
            'objectId': oid,
            'textRange': {'type': 'ALL'},
            'style': {
                'alignment': align,
                'spaceAbove': {'magnitude': 0, 'unit': 'PT'},
                'spaceBelow': {'magnitude': 0, 'unit': 'PT'}},
            'fields': 'alignment,spaceAbove,spaceBelow'}},
    ])


def smart_text_in(oid, text, container_w_emu, max_sz=12, min_sz=7,
                  bold=False, color=None, align='CENTER'):
    """text_in() with auto-sized font to prevent overflow.

    Measures text width, picks the largest font that fits.
    Returns the chosen font size.
    """
    sz = auto_font(text, container_w_emu, max_sz, min_sz, bold)
    text_in(oid, text, sz, bold, color, align)
    return sz


def rich_in(oid, runs, align='START'):
    """Insert multi-run styled text directly into an existing shape.
    runs = [(text, sz, bold, color), ...]
    """
    if not runs:
        return
    reqs.append({'updateShapeProperties': {
        'objectId': oid,
        'fields': 'contentAlignment',
        'shapeProperties': {'contentAlignment': 'MIDDLE'}}})
    full = ''.join(r[0] for r in runs)
    if not full:
        return
    reqs.append({'insertText': {'objectId': oid, 'text': full}})
    idx = 0
    for txt_s, sz, bld, clr in runs:
        end = idx + len(txt_s)
        reqs.append({'updateTextStyle': {
            'objectId': oid,
            'textRange': {'type': 'FIXED_RANGE',
                          'startIndex': idx, 'endIndex': end},
            'style': {
                'fontFamily': FONT,
                'fontSize': {'magnitude': sz, 'unit': 'PT'},
                'bold': bld,
                'foregroundColor': {'opaqueColor': {'rgbColor': clr}}},
            'fields': 'fontFamily,fontSize,bold,foregroundColor'}})
        idx = end
    reqs.append({'updateParagraphStyle': {
        'objectId': oid,
        'textRange': {'type': 'ALL'},
        'style': {
            'alignment': align,
            'spaceAbove': {'magnitude': 0, 'unit': 'PT'},
            'spaceBelow': {'magnitude': 0, 'unit': 'PT'}},
        'fields': 'alignment,spaceAbove,spaceBelow'}})


def textbox(oid, pid, l, t, w, h, runs, align='START', valign='MIDDLE'):
    """Multi-run standalone text box. No shape behind.
    runs = [(text, sz, bold, color), ...]
    valign: 'MIDDLE' (default) or 'TOP' for multi-line lists
    """
    reqs.append({'createShape': {
        'objectId': oid, 'shapeType': 'TEXT_BOX',
        'elementProperties': {'pageObjectId': pid,
            'size': {'width': {'magnitude': w, 'unit': 'EMU'},
                     'height': {'magnitude': h, 'unit': 'EMU'}},
            'transform': {'scaleX': 1, 'scaleY': 1,
                'translateX': l, 'translateY': t, 'unit': 'EMU'}}}})
    reqs.append({'updateShapeProperties': {
        'objectId': oid,
        'fields': 'contentAlignment',
        'shapeProperties': {'contentAlignment': valign}}})
    full = ''.join(r[0] for r in runs)
    if not full:
        return
    reqs.append({'insertText': {'objectId': oid, 'text': full}})
    idx = 0
    for txt, sz, bld, clr in runs:
        end = idx + len(txt)
        reqs.append({'updateTextStyle': {
            'objectId': oid,
            'textRange': {'type': 'FIXED_RANGE',
                          'startIndex': idx, 'endIndex': end},
            'style': {
                'fontFamily': FONT,
                'fontSize': {'magnitude': sz, 'unit': 'PT'},
                'bold': bld,
                'foregroundColor': {'opaqueColor': {'rgbColor': clr}}},
            'fields': 'fontFamily,fontSize,bold,foregroundColor'}})
        idx = end
    reqs.append({'updateParagraphStyle': {
        'objectId': oid,
        'textRange': {'type': 'ALL'},
        'style': {
            'alignment': align,
            'spaceAbove': {'magnitude': 0, 'unit': 'PT'},
            'spaceBelow': {'magnitude': 0, 'unit': 'PT'}},
        'fields': 'alignment,spaceAbove,spaceBelow'}})


def label(oid, pid, l, t, w, h, text, sz=12, bold=False, color=None,
          align='START', valign='MIDDLE'):
    """Single-run standalone text box. No shape behind."""
    if not text:
        return
    color = color or DARK
    textbox(oid, pid, l, t, w, h, [(text, sz, bold, color)], align, valign)


def new_slide(sid):
    """Create blank slide."""
    reqs.append({'createSlide': {
        'objectId': sid,
        'slideLayoutReference': {'predefinedLayout': 'BLANK'}}})


def styled_element(oid, segments):
    """Replace text in existing element with auto-computed style indices.
    segments: [(text, font_size, bold, color), ...]
    Returns list of API requests — append with: reqs += styled_element(...)
    """
    full = ''.join(s[0] for s in segments)
    ops = [
        {'deleteText': {'objectId': oid, 'textRange': {'type': 'ALL'}}},
        {'insertText': {'objectId': oid, 'insertionIndex': 0, 'text': full}},
    ]
    idx = 0
    for text, sz, bld, color in segments:
        end = idx + len(text)
        s = {'fontFamily': FONT}
        fields = ['fontFamily']
        if sz:
            s['fontSize'] = {'magnitude': sz, 'unit': 'PT'}
            fields.append('fontSize')
        if bld is not None:
            s['bold'] = bld
            fields.append('bold')
        if color:
            s['foregroundColor'] = {'opaqueColor': {'rgbColor': color}}
            fields.append('foregroundColor')
        ops.append({'updateTextStyle': {
            'objectId': oid,
            'textRange': {'type': 'FIXED_RANGE',
                          'startIndex': idx, 'endIndex': end},
            'style': s,
            'fields': ','.join(fields)}})
        idx = end
    return ops


# ═══════════════════════════════════════════════════════════════════
# §5  NATIVE TABLES
# ═══════════════════════════════════════════════════════════════════

def build_table(tbl_id, slide_id, x, y, w, h, headers, rows,
                col_widths=None, col_types=None, totals=None):
    """Build a native Slides table with styled header, data rows, optional total.

    Pass col_types for consistent auto-sizing across slides:
        reqs += build_table(..., col_types=['label', 'price', 'price', 'status'])

    Or pass explicit col_widths for manual control:
        reqs += build_table(..., col_widths=[emu(3.0), emu(2.0), ...])
    """
    # Resolve column widths
    if col_types and not col_widths:
        col_widths = auto_col_widths(col_types, w / INCH)
    elif not col_widths:
        ncols = len(headers)
        col_widths = [emu((w / INCH) / ncols)] * ncols

    r = []
    nrows = 1 + len(rows) + (1 if totals else 0)
    ncols = len(headers)

    r.append({'createTable': {
        'objectId': tbl_id,
        'elementProperties': {'pageObjectId': slide_id,
            'size': {'width': {'magnitude': w, 'unit': 'EMU'},
                     'height': {'magnitude': h, 'unit': 'EMU'}},
            'transform': {'scaleX': 1, 'scaleY': 1,
                          'translateX': x, 'translateY': y, 'unit': 'EMU'}},
        'rows': nrows, 'columns': ncols}})

    for ci, cw in enumerate(col_widths):
        r.append({'updateTableColumnProperties': {
            'objectId': tbl_id, 'columnIndices': [ci],
            'tableColumnProperties': {
                'columnWidth': {'magnitude': cw, 'unit': 'EMU'}},
            'fields': 'columnWidth'}})

    def cell(ri, ci, text, sz=9, bold=False, color=DARK, bg=None):
        if text:
            r.append({'insertText': {
                'objectId': tbl_id,
                'cellLocation': {'rowIndex': ri, 'columnIndex': ci},
                'text': text, 'insertionIndex': 0}})
            r.append({'updateTextStyle': {
                'objectId': tbl_id,
                'cellLocation': {'rowIndex': ri, 'columnIndex': ci},
                'textRange': {'type': 'ALL'},
                'style': {
                    'fontFamily': FONT,
                    'fontSize': {'magnitude': sz, 'unit': 'PT'},
                    'bold': bold,
                    'foregroundColor': {'opaqueColor': {'rgbColor': color}}},
                'fields': 'fontFamily,fontSize,bold,foregroundColor'}})
            r.append({'updateParagraphStyle': {
                'objectId': tbl_id,
                'cellLocation': {'rowIndex': ri, 'columnIndex': ci},
                'textRange': {'type': 'ALL'},
                'style': {
                    'alignment': 'START',
                    'spaceAbove': {'magnitude': 2, 'unit': 'PT'},
                    'spaceBelow': {'magnitude': 2, 'unit': 'PT'}},
                'fields': 'alignment,spaceAbove,spaceBelow'}})
        props = {'contentAlignment': 'MIDDLE'}
        fields = 'contentAlignment'
        if bg:
            props['tableCellBackgroundFill'] = {
                'solidFill': {'color': {'rgbColor': bg}}}
            fields += ',tableCellBackgroundFill.solidFill.color'
        r.append({'updateTableCellProperties': {
            'objectId': tbl_id,
            'tableRange': {'location': {'rowIndex': ri, 'columnIndex': ci},
                           'rowSpan': 1, 'columnSpan': 1},
            'tableCellProperties': props, 'fields': fields}})

    # Header row
    for ci, h in enumerate(headers):
        cell(0, ci, h, TYPE_SCALE['table_header'], True, WHITE, BLUE)

    # Data rows (alternating bg)
    for ri, row in enumerate(rows):
        bg = WHITE if ri % 2 == 0 else LTBG
        for ci, val in enumerate(row):
            cell(ri + 1, ci, val, TYPE_SCALE['table_body'], False, DARK, bg)

    # Total row
    if totals:
        tr = len(rows) + 1
        for ci, val in enumerate(totals):
            cell(tr, ci, val, TYPE_SCALE['table_header'], True, WHITE, BLUE)

    # Invisible borders
    r.append({'updateTableBorderProperties': {
        'objectId': tbl_id,
        'tableRange': {'location': {'rowIndex': 0, 'columnIndex': 0},
                       'rowSpan': nrows, 'columnSpan': ncols},
        'borderPosition': 'ALL',
        'tableBorderProperties': {
            'weight': {'magnitude': 0.1, 'unit': 'PT'},
            'dashStyle': 'SOLID',
            'tableBorderFill': {
                'solidFill': {'color': {'rgbColor': WHITE}}}},
        'fields': 'weight,dashStyle,tableBorderFill.solidFill.color'}})

    # Subtle inner horizontal dividers
    for ri in range(1, nrows - 1):
        r.append({'updateTableBorderProperties': {
            'objectId': tbl_id,
            'tableRange': {'location': {'rowIndex': ri, 'columnIndex': 0},
                           'rowSpan': 1, 'columnSpan': ncols},
            'borderPosition': 'BOTTOM',
            'tableBorderProperties': {
                'weight': {'magnitude': 0.5, 'unit': 'PT'},
                'dashStyle': 'SOLID',
                'tableBorderFill': {'solidFill': {'color': {'rgbColor': {
                    'red': 0.9, 'green': 0.9, 'blue': 0.93}}}}},
            'fields': 'weight,dashStyle,tableBorderFill.solidFill.color'}})

    return r


# ── Proposal Table Defaults ───────────────────────────────────────
# Canonical position and sizing for proposal/comparison tables.
# All option tables in a deck share these values for visual consistency.

PROPOSAL_TABLE = {
    'x': emu(0.52),   'y': emu(1.41),
    'w': emu(9.16),   'h': emu(3.28),
    'col_types_3col': ['label', 'detail', 'price', 'price'],
    'col_types_4col': ['label', 'detail', 'price', 'price'],
}


def proposal_table(tbl_id, slide_id, headers, rows, totals=None,
                   col_types=None):
    """Standard proposal table at the canonical position.

    All option/comparison tables in a deck should use this so they
    share identical positioning, column widths, and sizing.
    """
    ct = col_types or PROPOSAL_TABLE['col_types_4col']
    return build_table(
        tbl_id, slide_id,
        PROPOSAL_TABLE['x'], PROPOSAL_TABLE['y'],
        PROPOSAL_TABLE['w'], PROPOSAL_TABLE['h'],
        headers, rows, col_types=ct, totals=totals)


# ── Option Pill Vocabulary ────────────────────────────────────────
# Semantic color mapping for proposal pills. Consistent across all decks.

OPTION_PILLS = {
    'basic':       {'bg': CORAL,   'text': 'OPTION 1'},
    'recommended': {'bg': EMERALD, 'text': 'OPTION 2  \u00b7  RECOMMENDED'},
    'comparison':  {'bg': DKBLUE,  'text': 'SIDE-BY-SIDE COMPARISON'},
    'summary':     {'bg': DKBLUE,  'text': 'SUMMARY'},
    'internal':    {'bg': GRAY,    'text': 'INTERNAL'},
}


def option_pill(oid, pid, l, t, option_key):
    """Semantic option pill from OPTION_PILLS vocabulary."""
    spec = OPTION_PILLS[option_key]
    pill(oid, pid, l, t, spec['text'], spec['bg'])


# ═══════════════════════════════════════════════════════════════════
# §6  COMPOSITE HELPERS
# ═══════════════════════════════════════════════════════════════════

def pill(oid, pid, l, t, text, bg=None, tc=None, w=None):
    """Colored pill label with auto-width sizing.

    Width auto-calculates from text length if not specified.
    Minimum 1.2", maximum 3.0", with 0.4" padding.
    """
    bg = bg or BLUE; tc = tc or WHITE
    if w is None:
        text_w = text_width_emu(text, TYPE_SCALE['pill'], bold=True)
        w = max(emu(1.2), min(emu(3.0), text_w + emu(0.4)))
    shape(oid, pid, l, t, w, emu(0.24), bg, 'ROUND_RECTANGLE')
    text_in(oid, text, TYPE_SCALE['pill'], True, tc, 'CENTER')


def kpi_card(oid, pid, l, t, w, h, value, lbl, accent=None, bg=None):
    """Metric card with accent top bar."""
    accent = accent or BLUE; bg = bg or LTBG
    shape(oid, pid, l, t, w, h, bg)
    shape(oid + '_bar', pid, l, t, w, emu(0.04), accent)
    textbox(oid + '_t', pid, l + SP['sm'], t + SP['sm'],
            w - 2 * SP['sm'], h - 2 * SP['sm'],
            [(value + '\n', TYPE_SCALE['stat_number'], True, accent),
             (lbl, TYPE_SCALE['card_label'], False, GRAY)], 'CENTER')


def insight_card(oid, pid, l, t, w, h, lbl, title, body, accent, bg):
    """Insight with accent bar + label + title + body."""
    shape(oid, pid, l, t, w, h, bg)
    shape(oid + '_bar', pid, l, t, emu(0.04), h, accent)
    textbox(oid + '_t', pid, l + SP['sm'], t + SP['xs'],
            w - emu(0.25), h - emu(0.2),
            [(lbl + '\n', TYPE_SCALE['caption'], True, accent),
             (title + '\n', TYPE_SCALE['body'], True, DARK),
             (body, TYPE_SCALE['card_label'], False, GRAY)])


def action_card(oid, pid, l, t, w, h, num, title, desc, owner, timeline):
    """Numbered action item with blue accent circle."""
    shape(oid, pid, l, t, w, h, LTBG)
    shape(oid + '_circ', pid, l + emu(0.12), t + emu(0.12),
          emu(0.32), emu(0.32), BLUE, 'ELLIPSE')
    text_in(oid + '_circ', str(num), 14, True, WHITE, 'CENTER')
    textbox(oid + '_t', pid, l + emu(0.55), t + emu(0.1),
            w - emu(0.7), h - emu(0.2),
            [(title + '\n', TYPE_SCALE['subtitle'], True, DARK),
             (desc + '\n', TYPE_SCALE['card_label'], False, GRAY),
             (f'{owner} \u00b7 {timeline}', TYPE_SCALE['caption'],
              True, BLUE)])


def feature_card(oid, pid, l, t, w, h, name, detail_text, status,
                 accent, bg=None):
    """Feature status card."""
    bg = bg or LTBG
    shape(oid, pid, l, t, w, h, bg)
    shape(oid + '_bar', pid, l, t, emu(0.04), h, accent)
    textbox(oid + '_t', pid, l + SP['sm'], t + SP['xs'],
            w - emu(0.25), h - emu(0.16),
            [(name + '\n', TYPE_SCALE['body'], True, DARK),
             (detail_text + '\n', TYPE_SCALE['card_label'], False, GRAY),
             (status, TYPE_SCALE['caption'], True, accent)])


def benefit_card(oid, pid, l, t, w, h, tag, title, body, footnote,
                 accent, bg=None):
    """4-layer benefit card: tag + title + body + footnote.

    Modeled on the Zoom v4 "What This Means" slide — each card explains
    one customer benefit with context.

    Layout (left accent bar + 4 text zones):
        ┌──────────────────────────┐
        │ TAG            (10pt bold, accent)
        │ Title          (14pt bold, DARK)
        │ Body text      (11pt, GRAY)
        │ Footnote       (10pt, GRAY)
        └──────────────────────────┘
    """
    bg = bg or WHITE
    shape(oid, pid, l, t, w, h, bg, 'ROUND_RECTANGLE')
    shape(oid + '_bar', pid, l, t, emu(0.04), h, accent)
    # Tag
    textbox(oid + '_tag', pid, l + emu(0.18), t + emu(0.10),
            w - emu(0.3), emu(0.20),
            [(tag, 10, True, accent)], 'START')
    # Title
    textbox(oid + '_t', pid, l + emu(0.18), t + emu(0.32),
            w - emu(0.3), emu(0.30),
            [(title, 14, True, DARK)], 'START')
    # Body
    textbox(oid + '_b', pid, l + emu(0.18), t + emu(0.65),
            w - emu(0.3), h - emu(1.05),
            [(body, TYPE_SCALE['body'], False, GRAY)], 'START', 'TOP')
    # Footnote
    if footnote:
        textbox(oid + '_fn', pid, l + emu(0.18), t + h - emu(0.30),
                w - emu(0.3), emu(0.20),
                [(footnote, 10, False, GRAY)], 'START')


def numbered_circle(oid, pid, l, t, num, bg=None, sz=0.36):
    """Colored numbered circle."""
    bg = bg or CORAL
    shape(oid, pid, l, t, emu(sz), emu(sz), bg, 'ELLIPSE')
    text_in(oid, str(num), 14, True, WHITE, 'CENTER')


def quote_block(oid, pid, l, t, w, quote_text, attribution, accent=None):
    """Quote with left accent bar + attribution."""
    accent = accent or BLUE
    h = emu(1.2)
    shape(oid + '_bar', pid, l, t, emu(0.04), h, accent)
    textbox(oid + '_t', pid, l + SP['sm'], t, w - SP['sm'], h,
            [(f'\u201c{quote_text}\u201d\n', TYPE_SCALE['quote'],
              False, DARK),
             (f'\u2014 {attribution}', 10, False, GRAY)])


def phase_card(oid, pid, l, t, num, title, timeframe, items, owner):
    """Single phase in a phased plan layout."""
    w, h = emu(2.1), emu(2.5)
    shape(oid, pid, l, t, w, h, LTBG)
    shape(oid + '_bar', pid, l, t, w, emu(0.04), BLUE)
    numbered_circle(oid + '_n', pid, l + emu(0.85), t + emu(0.12),
                    num, BLUE, 0.32)
    textbox(oid + '_t', pid, l + emu(0.1), t + emu(0.5),
            w - emu(0.2), emu(0.3),
            [(title + '\n', TYPE_SCALE['subtitle'], True, DARK),
             (timeframe, TYPE_SCALE['card_label'], False, GRAY)], 'CENTER')
    items_text = '\n'.join(f'\u2022 {item}' for item in items)
    textbox(oid + '_i', pid, l + SP['sm'], t + emu(1.1),
            w - emu(0.3), emu(1.0),
            [(items_text, TYPE_SCALE['card_label'], False, DARK)],
            'START', 'TOP')
    textbox(oid + '_o', pid, l + emu(0.1), t + emu(2.2),
            w - emu(0.2), emu(0.25),
            [(owner, TYPE_SCALE['caption'], True, BLUE)], 'CENTER')


def sheets_chart(oid, pid, spreadsheet_id, chart_id, l, t, w, h):
    """Embed linked Google Sheets chart."""
    reqs.append({'createSheetsChart': {
        'objectId': oid,
        'spreadsheetId': spreadsheet_id, 'chartId': chart_id,
        'linkingMode': 'LINKED',
        'elementProperties': {'pageObjectId': pid,
            'size': {'width': {'magnitude': w, 'unit': 'EMU'},
                     'height': {'magnitude': h, 'unit': 'EMU'}},
            'transform': {'scaleX': 1, 'scaleY': 1,
                'translateX': l, 'translateY': t, 'unit': 'EMU'}}}})


# ═══════════════════════════════════════════════════════════════════
# §6b  TIMELINE TEMPLATES
# ═══════════════════════════════════════════════════════════════════

def timeline_staggered(pid, months, bars, milestones, cards,
                       note_text=None, title_text='Implementation Timeline'):
    """Staggered bar timeline — diagonal cascade with circle endpoints,
    diamond milestones, and description cards below.

    Args:
        pid: slide objectId
        months: list of month labels, e.g. ['APR','MAY','JUN','JUL','AUG','SEP']
        bars: list of (name, start_float, end_float, color) — position in month units
        milestones: list of (col_pos, title, detail, color) for milestone markers
        cards: list of (title, desc, color) for bottom description cards
        note_text: optional footer note string
        title_text: slide title
    """
    pill(f'{pid}_pill', pid, emu(M), emu(0.3), 'IMPLEMENTATION ROADMAP', BLUE, WHITE)
    label(f'{pid}_title', pid, emu(M), emu(0.65), emu(9.0), emu(0.35),
          title_text, 20, True, DARK, 'START')

    col_w = emu(1.3)
    grid_left = emu(1.1)

    # Month headers
    for i, m in enumerate(months):
        shape(f'{pid}_mh{i}', pid, grid_left + i * col_w, emu(1.2),
              col_w - emu(0.05), emu(0.28), LTBG, 'ROUND_RECTANGLE')
        text_in(f'{pid}_mh{i}', m, 8, True, GRAY)

    # Grid lines
    for i in range(len(months) + 1):
        shape(f'{pid}_gl{i}', pid, grid_left + i * col_w - emu(0.025),
              emu(1.55), emu(0.005), emu(2.3), LTBG)

    # Staggered bars
    bar_h = emu(0.32)
    for bi, (bname, start, end, accent) in enumerate(bars):
        y_pos = emu(1.65 + bi * 0.5)
        bx = grid_left + emu(start * 1.3)
        bw = emu((end - start) * 1.3)
        oid = f'{pid}_bar{bi}'

        light = {k: min(1.0, v * 0.25 + 0.75) for k, v in accent.items()}
        shape(oid, pid, bx, y_pos, bw, bar_h, light, 'ROUND_RECTANGLE')

        # Circle endpoints
        shape(f'{oid}_lc', pid, bx - emu(0.06), y_pos + emu(0.07),
              emu(0.18), emu(0.18), WHITE, 'ELLIPSE')
        shape(f'{oid}_ld', pid, bx - emu(0.02), y_pos + emu(0.11),
              emu(0.10), emu(0.10), accent, 'ELLIPSE')
        rx = bx + bw - emu(0.12)
        shape(f'{oid}_rc', pid, rx, y_pos + emu(0.07),
              emu(0.18), emu(0.18), WHITE, 'ELLIPSE')
        shape(f'{oid}_rd', pid, rx + emu(0.04), y_pos + emu(0.11),
              emu(0.10), emu(0.10), accent, 'ELLIPSE')

        # Diamond milestone at ~55%
        shape(f'{oid}_dia', pid, bx + bw * 0.55, y_pos + emu(0.06),
              emu(0.20), emu(0.20), accent, 'DIAMOND')

        # Bar label
        textbox(f'{oid}_name', pid, bx + emu(0.15), y_pos + emu(0.02),
                bw - emu(0.3), bar_h - emu(0.04),
                [(bname, 8, True, DARK)], 'START')

    # Milestone labels
    ml_y = emu(1.65 + len(bars) * 0.5 + 0.15)
    for mi, (col_pos, ml_title, ml_detail, accent) in enumerate(milestones):
        mx = grid_left + emu(col_pos * 1.3)
        oid = f'{pid}_ml{mi}'
        shape(f'{oid}_dia', pid, mx, ml_y, emu(0.16), emu(0.16), accent, 'DIAMOND')
        textbox(f'{oid}_title', pid, mx + emu(0.22), ml_y - emu(0.03),
                emu(1.8), emu(0.2), [(ml_title, 10, True, DARK)], 'START')
        textbox(f'{oid}_date', pid, mx + emu(0.22), ml_y + emu(0.17),
                emu(1.8), emu(0.18), [(ml_detail, 8, False, accent)], 'START')

    # Description cards
    card_y = emu(4.25)
    card_w = emu(9.0 / len(cards) - 0.1)
    for ci, (ctitle, cdesc, accent) in enumerate(cards):
        cx = emu(M) + ci * (card_w + emu(0.1))
        oid = f'{pid}_card{ci}'
        shape(oid, pid, cx, card_y, card_w, emu(0.9), WHITE, 'ROUND_RECTANGLE')
        shape(f'{oid}_bar', pid, cx, card_y, emu(0.04), emu(0.9), accent)
        shape(f'{oid}_dot', pid, cx + emu(0.14), card_y + emu(0.12),
              emu(0.12), emu(0.12), accent, 'ELLIPSE')
        textbox(f'{oid}_t', pid, cx + emu(0.32), card_y + emu(0.08),
                card_w - emu(0.4), emu(0.2), [(ctitle, 9, True, DARK)], 'START')
        textbox(f'{oid}_d', pid, cx + emu(0.14), card_y + emu(0.35),
                card_w - emu(0.24), emu(0.5), [(cdesc, 8, False, GRAY)], 'START', 'TOP')

    # Optional note
    if note_text:
        shape(f'{pid}_note', pid, emu(M), emu(5.25), emu(9.0), emu(0.25), LTPINK)
        shape(f'{pid}_noteacc', pid, emu(M), emu(5.25), emu(0.04), emu(0.25), CORAL)
        textbox(f'{pid}_notet', pid, emu(0.7), emu(5.27), emu(8.5), emu(0.2),
                [(note_text, 8, False, DARK)], 'START')


def timeline_cascading(pid, months, arrows, descs,
                       note_text=None, title_text='Tentative Implementation Timeline'):
    """Cascading arrow timeline — stepped arrow bars with month header,
    alternating row backgrounds, and description cards below.

    Args:
        pid: slide objectId
        months: list of month labels
        arrows: list of (name, start_col, span_cols, row, color)
        descs: list of (title, desc, color) for bottom description cards
        note_text: optional footer note
        title_text: slide title
    """
    pill(f'{pid}_pill', pid, emu(M), emu(0.3), 'IMPLEMENTATION ROADMAP', BLUE, WHITE)
    label(f'{pid}_title', pid, emu(M), emu(0.65), emu(9.0), emu(0.35),
          title_text, 20, True, DARK, 'START')

    col_w = emu(1.3)
    grid_left = emu(1.1)

    # Month header bar
    shape(f'{pid}_mhbar', pid, grid_left, emu(1.15),
          col_w * len(months) - emu(0.05), emu(0.32), BLUE, 'ROUND_RECTANGLE')
    for i, m in enumerate(months):
        textbox(f'{pid}_mh{i}', pid, grid_left + i * col_w, emu(1.15),
                col_w, emu(0.32), [(m, 9, True, WHITE)], 'CENTER')

    # Row backgrounds
    row_h = emu(0.52)
    row_start = emu(1.55)
    n_rows = max(a[3] for a in arrows) + 1
    for ri in range(n_rows):
        bg = LTBG if ri % 2 == 0 else WHITE
        shape(f'{pid}_rowbg{ri}', pid, grid_left, row_start + ri * row_h,
              col_w * len(months) - emu(0.05), row_h, bg)

    # Arrow bars
    for ai, (aname, start, span, row, accent) in enumerate(arrows):
        y = row_start + row * row_h + emu(0.06)
        bx = grid_left + emu(start * 1.3)
        bw = emu(span * 1.3)
        bh = row_h - emu(0.12)
        oid = f'{pid}_arrow{ai}'

        shape(oid, pid, bx, y, bw - emu(0.15), bh, accent, 'ROUND_RECTANGLE')
        text_in(oid, aname, 8, True, WHITE)
        shape(f'{oid}_tip', pid, bx + bw - emu(0.25), y,
              emu(0.25), bh, accent, 'RIGHT_ARROW')

    # Description cards
    card_y = emu(row_start / 914400 + n_rows * 0.52 / 914400 + 0.3)
    # Simpler: fixed position
    card_y = emu(4.25)
    card_w = emu(9.0 / len(descs) - 0.1)
    for di, (dtitle, ddesc, accent) in enumerate(descs):
        dx = emu(M) + di * (card_w + emu(0.1))
        oid = f'{pid}_desc{di}'
        textbox(f'{oid}_t', pid, dx, card_y, card_w, emu(0.22),
                [(dtitle, 9, True, accent)], 'CENTER')
        textbox(f'{oid}_b', pid, dx, card_y + emu(0.25), card_w, emu(0.65),
                [(ddesc, 8, False, GRAY)], 'CENTER', 'TOP')

    if note_text:
        label(f'{pid}_foot', pid, emu(M), emu(5.25), emu(9.0), emu(0.2),
              note_text, 8, False, GRAY, 'START')


def timeline_waterfall(pid, phases, month_strip,
                       title_text='Implementation Phases'):
    """Waterfall block timeline — descending colored blocks with date labels
    on the left and a month strip at the bottom.

    Args:
        pid: slide objectId
        phases: list of (name, desc, date_range, color) — max 3-4
        month_strip: list of month labels for the bottom bar
        title_text: slide title
    """
    pill(f'{pid}_pill', pid, emu(M), emu(0.3), 'IMPLEMENTATION ROADMAP', BLUE, WHITE)
    label(f'{pid}_title', pid, emu(M), emu(0.65), emu(9.0), emu(0.35),
          title_text, 20, True, DARK, 'START')

    block_w_base = emu(5.0)
    block_h = emu(0.55)
    start_x = emu(2.0)
    start_y = emu(1.4)

    for pi, (pname, pdesc, dates, accent) in enumerate(phases):
        # Each block shifts right and shrinks slightly
        bx = start_x + emu(pi * 0.8)
        by = start_y + emu(pi * 0.75)
        bw = block_w_base - emu(pi * 0.5)
        oid = f'{pid}_phase{pi}'

        shape(oid, pid, bx, by, bw, block_h, accent, 'ROUND_RECTANGLE')
        text_in(oid, pname, 10, True, WHITE)

        # Date label to the left
        textbox(f'{oid}_dates', pid, emu(M), by + emu(0.05),
                emu(1.3), block_h - emu(0.1),
                [(dates, 8, True, GRAY)], 'END')

    # Description cards below
    card_y = start_y + emu(len(phases) * 0.75 + 0.4)
    card_w = emu(9.0 / len(phases) - 0.15)
    for pi, (pname, pdesc, dates, accent) in enumerate(phases):
        cx = emu(M) + pi * (card_w + emu(0.15))
        oid = f'{pid}_card{pi}'
        shape(f'{oid}_dot', pid, cx, card_y, emu(0.14), emu(0.14), accent, 'ELLIPSE')
        textbox(f'{oid}_t', pid, cx + emu(0.2), card_y - emu(0.03),
                card_w - emu(0.25), emu(0.2), [(pname, 10, True, DARK)], 'START')
        textbox(f'{oid}_d', pid, cx + emu(0.2), card_y + emu(0.2),
                card_w - emu(0.25), emu(0.5), [(pdesc, 9, False, GRAY)], 'START', 'TOP')

    # Month strip at bottom
    strip_y = emu(4.6)
    strip_w = emu(9.0 / len(month_strip))
    # Gradient bar
    shape(f'{pid}_strip', pid, emu(M), strip_y,
          emu(9.0), emu(0.35), BLUE, 'ROUND_RECTANGLE')
    for mi, m in enumerate(month_strip):
        textbox(f'{pid}_ms{mi}', pid, emu(M) + mi * strip_w, strip_y,
                strip_w, emu(0.35), [(m, 8, True, WHITE)], 'CENTER')


# ═══════════════════════════════════════════════════════════════════
# §6c  SLIDE TEMPLATES (v4.1)
# ═══════════════════════════════════════════════════════════════════

DEFAULT_ACCENT_ROTATION = [BLUE, CYAN, EMERALD, PURPLE, PINK, GOLD]


def chevron_flow(pid, steps, title_text='Process Overview',
                 note_text=None):
    """Full-slide horizontal chevron flow diagram.

    Args:
        pid: slide objectId
        steps: list of (label, description, color) tuples
            e.g. [('Discover', 'Map data sources', BLUE),
                  ('Build', 'Integrations & model', CYAN),
                  ('Adopt', 'Rollout & training', EMERALD),
                  ('Scale', 'Expand domains', PURPLE)]
            Supports 3-6 steps. Colors default to accent rotation if None.
        title_text: slide title
        note_text: optional footer note
    """
    n = len(steps)
    pill(f'{pid}_pill', pid, emu(M), emu(0.3), title_text.upper()[:30], BLUE, WHITE)
    label(f'{pid}_title', pid, emu(M), emu(0.65), emu(9.0), emu(0.35),
          title_text, 20, True, DARK, 'START')

    # Distribute chevrons across slide width
    chevrons = Layout.distribute(n, emu(9.0), emu(0.05), emu(M))
    chev_y = emu(1.6)
    chev_h = emu(0.7)
    desc_y = chev_y + chev_h + emu(0.2)

    for i, ((cx, cw), (lbl, desc, color)) in enumerate(zip(chevrons, steps)):
        color = color or DEFAULT_ACCENT_ROTATION[i % len(DEFAULT_ACCENT_ROTATION)]
        oid = f'{pid}_ch{i}'

        # Chevron shape
        shape(oid, pid, cx, chev_y, cw, chev_h, color, 'CHEVRON')
        text_in(oid, lbl, 10, True, WHITE, 'CENTER')

        # Description card below
        textbox(f'{oid}_desc', pid, cx, desc_y, cw, emu(1.2),
                [(lbl + '\n', 9, True, color),
                 (desc, 8, False, GRAY)], 'CENTER')

    if note_text:
        shape(f'{pid}_note_bg', pid, emu(M), emu(4.8), emu(9.0), emu(0.5), LTBG,
              'ROUND_RECTANGLE')
        textbox(f'{pid}_note', pid, emu(M + 0.15), emu(4.85), emu(8.7), emu(0.4),
                [(note_text, 8, False, GRAY)], 'START')


def funnel(pid, stages, title_text='Adoption Funnel',
           note_text=None):
    """Full-slide funnel diagram with tapering stages.

    Args:
        pid: slide objectId
        stages: list of (label, description, color) tuples
            e.g. [('Awareness', '500 users invited', BLUE),
                  ('Activation', '200 logged in first week', CYAN),
                  ('Adoption', '80 weekly active', EMERALD),
                  ('Advocacy', '15 power users', PURPLE)]
            Supports 3-6 stages. Width tapers from widest to narrowest.
        title_text: slide title
        note_text: optional footer note
    """
    n = len(stages)
    pill(f'{pid}_pill', pid, emu(M), emu(0.3), title_text.upper()[:30], BLUE, WHITE)
    label(f'{pid}_title', pid, emu(M), emu(0.65), emu(9.0), emu(0.35),
          title_text, 20, True, DARK, 'START')

    max_w = emu(6.0)
    min_w = emu(2.5)
    stage_h = emu(0.55)
    gap = emu(0.08)
    start_y = emu(1.3)
    desc_x_offset = emu(0.3)

    y_positions = Layout.v_stack([stage_h] * n, gap, start_y)

    for i, (y, (lbl, desc, color)) in enumerate(zip(y_positions, stages)):
        color = color or DEFAULT_ACCENT_ROTATION[i % len(DEFAULT_ACCENT_ROTATION)]
        oid = f'{pid}_st{i}'

        w = int(max_w - i * (max_w - min_w) / max(n - 1, 1))
        x = Layout.center(w, emu(SW))

        shape(oid, pid, x, y, w, stage_h, color, 'ROUND_RECTANGLE')
        text_in(oid, lbl, 11, True, WHITE, 'CENTER')

        desc_x = x + w + desc_x_offset
        desc_w = emu(SW) - desc_x - emu(M)
        if desc_w > emu(0.5):
            textbox(f'{oid}_desc', pid, desc_x, y, desc_w, stage_h,
                    [(desc, 9, False, GRAY)], 'START')

    if note_text:
        note_y = y_positions[-1] + stage_h + emu(0.4)
        shape(f'{pid}_note_bg', pid, emu(M), note_y, emu(9.0), emu(0.5), LTBG,
              'ROUND_RECTANGLE')
        textbox(f'{pid}_note', pid, emu(M + 0.15), note_y + emu(0.05),
                emu(8.7), emu(0.4), [(note_text, 8, False, GRAY)], 'START')


SCORE_SCALE_COLORS = [PINK, ORANGE, GOLD, EMERALD]
SCORE_SCALE_LABELS = ['Needs Work', 'Fair', 'Good', 'Excellent']


def score_card(pid, criteria, scores, scale_labels=None,
               scale_colors=None, title_text='Health Score Card',
               note_text=None):
    """Full-slide scoring rubric with colored scale.

    Args:
        pid: slide objectId
        criteria: list of strings, e.g. ['Data Quality', 'Adoption', 'Governance']
        scores: list of ints (1-based), e.g. [2, 3, 4] — which column gets the marker
        scale_labels: list of column headers, default ['Needs Work','Fair','Good','Excellent']
        scale_colors: list of colors for headers, default [PINK, ORANGE, GOLD, EMERALD]
        title_text: slide title
        note_text: optional footer note
    """
    labels = scale_labels or SCORE_SCALE_LABELS
    colors = scale_colors or SCORE_SCALE_COLORS
    ncols = len(labels)

    pill(f'{pid}_pill', pid, emu(M), emu(0.3), title_text.upper()[:30], BLUE, WHITE)
    label(f'{pid}_title', pid, emu(M), emu(0.65), emu(9.0), emu(0.35),
          title_text, 20, True, DARK, 'START')

    # Build headers: "Criteria" + scale labels
    headers = ['Criteria'] + labels

    # Build rows: criteria name + score markers
    rows = []
    for ci, (crit, score) in enumerate(zip(criteria, scores)):
        row = [crit]
        for si in range(ncols):
            if si + 1 == score:
                row.append('\u25cf')  # filled circle
            else:
                row.append('\u25cb')  # open circle
        rows.append(row)

    # Add legend row
    rows.append([''] + labels)

    # Column widths: criteria col wide, score cols equal
    crit_w = emu(3.0)
    score_col_w = emu((9.0 - 3.0) / ncols)
    col_widths = [crit_w] + [score_col_w] * ncols

    tbl_y = emu(1.2)
    tbl_h = emu(0.45 * (len(rows) + 1))

    tbl_reqs = build_table(
        f'{pid}_tbl', pid, emu(M), tbl_y, emu(9.0), tbl_h,
        headers, rows, col_widths=col_widths)
    reqs.extend(tbl_reqs)

    # Color the header cells
    for si, color in enumerate(colors):
        reqs.append({'updateTableCellProperties': {
            'objectId': f'{pid}_tbl',
            'tableRange': {'location': {'rowIndex': 0, 'columnIndex': si + 1},
                           'rowSpan': 1, 'columnSpan': 1},
            'tableCellProperties': {
                'tableCellBackgroundFill': {
                    'solidFill': {'color': {'rgbColor': color}}}},
            'fields': 'tableCellBackgroundFill.solidFill.color'}})

    # Color the legend row cells (last row)
    legend_ri = len(rows)
    for si, color in enumerate(colors):
        reqs.append({'updateTableCellProperties': {
            'objectId': f'{pid}_tbl',
            'tableRange': {'location': {'rowIndex': legend_ri, 'columnIndex': si + 1},
                           'rowSpan': 1, 'columnSpan': 1},
            'tableCellProperties': {
                'tableCellBackgroundFill': {
                    'solidFill': {'color': {'rgbColor': color}}}},
            'fields': 'tableCellBackgroundFill.solidFill.color'}})

    # Color score markers in data rows
    for ri, (crit, score) in enumerate(zip(criteria, scores)):
        if 1 <= score <= ncols:
            marker_color = colors[score - 1]
            reqs.append({'updateTextStyle': {
                'objectId': f'{pid}_tbl',
                'cellLocation': {'rowIndex': ri + 1, 'columnIndex': score},
                'textRange': {'type': 'ALL'},
                'style': {'foregroundColor': {'opaqueColor': {'rgbColor': marker_color}},
                          'bold': True,
                          'fontSize': {'magnitude': 14, 'unit': 'PT'}},
                'fields': 'foregroundColor,bold,fontSize'}})

    if note_text:
        note_y = tbl_y + tbl_h + emu(0.2)
        shape(f'{pid}_note_bg', pid, emu(M), note_y, emu(9.0), emu(0.4), LTBG,
              'ROUND_RECTANGLE')
        shape(f'{pid}_note_acc', pid, emu(M), note_y, emu(0.04), emu(0.4), BLUE)
        textbox(f'{pid}_note', pid, emu(M + 0.2), note_y + emu(0.05),
                emu(8.6), emu(0.3), [(note_text, 8, False, GRAY)], 'START')


# ═══════════════════════════════════════════════════════════════════
# §7  STORYBOARD PREVIEW
# ═══════════════════════════════════════════════════════════════════

def slide_spec(stype, title='', subtitle='', items=0, rows=0,
               density=None):
    """Create a slide plan entry for storyboard preview."""
    if density is None:
        density = _auto_density(stype, items, rows)
    return {'type': stype, 'title': title, 'subtitle': subtitle,
            'items': items, 'rows': rows, 'density': density}


def _auto_density(stype, items=0, rows=0):
    if stype in ('title', 'section', 'close', 'quote'):
        return 'light'
    if rows > 8 or items > 6:
        return 'dense'
    if rows > 4 or items > 3:
        return 'normal'
    return 'light'


_THUMBS = {
    'title':   [' ████████████████ ', ' ████████████████ ',
                ' {t:<16s} ', ' {s:<16s} '],
    'section': [' ████████████████ ', ' 01               ',
                ' {t:<16s} ', '                  '],
    'stats':   ['                  ', ' ┌──┐┌──┐┌──┐    ',
                ' │##││##││##│    ', ' └──┘└──┘└──┘    '],
    'cards':   ['                  ', ' ┌────┐┌────┐    ',
                ' │    ││    │    ', ' └────┘└────┘    '],
    'table':   ['                  ', ' ┌─┬──┬──┐       ',
                ' ├─┼──┼──┤       ', ' └─┴──┴──┘       '],
    'split':   [' ███│░░░░░░░░░░  ', ' ███│┌────┐░░░  ',
                ' ███││    │░░░  ', ' ███│└────┘░░░  '],
    'quote':   ['                  ', ' │ "Quote..."     ',
                ' │                ', ' │ — Author       '],
    'close':   [' ████████████████ ', ' ████████████████ ',
                ' {t:<16s} ', ' ① ② ③            '],
    'diagram': ['                  ', ' ┌─┐→┌─┐→┌─┐    ',
                ' └─┘ └─┘ └─┘    ', '                  '],
    'chart':   ['                  ', ' │▄  █▄          ',
                ' │█▄██▄         ', ' └─────          '],
}

_DENSITY_METER = {'light': '░░', 'normal': '▒▒', 'dense': '▓▓'}
_DENSITY_LABEL = {'light': 'LITE', 'normal': 'NORM', 'dense': 'DNSE'}


def storyboard(slides, deck_title='Deck'):
    """Print terminal storyboard preview with pacing analysis.

    Usage:
        plan = [
            slide_spec('title', 'Zoom + Atlan', 'FY26 Renewal'),
            slide_spec('stats', 'Key Metrics', items=4),
            slide_spec('table', 'Comparison', rows=10),
            slide_spec('close', 'Next Steps'),
        ]
        storyboard(plan, 'Zoom FY26')
    """
    B = '\033[1m'; R = '\033[0m'
    CY = '\033[96m'; BL = '\033[94m'; GR = '\033[90m'
    YE = '\033[93m'; GN = '\033[92m'
    BAR = BL + '\u2501' * 52 + R

    print(f'\n{BAR}')
    print(f'  {B}STORYBOARD{R}  {GR}|{R}  '
          f'{deck_title}  {GR}({len(slides)} slides){R}')
    print(f'{BAR}\n')

    for row_start in range(0, len(slides), 3):
        row = slides[row_start:row_start + 3]

        # Header: [N] TYPE  density
        hdrs = []
        for i, s in enumerate(row):
            idx = row_start + i + 1
            stype = s['type'].upper()[:7]
            meter = _DENSITY_METER.get(s['density'], '░░')
            hdrs.append(f'  {CY}[{idx:>2}]{R} {B}{stype:<7s}{R} {GR}{meter}{R}')
        # Pad each header to 24 chars (accounting for ANSI)
        print(''.join(hdrs))

        # Thumbnail lines
        for line_idx in range(4):
            parts = []
            for s in row:
                tmpl = _THUMBS.get(s['type'], _THUMBS['cards'])
                line = tmpl[line_idx] if line_idx < len(tmpl) else ' ' * 18
                t = s.get('title', '')[:16]
                sub = s.get('subtitle', '')[:16]
                line = line.format(t=t, s=sub) if '{' in line else line
                parts.append(f'  {GR}{line}{R}')
            print(''.join(parts))
        print()

    # Pacing strip
    print(f'{BAR}')
    print(f'  {B}PACING{R}\n')
    densities = [s['density'] for s in slides]
    pacing = '  '
    for d in densities:
        if d == 'light':
            pacing += f'{GR}░░{R}'
        elif d == 'normal':
            pacing += f'{CY}▒▒{R}'
        else:
            pacing += f'{YE}▓▓{R}'
    print(pacing)
    labels = '  ' + ''.join(f'{GR}{_DENSITY_LABEL[d]}{R}' for d in densities)
    print(labels)

    # Flag issues
    issues = []
    for i in range(len(densities) - 1):
        if densities[i] == 'dense' and densities[i + 1] == 'dense':
            issues.append(f'  {YE}!{R}  Slides {i+1} & {i+2} are both '
                          f'dense -- add a breather')
    if densities and densities[0] == 'dense':
        issues.append(f'  {YE}!{R}  Opens dense -- consider a lighter start')
    if densities and densities[-1] == 'dense':
        issues.append(f'  {YE}!{R}  Ends dense -- close slide should be light')

    if issues:
        print()
        for iss in issues:
            print(iss)
    else:
        print(f'\n  {GN}OK{R}  Pacing looks good')

    print(f'\n{BAR}\n')
    return issues


# ═══════════════════════════════════════════════════════════════════
# §8  DEAL RECONCILIATION
# ═══════════════════════════════════════════════════════════════════

def fmt_currency(val, decimals=0):
    """Format number as currency: $329,898"""
    if decimals:
        return f'${val:,.{decimals}f}'
    return f'${val:,.0f}'


def fmt_pct(val, decimals=1):
    """Format number as percentage: 3.0%"""
    return f'{val:.{decimals}f}%'


def fmt_number(val, decimals=0):
    """Format number with commas: 659,796"""
    if decimals:
        return f'{val:,.{decimals}f}'
    return f'{val:,.0f}'


def fmt_compact(val):
    """Format number in compact form: 6.2M, 750K, 329,898.

    Uses M for millions, K for thousands. Numbers under 10K
    get full comma formatting. Drops trailing .0 for clean display.
    """
    if abs(val) >= 1_000_000:
        n = val / 1_000_000
        s = f'{n:.1f}'.rstrip('0').rstrip('.')
        return f'{s}M'
    if abs(val) >= 10_000:
        n = val / 1_000
        s = f'{n:.1f}'.rstrip('0').rstrip('.')
        return f'{s}K'
    return f'{val:,.0f}'


def _flatten_deal(deal, prefix=''):
    """Recursively flatten a DEAL dict to {path: value} for all numerics."""
    flat = {}
    if isinstance(deal, dict):
        for k, v in deal.items():
            path = f'{prefix}.{k}' if prefix else k
            flat.update(_flatten_deal(v, path))
    elif isinstance(deal, (list, tuple)):
        for i, v in enumerate(deal):
            flat.update(_flatten_deal(v, f'{prefix}[{i}]'))
    elif isinstance(deal, (int, float)):
        flat[prefix] = deal
    return flat


def _extract_numbers_from_text(text):
    """Extract all numeric values from rendered text.
    Handles: $329,898  43%  659,796  3.0%  +9.3%  -5.2%
    """
    if not text:
        return []
    numbers = []
    for match in re.finditer(r'[\-+]?\$?[\d,]+(?:\.\d+)?%?', text):
        raw = match.group().replace('$', '').replace('%', '').replace(',', '')
        raw = raw.lstrip('+')
        try:
            numbers.append(float(raw))
        except ValueError:
            pass
    return numbers


def reconcile(deal, tolerance=0.01):
    """Validate DEAL dict internal consistency before building.

    Checks TCV = price * term, line items sum to totals, etc.
    Returns list of issue strings (empty = all consistent).
    """
    issues = []

    def _check_node(node, path=''):
        if not isinstance(node, dict):
            return
        price = node.get('unit_price') or node.get('price') or node.get('arr')
        term = node.get('term') or node.get('years')
        tcv = node.get('tcv') or node.get('total')
        if price and term and tcv:
            expected = price * term
            if abs(expected - tcv) > abs(expected) * tolerance:
                issues.append(
                    f'{path}: TCV mismatch -- '
                    f'{fmt_currency(price)} x {term}yr = '
                    f'{fmt_currency(expected)}, '
                    f'but TCV = {fmt_currency(tcv)}')

        line_items = node.get('line_items')
        total = node.get('total') or node.get('tcv')
        if isinstance(line_items, (list, tuple)) and total:
            items_sum = sum(
                li.get('amount', 0) for li in line_items
                if isinstance(li, dict))
            if abs(items_sum - total) > abs(total) * tolerance:
                issues.append(
                    f'{path}: Line items sum to {fmt_currency(items_sum)}'
                    f' but total is {fmt_currency(total)}')

        for k, v in node.items():
            _check_node(v, f'{path}.{k}' if path else k)

    _check_node(deal)
    return issues


# ═══════════════════════════════════════════════════════════════════
# §9  VALIDATION ENGINE
# ═══════════════════════════════════════════════════════════════════

@dataclass
class Issue:
    """A detected design issue in the built deck."""
    slide_idx:  int
    element_id: str
    category:   str       # font, outline, overflow, alignment, density,
                          # color_budget, pacing, number
    severity:   str       # error, warning, info
    message:    str
    fix:        Optional[dict] = None


# ── Element extraction helpers ────────────────────────────────────

def _el_text(element):
    """Get all text from a page element."""
    shape_data = element.get('shape', {})
    for te in shape_data.get('text', {}).get('textElements', []):
        pass  # ensure we iterate
    return ''.join(
        te.get('textRun', {}).get('content', '')
        for te in shape_data.get('text', {}).get('textElements', [])
        if 'textRun' in te
    ).strip()


def _el_fonts(element):
    """Get all font families used in an element."""
    fonts = set()
    for te in element.get('shape', {}).get('text', {}).get(
            'textElements', []):
        ff = te.get('textRun', {}).get('style', {}).get('fontFamily')
        if ff:
            fonts.add(ff)
    return fonts


def _el_font_sizes(element):
    """Get all font sizes as list of (text, size_pt)."""
    sizes = []
    for te in element.get('shape', {}).get('text', {}).get(
            'textElements', []):
        run = te.get('textRun', {})
        text = run.get('content', '')
        sz = run.get('style', {}).get('fontSize', {}).get('magnitude')
        if text.strip() and sz:
            sizes.append((text, sz))
    return sizes


def _el_fill(element):
    """Get the solid fill RGB dict from a shape, or None."""
    props = element.get('shape', {}).get('shapeProperties', {})
    fill = props.get('shapeBackgroundFill', {}).get('solidFill', {})
    return fill.get('color', {}).get('rgbColor')


def _el_outline_rendered(element):
    """True if outline is visible (not NOT_RENDERED)."""
    props = element.get('shape', {}).get('shapeProperties', {})
    state = props.get('outline', {}).get('propertyState', 'RENDERED')
    return state != 'NOT_RENDERED'


def _el_alignment(element):
    """Get contentAlignment string, or None."""
    return element.get('shape', {}).get('shapeProperties', {}).get(
        'contentAlignment')


def _el_size(element):
    """Get (width_emu, height_emu)."""
    size = element.get('size', {})
    return (size.get('width', {}).get('magnitude', 0),
            size.get('height', {}).get('magnitude', 0))


def _el_is_shape(element):
    return 'shape' in element


def _el_shape_type(element):
    return element.get('shape', {}).get('shapeType')


class Validator:
    """Post-build validation engine.

    Usage:
        pres = slides_svc.presentations().get(presentationId=ID).execute()
        v = Validator(pres, deal=DEAL)
        issues = v.run_all()
    """

    NOISE_NUMBERS = (
        set(range(2020, 2031))  # years
        | set(range(0, 1000))    # small numbers (percentages, counts, compact remainders)
        | {500, 840}             # common narrative numbers
    )

    def __init__(self, pres, deal=None):
        self.pres = pres
        self.deal = deal or {}
        self.issues = []
        self._slide_densities = []

    def run_all(self):
        self.issues = []
        self._slide_densities = []

        for idx, slide in enumerate(self.pres.get('slides', [])):
            elements = slide.get('pageElements', [])
            self._check_density(idx, elements)
            self._check_color_budget(idx, elements)

            for el in elements:
                oid = el.get('objectId', '')
                if _el_is_shape(el):
                    self._check_font(idx, oid, el)
                    self._check_outline(idx, oid, el)
                    self._check_text_overflow(idx, oid, el)
                    self._check_alignment(idx, oid, el)
                if self.deal:
                    self._check_numbers(idx, oid, el)

        self._check_pacing()
        self._check_title_consistency()
        return self.issues

    def _check_title_consistency(self):
        """Flag inconsistent title sizes across content slides.

        Collects the largest font on each slide (the title) and flags
        any that differ from the majority. Skips slide 1 (title slide
        uses 42pt intentionally).
        """
        title_sizes = {}
        for idx, slide in enumerate(self.pres.get('slides', [])):
            if idx == 0:
                continue
            max_sz = 0
            max_text = ''
            for el in slide.get('pageElements', []):
                for text, sz in _el_font_sizes(el):
                    if sz > max_sz and text.strip():
                        max_sz = sz
                        max_text = text.strip()[:40]
            if max_sz > 0:
                title_sizes[idx] = (max_sz, max_text)

        if len(title_sizes) < 2:
            return

        sizes = [s for s, _ in title_sizes.values()]
        expected = max(set(sizes), key=sizes.count)

        for idx, (sz, text) in title_sizes.items():
            if sz != expected:
                self.issues.append(Issue(
                    idx, '', 'consistency', 'warning',
                    f'Title "{text}..." is {sz}pt but '
                    f'other slides use {expected}pt'))

    def _check_font(self, idx, oid, el):
        bad = _el_fonts(el) - {FONT}
        if bad:
            self.issues.append(Issue(
                idx, oid, 'font', 'error',
                f'Non-brand font: {bad} (expected {FONT})',
                fix={'updateTextStyle': {
                    'objectId': oid,
                    'textRange': {'type': 'ALL'},
                    'style': {'fontFamily': FONT},
                    'fields': 'fontFamily'}}))

    def _check_outline(self, idx, oid, el):
        if _el_shape_type(el) == 'TEXT_BOX':
            return
        # Skip shapes with intentional borders (bordered/dashed helpers)
        # These have outline fill + weight explicitly set
        props = el.get('shape', {}).get('shapeProperties', {})
        outline = props.get('outline', {})
        has_fill = 'outlineFill' in outline
        has_weight = 'weight' in outline
        if has_fill and has_weight:
            return  # Intentional border — not a bug
        if _el_outline_rendered(el):
            self.issues.append(Issue(
                idx, oid, 'outline', 'error',
                'Shape has visible outline (should be NOT_RENDERED)',
                fix={'updateShapeProperties': {
                    'objectId': oid,
                    'fields': 'outline.propertyState',
                    'shapeProperties': {
                        'outline': {'propertyState': 'NOT_RENDERED'}}}}))

    def _check_text_overflow(self, idx, oid, el):
        """Flag text overflow on single-line elements only.

        Skips multi-line elements (cards, body text) where wrapping is
        expected by design. Only flags titles, pills, and other elements
        where text should fit on one line.
        """
        w, h = _el_size(el)
        if w <= 0:
            return
        # Skip tall containers — text wraps by design in cards/body areas
        if h > emu(0.5):
            return
        all_text = _el_text(el)
        # Skip multi-line text — wrapping is intentional
        if '\n' in all_text:
            return
        for text, sz in _el_font_sizes(el):
            text_clean = text.strip()
            if not text_clean:
                continue
            est = text_width_emu(text_clean, sz)
            if est > w * 0.95:
                new_sz = auto_font(text_clean, w, int(sz), 7)
                if new_sz < sz:
                    self.issues.append(Issue(
                        idx, oid, 'overflow', 'warning',
                        f'Text overflows: "{text_clean[:35]}..." '
                        f'at {sz}pt (est {est/INCH:.1f}" in '
                        f'{w/INCH:.1f}" box). Shorten text or use '
                        f'smart_text_in().'))

    def _check_alignment(self, idx, oid, el):
        if _el_shape_type(el) == 'TEXT_BOX':
            return
        alignment = _el_alignment(el)
        if alignment not in ('MIDDLE', 'TOP'):
            self.issues.append(Issue(
                idx, oid, 'alignment', 'warning',
                'Shape missing contentAlignment (should be MIDDLE)',
                fix={'updateShapeProperties': {
                    'objectId': oid,
                    'fields': 'contentAlignment',
                    'shapeProperties': {'contentAlignment': 'MIDDLE'}}}))

    def _check_density(self, idx, elements):
        n = len(elements)
        if n > 25:
            density = 'dense'
            self.issues.append(Issue(
                idx, '', 'density', 'warning',
                f'Slide has {n} elements (>25) -- consider splitting'))
        elif n > 15:
            density = 'dense'
        elif n > 8:
            density = 'normal'
        else:
            density = 'light'
        self._slide_densities.append(density)

    def _check_color_budget(self, idx, elements):
        accents = set()
        for el in elements:
            fill = _el_fill(el)
            if fill:
                key = _color_key(fill)
                if key and key not in NEUTRAL_COLORS:
                    accents.add(key)
        if len(accents) > 3:
            self.issues.append(Issue(
                idx, '', 'color_budget', 'info',
                f'Slide uses {len(accents)} accent colors (max 3)'))

    def _check_pacing(self):
        d = self._slide_densities
        for i in range(len(d) - 1):
            if d[i] == 'dense' and d[i + 1] == 'dense':
                self.issues.append(Issue(
                    i, '', 'pacing', 'info',
                    f'Slides {i+1} and {i+2} are both dense'
                    ' -- add a breather between them'))

    def _check_numbers(self, idx, oid, el):
        text = _el_text(el)
        if not text:
            return
        deal_values = set(_flatten_deal(self.deal).values())
        for num in _extract_numbers_from_text(text):
            # Skip small numbers — percentages, counts, compact
            # remainders (205.9 from "205.9K"), multipliers
            if num < 1000:
                continue
            # Skip years
            if int(num) in self.NOISE_NUMBERS:
                continue
            matched = any(
                abs(num - dv) <= abs(dv) * 0.01
                for dv in deal_values if dv != 0)
            if not matched:
                self.issues.append(Issue(
                    idx, oid, 'number', 'warning',
                    f'Number {num:,.0f} not found in DEAL dict'
                    ' -- verify correctness'))


# ═══════════════════════════════════════════════════════════════════
# §10  SELF-HEALING LOOP
# ═══════════════════════════════════════════════════════════════════

@dataclass
class HealResult:
    """Result of a self-healing run."""
    rounds:     int
    fixed:      int
    remaining:  List[Issue]
    report:     str


class Healer:
    """Auto-fix detected issues via validate -> fix -> re-validate loop.

    Usage:
        healer = Healer(PRES_ID, slides_svc, deal=DEAL)
        result = healer.heal()
        print(result.report)
    """
    FIXABLE = {'font', 'outline', 'alignment'}

    def __init__(self, pres_id, slides_svc, deal=None):
        self.pres_id = pres_id
        self.slides_svc = slides_svc
        self.deal = deal

    def heal(self, max_rounds=3):
        B = '\033[1m'; R = '\033[0m'
        GN = '\033[92m'; YE = '\033[93m'; RD = '\033[91m'
        BL = '\033[94m'; GR = '\033[90m'
        OK = f'{GN}OK{R}'; WN = f'{YE}!{R}'
        BAR = BL + '\u2501' * 52 + R

        print(f'\n{BAR}')
        print(f'  {B}SELF-HEALING ENGINE{R}')
        print(f'{BAR}\n')

        total_fixed = 0
        remaining = []
        round_num = 0

        for round_num in range(1, max_rounds + 1):
            print(f'  {BL}*{R}  Round {round_num}/{max_rounds}'
                  f' -- reading deck...')

            pres = self.slides_svc.presentations().get(
                presentationId=self.pres_id).execute()

            validator = Validator(pres, self.deal)
            issues = validator.run_all()

            fixable = [i for i in issues
                       if i.fix and i.category in self.FIXABLE]
            unfixable = [i for i in issues
                         if not i.fix or i.category not in self.FIXABLE]

            print(f'     Found {len(issues)} issue(s): '
                  f'{len(fixable)} fixable, {len(unfixable)} manual')

            if not fixable:
                remaining = unfixable
                print(f'  {OK}  Nothing to fix in round {round_num}')
                break

            fixes = [i.fix for i in fixable]
            print(f'     Applying {len(fixes)} fix(es)...')

            try:
                self.slides_svc.presentations().batchUpdate(
                    presentationId=self.pres_id,
                    body={'requests': fixes}).execute()
                total_fixed += len(fixes)
                print(f'  {OK}  Applied {len(fixes)} fix(es)')
            except Exception as e:
                print(f'  {RD}X{R}  Fix batch failed: {e}')
                remaining = issues
                break

            remaining = unfixable
            time.sleep(1)

        # Report
        lines = []
        lines.append(f'\n{BAR}')
        lines.append(f'  {B}HEALING REPORT{R}')
        lines.append(f'{BAR}\n')
        lines.append(f'  Rounds:    {round_num}')
        lines.append(f'  Fixed:     {total_fixed}')
        lines.append(f'  Remaining: {len(remaining)}')

        if remaining:
            lines.append(f'\n  {WN}  Issues requiring manual review:\n')
            by_cat = {}
            for iss in remaining:
                by_cat.setdefault(iss.category, []).append(iss)
            for cat, cat_issues in sorted(by_cat.items()):
                lines.append(f'  {B}{cat.upper()}{R} ({len(cat_issues)})')
                for iss in cat_issues[:5]:
                    lines.append(f'    {GR}Slide {iss.slide_idx+1}:{R} '
                                 f'{iss.message}')
                if len(cat_issues) > 5:
                    lines.append(f'    {GR}... and '
                                 f'{len(cat_issues)-5} more{R}')
        else:
            lines.append(f'\n  {OK}  {B}All issues resolved{R}')

        lines.append(f'\n{BAR}\n')
        report = '\n'.join(lines)
        print(report)

        return HealResult(round_num, total_fixed, remaining, report)


# ═══════════════════════════════════════════════════════════════════
# §11  BUILD INFRASTRUCTURE
# ═══════════════════════════════════════════════════════════════════

class S:
    """Terminal styling constants."""
    B    = '\033[1m'
    D    = '\033[2m'
    I    = '\033[3m'
    U    = '\033[4m'
    R    = '\033[0m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    PINK = '\033[95m'
    GRN  = '\033[92m'
    YEL  = '\033[93m'
    RED  = '\033[91m'
    GRY  = '\033[90m'
    WHT  = '\033[97m'
    OK   = '\033[92mOK\033[0m'
    FAIL = '\033[91mX\033[0m'
    WARN = '\033[93m!\033[0m'
    DOT  = '\033[94m*\033[0m'
    ARR  = '\033[96m->\033[0m'
    BAR  = '\033[94m' + '=' * 52 + '\033[0m'
    THIN = '\033[90m' + '-' * 52 + '\033[0m'


def banner(title, subtitle=None):
    print(f'\n{S.BAR}')
    print(f'  {S.B}{S.BLUE}ATLAN DECK BUILDER{S.R}  '
          f'{S.GRY}|{S.R}  {S.B}{title}{S.R}')
    if subtitle:
        print(f'  {S.D}{subtitle}{S.R}')
    print(f'{S.BAR}')


def step(num, total, msg):
    filled = '#' * num
    empty = '.' * (total - num)
    print(f'\n  {S.CYAN}[{filled}{empty}]{S.R} '
          f'{S.B}Step {num}/{total}{S.R} -- {msg}')


def done(msg):
    print(f'  {S.OK}  {msg}')


def warn(msg):
    print(f'  {S.WARN}  {S.YEL}{msg}{S.R}')


def fail(msg):
    print(f'  {S.FAIL}  {S.RED}{msg}{S.R}')
    sys.exit(1)


def info(msg):
    print(f'  {S.DOT}  {msg}')


def detail(msg):
    print(f'       {S.GRY}{msg}{S.R}')


# ── Config ────────────────────────────────────────────────────────
TEMPLATE_ID = '1SOajzd0opagErD3ATLmj77tlSeOEIvlWaqW6l6MfXQU'
TOKEN_FILE  = '/tmp/google_slides_token.pickle'

SCOPES = [
    'https://www.googleapis.com/auth/presentations',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/spreadsheets',
]

CLIENT_CONFIG = {
    'installed': {
        'client_id': '107177905468-kcrb1491ei687rrkebms35nskr2cimef'
                     '.apps.googleusercontent.com',
        'client_secret': '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',
        'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
        'token_uri': 'https://oauth2.googleapis.com/token',
        'redirect_uris': ['http://localhost'],
    }
}


def get_creds():
    """Load, refresh, or create Google OAuth credentials."""
    from google.auth.transport.requests import Request

    if Path(TOKEN_FILE).exists():
        with open(TOKEN_FILE, 'rb') as f:
            creds = pickle.load(f)
        if creds.valid:
            done('OAuth token loaded (valid)')
            return creds
        if creds.expired and creds.refresh_token:
            info('Token expired -- refreshing...')
            creds.refresh(Request())
            with open(TOKEN_FILE, 'wb') as f:
                pickle.dump(creds, f)
            done('Token refreshed')
            return creds

    warn('No valid token -- opening browser for Google login...')
    from google_auth_oauthlib.flow import InstalledAppFlow
    flow = InstalledAppFlow.from_client_config(CLIENT_CONFIG, SCOPES)
    creds = flow.run_local_server(port=0)
    with open(TOKEN_FILE, 'wb') as f:
        pickle.dump(creds, f)
    done(f'Token saved to {TOKEN_FILE}')
    return creds


def init_services(creds=None):
    """Initialize Google API services.
    Returns (slides_svc, drive_svc, sheets_svc).
    """
    from googleapiclient.discovery import build as build_svc
    if creds is None:
        creds = get_creds()
    slides_svc = build_svc('slides', 'v1', credentials=creds)
    drive_svc  = build_svc('drive', 'v3', credentials=creds)
    sheets_svc = build_svc('sheets', 'v4', credentials=creds)
    return slides_svc, drive_svc, sheets_svc


def copy_template(drive_svc, title='Untitled Deck'):
    """Copy the Atlan template. Returns new presentation ID."""
    pres = drive_svc.files().copy(
        fileId=TEMPLATE_ID, body={'name': title}).execute()
    pres_id = pres['id']
    done(f'Deck created: {pres_id}')
    detail(f'https://docs.google.com/presentation/d/{pres_id}/edit')
    return pres_id


def clean_template(slides_svc, pres_id):
    """Delete all template slides from a freshly copied deck."""
    existing = slides_svc.presentations().get(
        presentationId=pres_id).execute()
    del_ids = [s['objectId'] for s in existing.get('slides', [])]
    for did in del_ids:
        reqs.append({'deleteObject': {'objectId': did}})
    done(f'Queued {len(del_ids)} template slide(s) for deletion')


def flush(slides_svc=None, pres_id=None, batch_size=350, sleep_sec=8):
    """Execute all queued requests in batches."""
    if not reqs:
        return
    if not slides_svc or not pres_id:
        raise ValueError('flush() requires slides_svc and pres_id')

    total_batches = (len(reqs) + batch_size - 1) // batch_size
    total_reqs = len(reqs)

    for batch_num, i in enumerate(range(0, len(reqs), batch_size), 1):
        batch = reqs[i:i + batch_size]
        if total_batches > 1:
            info(f'Sending batch {batch_num}/{total_batches} '
                 f'({len(batch)} requests)...')
        slides_svc.presentations().batchUpdate(
            presentationId=pres_id,
            body={'requests': batch}).execute()
        if i + batch_size < len(reqs):
            detail(f'Rate limit pause ({sleep_sec}s)...')
            time.sleep(sleep_sec)

    done(f'Flushed {total_reqs} API requests '
         f'in {total_batches} batch(es)')
    reqs.clear()


def save_context(pres_id, slides_svc, state_file):
    """Snapshot full deck state. Saves pickle + JSON manifest."""
    pres = slides_svc.presentations().get(
        presentationId=pres_id).execute()
    slides_info = []

    for s in pres.get('slides', []):
        slide_id = s['objectId']
        elements = []
        for el in s.get('pageElements', []):
            el_info = {
                'objectId': el.get('objectId'),
                'type': ('table' if 'table' in el
                         else 'shape' if 'shape' in el
                         else 'image' if 'image' in el
                         else 'sheetsChart' if 'sheetsChart' in el
                         else 'other'),
            }
            if 'shape' in el:
                el_info['shapeType'] = el['shape'].get('shapeType', '')
                text_els = el['shape'].get('text', {}).get(
                    'textElements', [])
                text = ''.join(
                    te.get('textRun', {}).get('content', '')
                    for te in text_els if 'textRun' in te).strip()
                if text:
                    el_info['text'] = text[:100]
            if 'size' in el:
                ew = el['size'].get('width', {}).get('magnitude', 0)
                eh = el['size'].get('height', {}).get('magnitude', 0)
                el_info['size'] = f'{ew/INCH:.2f}x{eh/INCH:.2f}in'
            if 'transform' in el:
                t = el['transform']
                el_info['pos'] = (
                    f'({t.get("translateX",0)/INCH:.2f}, '
                    f'{t.get("translateY",0)/INCH:.2f})')
            elements.append(el_info)

        slides_info.append({
            'objectId': slide_id,
            'index': len(slides_info),
            'elementCount': len(elements),
            'elements': elements,
        })

    state = {
        'PRES_ID': pres_id,
        'slide_count': len(slides_info),
        'slides': slides_info,
        'url': f'https://docs.google.com/presentation/d/{pres_id}/edit',
    }

    with open(state_file, 'wb') as f:
        pickle.dump(state, f)

    manifest_file = state_file.replace('.pkl', '_manifest.json')
    with open(manifest_file, 'w') as f:
        json.dump(state, f, indent=2, default=str)

    total_els = sum(s['elementCount'] for s in slides_info)
    done(f'Context saved: {len(slides_info)} slides, {total_els} elements')
    detail(f'State:    {state_file}')
    detail(f'Manifest: {manifest_file}')
    return state


def load_context(state_file):
    """Load a previously saved deck state from pickle."""
    with open(state_file, 'rb') as f:
        state = pickle.load(f)
    info(f'Loaded deck state: {state["slide_count"]} slides')
    detail(f'URL: {state["url"]}')
    return state


def print_summary(pres_id, state_file=None):
    """Print the final build summary block."""
    print(f'\n{S.BAR}')
    print(f'  {S.OK}  {S.B}DECK BUILD COMPLETE{S.R}')
    print(f'{S.THIN}')
    print(f'  {S.ARR}  URL:    {S.U}'
          f'https://docs.google.com/presentation/d/{pres_id}/edit{S.R}')
    if state_file:
        print(f'  {S.ARR}  State:  {state_file}')
        manifest = state_file.replace('.pkl', '_manifest.json')
        print(f'  {S.ARR}  Manifest: {manifest}')
    print(f'{S.BAR}\n')


# ═══════════════════════════════════════════════════════════════════
# PUBLIC API
# ═══════════════════════════════════════════════════════════════════

__all__ = [
    # §1 Tokens
    'BLUE', 'CYAN', 'PINK', 'DARK', 'GRAY', 'WHITE', 'DKBLUE',
    'LTBG', 'LTCYAN', 'LTPINK', 'LTGREEN', 'GREEN', 'ORANGE',
    'CORAL', 'EMERALD', 'PURPLE', 'GOLD', 'BRAND_COLORS', 'ROLE',
    'FONT', 'TYPE_SCALE', 'INCH', 'SW', 'SH', 'emu', 'M', 'SP',
    # §2 Grid + Layout
    'Grid', 'Layout', 'COL_SPECS', 'auto_col_widths',
    # §3 Measurement + Synthesis
    'text_width_emu', 'auto_font', 'will_fit', 'lines_needed',
    'text_height_emu', 'auto_container_height', 'synthesize',
    # §4 Helpers
    'reqs', 'shape', 'bordered', 'dashed', 'text_in', 'smart_text_in',
    'rich_in', 'textbox', 'label', 'new_slide', 'styled_element',
    'group_elements', 'connector',
    # §5 Tables
    'build_table', 'PROPOSAL_TABLE', 'proposal_table',
    'OPTION_PILLS', 'option_pill',
    # §6 Composites
    'pill', 'kpi_card', 'insight_card', 'action_card', 'feature_card',
    'benefit_card', 'numbered_circle', 'quote_block', 'phase_card',
    'sheets_chart',
    # §6b Timeline templates (v4.0)
    'timeline_staggered', 'timeline_cascading', 'timeline_waterfall',
    # §6c Slide templates (v4.1)
    'DEFAULT_ACCENT_ROTATION', 'SCORE_SCALE_COLORS', 'SCORE_SCALE_LABELS',
    'chevron_flow', 'funnel', 'score_card',
    # §7 Storyboard
    'slide_spec', 'storyboard',
    # §8 Reconciliation
    'fmt_currency', 'fmt_pct', 'fmt_number', 'fmt_compact', 'reconcile',
    # §9 Validation
    'Issue', 'Validator',
    # §10 Healing
    'HealResult', 'Healer',
    # §11 Infrastructure
    'S', 'banner', 'step', 'done', 'warn', 'fail', 'info', 'detail',
    'TEMPLATE_ID', 'TOKEN_FILE', 'SCOPES', 'CLIENT_CONFIG',
    'get_creds', 'init_services', 'copy_template', 'clean_template',
    'flush', 'save_context', 'load_context', 'print_summary',
]
