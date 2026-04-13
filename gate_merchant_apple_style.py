"""
Gate Merchant — Apple-style case study PDF.

Re-imagines the original Figma portfolio page (node 501-81395 in
"Gate 作品集") as a multi-page document that follows Apple's marketing
design language: black/white extremes, generous whitespace, oversized
headlines, hairline dividers, and sentence-as-statement copy.

Run: python3 gate_merchant_apple_style.py
Output: gate_merchant_apple_style.pdf
"""

from reportlab.lib.colors import Color, HexColor, white, black
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

# ---------- Constants ----------------------------------------------------- #

PAGE_W, PAGE_H = A4  # 595 x 842 pt

# Apple-ish neutrals
APPLE_BLACK = HexColor("#000000")
APPLE_NEAR_BLACK = HexColor("#1d1d1f")  # Apple's actual body black
APPLE_WHITE = HexColor("#ffffff")
APPLE_OFFWHITE = HexColor("#fbfbfd")    # Apple's marketing background
APPLE_GRAY_TEXT = HexColor("#86868b")   # Apple's caption gray
APPLE_HAIRLINE = HexColor("#d2d2d7")    # Apple's divider gray
APPLE_HAIRLINE_DARK = HexColor("#2a2a2d")
APPLE_BLUE = HexColor("#0071e3")        # Apple's link blue
GATE_GREEN = HexColor("#c6f24e")        # The signature Gate accent

# Apple's marketing typography stack falls back to Helvetica Neue, so the
# built-in Helvetica family is a faithful enough stand-in for a static PDF.
F_REG = "Helvetica"
F_BOLD = "Helvetica-Bold"
F_LIGHT = "Helvetica"  # reportlab core fonts have no light weight


# ---------- Drawing helpers ---------------------------------------------- #

def fill_page(c, color):
    c.setFillColor(color)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)


def hairline(c, x1, y, x2, color=APPLE_HAIRLINE):
    c.setStrokeColor(color)
    c.setLineWidth(0.5)
    c.line(x1, y, x2, y)


def _draw_tracked(c, x, y, text, font, size, color, tracking):
    """Draw text with letter-spacing using a text object."""
    t = c.beginText()
    t.setFont(font, size)
    t.setFillColor(color)
    t.setCharSpace(tracking)
    t.setTextOrigin(x, y)
    t.textOut(text)
    c.drawText(t)


def _tracked_width(text, font, size, tracking):
    return pdfmetrics.stringWidth(text, font, size) + tracking * len(text)


def centered_text(c, text, y, font, size, color, tracking=0):
    if tracking:
        w = _tracked_width(text, font, size, tracking)
        _draw_tracked(c, (PAGE_W - w) / 2, y, text, font, size, color, tracking)
        return
    c.setFillColor(color)
    c.setFont(font, size)
    c.drawCentredString(PAGE_W / 2, y, text)


def left_text(c, text, x, y, font, size, color, tracking=0):
    if tracking:
        _draw_tracked(c, x, y, text, font, size, color, tracking)
        return
    c.setFillColor(color)
    c.setFont(font, size)
    c.drawString(x, y, text)


def wrap(text, max_chars):
    """Naive word-wrap that's good enough for short marketing copy."""
    words = text.split()
    lines, current = [], ""
    for w in words:
        candidate = (current + " " + w).strip()
        if len(candidate) <= max_chars:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines


def paragraph(c, text, x, y, width_chars, font, size, color, leading):
    c.setFillColor(color)
    c.setFont(font, size)
    for line in wrap(text, width_chars):
        c.drawString(x, y, line)
        y -= leading
    return y


# ---------- Page 1 — Cover ----------------------------------------------- #

def page_cover(c):
    fill_page(c, APPLE_BLACK)

    # Eyebrow — small caps with letter-spacing, Apple style
    centered_text(
        c, "GATE  PROJECTS", PAGE_H - 110,
        F_BOLD, 9, APPLE_GRAY_TEXT, tracking=2.5,
    )

    # Hero headline — oversized, tight tracking
    centered_text(c, "Gate Merchant.", PAGE_H / 2 + 100,
                  F_BOLD, 60, APPLE_WHITE)
    centered_text(c, "Reimagined for crypto.", PAGE_H / 2 + 50,
                  F_BOLD, 30, APPLE_GRAY_TEXT)

    # Sub-tagline, Apple's signature one-liner
    centered_text(
        c,
        "A zero-to-one merchant platform.",
        PAGE_H / 2 - 10, F_REG, 14, APPLE_GRAY_TEXT,
    )
    centered_text(
        c,
        "Payments, payouts, and access, all in one place.",
        PAGE_H / 2 - 30, F_REG, 14, APPLE_GRAY_TEXT,
    )

    # Bottom meta block
    centered_text(c, "A case study", 90, F_REG, 11, APPLE_GRAY_TEXT)
    centered_text(c, "by the sole designer.", 75, F_REG, 11, APPLE_GRAY_TEXT)

    # Tiny accent dot in Gate green — single brand cue
    c.setFillColor(GATE_GREEN)
    c.circle(PAGE_W / 2, 50, 2, fill=1, stroke=0)


# ---------- Page 2 — The three products --------------------------------- #

def page_lineup(c):
    fill_page(c, APPLE_BLACK)

    centered_text(c, "THE  LINEUP", PAGE_H - 90,
                  F_BOLD, 9, APPLE_GRAY_TEXT, tracking=2.5)
    centered_text(c, "Three products.", PAGE_H - 145,
                  F_BOLD, 38, APPLE_WHITE)
    centered_text(c, "One vision.", PAGE_H - 185,
                  F_BOLD, 38, APPLE_GRAY_TEXT)

    # Three cards — equal columns
    card_w = 145
    card_h = 200
    gap = 24
    total_w = card_w * 3 + gap * 2
    start_x = (PAGE_W - total_w) / 2
    card_y = PAGE_H / 2 - 200

    products = [
        ("GATE TRAVEL", "Book the world,", "pay in crypto."),
        ("GATE MERCHANT", "Accept, manage,", "and grow."),
        ("GATE CARD", "Spend anywhere,", "settle anywhere."),
    ]

    for i, (name, l1, l2) in enumerate(products):
        x = start_x + i * (card_w + gap)
        # Card surface — subtle near-black with hairline border
        c.setFillColor(HexColor("#161618"))
        c.setStrokeColor(APPLE_HAIRLINE_DARK)
        c.setLineWidth(0.75)
        c.roundRect(x, card_y, card_w, card_h, 14, fill=1, stroke=1)

        # Highlight the middle (Merchant) card with the Gate accent
        if name == "GATE MERCHANT":
            c.setFillColor(GATE_GREEN)
            c.circle(x + card_w - 18, card_y + card_h - 18, 3,
                     fill=1, stroke=0)

        # Card name — eyebrow style
        name_color = APPLE_WHITE if name == "GATE MERCHANT" else APPLE_GRAY_TEXT
        name_w = _tracked_width(name, F_BOLD, 9, 2)
        _draw_tracked(c, x + (card_w - name_w) / 2, card_y + 70,
                      name, F_BOLD, 9, name_color, 2)

        # Tagline — two short lines
        c.setFillColor(APPLE_WHITE if name == "GATE MERCHANT"
                       else HexColor("#6e6e73"))
        c.setFont(F_BOLD, 13)
        c.drawCentredString(x + card_w / 2, card_y + 50, l1)
        c.drawCentredString(x + card_w / 2, card_y + 33, l2)

    # Footer caption
    centered_text(c, "Today's chapter — Gate Merchant.", 90,
                  F_REG, 11, APPLE_GRAY_TEXT)


# ---------- Page 3 — Hero showcase --------------------------------------- #

def draw_laptop_mockup(c, cx, cy, w):
    """Draw a stylised laptop showing a payment dashboard."""
    h = w * 0.62  # 16:10-ish
    screen_x = cx - w / 2
    screen_y = cy - h / 2

    # Laptop bezel
    c.setFillColor(HexColor("#0a0a0c"))
    c.setStrokeColor(HexColor("#3a3a3d"))
    c.setLineWidth(1)
    c.roundRect(screen_x - 8, screen_y - 8, w + 16, h + 16, 10,
                fill=1, stroke=1)

    # Inner screen — light dashboard background
    inner_pad = 4
    sx = screen_x + inner_pad
    sy = screen_y + inner_pad
    sw = w - inner_pad * 2
    sh = h - inner_pad * 2
    c.setFillColor(APPLE_OFFWHITE)
    c.roundRect(sx, sy, sw, sh, 6, fill=1, stroke=0)

    # Sidebar
    side_w = sw * 0.18
    c.setFillColor(HexColor("#f5f5f7"))
    c.roundRect(sx, sy, side_w, sh, 6, fill=1, stroke=0)
    # Sidebar nav dots
    c.setFillColor(APPLE_HAIRLINE)
    for i in range(6):
        c.rect(sx + 10, sy + sh - 22 - i * 16, side_w - 20, 4,
               fill=1, stroke=0)

    # Main content area
    main_x = sx + side_w + 10
    main_w = sw - side_w - 20
    main_top = sy + sh - 12

    # "Today's Total Payments" label
    c.setFillColor(HexColor("#6e6e73"))
    c.setFont(F_REG, 4)
    c.drawString(main_x, main_top - 4, "Today's Total Payments")

    # Big number
    c.setFillColor(APPLE_NEAR_BLACK)
    c.setFont(F_BOLD, 11)
    c.drawString(main_x, main_top - 16, "4,200 USD")

    # Stat row (3 cards)
    stat_y = main_top - 46
    stat_w = (main_w - 8) / 3
    for i, (label, value) in enumerate(
        [("Pending", "224"), ("Active", "768"), ("Merchants", "16")]
    ):
        bx = main_x + i * (stat_w + 4)
        c.setFillColor(white)
        c.setStrokeColor(APPLE_HAIRLINE)
        c.roundRect(bx, stat_y, stat_w, 22, 2, fill=1, stroke=1)
        c.setFillColor(HexColor("#86868b"))
        c.setFont(F_REG, 3.2)
        c.drawString(bx + 4, stat_y + 14, label)
        c.setFillColor(APPLE_NEAR_BLACK)
        c.setFont(F_BOLD, 7)
        c.drawString(bx + 4, stat_y + 5, value)

    # Chart area
    chart_y = stat_y - 60
    c.setFillColor(white)
    c.setStrokeColor(APPLE_HAIRLINE)
    c.roundRect(main_x, chart_y, main_w, 52, 2, fill=1, stroke=1)
    c.setFillColor(HexColor("#86868b"))
    c.setFont(F_REG, 3.2)
    c.drawString(main_x + 5, chart_y + 44, "Data Overview")

    # Faux line chart with the brand accent
    c.setStrokeColor(GATE_GREEN)
    c.setLineWidth(1.4)
    pts = [(0, 8), (1, 14), (2, 10), (3, 22), (4, 18),
           (5, 30), (6, 24), (7, 32), (8, 28), (9, 36)]
    step = (main_w - 20) / (len(pts) - 1)
    base_x = main_x + 10
    base_y = chart_y + 8
    path = c.beginPath()
    path.moveTo(base_x + pts[0][0] * step, base_y + pts[0][1])
    for px, py in pts[1:]:
        path.lineTo(base_x + px * step, base_y + py)
    c.drawPath(path, stroke=1, fill=0)


def page_showcase(c):
    fill_page(c, APPLE_BLACK)

    # Top eyebrow
    centered_text(c, "THE  PRODUCT", PAGE_H - 80,
                  F_BOLD, 9, APPLE_GRAY_TEXT, tracking=2.5)
    centered_text(c, "Every payment, beautifully managed.",
                  PAGE_H - 125, F_BOLD, 24, APPLE_WHITE)
    centered_text(c, "From a single dashboard.",
                  PAGE_H - 150, F_BOLD, 24, APPLE_GRAY_TEXT)

    # The mockup
    draw_laptop_mockup(c, PAGE_W / 2, PAGE_H / 2 - 30, 380)

    # Caption
    centered_text(
        c, "Real-time payments, payouts, RBAC and API management —",
        130, F_REG, 11, APPLE_GRAY_TEXT,
    )
    centered_text(c, "in a single pane of glass.", 115,
                  F_REG, 11, APPLE_GRAY_TEXT)


# ---------- Page 4 — At a glance (stats) --------------------------------- #

def page_stats(c):
    fill_page(c, APPLE_OFFWHITE)

    centered_text(c, "AT  A  GLANCE", PAGE_H - 110,
                  F_BOLD, 9, APPLE_GRAY_TEXT, tracking=2.5)
    centered_text(c, "Small team.", PAGE_H - 160,
                  F_BOLD, 38, APPLE_NEAR_BLACK)
    centered_text(c, "Big numbers.", PAGE_H - 200,
                  F_BOLD, 38, APPLE_GRAY_TEXT)

    # Three-up stats row, separated by hairlines
    row_y = PAGE_H / 2
    stats = [
        ("Role", "Sole", "designer"),
        ("Period", "2", "weeks"),
        ("DAU growth", "1000", "%"),
    ]
    col_w = PAGE_W / 3

    for i, (label, big, unit) in enumerate(stats):
        cx = col_w * i + col_w / 2

        # Eyebrow label
        lbl = label.upper()
        lbl_w = _tracked_width(lbl, F_BOLD, 9, 1.5)
        _draw_tracked(c, cx - lbl_w / 2, row_y + 70,
                      lbl, F_BOLD, 9, APPLE_GRAY_TEXT, 1.5)

        # Big value
        c.setFillColor(APPLE_NEAR_BLACK)
        c.setFont(F_BOLD, 56)
        c.drawCentredString(cx, row_y, big)

        # Unit
        c.setFillColor(APPLE_GRAY_TEXT)
        c.setFont(F_REG, 14)
        c.drawCentredString(cx, row_y - 24, unit)

        # Vertical hairline divider between columns
        if i < len(stats) - 1:
            c.setStrokeColor(APPLE_HAIRLINE)
            c.setLineWidth(0.5)
            c.line(col_w * (i + 1), row_y - 40,
                   col_w * (i + 1), row_y + 60)

    # Footnote
    centered_text(
        c, "Designed, prototyped, and shipped in two weeks.",
        140, F_REG, 12, APPLE_GRAY_TEXT,
    )
    centered_text(
        c, "Daily active users grew 10× post-launch.",
        122, F_REG, 12, APPLE_GRAY_TEXT,
    )


# ---------- Page 5 — Background & Challenge ------------------------------ #

def page_story(c):
    fill_page(c, APPLE_OFFWHITE)

    centered_text(c, "THE  STORY", PAGE_H - 90,
                  F_BOLD, 9, APPLE_GRAY_TEXT, tracking=2.5)

    # ---- Background block ----
    left_text(c, "Background.", 60, PAGE_H - 165,
              F_BOLD, 34, APPLE_NEAR_BLACK)

    body_x = 60
    body_y = PAGE_H - 210
    body_y = paragraph(
        c,
        "Gate Merchant is a zero-to-one product. It bundles "
        "payment collection, deposits, withdrawals, payouts, "
        "role-based access, and a full API into one cohesive "
        "platform, replacing what used to be five disconnected "
        "tools.",
        body_x, body_y, 58,
        F_REG, 13, HexColor("#3a3a3d"), 19,
    )

    # Hairline divider
    hairline(c, 60, PAGE_H - 350, PAGE_W - 60)

    # ---- Challenge block ----
    left_text(c, "The challenge.", 60, PAGE_H - 395,
              F_BOLD, 34, APPLE_NEAR_BLACK)

    chal_y = PAGE_H - 440
    challenges = [
        ("01", "Make crypto feel familiar.",
         "Translate the language of on-chain finance into concepts "
         "any merchant already understands."),
        ("02", "Sharpen the value proposition.",
         "Rewrite the product narrative so a first-time visitor "
         "knows what to do within five seconds."),
        ("03", "Upgrade the interaction model.",
         "Replace dense, table-heavy flows with focused, "
         "task-oriented surfaces."),
    ]

    for num, title, body in challenges:
        # Number — Apple-style oversized index
        c.setFillColor(APPLE_GRAY_TEXT)
        c.setFont(F_BOLD, 11)
        c.drawString(60, chal_y, num)

        # Title
        c.setFillColor(APPLE_NEAR_BLACK)
        c.setFont(F_BOLD, 15)
        c.drawString(95, chal_y, title)

        # Body
        c.setFillColor(HexColor("#6e6e73"))
        c.setFont(F_REG, 11)
        ny = chal_y - 17
        for line in wrap(body, 65):
            c.drawString(95, ny, line)
            ny -= 14

        chal_y = ny - 16


# ---------- Page 6 — Outro ----------------------------------------------- #

def page_outro(c):
    fill_page(c, APPLE_BLACK)

    centered_text(c, "Designed by one.", PAGE_H / 2 + 30,
                  F_BOLD, 44, APPLE_WHITE)
    centered_text(c, "Built for many.", PAGE_H / 2 - 20,
                  F_BOLD, 44, APPLE_GRAY_TEXT)

    # Hairline + signature row, Apple-press-release style
    hairline(c, PAGE_W / 2 - 80, PAGE_H / 2 - 70,
             PAGE_W / 2 + 80, color=APPLE_HAIRLINE_DARK)

    centered_text(c, "Gate Merchant  ·  Case study  ·  2024",
                  PAGE_H / 2 - 95, F_REG, 10, APPLE_GRAY_TEXT)

    # Tiny brand dot
    c.setFillColor(GATE_GREEN)
    c.circle(PAGE_W / 2, 60, 2, fill=1, stroke=0)
    centered_text(c, "Thank you.", 40, F_REG, 9, APPLE_GRAY_TEXT)


# ---------- Build -------------------------------------------------------- #

def build(path="gate_merchant_apple_style.pdf"):
    c = canvas.Canvas(path, pagesize=A4)
    c.setTitle("Gate Merchant — Case Study")
    c.setAuthor("Sole designer")
    c.setSubject("Apple-style redesign of the Gate Merchant case study")

    for page in (page_cover, page_lineup, page_showcase,
                 page_stats, page_story, page_outro):
        page(c)
        c.showPage()

    c.save()
    print(f"Wrote {path}")


if __name__ == "__main__":
    build()
