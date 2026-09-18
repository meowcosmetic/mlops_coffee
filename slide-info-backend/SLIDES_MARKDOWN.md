---
marp: true
theme: default
paginate: true
header: "DrinkBot MLOps — Backend Architecture & Status"
footer: "TMA Solutions • F&B AI Workshop 2026"
style: |
  section {
    background: #0f172a;
    color: #f1f5f9;
    font-family: 'Segoe UI', system-ui, sans-serif;
  }
  h1, h2 { color: #f59e0b; }
  table { font-size: 0.85rem; }
  th { background: #1e293b; color: #38bdf8; }
  td { border-color: #334155; }
  pre, code { background: #1e293b; color: #a5f3fc; }
  .badge-done { color: #10b981; font-weight: bold; }
  .badge-partial { color: #f59e0b; font-weight: bold; }
  .badge-todo { color: #ef4444; font-weight: bold; }
---

# ☕ DrinkBot MLOps
## Backend Architecture, Multi-Agent & Deployment Review
**Báo cáo Tiến độ & Thiết kế Kỹ thuật Backend**

- **Hệ thống**: Chatbot Khuyến nghị Đồ uống Thông minh & MLOps Hub
- **Tech Stack**: FastAPI • SQLAlchemy Async • LangChain • PostgreSQL • Ollama
- **Ngày báo cáo**: Tháng 09/2026

---

## 🎯 1. Mục tiêu & Phạm vi Dự án (Section Goal)

- **Mục tiêu Workshop**: Xây dựng trợ lý ảo F&B tự động thu thập thực thể người dùng, tư vấn đồ uống cá nhân hóa (cà phê, trà detox, protein shakes), và lưu trữ an toàn vào DB.
- **Tiêu chí MLOps**:
  - Quản lý phiên bản Prompt & Model (`PromptVersion`, Model Registry).
  - Ghi nhận chi tiết lịch sử trò chuyện, token, latency và chi phí.
  - Đảm bảo an toàn dị ứng (Allergen Guardrails) và cơ chế Human-in-the-loop.
- **Tinh thần báo cáo**: **Minh bạch và khách quan** — làm rõ những phần đã hoàn tất (Done), đang hoàn thiện (Partial) và chưa triển khai (Not started như Bedrock VPC).

<!-- note
Slide này mở đầu để định vị mục tiêu của backend trong workshop: vừa đáp ứng nghiệp vụ F&B, vừa tuân thủ tiêu chuẩn MLOps.
-->

---

## ⚡ 2. Kiến trúc Công nghệ Tổng thể (Tech Stack)

| Lớp (Layer) | Công nghệ | Chi tiết triển khai |
|---|---|---|
| **API Framework** | FastAPI + Uvicorn | Xử lý bất đồng bộ (async/await), validation Pydantic v2 |
| **Database & ORM** | PostgreSQL 16 + SQLAlchemy Async | Kết nối asyncpg, quản lý migration qua Alembic |
| **Agent & LLM** | LangChain + LangChain-OpenAI | Tool calling loop, tích hợp fallback thông minh |
| **Inference Engines** | OpenAI API + Ollama Local | Fallback zero-cost với mô hình cục bộ `gemma4:e4b` |
| **Observability** | Langfuse + Structured JSON Logs | Tracing end-to-end, đo lường token, latency, chi phí |
| **Đóng gói / Deploy** | Docker Compose + Nginx Gateway | Backend, Frontend, Postgres, Adminer, Nginx reverse proxy |
| **Test Suite** | Pytest Asyncio (73 passed) | 100% pass: Auth, Chat, Menu, Prompt Admin, RAG, Evals |

---

## 🗄️ 3. Mô hình Dữ liệu Nghiệp vụ (Domain Model)

*Tuân thủ chặt chẽ đề bài workshop: Thu thập thực thể & đẩy vào DB*

- **`User`**: Thu thập đầy đủ 3 thực thể cốt lõi: `phone`, `name`, `address`. Xác thực Regex số điện thoại VN.
- **`UserPreference`**: Lưu trữ sở thích cá nhân hóa:
  - `tastes` (ngọt, đắng, chua...), `drink_types` (trà, cà phê, sinh tố)
  - `temperature` (nóng/đá), `caffeine` (có/không/ít)
  - `allergies` (sữa, đậu phộng...), `dietary_restrictions` (ăn chay, keto)
- **`MenuItem`**: Danh mục phong phú với phân loại rõ ràng (Coffee, Tea, Protein, Detox, Juices) kèm danh sách dị nguyên (`allergens`).
- **`ChatMessage`**: Lưu hội thoại kèm metadata MLOps (`model_name`, `input_tokens`, `output_tokens`, `estimated_cost_usd`).
- **`PromptVersion` & `PendingPreferenceChange`**: Lưu trữ lịch sử prompt và hàng đợi xác nhận thay đổi thông tin người dùng.

---

## 🤖 4. Autonomous Chat Agent & Human-in-the-Loop

**Quy trình ReAct Agent (Max 4 vòng lặp) với 3 công cụ (Tools):**

```
User Message ──► [LLM Agent] ──► Gọi Tool
                                  ├─ 1. recommend_drink (Tra cứu menu + RAG)
                                  ├─ 2. update_profile   (Tạo PendingPreferenceChange)
                                  └─ 3. order            (Tạo Pending Order)
```

- **Business Guardrail tuyệt đối bằng mã nguồn Python**:
  - Không bao giờ tin tưởng hoàn toàn vào LLM đối với quy tắc an toàn.
  - Loại trừ nghiêm ngặt các món chứa chất gây dị ứng (`allergens`) ngay trong hàm thực thi Python.
- **Cơ chế Duyệt 2 Tầng (Two-Stage Human Confirmation Gate)**:
  - `order`: Tạo preview trạng thái `pending`. Chỉ chuyển sang `placed` khi khách bấm Xác nhận.
  - `update_profile`: Tạo `PendingPreferenceChange`. Phải có xác nhận của khách hàng mới cập nhật DB chính thức.

---

## 📝 5. Quản lý Prompt & Version Control Động

*Giải quyết triệt để vấn đề "Prompt Hardcoding" trước đây*

- **Lưu trữ hoàn toàn trong Database**: Bảng `PromptVersion` theo dõi lịch sử chỉnh sửa, tác giả, trạng thái kích hoạt (`is_active`).
- **Phát hiện trôi dạt (Drift Detection)**: Tự động băm SHA-256 (`prompt_hash`) cho mọi template prompt.
- **Giao diện Quản trị viên (Admin API)**:
  - `POST /api/prompts`: Tạo phiên bản mới (tự động validate biến template).
  - `GET /api/prompts?name=...`: Xem toàn bộ lịch sử các phiên bản.
  - `POST /api/prompts/{id}/activate`: Kích hoạt phiên bản ngay lập tức mà **không cần redeploy backend** (Hỗ trợ Rollback & A/B Testing).
- **Tích hợp Telemetry**: Truy vết chính xác `prompt_name`, `prompt_version`, `prompt_hash` trong từng request log.

---

## ⚙️ 6. Hạ tầng Suy luận Đa Mô hình (Inference & Fallback)

- **Đa tầng Engine**:
  - **Primary**: Cloud LLM (`gpt-4o-mini` hoặc `ag/gemini-3.8-flash-low`).
  - **Local Zero-Cost**: Kết nối trực tiếp Ollama Local (`gemma4:e4b`) qua mạng Docker nội bộ.
- **Cơ chế Tự động Phục hồi (Auto-Fallback)**:
  - Nếu Cloud Model gặp sự cố (hết quota, mất mạng, lỗi API key) $\rightarrow$ Tự động chuyển tiếp sang mô hình local Ollama.
  - Đảm bảo chatbot không bao giờ trả về lỗi trắng màn hình cho người dùng cuối.
- **Structured JSON Logging**: Mỗi lần gọi LLM ghi lại:
  `request_id`, `provider`, `model`, `latency_ms`, `tokens`, `estimated_cost_usd`.

---

## 🔬 7. Năng lực MLOps Nâng cao (MLOps Hub)

Dự án đã tích hợp sẵn pipeline MLOps hoàn chỉnh trong thư mục `backend/app/services/`:

1. **Model Registry & Experiment Tracking**:
   - Quản lý các checkpoint mô hình (Local LoRA weights, Embeddings).
   - Theo dõi siêu tham số (Hyperparameters), lịch sử loss (`loss_history`), đồ thị độ chính xác.
2. **SLM Fine-Tuning Pipeline**:
   - Tinh chỉnh Gemma 2B qua LoRA (`r=8, alpha=16, target=q_proj,v_proj`).
   - Huấn luyện trên bộ dữ liệu F&B domain riêng biệt.
3. **Contrastive RAG Embedding Adapter**:
   - Adapter tuyến tính cải thiện độ tương đồng ngữ nghĩa cho tiếng lóng và thuật ngữ đồ uống Việt Nam.

---

## 📊 8. Bảng Đánh Giá Chi Tiết (Scorecard vs Workshop Brief)

| Yêu cầu từ Workshop / Mentor | Trạng thái | Ghi chú & Đánh giá kỹ thuật |
|---|:---:|---|
| **1. Thu thập tên, SĐT, địa chỉ $\rightarrow$ DB** | <span class="badge-done">DONE</span> | Hoàn thành xuất sắc qua `User` model, regex phone VN |
| **2. Gợi ý Detox / Cà phê / Protein drinks** | <span class="badge-done">DONE</span> | Seed menu đủ nhóm Protein, Detox, Coffee, Tea, Juices |
| **3. Lưu chat history để đo độ chính xác** | <span class="badge-partial">PARTIAL</span> | Đã lưu tin nhắn + Token + Chi phí; Chưa có nút Like/Dislike |
| **4. App $\rightarrow$ VPC Endpoint $\rightarrow$ AWS Bedrock** | <span class="badge-todo">NOT STARTED</span> | **Khoảng trống lớn nhất**: Đang gọi trực tiếp OpenAI / Ollama |
| **5. Docker hóa Backend & Frontend** | <span class="badge-done">DONE</span> | Dockerfile tối ưu + Docker Compose + Nginx Gateway |
| **6. Tracking Model & Token từng message** | <span class="badge-done">DONE</span> | Cột `model_name`, `input_tokens`, `cost` trên `ChatMessage` |
| **7. Prompt Version Control & Rollback** | <span class="badge-done">DONE</span> | DB-backed `PromptVersion` + API quản trị + SHA256 hash |
| **8. AI Agent có bước duyệt (Human Approval)** | <span class="badge-done">DONE</span> | Xác nhận đặt món (Order) + Xác nhận đổi sở thích (Preferences) |

---

## 🚀 9. Kế hoạch Phát triển Tiếp theo (Roadmap & Q&A)

1. **Ưu tiên 1: Tích hợp AWS Bedrock & VPC Endpoint**
   - Chuyển đổi tầng `llm.py` sang hỗ trợ AWS Boto3 Bedrock client (`anthropic.claude-3-haiku` / `meta.llama3`).
   - Cấu hình VPC Endpoint bảo mật theo yêu cầu kiến trúc đám mây của doanh nghiệp.
2. **Ưu tiên 2: Vòng phản hồi đánh giá trực tiếp (User Feedback Loop)**
   - Bổ sung nút Like / Dislike trên giao diện Frontend `Chat.jsx`.
   - Lưu trữ phản hồi người dùng về Langfuse để tạo tập dữ liệu đánh giá (Eval dataset) tự động.
3. **Ưu tiên 3: Tự động hóa CI/CD Trigger Fine-Tuning**
   - Kích hoạt pipeline huấn luyện lại khi tập dữ liệu mẫu đạt ngưỡng (Threshold) mới.

---

# ☕ Cảm Ơn Quý Thầy Cô & Các Bạn!
### DrinkBot MLOps — Sẵn sàng cho phần Hỏi & Đáp (Q&A)
