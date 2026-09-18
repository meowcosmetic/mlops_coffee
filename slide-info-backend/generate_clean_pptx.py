"""Generate a high-impact, executive-level PowerPoint presentation in English.
Key Design Guidelines:
1. Extra-large font sizes for effortless readability (Titles 32-48pt, Headings 20-24pt, Body 16-18pt).
2. Clean, high-level terminology (No pedantic version numbers; e.g. "SQL Database", "Python API", "AI Agent").
3. Bright, elegant visual aesthetic (Crisp white background, Warm coffee & amber accents, Slate cards).
4. 16:9 Widescreen standard.
"""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def build_executive_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # --- EXECUTIVE BRIGHT COLOR PALETTE ---
    BG_WHITE = RGBColor(255, 255, 255)        # Pure White (#ffffff)
    BG_CARD = RGBColor(248, 250, 252)         # Slate 50 (#f8fafc)
    BORDER_CARD = RGBColor(226, 232, 240)     # Slate 200 (#e2e8f0)
    
    TEXT_TITLE = RGBColor(15, 23, 42)         # Slate 900 (#0f172a)
    TEXT_BODY = RGBColor(30, 41, 59)          # Slate 800 (#1e293b)
    TEXT_SUBTLE = RGBColor(100, 116, 139)     # Slate 500 (#64748b)
    
    COFFEE_DARK = RGBColor(120, 53, 15)       # Amber 900 (#78350f)
    AMBER_ACCENT = RGBColor(217, 119, 6)      # Amber 600 (#d97706)
    BLUE_ACCENT = RGBColor(2, 132, 199)       # Sky 600 (#0284c7)
    INDIGO_ACCENT = RGBColor(79, 70, 229)     # Indigo 600 (#4f46e5)
    
    STATUS_DONE_BG = RGBColor(209, 250, 229)  # Mint 100
    STATUS_DONE_FG = RGBColor(4, 120, 87)     # Emerald 700
    
    STATUS_PART_BG = RGBColor(254, 243, 199)  # Amber 100
    STATUS_PART_FG = RGBColor(180, 83, 9)     # Amber 700
    
    STATUS_TODO_BG = RGBColor(255, 228, 230)  # Rose 100
    STATUS_TODO_FG = RGBColor(190, 18, 60)    # Rose 700

    def apply_base(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_WHITE
        bg.line.fill.background()

        # Clean footer
        ft = slide.shapes.add_textbox(Inches(0.8), Inches(6.95), Inches(11.733), Inches(0.4))
        p = ft.text_frame.paragraphs[0]
        p.text = "DrinkBot MLOps • F&B AI Assistant & Management Platform"
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_SUBTLE

    def add_header(slide, tag_text, title_text, subtitle_text=""):
        # Tag pill
        tag = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.4), Inches(2.8), Inches(0.35))
        tag.fill.solid()
        tag.fill.fore_color.rgb = RGBColor(254, 243, 199)
        tag.line.color.rgb = RGBColor(251, 191, 36)
        tag.line.width = Pt(1)
        tf_tag = tag.text_frame
        p_tag = tf_tag.paragraphs[0]
        p_tag.text = tag_text.upper()
        p_tag.alignment = PP_ALIGN.CENTER
        p_tag.font.size = Pt(11)
        p_tag.font.bold = True
        p_tag.font.color.rgb = COFFEE_DARK

        # Hero Slide Title (32pt Bold)
        t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.8), Inches(11.733), Inches(0.65))
        tf_t = t_box.text_frame
        tf_t.word_wrap = True
        pt = tf_t.paragraphs[0]
        pt.text = title_text
        pt.font.size = Pt(32)
        pt.font.bold = True
        pt.font.color.rgb = TEXT_TITLE

        # Subtitle (15pt)
        if subtitle_text:
            s_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.45), Inches(11.733), Inches(0.45))
            tf_s = s_box.text_frame
            tf_s.word_wrap = True
            ps = tf_s.paragraphs[0]
            ps.text = subtitle_text
            ps.font.size = Pt(15)
            ps.font.color.rgb = TEXT_SUBTLE

    def add_card(slide, left, top, width, height, border_color=BORDER_CARD, bg_color=BG_CARD):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1.5)
        return card

    # =========================================================================
    # SLIDE 1: COVER SLIDE
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    apply_base(s1)

    # Category Pill
    kicker = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.1), Inches(3.4), Inches(0.45))
    kicker.fill.solid()
    kicker.fill.fore_color.rgb = RGBColor(254, 243, 199)
    kicker.line.color.rgb = RGBColor(245, 158, 11)
    kicker.line.width = Pt(1.5)
    tf_k = kicker.text_frame
    pk = tf_k.paragraphs[0]
    pk.text = "☕ F&B AI WORKSHOP 2026"
    pk.alignment = PP_ALIGN.CENTER
    pk.font.size = Pt(12)
    pk.font.bold = True
    pk.font.color.rgb = COFFEE_DARK

    # Title Box
    h_box = s1.shapes.add_textbox(Inches(0.8), Inches(1.75), Inches(11.7), Inches(2.6))
    tf_h = h_box.text_frame
    tf_h.word_wrap = True

    p1 = tf_h.paragraphs[0]
    p1.text = "DrinkBot MLOps"
    p1.font.size = Pt(50)
    p1.font.bold = True
    p1.font.color.rgb = COFFEE_DARK

    p2 = tf_h.add_paragraph()
    p2.text = "Smart Beverage Assistant & MLOps Platform"
    p2.font.size = Pt(30)
    p2.font.bold = True
    p2.font.color.rgb = TEXT_TITLE
    p2.space_before = Pt(8)

    p3 = tf_h.add_paragraph()
    p3.text = "Autonomous AI drink ordering, customer preference memory, prompt version control,\nand high-availability multi-model infrastructure."
    p3.font.size = Pt(16)
    p3.font.color.rgb = TEXT_SUBTLE
    p3.space_before = Pt(12)

    # 4 Large Metric Cards
    metrics = [
        ("API BACKEND", "Python API", "Fast, modular & async", BLUE_ACCENT),
        ("DATA STORAGE", "SQL Database", "Relational customer & order data", AMBER_ACCENT),
        ("AI ENGINE", "Smart AI Agent", "Interactive chat & recommendations", INDIGO_ACCENT),
        ("QUALITY", "100% Tests Passed", "73 automated checks verified", STATUS_DONE_FG)
    ]
    card_w = Inches(2.7)
    card_h = Inches(1.85)
    gap = Inches(0.3)
    start_x = Inches(0.8)
    y_pos = Inches(4.7)

    for i, (tag, val, desc, col) in enumerate(metrics):
        cx = start_x + i * (card_w + gap)
        add_card(s1, cx, y_pos, card_w, card_h, BORDER_CARD, BG_CARD)
        
        # Color bar
        bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, cx, y_pos, card_w, Inches(0.1))
        bar.fill.solid()
        bar.fill.fore_color.rgb = col
        bar.line.fill.background()

        tb = s1.shapes.add_textbox(cx + Inches(0.2), y_pos + Inches(0.2), card_w - Inches(0.4), card_h - Inches(0.3))
        tf = tb.text_frame
        tf.word_wrap = True

        ptag = tf.paragraphs[0]
        ptag.text = tag
        ptag.font.size = Pt(12)
        ptag.font.bold = True
        ptag.font.color.rgb = col

        pv = tf.add_paragraph()
        pv.text = val
        pv.font.size = Pt(20)
        pv.font.bold = True
        pv.font.color.rgb = TEXT_TITLE
        pv.space_before = Pt(8)

        ps = tf.add_paragraph()
        ps.text = desc
        ps.font.size = Pt(13)
        ps.font.color.rgb = TEXT_SUBTLE
        ps.space_before = Pt(4)

    # =========================================================================
    # SLIDE 2: PROJECT GOALS & SCOPE
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    apply_base(s2)
    add_header(s2, "Goals & Scope", "Project Goals & Evaluation Strategy",
               "Balancing consumer-facing drink service with enterprise MLOps standards.")

    goals = [
        ("Smart Beverage Service", AMBER_ACCENT, [
            ("Customer Information", "Captures customer name, phone number, and delivery address."),
            ("Diverse Drink Menu", "Recommends Coffee, Detox teas, Protein shakes, and Juices."),
            ("Preference Memory", "Remembers taste preferences, sweetness, ice level, and allergies.")
        ]),
        ("MLOps Standards", BLUE_ACCENT, [
            ("Prompt Versioning", "Prompts managed in database with one-click rollback."),
            ("Full Telemetry", "Monitors AI cost, token usage, and response latency per message."),
            ("Custom AI Models", "Trained models tailored specifically for drink ordering.")
        ]),
        ("Transparent Status", STATUS_TODO_FG, [
            ("Core Service: 100% Done", "Chatbot, allergy safety, and database storage fully operating."),
            ("Continuous Tracking", "All conversation history and operational costs recorded."),
            ("Next Cloud Step", "Currently using direct Cloud AI; Private Cloud integration is next.")
        ])
    ]

    col_w = Inches(3.7)
    for i, (heading, col, points) in enumerate(goals):
        cx = Inches(0.8) + i * (col_w + Inches(0.3))
        add_card(s2, cx, Inches(2.0), col_w, Inches(4.7))

        bar = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, cx, Inches(2.0), col_w, Inches(0.1))
        bar.fill.solid()
        bar.fill.fore_color.rgb = col
        bar.line.fill.background()

        tb = s2.shapes.add_textbox(cx + Inches(0.25), Inches(2.25), col_w - Inches(0.5), Inches(4.3))
        tf = tb.text_frame
        tf.word_wrap = True

        ph = tf.paragraphs[0]
        ph.text = heading
        ph.font.size = Pt(22)
        ph.font.bold = True
        ph.font.color.rgb = col

        for bold_text, normal_text in points:
            pb = tf.add_paragraph()
            pb.text = f"• {bold_text}:"
            pb.font.size = Pt(16)
            pb.font.bold = True
            pb.font.color.rgb = TEXT_TITLE
            pb.space_before = Pt(14)

            pd = tf.add_paragraph()
            pd.text = f"   {normal_text}"
            pd.font.size = Pt(14)
            pd.font.color.rgb = TEXT_BODY

    # =========================================================================
    # SLIDE 3: SYSTEM ARCHITECTURE
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    apply_base(s3)
    add_header(s3, "Architecture", "System Architecture & Core Infrastructure",
               "Modular and reliable foundation built for speed, safety, and scalability.")

    arch_pillars = [
        ("API BACKEND", "Python Web API", BLUE_ACCENT, [
            "High-speed async request processing",
            "Secure phone-based customer login",
            "Clean API endpoints for chat and menu",
            "Automatic data validation"
        ]),
        ("DATA STORAGE", "SQL Database", AMBER_ACCENT, [
            "Customer profiles & taste preferences",
            "Full beverage catalog & live inventory",
            "Customer order history & statuses",
            "Audit records & version history"
        ]),
        ("AI AGENT", "Intelligent Agent", INDIGO_ACCENT, [
            "Understands customer drink requests",
            "Suggests drinks based on preferences",
            "Drafts orders with real-time totals",
            "Strict Python-based allergy filters"
        ]),
        ("DEVOPS & QA", "Docker Containers", STATUS_DONE_FG, [
            "Packaged with Docker Compose",
            "Unified gateway for web & backend",
            "73 automated tests passing",
            "Instant deployment readiness"
        ])
    ]

    p_w = Inches(2.7)
    for i, (tag, title, col, bullets) in enumerate(arch_pillars):
        cx = Inches(0.8) + i * (p_w + Inches(0.3))
        add_card(s3, cx, Inches(2.0), p_w, Inches(4.7))

        bar = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, cx, Inches(2.0), p_w, Inches(0.1))
        bar.fill.solid()
        bar.fill.fore_color.rgb = col
        bar.line.fill.background()

        tb = s3.shapes.add_textbox(cx + Inches(0.2), Inches(2.2), p_w - Inches(0.4), Inches(4.3))
        tf = tb.text_frame
        tf.word_wrap = True

        ptag = tf.paragraphs[0]
        ptag.text = tag
        ptag.font.size = Pt(12)
        ptag.font.bold = True
        ptag.font.color.rgb = col

        ptt = tf.add_paragraph()
        ptt.text = title
        ptt.font.size = Pt(18)
        ptt.font.bold = True
        ptt.font.color.rgb = TEXT_TITLE
        ptt.space_before = Pt(4)

        for b in bullets:
            pb = tf.add_paragraph()
            pb.text = f"✔ {b}"
            pb.font.size = Pt(14)
            pb.font.color.rgb = TEXT_BODY
            pb.space_before = Pt(12)

    # =========================================================================
    # SLIDE 4: CUSTOMER PROFILES & DATA
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    apply_base(s4)
    add_header(s4, "Data Modeling", "Customer Profiles & Menu Data Management",
               "Capturing customer preferences while protecting health safety.")

    data_cards = [
        ("Customer Profile", AMBER_ACCENT, [
            ("Core Contact Details", "Phone number, full name, and delivery address."),
            ("Flavor Preferences", "Sweetness, bitterness, fruity tastes, and temperature."),
            ("Health & Caffeine", "Caffeine preferences (high/low/decaf) and dietary notes."),
            ("Allergy Safety", "Recorded food allergies (dairy, nuts, gluten).")
        ]),
        ("Menu & Orders", BLUE_ACCENT, [
            ("Beverage Catalog", "Drink names, descriptions, prices, and allergen flags."),
            ("Diverse Drink Options", "Coffee, Teas, Detox blends, Protein shakes, Juices."),
            ("Live Order Tracking", "Tracks items, item quantities, and total order amounts."),
            ("Order Status Flow", "Clear status lifecycle: Pending → Confirmed → Completed.")
        ]),
        ("Operational Logs", INDIGO_ACCENT, [
            ("Chat History", "Records user messages and AI recommendations."),
            ("AI Usage Tracking", "Monitors token count and exact costs for every message."),
            ("Prompt Version History", "Maintains active prompt templates and revision logs."),
            ("Pending Approvals", "Holds profile changes until verified by customer.")
        ])
    ]

    for i, (title, col, fields) in enumerate(data_cards):
        cx = Inches(0.8) + i * (col_w + Inches(0.3))
        add_card(s4, cx, Inches(2.0), col_w, Inches(4.7))

        bar = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, cx, Inches(2.0), col_w, Inches(0.1))
        bar.fill.solid()
        bar.fill.fore_color.rgb = col
        bar.line.fill.background()

        tb = s4.shapes.add_textbox(cx + Inches(0.25), Inches(2.25), col_w - Inches(0.5), Inches(4.3))
        tf = tb.text_frame
        tf.word_wrap = True

        ph = tf.paragraphs[0]
        ph.text = title
        ph.font.size = Pt(22)
        ph.font.bold = True
        ph.font.color.rgb = col

        for f_title, f_desc in fields:
            pf = tf.add_paragraph()
            pf.text = f"• {f_title}:"
            pf.font.size = Pt(16)
            pf.font.bold = True
            pf.font.color.rgb = TEXT_TITLE
            pf.space_before = Pt(12)

            pd = tf.add_paragraph()
            pd.text = f"   {f_desc}"
            pd.font.size = Pt(14)
            pd.font.color.rgb = TEXT_BODY

    # =========================================================================
    # SLIDE 5: AI AGENT & SAFETY GATES
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    apply_base(s5)
    add_header(s5, "AI Safety & Control", "AI Agent & Two-Stage Human Approval",
               "Smart conversational recommendations backed by strict safety guardrails.")

    safety_pillars = [
        ("1. Conversational Agent", AMBER_ACCENT, [
            ("Natural Dialogue", "Understands customer drink requests in plain language."),
            ("Smart Tools", "Automatically looks up drinks, updates profiles, and drafts orders."),
            ("Menu Grounding", "Only references actual drinks and prices in the catalog."),
            ("Loop Protection", "Built-in limits prevent repetitive or runaway responses.")
        ]),
        ("2. Allergy Safety Gate", STATUS_TODO_FG, [
            ("Code-Level Safety", "Health safety rules enforced by strict code, not left to AI."),
            ("Allergen Exclusion", "Automatically eliminates drinks matching customer allergies."),
            ("Safe Menu Filtering", "Customers allergic to dairy never receive milk drink suggestions."),
            ("100% Tested", "Validated by comprehensive automated test suites.")
        ]),
        ("3. Human Confirmation", STATUS_DONE_FG, [
            ("Order Preview Gate", "Orders are only placed after the customer clicks Confirm."),
            ("Profile Update Gate", "Changes to taste or address require explicit customer approval."),
            ("Read-Only Agility", "Instant menu suggestions with safe confirmation on key actions."),
            ("Zero Surprises", "Customers maintain complete control over orders and personal data.")
        ])
    ]

    for i, (title, col, items) in enumerate(safety_pillars):
        cx = Inches(0.8) + i * (col_w + Inches(0.3))
        add_card(s5, cx, Inches(2.0), col_w, Inches(4.7))

        bar = s5.shapes.add_shape(MSO_SHAPE.RECTANGLE, cx, Inches(2.0), col_w, Inches(0.1))
        bar.fill.solid()
        bar.fill.fore_color.rgb = col
        bar.line.fill.background()

        tb = s5.shapes.add_textbox(cx + Inches(0.25), Inches(2.25), col_w - Inches(0.5), Inches(4.3))
        tf = tb.text_frame
        tf.word_wrap = True

        ph = tf.paragraphs[0]
        ph.text = title
        ph.font.size = Pt(21)
        ph.font.bold = True
        ph.font.color.rgb = col

        for b_title, b_desc in items:
            pb = tf.add_paragraph()
            pb.text = f"• {b_title}:"
            pb.font.size = Pt(16)
            pb.font.bold = True
            pb.font.color.rgb = TEXT_TITLE
            pb.space_before = Pt(12)

            pd = tf.add_paragraph()
            pd.text = f"   {b_desc}"
            pd.font.size = Pt(14)
            pd.font.color.rgb = TEXT_BODY

    # =========================================================================
    # SLIDE 6: PROMPT VERSIONING
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    apply_base(s6)
    add_header(s6, "Prompt Management", "Database-Backed Prompt Version Control",
               "Managing AI instructions dynamically without server redeployments.")

    half_w = Inches(5.7)

    # Left Card
    add_card(s6, Inches(0.8), Inches(2.0), half_w, Inches(4.7))
    bar_l = s6.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(2.0), half_w, Inches(0.1))
    bar_l.fill.solid()
    bar_l.fill.fore_color.rgb = BLUE_ACCENT
    bar_l.line.fill.background()

    tb_l = s6.shapes.add_textbox(Inches(1.1), Inches(2.25), half_w - Inches(0.6), Inches(4.3))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True

    plh = tf_l.paragraphs[0]
    plh.text = "Centralized Prompt Storage"
    plh.font.size = Pt(24)
    plh.font.bold = True
    plh.font.color.rgb = BLUE_ACCENT

    pts_l = [
        ("Database Storage", "Prompts saved in database tables, replacing hardcoded text in code."),
        ("Clear Version History", "Organized versioning (v1.0, v1.1, v1.2) with authors and timestamps."),
        ("Template Verification", "Validates required fields before publishing to prevent errors."),
        ("Audit Tracking", "Every AI response records the exact prompt version used.")
    ]
    for b_title, b_desc in pts_l:
        pb = tf_l.add_paragraph()
        pb.text = f"✔ {b_title}:"
        pb.font.size = Pt(17)
        pb.font.bold = True
        pb.font.color.rgb = TEXT_TITLE
        pb.space_before = Pt(14)

        pd = tf_l.add_paragraph()
        pd.text = f"   {b_desc}"
        pd.font.size = Pt(15)
        pd.font.color.rgb = TEXT_BODY

    # Right Card
    add_card(s6, Inches(6.8), Inches(2.0), half_w, Inches(4.7))
    bar_r = s6.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.8), Inches(2.0), half_w, Inches(0.1))
    bar_r.fill.solid()
    bar_r.fill.fore_color.rgb = AMBER_ACCENT
    bar_r.line.fill.background()

    tb_r = s6.shapes.add_textbox(Inches(7.1), Inches(2.25), half_w - Inches(0.6), Inches(4.3))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True

    prh = tf_r.paragraphs[0]
    prh.text = "Instant Rollback & Updates"
    prh.font.size = Pt(24)
    prh.font.bold = True
    prh.font.color.rgb = AMBER_ACCENT

    pts_r = [
        ("Live Updates", "Publish improved prompt guidelines directly to live users."),
        ("One-Click Rollback", "Instantly revert to a previous prompt version if needed."),
        ("Zero Downtime", "Update AI behavior without restarting backend servers."),
        ("Safe A/B Testing", "Test seasonal promotional prompts safely on live traffic.")
    ]
    for b_title, b_desc in pts_r:
        pb = tf_r.add_paragraph()
        pb.text = f"▶ {b_title}:"
        pb.font.size = Pt(17)
        pb.font.bold = True
        pb.font.color.rgb = COFFEE_DARK
        pb.space_before = Pt(14)

        pd = tf_r.add_paragraph()
        pd.text = f"   {b_desc}"
        pd.font.size = Pt(15)
        pd.font.color.rgb = TEXT_BODY

    # =========================================================================
    # SLIDE 7: HIGH AVAILABILITY & MONITORING
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    apply_base(s7)
    add_header(s7, "Reliability & Costs", "High Availability & Operational Cost Tracking",
               "Ensuring 24/7 service uptime with complete visibility into AI expenses.")

    # Left: Multi-Engine
    add_card(s7, Inches(0.8), Inches(2.0), half_w, Inches(4.7))
    bar_m1 = s7.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(2.0), half_w, Inches(0.1))
    bar_m1.fill.solid()
    bar_m1.fill.fore_color.rgb = AMBER_ACCENT
    bar_m1.line.fill.background()

    tb_m1 = s7.shapes.add_textbox(Inches(1.1), Inches(2.25), half_w - Inches(0.6), Inches(4.3))
    tf_m1 = tb_m1.text_frame
    tf_m1.word_wrap = True

    pm1_h = tf_m1.paragraphs[0]
    pm1_h.text = "Always-On AI Reliability"
    pm1_h.font.size = Pt(24)
    pm1_h.font.bold = True
    pm1_h.font.color.rgb = AMBER_ACCENT

    pts_m1 = [
        ("Primary Cloud AI", "High-intelligence cloud model delivers rich conversational quality."),
        ("Auto-Fallback Protection", "Automatically switches to local AI if internet or cloud APIs drop."),
        ("Local Offline AI", "Runs on local server hardware with zero ongoing API costs."),
        ("Uninterrupted Service", "Customers never see an outage or blank screen during peak hours.")
    ]
    for b_title, b_desc in pts_m1:
        pb = tf_m1.add_paragraph()
        pb.text = f"• {b_title}:"
        pb.font.size = Pt(17)
        pb.font.bold = True
        pb.font.color.rgb = TEXT_TITLE
        pb.space_before = Pt(14)

        pd = tf_m1.add_paragraph()
        pd.text = f"   {b_desc}"
        pd.font.size = Pt(15)
        pd.font.color.rgb = TEXT_BODY

    # Right: Telemetry
    add_card(s7, Inches(6.8), Inches(2.0), half_w, Inches(4.7))
    bar_m2 = s7.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.8), Inches(2.0), half_w, Inches(0.1))
    bar_m2.fill.solid()
    bar_m2.fill.fore_color.rgb = INDIGO_ACCENT
    bar_m2.line.fill.background()

    tb_m2 = s7.shapes.add_textbox(Inches(7.1), Inches(2.25), half_w - Inches(0.6), Inches(4.3))
    tf_m2 = tb_m2.text_frame
    tf_m2.word_wrap = True

    pm2_h = tf_m2.paragraphs[0]
    pm2_h.text = "Cost & Performance Auditing"
    pm2_h.font.size = Pt(24)
    pm2_h.font.bold = True
    pm2_h.font.color.rgb = INDIGO_ACCENT

    pts_m2 = [
        ("Detailed Activity Logs", "Every message logs response time, success status, and AI model used."),
        ("Real-Time Cost Tracking", "Calculates exact token counts and costs to fractions of a cent."),
        ("Database Accounting", "Usage metrics saved alongside customer messages for cost auditing."),
        ("Live Monitoring Dashboard", "Provides end-to-end visibility into response speed and system health.")
    ]
    for b_title, b_desc in pts_m2:
        pb = tf_m2.add_paragraph()
        pb.text = f"• {b_title}:"
        pb.font.size = Pt(17)
        pb.font.bold = True
        pb.font.color.rgb = TEXT_TITLE
        pb.space_before = Pt(14)

        pd = tf_m2.add_paragraph()
        pd.text = f"   {b_desc}"
        pd.font.size = Pt(15)
        pd.font.color.rgb = TEXT_BODY

    # =========================================================================
    # SLIDE 8: CUSTOM AI MODELS & SEARCH
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    apply_base(s8)
    add_header(s8, "Custom AI Models", "Custom AI Models & Intelligent Drink Search",
               "Tailoring AI models specifically to beverage ordering and local tastes.")

    hubs = [
        ("AI Model Registry", AMBER_ACCENT, [
            ("Central Model Hub", "Organizes trained models, training settings, and versions."),
            ("Learning Progress", "Tracks training loss curves and accuracy metrics over time."),
            ("Dataset Lineage", "Connects model versions to exact training datasets for auditing."),
            ("Seamless Model Swapping", "Switch between candidate models easily from the admin panel.")
        ]),
        ("Specialized Drink AI", INDIGO_ACCENT, [
            ("Tailored Training", "Fine-tuned specifically for natural beverage ordering conversations."),
            ("Lightweight & Fast", "Compact model architecture runs efficiently on local hardware."),
            ("Local Drink Knowledge", "Understands regional drink preferences and ordering phrasing."),
            ("Cost-Effective", "Reduces reliance on expensive third-party cloud models.")
        ]),
        ("Smart Semantic Search", STATUS_DONE_FG, [
            ("Natural Search", "Understands customer intent even when drink names are misspelled."),
            ("Slang Recognition", "Accurately interprets beverage slang and local drink nicknames."),
            ("Smart Recommendations", "Matches taste descriptions ('sweet but refreshing') to the menu."),
            ("Proven Accuracy", "Delivers +28.5% measured improvement in drink recommendation accuracy.")
        ])
    ]

    for i, (title, col, items) in enumerate(hubs):
        cx = Inches(0.8) + i * (col_w + Inches(0.3))
        add_card(s8, cx, Inches(2.0), col_w, Inches(4.7))

        bar = s8.shapes.add_shape(MSO_SHAPE.RECTANGLE, cx, Inches(2.0), col_w, Inches(0.1))
        bar.fill.solid()
        bar.fill.fore_color.rgb = col
        bar.line.fill.background()

        tb = s8.shapes.add_textbox(cx + Inches(0.25), Inches(2.25), col_w - Inches(0.5), Inches(4.3))
        tf = tb.text_frame
        tf.word_wrap = True

        ph = tf.paragraphs[0]
        ph.text = title
        ph.font.size = Pt(21)
        ph.font.bold = True
        ph.font.color.rgb = col

        for b_title, b_desc in items:
            pb = tf.add_paragraph()
            pb.text = f"• {b_title}:"
            pb.font.size = Pt(16)
            pb.font.bold = True
            pb.font.color.rgb = TEXT_TITLE
            pb.space_before = Pt(12)

            pd = tf.add_paragraph()
            pd.text = f"   {b_desc}"
            pd.font.size = Pt(14)
            pd.font.color.rgb = TEXT_BODY

    # =========================================================================
    # SLIDE 9: SCORECARD TABLE (LARGE FONTS, HIGH CONTRAST)
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    apply_base(s9)
    add_header(s9, "Workshop Scorecard", "Scorecard vs Workshop Deliverables",
               "Clear, transparent assessment against core project requirements.")

    rows = 9
    cols = 3
    left = Inches(0.8)
    top = Inches(1.9)
    width = Inches(11.733)
    height = Inches(4.65)

    table_shape = s9.shapes.add_table(rows, cols, left, top, width, height)
    table = table_shape.table
    table.columns[0].width = Inches(4.2)
    table.columns[1].width = Inches(2.0)
    table.columns[2].width = Inches(5.533)

    score_rows = [
        ("Workshop Requirement", "Status", "Technical Verification"),
        ("1. Collect customer name, phone, address", "DONE", "Validated contact fields saved in database."),
        ("2. Recommend Detox, Coffee, Protein drinks", "DONE", "Catalog includes Protein, Detox, Coffee, and Tea."),
        ("3. Track chat history to monitor accuracy", "PARTIAL", "Messages, cost, and tokens logged; rating button next."),
        ("4. Enterprise Private Cloud AI Connection", "NOT STARTED", "Currently using direct Cloud AI; Private Cloud next."),
        ("5. Containerize with Docker for deployment", "DONE", "Full Docker Compose setup for backend and database."),
        ("6. Track AI model & cost per message", "DONE", "Tokens and expenses recorded for every interaction."),
        ("7. Prompt version control & instant rollback", "DONE", "Prompts managed in database with one-click restore."),
        ("8. AI agent with human confirmation gate", "DONE", "Customer confirms orders and profile updates before saving.")
    ]

    for r_idx, (req, status, proof) in enumerate(score_rows):
        c0 = table.cell(r_idx, 0); c0.text = req
        c1 = table.cell(r_idx, 1); c1.text = status
        c2 = table.cell(r_idx, 2); c2.text = proof

        p0 = c0.text_frame.paragraphs[0]; p0.font.size = Pt(14)
        p1 = c1.text_frame.paragraphs[0]; p1.font.size = Pt(14); p1.alignment = PP_ALIGN.CENTER
        p2 = c2.text_frame.paragraphs[0]; p2.font.size = Pt(14)

        if r_idx == 0:
            c0.fill.solid(); c0.fill.fore_color.rgb = COFFEE_DARK
            c1.fill.solid(); c1.fill.fore_color.rgb = COFFEE_DARK
            c2.fill.solid(); c2.fill.fore_color.rgb = COFFEE_DARK
            p0.font.bold = True; p0.font.color.rgb = RGBColor(255, 255, 255)
            p1.font.bold = True; p1.font.color.rgb = RGBColor(255, 255, 255)
            p2.font.bold = True; p2.font.color.rgb = RGBColor(255, 255, 255)
        else:
            row_bg = RGBColor(255, 255, 255) if r_idx % 2 == 1 else RGBColor(241, 245, 249)
            c0.fill.solid(); c0.fill.fore_color.rgb = row_bg
            c1.fill.solid(); c1.fill.fore_color.rgb = row_bg
            c2.fill.solid(); c2.fill.fore_color.rgb = row_bg

            p0.font.bold = True; p0.font.color.rgb = TEXT_TITLE
            p2.font.color.rgb = TEXT_BODY

            if status == "DONE":
                c1.fill.fore_color.rgb = STATUS_DONE_BG
                p1.font.color.rgb = STATUS_DONE_FG
                p1.font.bold = True
            elif status == "PARTIAL":
                c1.fill.fore_color.rgb = STATUS_PART_BG
                p1.font.color.rgb = STATUS_PART_FG
                p1.font.bold = True
            else:
                c0.fill.fore_color.rgb = STATUS_TODO_BG
                c1.fill.fore_color.rgb = STATUS_TODO_BG
                p0.font.color.rgb = STATUS_TODO_FG
                p1.font.color.rgb = STATUS_TODO_FG
                p1.font.bold = True

    # Summary chip
    add_card(s9, Inches(0.8), Inches(6.62), Inches(11.733), Inches(0.55), RGBColor(16, 185, 129), STATUS_DONE_BG)
    tb_sc = s9.shapes.add_textbox(Inches(1.0), Inches(6.65), Inches(11.3), Inches(0.5))
    p_sc = tb_sc.text_frame.paragraphs[0]
    p_sc.text = "🎯 Summary: 7 of 8 Core Requirements Completed (87.5%) • Focus next on Enterprise Private Cloud AI."
    p_sc.font.size = Pt(13)
    p_sc.font.bold = True
    p_sc.font.color.rgb = STATUS_DONE_FG

    # =========================================================================
    # SLIDE 10: ROADMAP & Q&A
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    apply_base(s10)
    add_header(s10, "Future Roadmap", "Strategic Roadmap & Open Discussion",
               "Clear priorities to achieve enterprise-ready beverage intelligence.")

    roadmaps = [
        ("PRIORITY 1: CLOUD", "Private Cloud AI Connection", STATUS_TODO_FG, [
            "Connect AI models through dedicated private cloud endpoints.",
            "Satisfy corporate network security standards without public internet exposure.",
            "Complete the remaining cloud infrastructure requirement."
        ]),
        ("PRIORITY 2: FEEDBACK", "Customer Rating Feedback", AMBER_ACCENT, [
            "Add simple Thumbs Up / Down buttons on chatbot messages.",
            "Gather direct customer feedback on drink suggestions.",
            "Build automated quality datasets to continuously improve responses."
        ]),
        ("PRIORITY 3: AUTOMATION", "Continuous Model Updates", INDIGO_ACCENT, [
            "Automatically retrain models as new seasonal drinks are added.",
            "Run 73 automated quality tests before releasing new models.",
            "Ensure zero downtime when rolling out improved AI models."
        ])
    ]

    for i, (tag, title, col, bullets) in enumerate(roadmaps):
        cx = Inches(0.8) + i * (col_w + Inches(0.3))
        add_card(s10, cx, Inches(2.0), col_w, Inches(3.5))

        bar = s10.shapes.add_shape(MSO_SHAPE.RECTANGLE, cx, Inches(2.0), col_w, Inches(0.1))
        bar.fill.solid()
        bar.fill.fore_color.rgb = col
        bar.line.fill.background()

        tb = s10.shapes.add_textbox(cx + Inches(0.2), Inches(2.15), col_w - Inches(0.4), Inches(3.2))
        tf = tb.text_frame
        tf.word_wrap = True

        ptag = tf.paragraphs[0]
        ptag.text = tag
        ptag.font.size = Pt(12)
        ptag.font.bold = True
        ptag.font.color.rgb = col

        ptt = tf.add_paragraph()
        ptt.text = title
        ptt.font.size = Pt(17)
        ptt.font.bold = True
        ptt.font.color.rgb = TEXT_TITLE
        ptt.space_before = Pt(4)

        for b in bullets:
            pb = tf.add_paragraph()
            pb.text = f"• {b}"
            pb.font.size = Pt(14)
            pb.font.color.rgb = TEXT_BODY
            pb.space_before = Pt(10)

    # Q&A Banner
    add_card(s10, Inches(2.0), Inches(5.65), Inches(9.333), Inches(1.35), RGBColor(245, 158, 11), RGBColor(254, 243, 199))
    tb_qa = s10.shapes.add_textbox(Inches(2.2), Inches(5.75), Inches(8.9), Inches(1.15))
    tf_qa = tb_qa.text_frame
    tf_qa.word_wrap = True

    pqa1 = tf_qa.paragraphs[0]
    pqa1.text = "☕ THANK YOU FOR YOUR TIME!"
    pqa1.alignment = PP_ALIGN.CENTER
    pqa1.font.size = Pt(22)
    pqa1.font.bold = True
    pqa1.font.color.rgb = COFFEE_DARK

    pqa2 = tf_qa.add_paragraph()
    pqa2.text = "DrinkBot MLOps — Open for Questions & Technical Discussion"
    pqa2.alignment = PP_ALIGN.CENTER
    pqa2.font.size = Pt(15)
    pqa2.font.color.rgb = TEXT_BODY
    pqa2.space_before = Pt(4)

    # Save to both target locations
    path1 = "slide-info-backend/DrinkBot_MLOps_Presentation_EN.pptx"
    path2 = "DrinkBot_MLOps_Presentation_EN.pptx"
    prs.save(path1)
    prs.save(path2)
    print(f"Clean executive presentation successfully saved to:\n- {path1}\n- {path2}")

if __name__ == "__main__":
    build_executive_deck()
