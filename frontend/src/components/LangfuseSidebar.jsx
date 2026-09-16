import { useState, useEffect } from 'react'
import { api } from '../api'

export default function LangfuseSidebar({ isOpen, onClose, onRefreshTrigger }) {
  const [activeTab, setActiveTab] = useState('traces') // 'traces' | 'prompts'
  const [traces, setTraces] = useState([])
  const [loadingTraces, setLoadingTraces] = useState(false)
  const [selectedTrace, setSelectedTrace] = useState(null)
  const [copiedId, setCopiedId] = useState(null)

  // Prompt Registry state
  const [prompts, setPrompts] = useState([])
  const [activeVersion, setActiveVersion] = useState('1.1.0')
  const [loadingPrompts, setLoadingPrompts] = useState(false)
  const [activatingVersion, setActivatingVersion] = useState(null)
  const [expandedPromptVer, setExpandedPromptVer] = useState(null)
  const [showNewPromptModal, setShowNewPromptModal] = useState(false)
  const [newVersion, setNewVersion] = useState('')
  const [newDesc, setNewDesc] = useState('')
  const [newTemplate, setNewTemplate] = useState('')
  const [feedbackMsg, setFeedbackMsg] = useState(null)

  async function fetchTraces() {
    setLoadingTraces(true)
    try {
      const data = await api.traces(35)
      setTraces(data.traces || [])
    } catch (err) {
      console.error('Failed to load traces:', err)
    } finally {
      setLoadingTraces(false)
    }
  }

  async function fetchPrompts() {
    setLoadingPrompts(true)
    try {
      const data = await api.prompts()
      setPrompts(data.prompts || [])
      setActiveVersion(data.active_version || '1.1.0')
    } catch (err) {
      console.error('Failed to load prompts:', err)
    } finally {
      setLoadingPrompts(false)
    }
  }

  useEffect(() => {
    if (isOpen) {
      fetchTraces()
      fetchPrompts()
    }
  }, [isOpen, onRefreshTrigger])

  async function handleClear() {
    try {
      await api.clearTraces()
      setTraces([])
      setSelectedTrace(null)
    } catch (err) {
      console.error(err)
    }
  }

  async function handleActivatePrompt(version) {
    setActivatingVersion(version)
    try {
      const res = await api.activatePrompt(version)
      setActiveVersion(res.active_version)
      await fetchPrompts()
      setFeedbackMsg(`✓ Đã kích hoạt Prompt v${res.active_version}! Lượt chat tiếp theo sẽ dùng prompt này.`)
      setTimeout(() => setFeedbackMsg(null), 3500)
    } catch (err) {
      alert(`Lỗi kích hoạt prompt: ${err.message}`)
    } finally {
      setActivatingVersion(null)
    }
  }

  async function handleCreatePrompt(e) {
    e.preventDefault()
    if (!newVersion.trim() || !newTemplate.trim()) return
    try {
      await api.createPrompt({
        version: newVersion.trim(),
        description: newDesc.trim(),
        template: newTemplate.trim(),
        label: 'ab_test',
        activate: true,
      })
      setShowNewPromptModal(false)
      setNewVersion('')
      setNewDesc('')
      setNewTemplate('')
      await fetchPrompts()
      setFeedbackMsg('✓ Đã tạo và kích hoạt Prompt version mới cho thử nghiệm A/B!')
      setTimeout(() => setFeedbackMsg(null), 3500)
    } catch (err) {
      alert(`Lỗi tạo prompt: ${err.message}`)
    }
  }

  function handleCopy(text, id) {
    navigator.clipboard.writeText(typeof text === 'object' ? JSON.stringify(text, null, 2) : text)
    setCopiedId(id)
    setTimeout(() => setCopiedId(null), 1800)
  }

  if (!isOpen) return null

  return (
    <aside className="w-full md:w-1/2 bg-white border-l border-amber-200 shadow-sm flex flex-col flex-shrink-0 transition-all duration-300 h-full">
      {/* HEADER - Amber style matching main app */}
      <div className="px-4 py-3 border-b border-amber-100 bg-amber-50/90 flex items-center justify-between flex-shrink-0">
        <div className="flex items-center gap-2.5">
          <span className="text-xl">📊</span>
          <div>
            <h2 className="text-sm font-bold text-amber-900 flex items-center gap-1.5">
              Langfuse LLMOps Panel
              <span className="w-2 h-2 rounded-full bg-emerald-500 inline-block animate-pulse" title="Đang kết nối Telemetry & Prompt Registry"></span>
            </h2>
            <p className="text-[11px] text-amber-700/90">
              Observability Traces & Prompt Version Management
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-amber-100 text-amber-900 border border-amber-200 hidden sm:inline-block">
            50% Màn hình
          </span>
          <button
            onClick={onClose}
            className="w-7 h-7 rounded-lg hover:bg-amber-200/60 text-amber-800 flex items-center justify-center transition text-sm font-bold"
            title="Đóng bảng Langfuse"
          >
            ✕
          </button>
        </div>
      </div>

      {/* TABS NAVIGATION */}
      <div className="flex border-b border-amber-200 bg-amber-50/40 text-xs font-semibold">
        <button
          onClick={() => setActiveTab('traces')}
          className={`flex-1 py-2.5 px-3 flex items-center justify-center gap-2 transition border-b-2 ${
            activeTab === 'traces'
              ? 'border-amber-600 text-amber-950 bg-white font-bold'
              : 'border-transparent text-amber-800/80 hover:text-amber-900 hover:bg-amber-100/50'
          }`}
        >
          <span>📈</span> Traces & Logs
          <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-amber-100 text-amber-900 border border-amber-300">
            {traces.length}
          </span>
        </button>
        <button
          onClick={() => setActiveTab('prompts')}
          className={`flex-1 py-2.5 px-3 flex items-center justify-center gap-2 transition border-b-2 ${
            activeTab === 'prompts'
              ? 'border-amber-600 text-amber-950 bg-white font-bold'
              : 'border-transparent text-amber-800/80 hover:text-amber-900 hover:bg-amber-100/50'
          }`}
        >
          <span>🏷️</span> Quản Lý Prompt (A/B Test)
          <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-amber-600 text-white font-bold">
            v{activeVersion}
          </span>
        </button>
      </div>

      {/* FEEDBACK TOAST */}
      {feedbackMsg && (
        <div className="bg-emerald-600 text-white text-xs px-3 py-1.5 text-center font-medium animate-fadeIn">
          {feedbackMsg}
        </div>
      )}

      {/* TAB 1: TRACES & LOGS */}
      {activeTab === 'traces' && (
        <>
          {/* QUICK STATS & ACTION TOOLBAR */}
          <div className="px-4 py-2 bg-amber-50/30 border-b border-amber-100 flex items-center justify-between text-xs text-amber-900 flex-shrink-0">
            <span className="text-[11px] font-medium text-amber-800">
              Đã ghi: <strong className="text-amber-800">{traces.length}</strong> lượt • Prompt active: <strong className="font-mono text-amber-900">v{activeVersion}</strong>
            </span>
            <div className="flex items-center gap-2">
              <button
                onClick={fetchTraces}
                disabled={loadingTraces}
                className="px-2.5 py-1 bg-amber-100 hover:bg-amber-200 text-amber-900 rounded text-[11px] font-semibold transition"
              >
                {loadingTraces ? 'Đang tải...' : '↻ Tải lại'}
              </button>
              <button
                onClick={handleClear}
                className="px-2.5 py-1 hover:bg-red-100 text-red-600 rounded text-[11px] transition font-medium"
              >
                Xóa log
              </button>
            </div>
          </div>

          {/* TRACE LIST */}
          <div className="flex-1 overflow-y-auto p-3.5 space-y-3">
            {traces.length === 0 ? (
              <div className="text-center py-16 text-amber-700/60 space-y-2">
                <div className="text-3xl">☕</div>
                <p className="text-sm font-semibold text-amber-900">Chưa có lượt chat nào trong phiên.</p>
                <p className="text-xs text-amber-700">Gửi tin nhắn bên cạnh để kiểm tra latency, token, chi phí và tool call tại đây!</p>
              </div>
            ) : (
              traces.map((trace, idx) => {
                const isSelected = selectedTrace?.trace_id === trace.trace_id
                return (
                  <div
                    key={trace.trace_id || idx}
                    className={`p-3.5 rounded-xl border transition text-left ${
                      isSelected
                        ? 'bg-amber-50/70 border-amber-400 shadow-sm ring-1 ring-amber-300'
                        : 'bg-white border-amber-200 hover:border-amber-300 hover:bg-amber-50/30'
                    }`}
                  >
                    {/* TOP BAR OF TRACE */}
                    <div 
                      className="flex items-center justify-between text-xs cursor-pointer pb-1.5"
                      onClick={() => setSelectedTrace(isSelected ? null : trace)}
                    >
                      <div className="flex items-center gap-1.5 flex-wrap">
                        <span className="font-mono text-amber-900 font-bold text-[11px]">
                          {trace.trace_id}
                        </span>
                        <span className={`px-1.5 py-0.2 rounded text-[10px] font-semibold ${
                          trace.success ? 'bg-emerald-100 text-emerald-800 border border-emerald-300' : 'bg-red-100 text-red-800 border border-red-300'
                        }`}>
                          {trace.success ? 'SUCCESS' : 'ERROR'}
                        </span>
                        <span className="px-1.5 py-0.2 rounded text-[10px] font-mono font-bold bg-amber-200/90 text-amber-950 border border-amber-300">
                          v{trace.prompt_version || '1.1.0'}
                        </span>
                      </div>
                      <div className="flex items-center gap-1.5 text-gray-500 font-mono text-[10px]">
                        <span>{trace.timestamp ? trace.timestamp.split(' ')[1] : ''}</span>
                        <span className="text-amber-700 font-bold text-xs">{isSelected ? '▲ Thu gọn' : '▼ Chi tiết'}</span>
                      </div>
                    </div>

                    {/* USER INPUT SNIPPET */}
                    <div 
                      className="text-xs text-gray-800 font-medium line-clamp-2 mb-2.5 cursor-pointer"
                      onClick={() => setSelectedTrace(isSelected ? null : trace)}
                    >
                      <span className="text-amber-900 font-bold">User:</span> "{trace.input_text}"
                    </div>

                    {/* METRICS 4-COL BOX */}
                    <div className="grid grid-cols-4 gap-2 text-center text-[11px] bg-amber-100/50 p-2 rounded-lg border border-amber-200/70 text-gray-700 font-mono">
                      <div>
                        <div className="text-amber-800/70 text-[9px] font-sans">Độ trễ</div>
                        <div className="font-bold text-amber-900">{trace.latency_ms}ms</div>
                      </div>
                      <div>
                        <div className="text-amber-800/70 text-[9px] font-sans">In Token</div>
                        <div className="font-bold text-gray-800">{trace.input_tokens}</div>
                      </div>
                      <div>
                        <div className="text-amber-800/70 text-[9px] font-sans">Out Token</div>
                        <div className="font-bold text-gray-800">{trace.output_tokens}</div>
                      </div>
                      <div>
                        <div className="text-amber-800/70 text-[9px] font-sans">Chi phí</div>
                        <div className="font-bold text-amber-900">${trace.cost_usd}</div>
                      </div>
                    </div>

                    {/* TOOLS CHIPS */}
                    {trace.tools_called && trace.tools_called.length > 0 && (
                      <div className="flex flex-wrap items-center gap-1.5 mt-2.5 text-[10px]">
                        <span className="text-amber-800/80 font-medium">Tools đã gọi:</span>
                        {trace.tools_called.map((tool) => (
                          <span
                            key={tool}
                            className="px-2 py-0.5 rounded-md bg-amber-200/80 text-amber-950 border border-amber-300 font-mono font-bold"
                          >
                            🛠️ {tool}
                          </span>
                        ))}
                      </div>
                    )}

                    {/* EXPANDED FULL DETAILS */}
                    {isSelected && (
                      <div className="mt-3.5 pt-3.5 border-t border-amber-200 text-xs space-y-3 text-gray-700">
                        {/* 1. USER INPUT FULL */}
                        <div>
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-amber-900 font-bold text-[11px] flex items-center gap-1">
                              👤 Câu hỏi của User (Full Input):
                            </span>
                            <button
                              onClick={() => handleCopy(trace.input_text, `in-${trace.trace_id}`)}
                              className="text-[10px] text-amber-700 hover:text-amber-900 underline font-medium"
                            >
                              {copiedId === `in-${trace.trace_id}` ? '✓ Đã chép' : 'Sao chép'}
                            </button>
                          </div>
                          <div className="bg-white p-2.5 rounded-lg border border-amber-200 text-[11px] text-gray-800 leading-relaxed break-words whitespace-pre-wrap max-h-36 overflow-y-auto">
                            {trace.input_text}
                          </div>
                        </div>

                        {/* 2. FULL AI RESPONSE */}
                        <div>
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-amber-900 font-bold text-[11px] flex items-center gap-1">
                              🤖 Toàn bộ phản hồi của AI (Full Response):
                            </span>
                            <button
                              onClick={() => handleCopy(trace.output_text, `out-${trace.trace_id}`)}
                              className="text-[10px] text-amber-700 hover:text-amber-900 underline font-medium"
                            >
                              {copiedId === `out-${trace.trace_id}` ? '✓ Đã chép' : 'Sao chép'}
                            </button>
                          </div>
                          <div className="bg-white p-2.5 rounded-lg border border-amber-200 text-[11px] text-gray-800 leading-relaxed break-words whitespace-pre-wrap max-h-60 overflow-y-auto font-sans">
                            {trace.output_text}
                          </div>
                        </div>

                        {/* 3. TOOL CALLING DETAILED LOGS */}
                        <div>
                          <div className="flex items-center justify-between mb-1.5">
                            <span className="text-amber-900 font-bold text-[11px] flex items-center gap-1">
                              ⚙️ Log chi tiết Tool Calling ({trace.tool_calls_detail?.length || trace.tools_called?.length || 0}):
                            </span>
                          </div>

                          {trace.tool_calls_detail && trace.tool_calls_detail.length > 0 ? (
                            <div className="space-y-2.5">
                              {trace.tool_calls_detail.map((tc, tcIdx) => (
                                <div key={tcIdx} className="bg-white rounded-lg border border-amber-300 p-2.5 shadow-2xs space-y-2">
                                  <div className="flex items-center justify-between border-b border-amber-100 pb-1">
                                    <span className="font-mono font-bold text-amber-950 text-[11px]">
                                      #{tcIdx + 1} 🛠️ {tc.tool}
                                    </span>
                                    <span className="text-[9px] px-1.5 py-0.5 rounded bg-amber-100 text-amber-800 font-mono">
                                      executed
                                    </span>
                                  </div>

                                  <div>
                                    <span className="text-[10px] font-semibold text-slate-700 block mb-0.5">
                                      📥 Tham số truyền vào (Arguments từ LLM):
                                    </span>
                                    <pre className="p-2 rounded bg-[#0d1117] text-emerald-300 font-mono text-[10px] overflow-x-auto max-h-32 border border-slate-800">
                                      {JSON.stringify(tc.args, null, 2)}
                                    </pre>
                                  </div>

                                  <div>
                                    <span className="text-[10px] font-semibold text-slate-700 block mb-0.5">
                                      📤 Kết quả trả về (System / DB Return):
                                    </span>
                                    <pre className="p-2 rounded bg-[#0d1117] text-amber-300 font-mono text-[10px] overflow-x-auto max-h-48 border border-slate-800">
                                      {JSON.stringify(tc.result, null, 2)}
                                    </pre>
                                  </div>
                                </div>
                              ))}
                            </div>
                          ) : (
                            <div className="bg-white p-2 rounded border border-amber-200 text-[11px] text-gray-500 italic">
                              Không kích hoạt tool nào ở lượt này (Trả lời trực tiếp).
                            </div>
                          )}
                        </div>

                        {/* 4. PROMPT TEMPLATE & VERSION METADATA */}
                        <div className="bg-white rounded-lg border border-amber-300 p-2.5 shadow-2xs space-y-2">
                          <div className="flex items-center justify-between border-b border-amber-100 pb-1">
                            <span className="text-amber-950 font-bold text-[11px] flex items-center gap-1.5">
                              🏷️ Prompt Template & Version
                            </span>
                            <span className="px-2 py-0.5 rounded-full bg-amber-100 text-amber-900 font-mono font-bold text-[10px] border border-amber-300">
                              v{trace.prompt_version || '1.1.0'}
                            </span>
                          </div>

                          <div className="grid grid-cols-2 gap-1.5 text-[10px] text-gray-700 font-mono">
                            <div className="bg-amber-50/60 p-1.5 rounded border border-amber-200/60">
                              <div className="text-amber-800/80 text-[9px] font-sans font-medium">Tên Prompt</div>
                              <div className="font-semibold text-gray-900 truncate" title={trace.prompt_name || 'drink-assistant-system'}>
                                {trace.prompt_name || 'drink-assistant-system'}
                              </div>
                            </div>
                            <div className="bg-amber-50/60 p-1.5 rounded border border-amber-200/60">
                              <div className="text-amber-800/80 text-[9px] font-sans font-medium">Model AI</div>
                              <div className="font-semibold text-gray-900 truncate" title={trace.model}>
                                {trace.model}
                              </div>
                            </div>
                            <div className="bg-amber-50/60 p-1.5 rounded border border-amber-200/60 col-span-2">
                              <div className="text-amber-800/80 text-[9px] font-sans font-medium">SHA256 Hash</div>
                              <div className="font-semibold text-amber-950 truncate">
                                {trace.prompt_hash || 'a24d1ace09f1'}
                              </div>
                            </div>
                          </div>

                          {trace.system_prompt && (
                            <div>
                              <div className="flex items-center justify-between mb-0.5">
                                <span className="text-[10px] font-semibold text-slate-700">
                                  📜 System Prompt thực tế (Kèm Profile khách):
                                </span>
                                <button
                                  onClick={() => handleCopy(trace.system_prompt, `sys-${trace.trace_id}`)}
                                  className="text-[10px] text-amber-700 hover:text-amber-900 underline font-medium"
                                >
                                  {copiedId === `sys-${trace.trace_id}` ? '✓ Đã chép' : 'Sao chép'}
                                </button>
                              </div>
                              <pre className="p-2 rounded bg-[#0d1117] text-slate-300 font-mono text-[10px] overflow-x-auto max-h-40 border border-slate-800 whitespace-pre-wrap leading-relaxed">
                                {trace.system_prompt}
                              </pre>
                            </div>
                          )}
                        </div>

                        {/* 5. COPY RAW JSON BUTTON */}
                        <button
                          onClick={() => handleCopy(trace, `raw-${trace.trace_id}`)}
                          className="w-full py-1.5 px-2 bg-amber-100 hover:bg-amber-200 text-amber-900 rounded font-semibold text-[11px] transition flex items-center justify-center gap-1.5"
                        >
                          <span>📋</span>
                          {copiedId === `raw-${trace.trace_id}` ? '✓ Đã chép toàn bộ Trace JSON' : 'Sao chép toàn bộ Trace JSON'}
                        </button>
                      </div>
                    )}
                  </div>
                )
              })
            )}
          </div>
        </>
      )}

      {/* TAB 2: PROMPT REGISTRY (A/B TESTING & ROLLBACK) */}
      {activeTab === 'prompts' && (
        <div className="flex-1 overflow-y-auto p-4 space-y-4 text-xs">
          {/* BANNER EXPLANATION */}
          <div className="bg-amber-50 border border-amber-300 rounded-xl p-3.5 space-y-2 text-amber-950">
            <div className="flex items-center justify-between">
              <h3 className="font-bold text-sm text-amber-900 flex items-center gap-1.5">
                🏷️ Dynamic Prompt Registry
              </h3>
              <span className="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-mono text-[10px] font-bold border border-emerald-300">
                Active: v{activeVersion}
              </span>
            </div>
            <p className="text-[11px] text-amber-800 leading-relaxed">
              Quản lý phiên bản Prompt động theo chuẩn <strong>Person 4 (MLOps)</strong>. Bạn có thể 
              <strong> chuyển đổi biến thể A/B Test</strong> hoặc <strong>Rollback tức thì</strong> mà không cần sửa code hay redeploy lại server.
            </p>
            <div className="flex items-center gap-2 pt-1">
              <button
                onClick={() => setShowNewPromptModal(true)}
                className="px-3 py-1 bg-amber-600 hover:bg-amber-700 text-white rounded-lg text-xs font-semibold transition shadow-2xs"
              >
                + Tạo Version Prompt Mới (A/B Test)
              </button>
              <button
                onClick={fetchPrompts}
                disabled={loadingPrompts}
                className="px-2.5 py-1 bg-white hover:bg-amber-100 text-amber-900 border border-amber-300 rounded-lg text-xs font-medium transition"
              >
                {loadingPrompts ? '...' : '↻ Làm mới'}
              </button>
            </div>
          </div>

          {/* NEW PROMPT MODAL / FORM */}
          {showNewPromptModal && (
            <form onSubmit={handleCreatePrompt} className="bg-white border-2 border-amber-400 rounded-xl p-4 shadow-md space-y-3">
              <div className="flex items-center justify-between border-b border-amber-200 pb-2">
                <h4 className="font-bold text-amber-900 text-xs">Thêm phiên bản Prompt mới (A/B Testing)</h4>
                <button
                  type="button"
                  onClick={() => setShowNewPromptModal(false)}
                  className="text-gray-400 hover:text-gray-700 font-bold"
                >
                  ✕
                </button>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-[11px] font-semibold text-gray-700 mb-1">Mã Version (SemVer):</label>
                  <input
                    value={newVersion}
                    onChange={(e) => setNewVersion(e.target.value)}
                    placeholder="ví dụ: 1.3.0-promo"
                    className="w-full border border-gray-300 rounded px-2.5 py-1 text-xs font-mono"
                    required
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-semibold text-gray-700 mb-1">Mục đích / Ghi chú:</label>
                  <input
                    value={newDesc}
                    onChange={(e) => setNewDesc(e.target.value)}
                    placeholder="ví dụ: Prompt chào hàng mùa hè, câu từ vui vẻ"
                    className="w-full border border-gray-300 rounded px-2.5 py-1 text-xs"
                    required
                  />
                </div>
              </div>
              <div>
                <label className="block text-[11px] font-semibold text-gray-700 mb-1">
                  Nội dung Template (Hỗ trợ <code>{'{name}'}</code> và <code>{'{profile_json}'}</code>):
                </label>
                <textarea
                  value={newTemplate}
                  onChange={(e) => setNewTemplate(e.target.value)}
                  rows={6}
                  placeholder="You are a drink assistant chatting with {name}..."
                  className="w-full border border-gray-300 rounded p-2 text-xs font-mono"
                  required
                />
              </div>
              <div className="flex justify-end gap-2 pt-1">
                <button
                  type="button"
                  onClick={() => setShowNewPromptModal(false)}
                  className="px-3 py-1 text-gray-600 hover:bg-gray-100 rounded text-xs"
                >
                  Hủy
                </button>
                <button
                  type="submit"
                  className="px-4 py-1 bg-amber-600 hover:bg-amber-700 text-white rounded text-xs font-semibold shadow-xs"
                >
                  Lưu & Kích hoạt ngay
                </button>
              </div>
            </form>
          )}

          {/* LIST OF PROMPT VERSIONS */}
          <div className="space-y-3">
            <h4 className="font-bold text-amber-900 text-xs flex items-center justify-between">
              <span>Các phiên bản Prompt trong Registry ({prompts.length})</span>
              <span className="text-[10px] text-gray-500 font-normal">Được lưu vết hash SHA-256</span>
            </h4>

            {prompts.map((p) => {
              const isAct = p.version === activeVersion
              const isExpanded = expandedPromptVer === p.version

              return (
                <div
                  key={p.version}
                  className={`p-3.5 rounded-xl border transition ${
                    isAct
                      ? 'bg-amber-50/90 border-amber-500 shadow-sm ring-1 ring-amber-400'
                      : 'bg-white border-amber-200 hover:border-amber-300'
                  }`}
                >
                  {/* HEADER OF PROMPT VERSION */}
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-mono font-bold text-amber-950 text-sm">
                          v{p.version}
                        </span>
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                            isAct
                              ? 'bg-emerald-600 text-white'
                              : p.label === 'ab_test'
                              ? 'bg-purple-100 text-purple-800 border border-purple-300'
                              : 'bg-gray-100 text-gray-700 border border-gray-300'
                          }`}
                        >
                          {isAct ? 'Đang Chạy (Active)' : p.label}
                        </span>
                        <span className="text-[10px] font-mono text-gray-400">
                          #{p.prompt_hash}
                        </span>
                      </div>
                      <p className="text-gray-700 text-[11px] mt-1 font-medium">
                        {p.description}
                      </p>
                    </div>

                    {/* ACTION BUTTON */}
                    <div>
                      {isAct ? (
                        <span className="px-2.5 py-1 rounded-lg bg-emerald-100 text-emerald-800 font-semibold text-[11px] inline-block border border-emerald-300">
                          ✓ Đang Sử Dụng
                        </span>
                      ) : (
                        <button
                          onClick={() => handleActivatePrompt(p.version)}
                          disabled={activatingVersion === p.version}
                          className="px-3 py-1 rounded-lg bg-amber-600 hover:bg-amber-700 text-white font-semibold text-xs shadow-2xs transition"
                        >
                          {activatingVersion === p.version ? 'Đang chuyển...' : '🚀 Kích hoạt'}
                        </button>
                      )}
                    </div>
                  </div>

                  {/* TOGGLE TEMPLATE PREVIEW */}
                  <div className="mt-2.5 pt-2 border-t border-amber-200/60 flex items-center justify-between text-[11px]">
                    <button
                      onClick={() => setExpandedPromptVer(isExpanded ? null : p.version)}
                      className="text-amber-800 hover:text-amber-950 font-semibold underline"
                    >
                      {isExpanded ? '▲ Đóng xem Prompt Template' : '▼ Xem chi tiết Prompt Template'}
                    </button>
                    <button
                      onClick={() => handleCopy(p.template, `tpl-${p.version}`)}
                      className="text-gray-500 hover:text-gray-800 underline text-[10px]"
                    >
                      {copiedId === `tpl-${p.version}` ? '✓ Đã chép' : 'Sao chép Template'}
                    </button>
                  </div>

                  {isExpanded && (
                    <div className="mt-2">
                      <pre className="p-2.5 rounded bg-[#0d1117] text-slate-300 font-mono text-[10px] overflow-x-auto max-h-48 border border-slate-800 whitespace-pre-wrap leading-relaxed">
                        {p.template}
                      </pre>
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* FOOTER */}
      <div className="px-4 py-2.5 border-t border-amber-100 bg-amber-50/70 text-center text-[11px] text-amber-900 flex items-center justify-between flex-shrink-0">
        <span className="font-medium">DrinkBot LLMOps • Person 4</span>
        <a
          href="/LANGFUSE_INTEGRATION_GUIDE.html"
          target="_blank"
          rel="noreferrer"
          className="text-amber-800 hover:text-amber-950 font-bold hover:underline flex items-center gap-1"
        >
          📖 MLOps Guide
        </a>
      </div>
    </aside>
  )
}
