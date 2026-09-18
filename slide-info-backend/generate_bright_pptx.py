"""Generate a professional, bright-themed widescreen (.pptx) presentation in English.
Features:
- High contrast, modern bright coffee & clean tech color palette
- Large, highly legible typography (titles 30-40pt, body 14-18pt)
- Standard executive slide design rules (visual hierarchy, cards, status pills)
- 16:9 Widescreen format
"""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def build_deck():
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # --- MODERN BRIGHT COLOR PALETTE ---
    BG_LIGHT = RGBColor(248, 250, 252)       # Slate 50 (#f8fafc)
    BG_CARD = RGBColor(255, 255, 255)        # Pure White (#ffffff)
    BORDER_LIGHT = RGBColor(226, 232, 240)   # Slate 200 (#e2e8f0)
    BORDER_AMBER = RGBColor(245, 158, 11)    # Amber 500 (#f59e0b)
    
    TEXT_DARK = RGBColor(15, 23, 42)         # Slate 900 (#0f172a) - high contrast
    TEXT_BODY = RGBColor(30, 41, 59)         # Slate 800 (#1e293b)
    TEXT_MUTED = RGBColor(71, 85, 105)       # Slate 600 (#475569)
    TEXT_DIM = RGBColor(148, 163, 184)       # Slate 400 (#94a3b8)
    
    PRIMARY_COFFEE = RGBColor(120, 53, 15)   # Amber 900 (#78350f)
    ACCENT_AMBER = RGBColor(180, 83, 9)      # Amber 700 (#b45309)
    ACCENT_BLUE = RGBColor(2, 132, 199)      # Sky 600 (#0284c7)
    ACCENT_INDIGO = RGBColor(67, 56, 202)    # Indigo 700 (#4338ca)
    
    STATUS_DONE_BG = RGBColor(209, 250, 229) # Mint / Emerald 100
    STATUS_DONE_FG = RGBColor(4, 120, 87)    # Emerald 700
    
    STATUS_PARTIAL_BG = RGBColor(254, 243, 199) # Amber 100
    STATUS_PARTIAL_FG = RGBColor(180, 83, 9)    # Amber 700
    
    STATUS_TODO_BG = RGBColor(255, 228, 230)    # Rose 100
    STATUS_TODO_FG = RGBColor(190, 18, 60)      # Rose 700

    def apply_slide_base(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_LIGHT
        bg.line.fill.background()

        # Bottom footer
        ft_tb = slide.shapes.add_textbox(Inches(0.8), Inches(6.95), Inches(11.733), Inches(0.4))
        p = ft_tb.text_frame.paragraphs[0]
        p.text = "DrinkBot MLOps • TMA Solutions F&B AI Workshop 2026 • Backend Architecture Review"
        p.font.size = Pt(10)
        p.font.color.rgb = TEXT_DIM

    def add_header(slide, tag_text, title_text, subtitle_text=""):
        # Category Tag Pill
        tag_shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.42), Inches(3.2), Inches(0.32))
        tag_shape.fill.solid()
        tag_shape.fill.fore_color.rgb = RGBColor(254, 243, 199)
        tag_shape.line.color.rgb = RGBColor(251, 191, 36)
        tag_shape.line.width = Pt(1)
        tf_t = tag_shape.text_frame
        p_t = tf_t.paragraphs[0]
        p_t.text = f"● {tag_text.upper()}"
        p_t.alignment = PP_ALIGN.CENTER
        p_t.font.size = Pt(10)
        p_t.font.bold = True
        p_t.font.color.rgb = PRIMARY_COFFEE

        # Main Title (Bold & Large)
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.78), Inches(11.733), Inches(0.65))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(26)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_DARK

        # Subtitle
        if subtitle_text:
            sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.42), Inches(11.733), Inches(0.4))
            tf_sub = sub_box.text_frame
            tf_sub.word_wrap = True
            p_sub = tf_sub.paragraphs[0]
            p_sub.text = subtitle_text
            p_sub.font.size = Pt(13)
            p_sub.font.color.rgb = TEXT_MUTED

    def add_card(slide, left, top, width, height, border_color=BORDER_LIGHT, bg_color=BG_CARD):
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
    apply_slide_base(s1)

    # Top Brand Kicker
    kicker = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.1), Inches(3.6), Inches(0.42))
    kicker.fill.solid()
    kicker.fill.fore_color.rgb = RGBColor(254, 243, 199)
    kicker.line.color.rgb = RGBColor(245, 158, 11)
    kicker.line.width = Pt(1.2)
    tf_k = kicker.text_frame
    pk = tf_k.paragraphs[0]
    pk.text = "☕ TMA SOLUTIONS • F&B AI WORKSHOP 2026"
    pk.alignment = PP_ALIGN.CENTER
    pk.font.size = Pt(11)
    pk.font.bold = True
    pk.font.color.rgb = PRIMARY_COFFEE

    # Hero Title Block
    hero_box = s1.shapes.add_textbox(Inches(0.8), Inches(1.75), Inches(11.7), Inches(2.6))
    tf_h = hero_box.text_frame
    tf_h.word_wrap = True

    p1 = tf_h.paragraphs[0]
    p1.text = "DrinkBot MLOps"
    p1.font.size = Pt(46)
    p1.font.bold = True
    p1.font.color.rgb = PRIMARY_COFFEE

    p2 = tf_h.add_paragraph()
    p2.text = "Backend Architecture & Engineering Status Review"
    p2.font.size = Pt(28)
    p2.font.bold = True
    p2.font.color.rgb = TEXT_DARK
    p2.space_before = Pt(8)

    p3 = tf_h.add_paragraph()
    p3.text = "Production-grade autonomous beverage recommendation agent with DB prompt versioning,\ntwo-stage human-in-the-loop approval, local fine-tuned SLM, and zero-cost Ollama fallback."
    p3.font.size = Pt(15)
    p3.font.color.rgb = TEXT_MUTED
    p3.space_before = Pt(12)

    # 4 Highlights Metric Cards
    metrics = [
        ("CORE BACKEND", "FastAPI + AsyncIO", "Async SQLAlchemy 2.0 + Alembic", ACCENT_BLUE),
        ("DATABASE", "PostgreSQL 16", "Normalized F&B schema + Audit Logs", ACCENT_AMBER),
        ("INFERENCE HUB", "LangChain + Ollama", "Zero-cost local fallback + Cloud LLM", ACCENT_INDIGO),
        ("VERIFIED QUALITY", "73 / 73 Passed", "100% test pass rate across 11 suites", STATUS_DONE_FG)
    ]
    card_w = Inches(2.7)
    card_h = Inches(1.8)
    gap = Inches(0.3)
    start_x = Inches(0.8)
    y_pos = Inches(4.7)

    for i, (tag, big_val, sub_val, col) in enumerate(metrics):
        cx = start_x + i * (card_w + gap)
        add_card(s1, cx, y_pos, card_w, card_h, BORDER_LIGHT, BG_CARD)
        
        # Color accent header bar
        bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, cx, y_pos, card_w, Inches(0.08))
        bar.fill.solid()
        bar.fill.fore_color.rgb = col
        bar.line.fill.background()

        tb = s1.shapes.add_textbox(cx + Inches(0.2), y_pos + Inches(0.15), card_w - Inches(0.4), card_h - Inches(0.3))
        tf = tb.text_frame
        tf.word_wrap = True

        ptag = tf.paragraphs[0]
        ptag.text = tag
        ptag.font.size = Pt(11)
        ptag.font.bold = True
        ptag.font.color.rgb = col

        pv = tf.add_paragraph()
        pv.text = big_val
        pv.font.size = Pt(16)
        pv.font.bold = True
        pv.font.color.rgb = TEXT_DARK
        pv.space_before = Pt(8)

        ps = tf.add_paragraph()
        ps.text = sub_val
        ps.font.size = Pt(11)
        ps.font.color.rgb = TEXT_MUTED
        ps.space_before = Pt(4)

    # =========================================================================
    # SLIDE 2: SECTION GOALS & EVALUATION STRATEGY
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    apply_slide_base(s2)
    add_header(s2, "Executive Strategy", "Workshop Brief Objectives & Section Goals",
               "A transparent status update aligning technical deliverables with workshop requirements.")

    cards_s2 = [
        ("Core F&B Delivery", ACCENT_AMBER, [
            ("Entity Collection", "Captures user name, phone, delivery address with strict VN phone validation."),
            ("Category Coverage", "Recommends Detox, Coffee, and Protein drinks alongside teas and fruit juices."),
            ("Safe Persistence", "Relational persistence with full preference profiling in PostgreSQL.")
        ]),
        ("MLOps Standards", ACCENT_BLUE, [
            ("Prompt Lifecycle", "Database-backed PromptVersion store with semantic versions and SHA-256 hashes."),
            ("Observability", "Structured JSON logging capturing latency, token usage, and cost per message."),
            ("Model Experimentation", "Centralized Model Registry with local Gemma-2B LoRA fine-tuning & RAG adapter.")
        ]),
        ("Objective Transparency", STATUS_TODO_FG, [
            ("Verified Done", "Core chatbot, guardrails, Dockerization, and prompt versioning are 100% complete."),
            ("Partial Capability", "Full chat telemetry stored; user feedback rating (like/dislike) is pending."),
            ("Key Architectural Gap", "AWS Bedrock via VPC Endpoint is not started (currently direct OpenAI/Ollama).")
        ])
    ]

    col_w = Inches(3.7)
    for i, (heading, col, points) in enumerate(cards_s2):
        cx = Inches(0.8) + i * (col_w + Inches(0.3))
        add_card(s2, cx, Inches(2.0), col_w, Inches(4.7))
        
        # Color bar top
        bar = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, cx, Inches(2.0), col_w, Inches(0.1))
        bar.fill.solid()
        bar.fill.fore_color.rgb = col
        bar.line.fill.background()

        tb = s2.shapes.add_textbox(cx + Inches(0.25), Inches(2.25), col_w - Inches(0.5), Inches(4.3))
        tf = tb.text_frame
        tf.word_wrap = True

        ph = tf.paragraphs[0]
        ph.text = heading
        ph.font.size = Pt(18)
        ph.font.bold = True
        ph.font.color.rgb = col

        for bold_title, desc in points:
            pb = tf.add_paragraph()
            pb.text = f"• {bold_title}"
            pb.font.size = Pt(14)
            pb.font.bold = True
            pb.font.color.rgb = TEXT_DARK
            pb.space_before = Pt(12)

            pd = tf.add_paragraph()
            pd.text = f"   {desc}"
            pd.font.size = Pt(12)
            pd.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 3: SYSTEM ARCHITECTURE
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    apply_slide_base(s3)
    add_header(s3, "System Architecture", "High-Throughput Asynchronous Backend Stack",
               "Modular, async-first architecture designed for resilience, observability, and scale.")

    pillars = [
        ("API LAYER", "FastAPI + Uvicorn", ACCENT_AMBER, [
            "Non-blocking async request handlers",
            "Pydantic v2 schemas & validations",
            "Simplified phone-based JWT authentication",
            "6 REST routers: auth, chat, menu, prompts, telemetry, users"
        ]),
        ("DATA & ORM", "PostgreSQL 16", ACCENT_BLUE, [
            "SQLAlchemy 2.0 Async Session (asyncpg)",
            "Alembic auto-migrations (0001 → 0003)",
            "Pre-seeded catalog (Coffee, Detox, Protein)",
            "Audited PromptVersion & PendingChanges"
        ]),
        ("AGENT LOOP", "LangChain Tools", ACCENT_INDIGO, [
            "Autonomous ReAct tool loop (Max 4 turns)",
            "3 core tools: Profile, Recommend, Order",
            "Deterministic Python allergen safety gate",
            "Zero-cost local Ollama inference fallback"
        ]),
        ("DEVOPS & QA", "Docker + Pytest", STATUS_DONE_FG, [
            "Docker Compose multi-service topology",
            "Unified Nginx reverse proxy gateway (port 80)",
            "73/73 unit & integration tests passing",
            "Langfuse tracing & JSON structured logs"
        ])
    ]

    p_w = Inches(2.7)
    for i, (tag, title, col, bullets) in enumerate(pillars):
        cx = Inches(0.8) + i * (p_w + Inches(0.3))
        add_card(s3, cx, Inches(2.0), p_w, Inches(4.7))

        bar = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, cx, Inches(2.0), p_w, Inches(0.08))
        bar.fill.solid()
        bar.fill.fore_color.rgb = col
        bar.line.fill.background()

        tb = s3.shapes.add_textbox(cx + Inches(0.2), Inches(2.15), p_w - Inches(0.4), Inches(4.4))
        tf = tb.text_frame
        tf.word_wrap = True

        ptag = tf.paragraphs[0]
        ptag.text = tag
        ptag.font.size = Pt(11)
        ptag.font.bold = True
        ptag.font.color.rgb = col

        ptt = tf.add_paragraph()
        ptt.text = title
        ptt.font.size = Pt(16)
        ptt.font.bold = True
        ptt.font.color.rgb = TEXT_DARK
        ptt.space_before = Pt(4)

        for b in bullets:
            pb = tf.add_paragraph()
            pb.text = f"✔ {b}"
            pb.font.size = Pt(12)
            pb.font.color.rgb = TEXT_BODY
            pb.space_before = Pt(10)

    # =========================================================================
    # SLIDE 4: DOMAIN MODEL & ENTITY EXTRACTION
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    apply_slide_base(s4)
    add_header(s4, "Data Modeling", "Domain Entities & Customer Profile Extraction",
               "Capturing workshop-mandated user entities with rich preference structures.")

    domains = [
        ("Customer Profile Entities", ACCENT_AMBER, [
            ("User Entity", "phone (Unique Identifier), name, delivery address."),
            ("Taste Preferences", "Array of flavor profiles: sweet, bitter, fruity, sour."),
            ("Beverage Categories", "Preferred drink types: tea, coffee, smoothie, protein."),
            ("Health Constraints", "temperature (iced/hot), caffeine (high/low/none)."),
            ("Allergies", "dairy, nuts, gluten — triggers automatic exclusion.")
        ]),
        ("Menu & Commercial Orders", ACCENT_BLUE, [
            ("MenuItem Catalog", "name, category, price, description, is_available."),
            ("Allergen Metadata", "Structured array of declared allergens per item."),
            ("Category Diversity", "5 curated categories: Coffee, Tea, Protein, Detox, Juices."),
            ("Order & OrderItem", "Links customer to selected items with live prices."),
            ("Order Lifecycle", "Status transitions: pending → placed / cancelled.")
        ]),
        ("MLOps Telemetry & State", ACCENT_INDIGO, [
            ("ChatMessage", "Logs role, content, user_id, and timestamps."),
            ("Token & Cost Metrics", "Stores model_name, input_tokens, output_tokens, cost."),
            ("PromptVersion Store", "Immutable record of templates, hashes, and active flags."),
            ("PendingPreferenceChange", "Staged user profile changes awaiting human confirmation."),
            ("Audit Lineage", "Full traceability from customer query to LLM generation.")
        ])
    ]

    for i, (title, col, fields) in enumerate(domains):
        cx = Inches(0.8) + i * (col_w + Inches(0.3))
        add_card(s4, cx, Inches(2.0), col_w, Inches(4.7))

        bar = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, cx, Inches(2.0), col_w, Inches(0.08))
        bar.fill.solid()
        bar.fill.fore_color.rgb = col
        bar.line.fill.background()

        tb = s4.shapes.add_textbox(cx + Inches(0.25), Inches(2.15), col_w - Inches(0.5), Inches(4.4))
        tf = tb.text_frame
        tf.word_wrap = True

        ph = tf.paragraphs[0]
        ph.text = title
        ph.font.size = Pt(17)
        ph.font.bold = True
        ph.font.color.rgb = col

        for f_title, f_desc in fields:
            pf = tf.add_paragraph()
            pf.text = f"• {f_title}:"
            pf.font.size = Pt(13)
            pf.font.bold = True
            pf.font.color.rgb = TEXT_DARK
            pf.space_before = Pt(8)

            pd = tf.add_paragraph()
            pd.text = f"   {f_desc}"
            pd.font.size = Pt(12)
            pd.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 5: CHAT AGENT & HUMAN-IN-THE-LOOP
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    apply_slide_base(s5)
    add_header(s5, "Agent Intelligence & Safety", "Autonomous Chat Agent & Two-Stage Human Approval",
               "Balancing dynamic conversational flexibility with rigorous deterministic safeguards.")

    agent_cards = [
        ("1. Tool-Calling ReAct Loop", ACCENT_AMBER, 
         "Autonomous execution up to 4 iterations with dedicated tool executors:",
         [("recommend_drink", "Searches live menu items matching taste query & constraints."),
          ("update_profile", "Extracts newly disclosed customer preferences from conversation."),
          ("order", "Calculates totals and constructs pending order preview for checkout.")]),
        
        ("2. Python Allergen Guardrail", STATUS_TODO_FG, 
         "Never entrust customer health safety solely to stochastic LLM responses:",
         [("Deterministic Exclusion", "Strict Python filters unconditionally strip items containing user allergens."),
          ("Zero Hallucinations", "Menu item names and prices strictly verified against active database rows."),
          ("100% Verification", "Backed by allergen test suite with 100% pass rate in CI/CD pipeline.")]),
        
        ("3. Two-Stage Human Approval", STATUS_DONE_FG, 
         "Irreversible or sensitive database actions mandate explicit user confirmation:",
         [("Gate 1: Order Placement", "The agent only stages 'pending' orders; user must tap Confirm to charge/place."),
          ("Gate 2: Profile Changes", "Updates write to PendingPreferenceChange; user confirms before DB overwrite."),
          ("Read-Only Agility", "Only read-only recommendations execute immediately without approval gates.")])
    ]

    for i, (title, col, intro, bullets) in enumerate(agent_cards):
        cx = Inches(0.8) + i * (col_w + Inches(0.3))
        add_card(s5, cx, Inches(2.0), col_w, Inches(4.7))

        bar = s5.shapes.add_shape(MSO_SHAPE.RECTANGLE, cx, Inches(2.0), col_w, Inches(0.08))
        bar.fill.solid()
        bar.fill.fore_color.rgb = col
        bar.line.fill.background()

        tb = s5.shapes.add_textbox(cx + Inches(0.25), Inches(2.15), col_w - Inches(0.5), Inches(4.4))
        tf = tb.text_frame
        tf.word_wrap = True

        ph = tf.paragraphs[0]
        ph.text = title
        ph.font.size = Pt(17)
        ph.font.bold = True
        ph.font.color.rgb = col

        pi = tf.add_paragraph()
        pi.text = intro
        pi.font.size = Pt(12)
        pi.font.color.rgb = TEXT_MUTED
        pi.space_before = Pt(6)

        for b_bold, b_text in bullets:
            pb = tf.add_paragraph()
            pb.text = f"• {b_bold}:"
            pb.font.size = Pt(13)
            pb.font.bold = True
            pb.font.color.rgb = TEXT_DARK
            pb.space_before = Pt(8)

            pd = tf.add_paragraph()
            pd.text = f"   {b_text}"
            pd.font.size = Pt(12)
            pd.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 6: DB-BACKED PROMPT VERSIONING
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    apply_slide_base(s6)
    add_header(s6, "Prompt Engineering & MLOps", "Database-Backed Prompt Versioning & Instant Rollback",
               "Eliminating hardcoded templates with an audited, zero-downtime prompt management system.")

    half_w = Inches(5.7)
    
    # Left Card: Storage & Drift Detection
    add_card(s6, Inches(0.8), Inches(2.0), half_w, Inches(4.7))
    bar_l = s6.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(2.0), half_w, Inches(0.08))
    bar_l.fill.solid()
    bar_l.fill.fore_color.rgb = ACCENT_BLUE
    bar_l.line.fill.background()

    tb_l = s6.shapes.add_textbox(Inches(1.05), Inches(2.2), half_w - Inches(0.5), Inches(4.3))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True

    plh = tf_l.paragraphs[0]
    plh.text = "Relational Prompt Store & Drift Detection"
    plh.font.size = Pt(18)
    plh.font.bold = True
    plh.font.color.rgb = ACCENT_BLUE

    points_p1 = [
        ("Semantic Versioning (SemVer)", "Prompts tracked by name and version (e.g. 'drink-assistant-system' @ v1.2.0)."),
        ("SHA-256 Hash Drift Detection", "Automatic 12-char cryptographic hash computed on template to detect silent drift."),
        ("Template Pre-Validation", "Ensures required interpolation fields ({name}, {profile_json}) exist before committing."),
        ("Telemetry Correlation", "Every LLM invocation logs prompt_version & prompt_hash for exact response audits.")
    ]
    for b_title, b_desc in points_p1:
        pb = tf_l.add_paragraph()
        pb.text = f"✔ {b_title}"
        pb.font.size = Pt(14)
        pb.font.bold = True
        pb.font.color.rgb = TEXT_DARK
        pb.space_before = Pt(10)

        pd = tf_l.add_paragraph()
        pd.text = f"   {b_desc}"
        pd.font.size = Pt(12)
        pd.font.color.rgb = TEXT_MUTED

    # Right Card: Admin APIs & Instant Rollback
    add_card(s6, Inches(6.8), Inches(2.0), half_w, Inches(4.7))
    bar_r = s6.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.8), Inches(2.0), half_w, Inches(0.08))
    bar_r.fill.solid()
    bar_r.fill.fore_color.rgb = ACCENT_AMBER
    bar_r.line.fill.background()

    tb_r = s6.shapes.add_textbox(Inches(7.05), Inches(2.2), half_w - Inches(0.5), Inches(4.3))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True

    prh = tf_r.paragraphs[0]
    prh.text = "Admin Endpoints & Zero-Downtime Hot Swap"
    prh.font.size = Pt(18)
    prh.font.bold = True
    prh.font.color.rgb = ACCENT_AMBER

    points_p2 = [
        ("POST /api/prompts", "Publishes a new prompt version and validates syntax without redeploying code."),
        ("GET /api/prompts?name=...", "Inspects complete version history, authors, and previous release notes."),
        ("POST /api/prompts/{id}/activate", "Instant hot-swap: Activates target version and deactivates prior rows atomically."),
        ("Instant Rollback & A/B Testing", "Enables real-time canary deployments, rollbacks, and prompt experiments on live traffic.")
    ]
    for b_title, b_desc in points_p2:
        pb = tf_r.add_paragraph()
        pb.text = f"▶ {b_title}"
        pb.font.size = Pt(14)
        pb.font.bold = True
        pb.font.color.rgb = PRIMARY_COFFEE
        pb.space_before = Pt(10)

        pd = tf_r.add_paragraph()
        pd.text = f"   {b_desc}"
        pd.font.size = Pt(12)
        pd.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 7: MULTI-ENGINE INFERENCE & TELEMETRY
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    apply_slide_base(s7)
    add_header(s7, "Inference Infrastructure", "Multi-Engine Resilience & Granular Observability",
               "Ensuring 24/7 chatbot availability with zero-cost local fallback and full cost auditing.")

    # Left: Multi-Engine
    add_card(s7, Inches(0.8), Inches(2.0), half_w, Inches(4.7))
    bar_m1 = s7.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(2.0), half_w, Inches(0.08))
    bar_m1.fill.solid()
    bar_m1.fill.fore_color.rgb = ACCENT_AMBER
    bar_m1.line.fill.background()

    tb_m1 = s7.shapes.add_textbox(Inches(1.05), Inches(2.2), half_w - Inches(0.5), Inches(4.3))
    tf_m1 = tb_m1.text_frame
    tf_m1.word_wrap = True

    pm1_h = tf_m1.paragraphs[0]
    pm1_h.text = "High-Availability Multi-Engine Fallback"
    pm1_h.font.size = Pt(18)
    pm1_h.font.bold = True
    pm1_h.font.color.rgb = ACCENT_AMBER

    pts_m1 = [
        ("Tier 1: Cloud Foundation Model", "Primary inference via OpenAI gpt-4o-mini or Gemini Flash for top reasoning."),
        ("Intelligent Failure Recovery", "Catches quota exhaustion, network timeouts, or missing API keys automatically."),
        ("Tier 2: Local Zero-Cost Ollama", "Auto-fails over to local Ollama (gemma4:e4b) connected within Docker network."),
        ("Business Continuity Guarantee", "Ensures customers never see a blank crash screen; capable of running 100% offline.")
    ]
    for b_title, b_desc in pts_m1:
        pb = tf_m1.add_paragraph()
        pb.text = f"• {b_title}"
        pb.font.size = Pt(14)
        pb.font.bold = True
        pb.font.color.rgb = TEXT_DARK
        pb.space_before = Pt(10)

        pd = tf_m1.add_paragraph()
        pd.text = f"   {b_desc}"
        pd.font.size = Pt(12)
        pd.font.color.rgb = TEXT_MUTED

    # Right: Telemetry
    add_card(s7, Inches(6.8), Inches(2.0), half_w, Inches(4.7))
    bar_m2 = s7.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.8), Inches(2.0), half_w, Inches(0.08))
    bar_m2.fill.solid()
    bar_m2.fill.fore_color.rgb = ACCENT_INDIGO
    bar_m2.line.fill.background()

    tb_m2 = s7.shapes.add_textbox(Inches(7.05), Inches(2.2), half_w - Inches(0.5), Inches(4.3))
    tf_m2 = tb_m2.text_frame
    tf_m2.word_wrap = True

    pm2_h = tf_m2.paragraphs[0]
    pm2_h.text = "Structured JSON Logs & Langfuse Tracing"
    pm2_h.font.size = Pt(18)
    pm2_h.font.bold = True
    pm2_h.font.color.rgb = ACCENT_INDIGO

    pts_m2 = [
        ("Per-Call Structured Telemetry", "Emits structured JSON with request_id, provider, model, latency_ms, success/error."),
        ("Token & Cost Accounting", "Calculates exact input_tokens, output_tokens, and estimated_cost_usd to 8 decimals."),
        ("Database Row Persistence", "Usage metrics persisted directly into ChatMessage database columns for auditing."),
        ("Langfuse Tracing Integration", "Full end-to-end tracing showing agent thought process and tool execution times.")
    ]
    for b_title, b_desc in pts_m2:
        pb = tf_m2.add_paragraph()
        pb.text = f"• {b_title}"
        pb.font.size = Pt(14)
        pb.font.bold = True
        pb.font.color.rgb = TEXT_DARK
        pb.space_before = Pt(10)

        pd = tf_m2.add_paragraph()
        pd.text = f"   {b_desc}"
        pd.font.size = Pt(12)
        pd.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 8: MLOPS HUB CAPABILITIES
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    apply_slide_base(s8)
    add_header(s8, "MLOps Hub & Fine-Tuning", "Advanced MLOps Capabilities: Model Registry & Adapters",
               "Proactive asset ownership through localized small language models and retrieval adapters.")

    hubs = [
        ("Model Registry & Hub", ACCENT_AMBER, [
            ("Centralized Tracking", "Logs model checkpoints, hyperparameters (LR, batch, epochs), and metadata."),
            ("Loss History Graphs", "Maintains epoch-by-epoch loss reduction curves for transparent model validation."),
            ("Dataset Lineage", "Binds model weights to cryptographic SHA-256 hashes of the training dataset."),
            ("Active Hot-Swap", "Switch between candidate fine-tuned checkpoints directly via API.")
        ]),
        ("Gemma 2B LoRA Fine-Tuning", ACCENT_INDIGO, [
            ("Base Foundation", "google/gemma-2-2b-it fine-tuned for Vietnamese beverage conversational domain."),
            ("LoRA Hyperparameters", "r=8, lora_alpha=16, target_modules=['q_proj', 'v_proj'] with AdamW."),
            ("Domain Adaptability", "Trained on conversational drink ordering and preference extraction datasets."),
            ("Local Hardware Execution", "Runs cleanly on standard desktop GPUs (RTX 3060) or multi-core CPU.")
        ]),
        ("Contrastive RAG Adapter", STATUS_DONE_FG, [
            ("Semantic Enhancement", "Trained on top of all-MiniLM-L6-v2 (384-dimensional vector space)."),
            ("Adapter Architecture", "Linear projection + LayerNorm + Residual connection with Contrastive Loss."),
            ("F&B Slang Handling", "Accurately maps Vietnamese beverage slang ('bạc xỉu', 'trà mãng cầu')."),
            ("Empirical Validation", "Yields a +28.5% measured accuracy improvement in menu item retrieval.")
        ])
    ]

    for i, (title, col, items) in enumerate(hubs):
        cx = Inches(0.8) + i * (col_w + Inches(0.3))
        add_card(s8, cx, Inches(2.0), col_w, Inches(4.7))

        bar = s8.shapes.add_shape(MSO_SHAPE.RECTANGLE, cx, Inches(2.0), col_w, Inches(0.08))
        bar.fill.solid()
        bar.fill.fore_color.rgb = col
        bar.line.fill.background()

        tb = s8.shapes.add_textbox(cx + Inches(0.25), Inches(2.15), col_w - Inches(0.5), Inches(4.4))
        tf = tb.text_frame
        tf.word_wrap = True

        ph = tf.paragraphs[0]
        ph.text = title
        ph.font.size = Pt(17)
        ph.font.bold = True
        ph.font.color.rgb = col

        for b_title, b_desc in items:
            pb = tf.add_paragraph()
            pb.text = f"• {b_title}:"
            pb.font.size = Pt(13)
            pb.font.bold = True
            pb.font.color.rgb = TEXT_DARK
            pb.space_before = Pt(8)

            pd = tf.add_paragraph()
            pd.text = f"   {b_desc}"
            pd.font.size = Pt(12)
            pd.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 9: SCORECARD TABLE (HIGH IMPACT)
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    apply_slide_base(s9)
    add_header(s9, "Status Scorecard", "Comprehensive Workshop Scorecard vs Requirements",
               "Direct, rigorous evaluation against workshop criteria and mentor feedback.")

    rows = 9
    cols = 3
    left = Inches(0.8)
    top = Inches(1.9)
    width = Inches(11.733)
    height = Inches(4.65)

    table_shape = s9.shapes.add_table(rows, cols, left, top, width, height)
    table = table_shape.table
    table.columns[0].width = Inches(3.8)
    table.columns[1].width = Inches(1.8)
    table.columns[2].width = Inches(6.133)

    score_rows = [
        ("Workshop Requirement", "Status", "Technical Proof & Verification"),
        ("1. Collect name, phone, address → DB", "DONE", "User entity with phone regex validation, registration & profile endpoints."),
        ("2. Recommend Detox, Coffee, Protein drinks", "DONE", "Catalog seeded with Protein shakes (3 items), Detox, Coffees, Teas. Tested."),
        ("3. Log chat history to track accuracy", "PARTIAL", "Messages, model name, tokens, and cost logged. Thumbs up/down pending."),
        ("4. App → VPC Endpoint → AWS Bedrock", "NOT STARTED", "Biggest gap: Currently direct OpenAI API and local Ollama within Docker."),
        ("5. Dockerize Backend & Frontend", "DONE", "Production Dockerfiles + compose file (Postgres, Backend, Frontend, Nginx)."),
        ("6. Track model & token usage per message", "DONE", "Dedicated model_name, input_tokens, output_tokens, cost on ChatMessage."),
        ("7. Prompt version control & rollback", "DONE", "DB-backed PromptVersion store, SHA-256 hash, Admin activate/rollback APIs."),
        ("8. AI agent with human approval gate", "DONE", "2-stage approval: Order confirmation and profile preference confirmation.")
    ]

    for r_idx, (req, status, proof) in enumerate(score_rows):
        # Cell 0
        c0 = table.cell(r_idx, 0)
        c0.text = req
        p0 = c0.text_frame.paragraphs[0]
        p0.font.size = Pt(13)

        # Cell 1
        c1 = table.cell(r_idx, 1)
        c1.text = status
        p1 = c1.text_frame.paragraphs[0]
        p1.alignment = PP_ALIGN.CENTER
        p1.font.size = Pt(12)
        p1.font.bold = True

        # Cell 2
        c2 = table.cell(r_idx, 2)
        c2.text = proof
        p2 = c2.text_frame.paragraphs[0]
        p2.font.size = Pt(12)

        if r_idx == 0:
            c0.fill.solid(); c0.fill.fore_color.rgb = PRIMARY_COFFEE
            c1.fill.solid(); c1.fill.fore_color.rgb = PRIMARY_COFFEE
            c2.fill.solid(); c2.fill.fore_color.rgb = PRIMARY_COFFEE
            p0.font.bold = True; p0.font.color.rgb = RGBColor(255, 255, 255)
            p1.font.bold = True; p1.font.color.rgb = RGBColor(255, 255, 255)
            p2.font.bold = True; p2.font.color.rgb = RGBColor(255, 255, 255)
        else:
            row_bg = RGBColor(255, 255, 255) if r_idx % 2 == 1 else RGBColor(241, 245, 249)
            c0.fill.solid(); c0.fill.fore_color.rgb = row_bg
            c1.fill.solid(); c1.fill.fore_color.rgb = row_bg
            c2.fill.solid(); c2.fill.fore_color.rgb = row_bg

            p0.font.bold = True; p0.font.color.rgb = TEXT_DARK
            p2.font.color.rgb = TEXT_MUTED

            if status == "DONE":
                c1.fill.fore_color.rgb = STATUS_DONE_BG
                p1.font.color.rgb = STATUS_DONE_FG
            elif status == "PARTIAL":
                c1.fill.fore_color.rgb = STATUS_PARTIAL_BG
                p1.font.color.rgb = STATUS_PARTIAL_FG
            else:
                c0.fill.fore_color.rgb = STATUS_TODO_BG
                c1.fill.fore_color.rgb = STATUS_TODO_BG
                p0.font.color.rgb = STATUS_TODO_FG
                p1.font.color.rgb = STATUS_TODO_FG

    # Bottom summary chip
    add_card(s9, Inches(0.8), Inches(6.6), Inches(11.733), Inches(0.55), RGBColor(16, 185, 129), STATUS_DONE_BG)
    tb_sc = s9.shapes.add_textbox(Inches(1.0), Inches(6.62), Inches(11.3), Inches(0.5))
    p_sc = tb_sc.text_frame.paragraphs[0]
    p_sc.text = "🎯 Overall Completion Rate: 7 out of 8 Core Requirements Completed (87.5%) • Priority Focus: AWS Bedrock VPC Endpoint."
    p_sc.font.size = Pt(12)
    p_sc.font.bold = True
    p_sc.font.color.rgb = STATUS_DONE_FG

    # =========================================================================
    # SLIDE 10: ROADMAP & Q&A
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    apply_slide_base(s10)
    add_header(s10, "Strategic Roadmap", "Looking Forward: Priorities & Open Q&A Discussion",
               "Closing the remaining architectural gaps and transitioning to full enterprise production.")

    roadmaps = [
        ("PRIORITY 1: CRITICAL GAP", "AWS Bedrock via VPC Endpoint", STATUS_TODO_FG, [
            "Implement Boto3 AWS Bedrock client in llm.py for Claude 3 Haiku / Llama 3.",
            "Configure VPC Endpoint routing to satisfy enterprise private network policies.",
            "Eliminate external internet egress for cloud inference to meet mentor ask #1."
        ]),
        ("PRIORITY 2: ACCURACY FEEDBACK", "RLHF User Feedback Loop", ACCENT_AMBER, [
            "Add Thumbs Up / Down ratings on frontend messages to capture qualitative ground truth.",
            "Synchronize feedback scores to Langfuse to automate model evaluation datasets.",
            "Complete requirement #3 by actively tracking response quality over time."
        ]),
        ("PRIORITY 3: AUTOMATION", "Continuous Auto-Retraining", ACCENT_INDIGO, [
            "Trigger automatic fine-tuning when newly verified customer conversations reach thresholds.",
            "Execute regression test suites (73 tests) before promoting candidate checkpoints.",
            "Automate canary deployments for zero-downtime model upgrades."
        ])
    ]

    for i, (tag, title, col, bullets) in enumerate(roadmaps):
        cx = Inches(0.8) + i * (col_w + Inches(0.3))
        add_card(s10, cx, Inches(2.0), col_w, Inches(3.5))

        bar = s10.shapes.add_shape(MSO_SHAPE.RECTANGLE, cx, Inches(2.0), col_w, Inches(0.08))
        bar.fill.solid()
        bar.fill.fore_color.rgb = col
        bar.line.fill.background()

        tb = s10.shapes.add_textbox(cx + Inches(0.2), Inches(2.15), col_w - Inches(0.4), Inches(3.2))
        tf = tb.text_frame
        tf.word_wrap = True

        ptag = tf.paragraphs[0]
        ptag.text = tag
        ptag.font.size = Pt(11)
        ptag.font.bold = True
        ptag.font.color.rgb = col

        ptt = tf.add_paragraph()
        ptt.text = title
        ptt.font.size = Pt(15)
        ptt.font.bold = True
        ptt.font.color.rgb = TEXT_DARK
        ptt.space_before = Pt(4)

        for b in bullets:
            pb = tf.add_paragraph()
            pb.text = f"• {b}"
            pb.font.size = Pt(12)
            pb.font.color.rgb = TEXT_BODY
            pb.space_before = Pt(8)

    # Q&A Banner
    add_card(s10, Inches(2.0), Inches(5.65), Inches(9.333), Inches(1.35), BORDER_AMBER, RGBColor(254, 243, 199))
    tb_qa = s10.shapes.add_textbox(Inches(2.2), Inches(5.75), Inches(8.9), Inches(1.15))
    tf_qa = tb_qa.text_frame
    tf_qa.word_wrap = True

    pqa1 = tf_qa.paragraphs[0]
    pqa1.text = "☕ THANK YOU FOR YOUR TIME & ATTENTION!"
    pqa1.alignment = PP_ALIGN.CENTER
    pqa1.font.size = Pt(20)
    pqa1.font.bold = True
    pqa1.font.color.rgb = PRIMARY_COFFEE

    pqa2 = tf_qa.add_paragraph()
    pqa2.text = "DrinkBot MLOps Backend Team — Open for Technical Q&A and Architectural Discussion"
    pqa2.alignment = PP_ALIGN.CENTER
    pqa2.font.size = Pt(13)
    pqa2.font.color.rgb = TEXT_MUTED
    pqa2.space_before = Pt(4)

    # Save to both target locations
    path1 = "slide-info-backend/DrinkBot_MLOps_Presentation_EN.pptx"
    path2 = "DrinkBot_MLOps_Presentation_EN.pptx"
    prs.save(path1)
    prs.save(path2)
    print(f"Deck successfully generated and saved to:\n- {path1}\n- {path2}")

    # Also attempt to update the original filename if unlocked
    try:
        prs.save("slide-info-backend/DrinkBot_MLOps_Backend_Presentation.pptx")
        prs.save("DrinkBot_MLOps_Backend_Presentation.pptx")
    except PermissionError:
        print("Note: Original filename is currently open in PowerPoint; saved to _EN.pptx successfully!")

if __name__ == "__main__":
    build_deck()
