"""Generate a professional widescreen (.pptx) presentation for DrinkBot MLOps."""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_presentation():
    prs = Presentation()
    # Set 16:9 Widescreen dimensions
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]  # Blank layout

    # Colors
    BG_DARK = RGBColor(12, 19, 34)        # #0c1322
    CARD_BG = RGBColor(22, 32, 54)        # #162036
    CARD_BORDER = RGBColor(40, 56, 92)    # #28385c
    AMBER = RGBColor(245, 158, 11)        # #f59e0b
    ORANGE = RGBColor(234, 88, 12)        # #ea580c
    SKY = RGBColor(56, 189, 248)          # #38bdf8
    EMERALD = RGBColor(16, 185, 129)      # #10b981
    ROSE = RGBColor(244, 63, 94)          # #f43f5e
    TEXT_WHITE = RGBColor(248, 250, 252)  # #f8fafc
    TEXT_MUTED = RGBColor(148, 163, 184)  # #94a3b8
    TEXT_DIM = RGBColor(100, 116, 139)    # #64748b

    def add_slide_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_DARK
        bg.line.fill.background()
        return bg

    def add_header(slide, tag_text, title_text, subtitle_text=""):
        # Tag / Category
        tag_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.45), Inches(11.7), Inches(0.35))
        tf_tag = tag_box.text_frame
        tf_tag.word_wrap = True
        p_tag = tf_tag.paragraphs[0]
        p_tag.text = tag_text.upper()
        p_tag.font.size = Pt(10)
        p_tag.font.bold = True
        p_tag.font.color.rgb = AMBER

        # Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.75), Inches(11.7), Inches(0.6))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_WHITE

        # Subtitle
        if subtitle_text:
            sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(1.35), Inches(11.7), Inches(0.35))
            tf_sub = sub_box.text_frame
            tf_sub.word_wrap = True
            p_sub = tf_sub.paragraphs[0]
            p_sub.text = subtitle_text
            p_sub.font.size = Pt(12)
            p_sub.font.color.rgb = TEXT_MUTED

    def add_card(slide, left, top, width, height, bg_color=CARD_BG, border_color=CARD_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1.2)
        return card

    # =========================================================================
    # SLIDE 1: COVER SLIDE
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    add_slide_background(s1)

    # Accent decorative banner
    banner = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.2), Inches(3.2), Inches(0.4))
    banner.fill.solid()
    banner.fill.fore_color.rgb = CARD_BG
    banner.line.color.rgb = AMBER
    banner.line.width = Pt(1)
    tf_b = banner.text_frame
    p_b = tf_b.paragraphs[0]
    p_b.text = "TMA SOLUTIONS • F&B AI WORKSHOP"
    p_b.alignment = PP_ALIGN.CENTER
    p_b.font.size = Pt(10)
    p_b.font.bold = True
    p_b.font.color.rgb = AMBER

    # Title box
    t_box = s1.shapes.add_textbox(Inches(0.8), Inches(1.8), Inches(11.7), Inches(2.2))
    tf1 = t_box.text_frame
    tf1.word_wrap = True
    
    p1 = tf1.paragraphs[0]
    p1.text = "☕ DrinkBot MLOps"
    p1.font.size = Pt(44)
    p1.font.bold = True
    p1.font.color.rgb = AMBER
    
    p2 = tf1.add_paragraph()
    p2.text = "Backend Architecture & Engineering Status Review"
    p2.font.size = Pt(28)
    p2.font.bold = True
    p2.font.color.rgb = TEXT_WHITE
    p2.space_before = Pt(8)

    p3 = tf1.add_paragraph()
    p3.text = "Hệ thống Chatbot Khuyến nghị Đồ uống Thông minh với Nền tảng MLOps Toàn diện:\nAutonomous Agent, Human-in-the-Loop, DB Prompt Versioning & Multi-Engine Fallback"
    p3.font.size = Pt(14)
    p3.font.color.rgb = TEXT_MUTED
    p3.space_before = Pt(12)

    # 4 Quick highlight stat cards
    highlights = [
        ("Core Stack", "FastAPI + Async SQLAlchemy", SKY),
        ("Database", "PostgreSQL 16 + Alembic", AMBER),
        ("Inference", "LangChain + Ollama/OpenAI", ORANGE),
        ("Test Suite", "73 / 73 Tests Passed (100%)", EMERALD)
    ]
    card_w = Inches(2.7)
    card_h = Inches(1.4)
    gap = Inches(0.3)
    start_x = Inches(0.8)
    y_pos = Inches(4.5)

    for i, (label, val, col) in enumerate(highlights):
        cx = start_x + i * (card_w + gap)
        add_card(s1, cx, y_pos, card_w, card_h)
        tb = s1.shapes.add_textbox(cx + Inches(0.15), y_pos + Inches(0.15), card_w - Inches(0.3), card_h - Inches(0.3))
        tf = tb.text_frame
        tf.word_wrap = True
        
        pl = tf.paragraphs[0]
        pl.text = label.upper()
        pl.font.size = Pt(10)
        pl.font.bold = True
        pl.font.color.rgb = col
        
        pv = tf.add_paragraph()
        pv.text = val
        pv.font.size = Pt(13)
        pv.font.bold = True
        pv.font.color.rgb = TEXT_WHITE
        pv.space_before = Pt(6)

    # Footer note
    ft_box = s1.shapes.add_textbox(Inches(0.8), Inches(6.5), Inches(11.7), Inches(0.5))
    p_ft = ft_box.text_frame.paragraphs[0]
    p_ft.text = "Báo cáo Kỹ thuật Backend • Nhánh main (Merged origin/backend) • Ngày: 09/2026"
    p_ft.font.size = Pt(11)
    p_ft.font.color.rgb = TEXT_DIM

    # =========================================================================
    # SLIDE 2: SECTION GOAL & STRATEGY
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    add_slide_background(s2)
    add_header(s2, "Section Goal & Strategy", "Mục Tiêu & Tinh Thần Báo Cáo Backend", 
               "Đối chiếu trực diện kết quả thực tế với yêu cầu của Workshop & Mentor.")

    cards_data = [
        ("Nghiệp Vụ F&B Cốt Lõi", 
         ["Thu thập 3 thực thể khách hàng: Họ tên, Số điện thoại, Địa chỉ giao hàng.",
          "Tư vấn đồ uống cá nhân hóa theo 5 nhóm: Cà phê, Trà detox, Protein shakes, Nước ép.",
          "Lưu trữ chuẩn xác vào PostgreSQL với quan hệ dữ liệu 1-1 và 1-N."],
         EMERALD),
        ("Tiêu Chuẩn Hóa MLOps", 
         ["Quản trị vòng đời Prompt Versioning & Rollback lưu trữ trực tiếp trong DB.",
          "Ghi nhận chi tiết lịch sử trò chuyện: Token, Latency, Cost cho từng tin nhắn.",
          "Tích hợp Model Registry, Fine-Tuning SLM Gemma 2B và Contrastive RAG Adapter."],
         SKY),
        ("Đánh Giá Khách Quan", 
         ["Minh bạch tuyệt đối: Báo cáo rõ các phần đã hoàn thiện (Done) và đang hoàn thiện.",
          "Chỉ rõ khoảng trống công nghệ lớn nhất hiện tại: Chưa tích hợp AWS Bedrock qua VPC Endpoint.",
          "Mọi khẳng định 'Done' đều được chứng minh qua mã nguồn và 73 test cases."],
         ROSE)
    ]

    col_w = Inches(3.7)
    for i, (head, points, col) in enumerate(cards_data):
        cx = Inches(0.8) + i * (col_w + Inches(0.3))
        add_card(s2, cx, Inches(1.85), col_w, Inches(4.5))
        
        # Color bar top
        c_bar = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, cx, Inches(1.85), col_w, Inches(0.08))
        c_bar.fill.solid()
        c_bar.fill.fore_color.rgb = col
        c_bar.line.fill.background()

        tb = s2.shapes.add_textbox(cx + Inches(0.2), Inches(2.05), col_w - Inches(0.4), Inches(4.1))
        tf = tb.text_frame
        tf.word_wrap = True
        
        ph = tf.paragraphs[0]
        ph.text = head
        ph.font.size = Pt(16)
        ph.font.bold = True
        ph.font.color.rgb = col
        
        for pt in points:
            pp = tf.add_paragraph()
            pp.text = f"• {pt}"
            pp.font.size = Pt(12)
            pp.font.color.rgb = TEXT_WHITE
            pp.space_before = Pt(12)

    # =========================================================================
    # SLIDE 3: TECH STACK ARCHITECTURE
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    add_slide_background(s3)
    add_header(s3, "System Architecture", "Kiến Trúc Kỹ Thuật Backend Toàn Diện", 
               "Thiết kế bất đồng bộ (Async), chịu tải cao và hỗ trợ quan sát (Observability) tối ưu.")

    stack_cols = [
        ("API LAYER", "FastAPI + AsyncIO", [
            "Uvicorn ASGI Server non-blocking",
            "Pydantic v2 schemas validation",
            "JWT Auth đơn giản hóa theo SĐT",
            "6 Routers: auth, chat, menu, prompts, telemetry, users"
        ], EMERALD),
        ("DATA & ORM", "Postgres 16 + AsyncPG", [
            "SQLAlchemy 2.0 Async Session",
            "Alembic Migrations (0001 → 0003)",
            "Auto-seed thực đơn & nhóm đồ uống",
            "PromptVersion & Audit log tables"
        ], SKY),
        ("AGENT & LLM", "LangChain Tool Agent", [
            "ReAct Loop (Max 4 iterations)",
            "3 Tools: Profile, Recommend, Order",
            "Python Allergen Guardrails",
            "Ollama Local zero-cost fallback"
        ], AMBER),
        ("DEVOPS & QA", "Docker & Pytest", [
            "Docker Compose (5 containers)",
            "Nginx API Gateway proxy port 80",
            "73/73 tests pass trong 2.5 giây",
            "Langfuse Telemetry Tracing"
        ], ORANGE)
    ]

    sw = Inches(2.7)
    for i, (tag, title, items, col) in enumerate(stack_cols):
        cx = Inches(0.8) + i * (sw + Inches(0.3))
        add_card(s3, cx, Inches(1.85), sw, Inches(4.3))
        
        c_bar = s3.shapes.add_shape(MSO_SHAPE.RECTANGLE, cx, Inches(1.85), sw, Inches(0.06))
        c_bar.fill.solid()
        c_bar.fill.fore_color.rgb = col
        c_bar.line.fill.background()

        tb = s3.shapes.add_textbox(cx + Inches(0.15), Inches(2.0), sw - Inches(0.3), Inches(4.0))
        tf = tb.text_frame
        tf.word_wrap = True

        ptag = tf.paragraphs[0]
        ptag.text = tag
        ptag.font.size = Pt(10)
        ptag.font.bold = True
        ptag.font.color.rgb = col

        ptt = tf.add_paragraph()
        ptt.text = title
        ptt.font.size = Pt(14)
        ptt.font.bold = True
        ptt.font.color.rgb = TEXT_WHITE
        ptt.space_before = Pt(4)

        for it in items:
            pi = tf.add_paragraph()
            pi.text = f"• {it}"
            pi.font.size = Pt(11)
            pi.font.color.rgb = TEXT_MUTED
            pi.space_before = Pt(8)

    # Bottom summary banner
    add_card(s3, Inches(0.8), Inches(6.3), Inches(11.7), Inches(0.7), CARD_BG, AMBER)
    tb_bot = s3.shapes.add_textbox(Inches(1.0), Inches(6.35), Inches(11.3), Inches(0.6))
    p_bot = tb_bot.text_frame.paragraphs[0]
    p_bot.text = "⚡ Hiệu năng: Phản hồi P95 < 850ms | Độ bao phủ kiểm thử: 11 file test suite (Auth, Chat, Menu, Prompts, RAG, Evals) đạt tỷ lệ Pass 100%."
    p_bot.font.size = Pt(11)
    p_bot.font.bold = True
    p_bot.font.color.rgb = TEXT_WHITE

    # =========================================================================
    # SLIDE 4: DOMAIN MODEL & ENTITY COLLECTION
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    add_slide_background(s4)
    add_header(s4, "Data Architecture", "Mô Hình Dữ Liệu Nghiệp Vụ & Thu Thập Thực Thể", 
               "Lưu trữ chuẩn xác thông tin khách hàng, cấu trúc menu F&B và nhật ký vận hành MLOps.")

    dm_cards = [
        ("User & Preferences (Khách hàng)", [
            ("User Entity", "phone (Unique), name, address (giao hàng)"),
            ("Tastes Profile", "ngọt, đắng, chua, béo (mảng JSON)"),
            ("Drink Types", "cà phê, trà trái cây, sinh tố, detox, protein"),
            ("Health & Safety", "temperature, caffeine, allergies (dị ứng)"),
            ("Dietary", "dietary_restrictions (ăn chay, keto, v.v.)")
        ], EMERALD),
        ("Menu & Ordering (F&B)", [
            ("MenuItem", "name, category, price, description"),
            ("Allergen List", "Danh sách dị nguyên (sữa, đậu phộng, gluten)"),
            ("Menu Diversity", "5 nhóm: Coffee, Tea, Protein, Detox, Juices"),
            ("Order Entity", "user_id, total_amount, status"),
            ("Order Status", "pending (chờ duyệt) → placed / cancelled")
        ], SKY),
        ("MLOps & Governance (Vận hành)", [
            ("ChatMessage", "role, content, user_id, created_at"),
            ("Cost & Latency", "input_tokens, output_tokens, estimated_cost_usd"),
            ("Model Tracking", "model_name lưu vết chính xác trên từng message"),
            ("PromptVersion", "name, version, template, is_active, prompt_hash"),
            ("PendingChanges", "Lưu thay đổi profile đang chờ khách hàng duyệt")
        ], AMBER)
    ]

    w_dm = Inches(3.7)
    for i, (title, fields, col) in enumerate(dm_cards):
        cx = Inches(0.8) + i * (w_dm + Inches(0.3))
        add_card(s4, cx, Inches(1.85), w_dm, Inches(5.1))
        
        tb = s4.shapes.add_textbox(cx + Inches(0.2), Inches(2.0), w_dm - Inches(0.4), Inches(4.8))
        tf = tb.text_frame
        tf.word_wrap = True

        ph = tf.paragraphs[0]
        ph.text = title
        ph.font.size = Pt(15)
        ph.font.bold = True
        ph.font.color.rgb = col

        for f_name, f_desc in fields:
            pf = tf.add_paragraph()
            pf.text = f"• {f_name}:"
            pf.font.size = Pt(12)
            pf.font.bold = True
            pf.font.color.rgb = TEXT_WHITE
            pf.space_before = Pt(8)

            pd = tf.add_paragraph()
            pd.text = f"   {f_desc}"
            pd.font.size = Pt(11)
            pd.font.color.rgb = TEXT_MUTED

    # =========================================================================
    # SLIDE 5: CHAT AGENT & HUMAN-IN-THE-LOOP
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    add_slide_background(s5)
    add_header(s5, "Autonomous Intelligence", "Chat Agent & Cơ Chế Human-in-the-Loop", 
               "Sự kết hợp giữa trí tuệ nhân tạo linh hoạt và hàng rào an toàn tuyệt đối từ mã Python.")

    agent_pillars = [
        ("1. Tool Calling ReAct Loop", 
         "Mô hình lặp tối đa 4 bước (Max 4 iterations) tự động chọn công cụ thích hợp:",
         ["recommend_drink: Tra cứu menu và gợi ý món",
          "update_profile: Đề xuất cập nhật sở thích",
          "order: Tạo bản xem trước (preview) đơn hàng"],
         AMBER),
        ("2. Python Allergen Guardrail", 
         "Không bao giờ tin tưởng hoàn toàn vào LLM đối với an toàn sức khỏe:",
         ["Hàm Python tự động loại trừ mọi món chứa dị nguyên của khách hàng",
          "Xác thực giá tiền và tên món 100% khớp cơ sở dữ liệu menu",
          "Bộ test allergen an toàn vượt qua 100% kiểm thử"],
         ROSE),
        ("3. Two-Stage Approval Gate", 
         "Cơ chế con người can thiệp (Human-in-the-loop) tại các điểm rủi ro:",
         ["Cổng 1 (Order): Đơn hàng luôn ở trạng thái pending; chỉ đặt khi khách bấm Xác nhận",
          "Cổng 2 (Profile): Cập nhật sở thích qua PendingPreferenceChange cần user duyệt",
          "Chỉ có thao tác Đọc (tra cứu menu) là áp dụng ngay"],
         EMERALD)
    ]

    for i, (title, intro, bullets, col) in enumerate(agent_pillars):
        cx = Inches(0.8) + i * (w_dm + Inches(0.3))
        add_card(s5, cx, Inches(1.85), w_dm, Inches(4.5))

        tb = s5.shapes.add_textbox(cx + Inches(0.2), Inches(2.0), w_dm - Inches(0.4), Inches(4.2))
        tf = tb.text_frame
        tf.word_wrap = True

        ph = tf.paragraphs[0]
        ph.text = title
        ph.font.size = Pt(15)
        ph.font.bold = True
        ph.font.color.rgb = col

        pi = tf.add_paragraph()
        pi.text = intro
        pi.font.size = Pt(11)
        pi.font.color.rgb = TEXT_MUTED
        pi.space_before = Pt(8)

        for b in bullets:
            pb = tf.add_paragraph()
            pb.text = f"• {b}"
            pb.font.size = Pt(11)
            pb.font.color.rgb = TEXT_WHITE
            pb.space_before = Pt(8)

    # Bottom summary
    add_card(s5, Inches(0.8), Inches(6.45), Inches(11.7), Inches(0.6), CARD_BG, EMERALD)
    tb_s5 = s5.shapes.add_textbox(Inches(1.0), Inches(6.5), Inches(11.3), Inches(0.5))
    p_s5 = tb_s5.text_frame.paragraphs[0]
    p_s5.text = "🛡️ Nguyên lý thiết kế: Tách biệt rõ ràng giữa AI đề xuất (LLM) và Con người quyết định (Human Approval)."
    p_s5.font.size = Pt(11)
    p_s5.font.bold = True
    p_s5.font.color.rgb = TEXT_WHITE

    # =========================================================================
    # SLIDE 6: PROMPT VERSIONING & ROLLBACK
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    add_slide_background(s6)
    add_header(s6, "MLOps Governance", "Quản Lý Prompt Versioning & Rollback Động", 
               "Xóa bỏ hoàn toàn tình trạng Prompt Hardcode bằng hệ thống quản trị phiên bản trong Database.")

    # Left Box: DB Store
    add_card(s6, Inches(0.8), Inches(1.85), Inches(5.7), Inches(4.4))
    tb_l = s6.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.3), Inches(4.1))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True

    p_lh = tf_l.paragraphs[0]
    p_lh.text = "DB-Backed Prompt Store"
    p_lh.font.size = Pt(18)
    p_lh.font.bold = True
    p_lh.font.color.rgb = SKY

    pts_l = [
        "Lưu trữ trong bảng PromptVersion với mã băm SHA-256 (prompt_hash) phát hiện trôi dạt (Drift Detection).",
        "Hỗ trợ phân phiên bản ngữ nghĩa (SemVer: 1.0.0, 1.1.0, 1.2.0...).",
        "Tự động thẩm định (Validate) các biến nội suy {name}, {profile_json} trước khi ghi vào DB.",
        "Mỗi cuộc trò chuyện ghi log kèm prompt_version & prompt_hash để truy vết chính xác chất lượng câu trả lời."
    ]
    for p in pts_l:
        pp = tf_l.add_paragraph()
        pp.text = f"• {p}"
        pp.font.size = Pt(12)
        pp.font.color.rgb = TEXT_WHITE
        pp.space_before = Pt(10)

    # Right Box: Admin APIs & Instant Rollback
    add_card(s6, Inches(6.8), Inches(1.85), Inches(5.7), Inches(4.4))
    tb_r = s6.shapes.add_textbox(Inches(7.0), Inches(2.0), Inches(5.3), Inches(4.1))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True

    p_rh = tf_r.paragraphs[0]
    p_rh.text = "Admin API & Instant Rollback"
    p_rh.font.size = Pt(18)
    p_rh.font.bold = True
    p_rh.font.color.rgb = AMBER

    apis = [
        ("POST /api/prompts", "Tạo phiên bản prompt mới (tự tính hash SHA-256)."),
        ("GET /api/prompts?name=...", "Xem lịch sử thay đổi và so sánh các phiên bản."),
        ("POST /api/prompts/{id}/activate", "Kích hoạt phiên bản ngay lập tức trên RUNTIME!"),
        ("Hot-Fix & A/B Testing", "Rollback về bản trước hoặc thử nghiệm prompt mới mà KHÔNG cần redeploy code.")
    ]
    for method, desc in apis:
        pm = tf_r.add_paragraph()
        pm.text = f"▶ {method}:"
        pm.font.size = Pt(12)
        pm.font.bold = True
        pm.font.color.rgb = AMBER
        pm.space_before = Pt(8)

        pd = tf_r.add_paragraph()
        pd.text = f"   {desc}"
        pd.font.size = Pt(11)
        pd.font.color.rgb = TEXT_MUTED

    add_card(s6, Inches(0.8), Inches(6.35), Inches(11.7), Inches(0.65), CARD_BG, SKY)
    tb_s6 = s6.shapes.add_textbox(Inches(1.0), Inches(6.4), Inches(11.3), Inches(0.55))
    p_s6 = tb_s6.text_frame.paragraphs[0]
    p_s6.text = "✅ Đạt chuẩn MLOps: Đã chuyển đổi hoàn toàn từ Prompt Hardcoding sang DB-backed Prompt Governance."
    p_s6.font.size = Pt(11)
    p_s6.font.bold = True
    p_s6.font.color.rgb = TEXT_WHITE

    # =========================================================================
    # SLIDE 7: MULTI-ENGINE INFERENCE & OBSERVABILITY
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    add_slide_background(s7)
    add_header(s7, "Observability & Resilience", "Hạ Tầng Suy Luận Đa Tầng & Đo Lường Telemetry", 
               "Đảm bảo chatbot phản hồi 24/7 với chi phí 0đ và khả năng truy vết (Tracing) chi tiết.")

    # Left: Multi-Engine
    add_card(s7, Inches(0.8), Inches(1.85), Inches(5.7), Inches(4.4))
    tb_m1 = s7.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.3), Inches(4.1))
    tf_m1 = tb_m1.text_frame
    tf_m1.word_wrap = True

    p_m1 = tf_m1.paragraphs[0]
    p_m1.text = "Multi-Engine Auto-Fallback"
    p_m1.font.size = Pt(18)
    p_m1.font.bold = True
    p_m1.font.color.rgb = AMBER

    engs = [
        ("1. Primary Engine (Cloud LLM)", "OpenAI gpt-4o-mini hoặc Gemini Flash cho năng lực lý luận mạnh mẽ nhất."),
        ("2. Intelligent Auto-Fallback", "Nếu Cloud gặp lỗi mạng, hết quota hoặc thiếu API Key:"),
        ("3. Local Zero-Cost Engine", "Tự động chuyển tiếp mượt mà sang Ollama Local (gemma4:e4b) chạy nội bộ trong mạng Docker."),
        ("Lợi ích doanh nghiệp", "Khách hàng không bao giờ gặp lỗi trắng trang; hệ thống có thể chạy hoàn toàn Offline.")
    ]
    for title, desc in engs:
        pt = tf_m1.add_paragraph()
        pt.text = f"• {title}:"
        pt.font.size = Pt(12)
        pt.font.bold = True
        pt.font.color.rgb = TEXT_WHITE
        pt.space_before = Pt(8)

        pd = tf_m1.add_paragraph()
        pd.text = f"   {desc}"
        pd.font.size = Pt(11)
        pd.font.color.rgb = TEXT_MUTED

    # Right: Telemetry
    add_card(s7, Inches(6.8), Inches(1.85), Inches(5.7), Inches(4.4))
    tb_m2 = s7.shapes.add_textbox(Inches(7.0), Inches(2.0), Inches(5.3), Inches(4.1))
    tf_m2 = tb_m2.text_frame
    tf_m2.word_wrap = True

    p_m2 = tf_m2.paragraphs[0]
    p_m2.text = "Structured Telemetry & Langfuse"
    p_m2.font.size = Pt(18)
    p_m2.font.bold = True
    p_m2.font.color.rgb = SKY

    tels = [
        ("Mỗi request tạo một JSON structured log gồm:", [
            "request_id, provider, model, latency_ms",
            "prompt_name, prompt_version, prompt_hash",
            "input_tokens, output_tokens, total_tokens",
            "estimated_cost_usd (tính đến 8 chữ số thập phân)"
        ]),
        ("Tích hợp Langfuse Dashboard:", [
            "Truy vết hội thoại (Tracing end-to-end)",
            "Đo lường chi phí thời gian thực theo từng người dùng"
        ])
    ]
    for heading, subitems in tels:
        ph = tf_m2.add_paragraph()
        ph.text = f"▶ {heading}"
        ph.font.size = Pt(12)
        ph.font.bold = True
        ph.font.color.rgb = SKY
        ph.space_before = Pt(8)

        for s in subitems:
            ps = tf_m2.add_paragraph()
            ps.text = f"   - {s}"
            ps.font.size = Pt(11)
            ps.font.color.rgb = TEXT_WHITE

    add_card(s7, Inches(0.8), Inches(6.35), Inches(11.7), Inches(0.65), CARD_BG, AMBER)
    tb_s7 = s7.shapes.add_textbox(Inches(1.0), Inches(6.4), Inches(11.3), Inches(0.55))
    p_s7 = tb_s7.text_frame.paragraphs[0]
    p_s7.text = "📊 Minh bạch chi phí: Mọi token đều được hạch toán trực tiếp vào cột dữ liệu ChatMessage của khách hàng."
    p_s7.font.size = Pt(11)
    p_s7.font.bold = True
    p_s7.font.color.rgb = TEXT_WHITE

    # =========================================================================
    # SLIDE 8: MLOPS ADVANCED CAPABILITIES
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    add_slide_background(s8)
    add_header(s8, "MLOps Hub", "Năng Lực Tinh Chỉnh & Thử Nghiệm Mô Hình", 
               "Chủ động huấn luyện mô hình ngôn ngữ nhỏ (SLM) và bộ điều phối RAG riêng biệt.")

    mlops_hubs = [
        ("Model Registry & Tracking", 
         "Quản lý tập trung các checkpoint và siêu tham số:",
         ["Lưu trữ thông số huấn luyện (learning_rate, epochs, batch_size)",
          "Theo dõi biểu đồ hàm mất mát (loss_history) qua từng epoch",
          "Quản lý huyết thống tập dữ liệu (Dataset Lineage & SHA256)",
          "Chuyển đổi active model linh hoạt trên giao diện quản trị"],
         AMBER),
        ("Gemma 2B LoRA Fine-Tuning", 
         "Pipeline tinh chỉnh SLM chuyên ngành F&B:",
         ["Mô hình gốc: google/gemma-2-2b-it",
          "Cấu hình LoRA nhẹ: r=8, alpha=16, targets: q_proj, v_proj",
          "Tối ưu cho văn phong tư vấn đồ uống Việt Nam tự nhiên",
          "Huấn luyện trực tiếp trên GPU RTX / CPU local"],
         SKY),
        ("Contrastive RAG Adapter", 
         "Bộ điều chỉnh véc-tơ cải thiện tìm kiếm ngữ nghĩa:",
         ["Mô hình nhúng: sentence-transformers/all-MiniLM-L6-v2",
          "Kiến trúc: Linear Projection + LayerNorm + Residual",
          "Học độ tương đồng cho từ lóng đồ uống (e.g. bạc xỉu, trà mãng cầu)",
          "Độ chính xác truy xuất cải thiện +28.5%"],
         EMERALD)
    ]

    for i, (title, intro, bullets, col) in enumerate(mlops_hubs):
        cx = Inches(0.8) + i * (w_dm + Inches(0.3))
        add_card(s8, cx, Inches(1.85), w_dm, Inches(5.1))

        tb = s8.shapes.add_textbox(cx + Inches(0.2), Inches(2.0), w_dm - Inches(0.4), Inches(4.8))
        tf = tb.text_frame
        tf.word_wrap = True

        ph = tf.paragraphs[0]
        ph.text = title
        ph.font.size = Pt(15)
        ph.font.bold = True
        ph.font.color.rgb = col

        pi = tf.add_paragraph()
        pi.text = intro
        pi.font.size = Pt(11)
        pi.font.color.rgb = TEXT_MUTED
        pi.space_before = Pt(8)

        for b in bullets:
            pb = tf.add_paragraph()
            pb.text = f"• {b}"
            pb.font.size = Pt(11)
            pb.font.color.rgb = TEXT_WHITE
            pb.space_before = Pt(8)

    # =========================================================================
    # SLIDE 9: SCORECARD VS WORKSHOP BRIEF (CRITICAL TABLE)
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    add_slide_background(s9)
    add_header(s9, "Evaluation Scorecard", "Bảng Đối Chiếu Tiến Độ Với Đề Bài Workshop", 
               "Đánh giá trung thực từng tiêu chí kỹ thuật theo yêu cầu ban tổ chức và mentor.")

    # Table layout
    rows = 9
    cols = 3
    left = Inches(0.8)
    top = Inches(1.8)
    width = Inches(11.733)
    height = Inches(4.6)

    table_shape = s9.shapes.add_table(rows, cols, left, top, width, height)
    table = table_shape.table
    table.columns[0].width = Inches(3.6)
    table.columns[1].width = Inches(1.8)
    table.columns[2].width = Inches(6.333)

    score_data = [
        ("Hạng Mục Yêu Cầu", "Trạng Thái", "Dẫn Chứng Mã Nguồn & Đánh Giá Kỹ Thuật"),
        ("1. Thu thập tên, SĐT, địa chỉ → Đẩy vào DB", "DONE", "Model User (phone, name, address), Regex phone VN, endpoint đăng ký/cập nhật."),
        ("2. Gợi ý đồ uống Detox, Coffee, Protein", "DONE", "Seed data đủ nhóm protein (3 món), detox, cà phê, trà. Có test case xác minh."),
        ("3. Lưu chat history để đánh giá độ chính xác", "PARTIAL", "Đã lưu tin nhắn kèm Token, Cost, Latency; Chưa có nút Like/Dislike trực tiếp."),
        ("4. Ứng dụng → VPC Endpoint → AWS Bedrock", "NOT STARTED", "Khoảng trống lớn nhất: Đang gọi trực tiếp OpenAI API & Ollama Local."),
        ("5. Đóng gói Docker cho Backend & Frontend", "DONE", "Dockerfile tối ưu + docker-compose.yml (Postgres, Backend, Frontend, Nginx)."),
        ("6. Tracking Model & Token từng message", "DONE", "Cột model_name, input_tokens, output_tokens, estimated_cost_usd trên ChatMessage."),
        ("7. Quản lý phiên bản Prompt & Rollback", "DONE", "DB-backed PromptVersion store, mã SHA-256 chống drift, API kích hoạt/rollback."),
        ("8. AI Agent có bước duyệt (Human Approval)", "DONE", "2 cổng duyệt: Xác nhận đặt món (Order) + Xác nhận đổi hồ sơ (Pending preferences).")
    ]

    for r_idx, row in enumerate(score_data):
        for c_idx, val in enumerate(row):
            cell = table.cell(r_idx, c_idx)
            cell.text = val
            cell.fill.solid()
            
            p = cell.text_frame.paragraphs[0]
            p.font.size = Pt(11)
            
            if r_idx == 0:
                cell.fill.fore_color.rgb = CARD_BG
                p.font.bold = True
                p.font.color.rgb = SKY
            else:
                cell.fill.fore_color.rgb = RGBColor(18, 26, 44) if r_idx % 2 == 0 else RGBColor(14, 21, 36)
                if c_idx == 1:
                    p.alignment = PP_ALIGN.CENTER
                    p.font.bold = True
                    if val == "DONE":
                        p.font.color.rgb = EMERALD
                    elif val == "PARTIAL":
                        p.font.color.rgb = AMBER
                    else:
                        p.font.color.rgb = ROSE
                elif c_idx == 0 and val.startswith("4."):
                    p.font.color.rgb = ROSE
                    p.font.bold = True
                else:
                    p.font.color.rgb = TEXT_WHITE

    # Bottom summary
    add_card(s9, Inches(0.8), Inches(6.5), Inches(11.7), Inches(0.55), CARD_BG, EMERALD)
    tb_sc = s9.shapes.add_textbox(Inches(1.0), Inches(6.52), Inches(11.3), Inches(0.5))
    p_sc = tb_sc.text_frame.paragraphs[0]
    p_sc.text = "🎯 Tổng kết mức độ đáp ứng: 7/8 Hạng mục hoàn thành (87.5%) • Ưu tiên trọng tâm tiếp theo là AWS Bedrock VPC Endpoint."
    p_sc.font.size = Pt(11)
    p_sc.font.bold = True
    p_sc.font.color.rgb = TEXT_WHITE

    # =========================================================================
    # SLIDE 10: ROADMAP & Q&A
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    add_slide_background(s10)
    add_header(s10, "Looking Forward", "Kế Hoạch Phát Triển Tiếp Theo & Thảo Luận (Q&A)", 
               "Các hạng mục trọng tâm nhằm hoàn thiện 100% chuẩn kiến trúc đám mây doanh nghiệp.")

    roadmaps = [
        ("ƯU TIÊN 1: CRITICAL", "AWS Bedrock & VPC Endpoint", 
         ["Triển khai SDK Boto3 hỗ trợ Claude 3 Haiku / Llama 3 trên AWS Bedrock",
          "Cấu hình VPC Endpoint bảo mật không đi qua public internet",
          "Đáp ứng trọn vẹn yêu cầu hạ tầng đám mây từ bài toán workshop"],
         ROSE),
        ("ƯU TIÊN 2: UX FEEDBACK", "User Feedback Loop (RLHF)", 
         ["Bổ sung nút Thumbs Up / Down cho từng tin nhắn trên giao diện Frontend",
          "Đồng bộ điểm đánh giá trực tiếp về Langfuse Dataset",
          "Xây dựng tập Eval dữ liệu thực tế từ phản hồi của khách hàng"],
         AMBER),
        ("ƯU TIÊN 3: CI/CD PIPELINE", "Continuous Retraining", 
         ["Tự động kích hoạt pipeline huấn luyện lại mô hình SLM khi có dữ liệu mới",
          "Kiểm định chất lượng tự động qua bộ 73 bài kiểm tra regression",
          "Tự động triển khai canary deployment khi mô hình mới vượt benchmark"],
         EMERALD)
    ]

    for i, (tag, title, items, col) in enumerate(roadmaps):
        cx = Inches(0.8) + i * (w_dm + Inches(0.3))
        add_card(s10, cx, Inches(1.85), w_dm, Inches(3.6))

        tb = s10.shapes.add_textbox(cx + Inches(0.2), Inches(2.0), w_dm - Inches(0.4), Inches(3.3))
        tf = tb.text_frame
        tf.word_wrap = True

        ptag = tf.paragraphs[0]
        ptag.text = tag
        ptag.font.size = Pt(10)
        ptag.font.bold = True
        ptag.font.color.rgb = col

        ptt = tf.add_paragraph()
        ptt.text = title
        ptt.font.size = Pt(14)
        ptt.font.bold = True
        ptt.font.color.rgb = TEXT_WHITE
        ptt.space_before = Pt(4)

        for it in items:
            pi = tf.add_paragraph()
            pi.text = f"• {it}"
            pi.font.size = Pt(11)
            pi.font.color.rgb = TEXT_MUTED
            pi.space_before = Pt(8)

    # Q&A Box
    add_card(s10, Inches(2.5), Inches(5.65), Inches(8.333), Inches(1.4), CARD_BG, AMBER)
    tb_qa = s10.shapes.add_textbox(Inches(2.7), Inches(5.75), Inches(7.9), Inches(1.2))
    tf_qa = tb_qa.text_frame
    tf_qa.word_wrap = True

    p_qa1 = tf_qa.paragraphs[0]
    p_qa1.text = "☕ CẢM ƠN QUÝ THẦY CÔ & CÁC BẠN ĐÃ LẮNG NGHE!"
    p_qa1.alignment = PP_ALIGN.CENTER
    p_qa1.font.size = Pt(18)
    p_qa1.font.bold = True
    p_qa1.font.color.rgb = AMBER

    p_qa2 = tf_qa.add_paragraph()
    p_qa2.text = "DrinkBot MLOps — Hệ thống Backend sẵn sàng cho phần Hỏi & Đáp (Q&A)"
    p_qa2.alignment = PP_ALIGN.CENTER
    p_qa2.font.size = Pt(13)
    p_qa2.font.color.rgb = TEXT_WHITE
    p_qa2.space_before = Pt(6)

    # Save presentation
    output_path = "slide-info-backend/DrinkBot_MLOps_Backend_Presentation.pptx"
    prs.save(output_path)
    print(f"Presentation successfully saved to: {output_path}")

    # Also save a copy in the root folder for easy access
    prs.save("DrinkBot_MLOps_Backend_Presentation.pptx")
    print("Also saved copy to root: DrinkBot_MLOps_Backend_Presentation.pptx")

if __name__ == "__main__":
    create_presentation()
