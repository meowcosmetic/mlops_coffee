import { useState, useEffect } from 'react'
import { api } from '../api'

export default function LangfuseSidebar({ isOpen, onClose, onRefreshTrigger }) {
  const [activeTab, setActiveTab] = useState('traces') // 'traces' | 'prompts' | 'evals'
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

  // Evals & Centralized Dataset state
  const [datasetItems, setDatasetItems] = useState([])
  const [loadingDataset, setLoadingDataset] = useState(false)
  const [latestBenchmark, setLatestBenchmark] = useState(null)
  const [isRunningBenchmark, setIsRunningBenchmark] = useState(false)
  const [filterCategory, setFilterCategory] = useState('all')
  const [expandedResultId, setExpandedResultId] = useState(null)

  // Dynamic Model & Prompt selection for Benchmark
  const [availableModels, setAvailableModels] = useState([])
  const [benchmarkModel, setBenchmarkModel] = useState('ag/gemini-3.8-flash-low')
  const [benchmarkPromptVersion, setBenchmarkPromptVersion] = useState('1.1.0')
  const [customModelInput, setCustomModelInput] = useState('')
  const [useCustomModel, setUseCustomModel] = useState(false)

  // Add Test Case Modal state
  const [showAddModal, setShowAddModal] = useState(false)
  const [modalCategory, setModalCategory] = useState('menu_groundedness')
  const [modalName, setModalName] = useState('')
  const [modalInput, setModalInput] = useState('')
  const [modalExpectedDesc, setModalExpectedDesc] = useState('')

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

  async function fetchDataset() {
    setLoadingDataset(true)
    try {
      const data = await api.evalDataset()
      setDatasetItems(data.items || [])
    } catch (err) {
      console.error('Failed to load eval dataset:', err)
    } finally {
      setLoadingDataset(false)
    }
  }

  async function fetchLatestBenchmark() {
    try {
      const data = await api.latestBenchmark()
      if (data && data.benchmark) {
        setLatestBenchmark(data.benchmark)
      }
    } catch (err) {
      console.error('Failed to load latest benchmark:', err)
    }
  }

  async function fetchModels() {
    try {
      const data = await api.models()
      setAvailableModels(data.models || [])
      if (data.current_model) {
        setBenchmarkModel(data.current_model)
      }
    } catch (err) {
      console.error('Failed to load models:', err)
    }
  }

  useEffect(() => {
    if (isOpen) {
      fetchTraces()
      fetchPrompts()
      fetchDataset()
      fetchLatestBenchmark()
      fetchModels()
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

  async function handleRunBenchmark() {
    setIsRunningBenchmark(true)
    const effectiveModel = useCustomModel ? (customModelInput.trim() || benchmarkModel) : benchmarkModel
    try {
      const res = await api.runBenchmark(benchmarkPromptVersion, effectiveModel)
      if (res && res.benchmark) {
        setLatestBenchmark(res.benchmark)
        setFeedbackMsg(`✓ Đã hoàn tất Benchmark [${effectiveModel}] - Prompt [v${res.benchmark.prompt_version}]! Pass Rate: ${res.benchmark.overall_pass_rate}%`)
        setTimeout(() => setFeedbackMsg(null), 4500)
      }
    } catch (err) {
      alert(`Lỗi chạy Benchmark: ${err.message}`)
    } finally {
      setIsRunningBenchmark(false)
    }
  }

  async function handleAddEvalCase(e) {
    e.preventDefault()
    if (!modalInput.trim() || !modalName.trim()) return
    try {
      await api.addEvalItem({
        category: modalCategory,
        name: modalName.trim(),
        input_text: modalInput.trim(),
        description: modalExpectedDesc.trim() || 'Custom test case từ người dùng',
        expected: {},
      })
      setShowAddModal(false)
      setModalName('')
      setModalInput('')
      setModalExpectedDesc('')
      await fetchDataset()
      setFeedbackMsg('✓ Đã thêm Test Case mới vào Centralized Dataset!')
      setTimeout(() => setFeedbackMsg(null), 3500)
    } catch (err) {
      alert(`Lỗi thêm Test Case: ${err.message}`)
    }
  }

  async function handleDeleteEvalCase(id) {
    if (!confirm('Bạn có chắc muốn xóa Test Case này khỏi Benchmark Dataset?')) return
    try {
      await api.deleteEvalItem(id)
      await fetchDataset()
      setFeedbackMsg('✓ Đã xóa Test Case thành công.')
      setTimeout(() => setFeedbackMsg(null), 3000)
    } catch (err) {
      alert(`Lỗi xóa: ${err.message}`)
    }
  }

  function handleAddTraceToDataset(trace) {
    setModalCategory('menu_groundedness')
    setModalName(`Edge Case từ Trace #${(trace.trace_id || '').slice(-6)}`)
    setModalInput(trace.input_text || '')
    setModalExpectedDesc(`Câu trả lời mong muốn: ${trace.output_text?.slice(0, 100)}...`)
    setActiveTab('evals')
    setShowAddModal(true)
  }

  function handleCopy(text, id) {
    navigator.clipboard.writeText(typeof text === 'object' ? JSON.stringify(text, null, 2) : text)
    setCopiedId(id)
    setTimeout(() => setCopiedId(null), 1800)
  }

  const filteredDataset = datasetItems.filter(item => {
    if (filterCategory === 'all') return true
    return item.category === filterCategory
  })

  // Lookup result map by test_id from latest benchmark
  const resultsByTestId = {}
  if (latestBenchmark && latestBenchmark.results) {
    for (const r of latestBenchmark.results) {
      resultsByTestId[r.test_id] = r
    }
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
              Observability Traces • Prompt Versioning • Evals & Benchmark
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

      {/* TABS NAVIGATION (3 TABS) */}
      <div className="flex border-b border-amber-200 bg-amber-50/40 text-xs font-semibold">
        <button
          onClick={() => setActiveTab('traces')}
          className={`flex-1 py-2.5 px-2 flex items-center justify-center gap-1.5 transition border-b-2 ${
            activeTab === 'traces'
              ? 'border-amber-600 text-amber-950 bg-white font-bold'
              : 'border-transparent text-amber-800/80 hover:text-amber-900 hover:bg-amber-100/50'
          }`}
        >
          <span>📈</span> Traces
          <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-amber-100 text-amber-900 border border-amber-300">
            {traces.length}
          </span>
        </button>
        <button
          onClick={() => setActiveTab('prompts')}
          className={`flex-1 py-2.5 px-2 flex items-center justify-center gap-1.5 transition border-b-2 ${
            activeTab === 'prompts'
              ? 'border-amber-600 text-amber-950 bg-white font-bold'
              : 'border-transparent text-amber-800/80 hover:text-amber-900 hover:bg-amber-100/50'
          }`}
        >
          <span>🏷️</span> Prompts
          <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-amber-600 text-white font-bold">
            v{activeVersion}
          </span>
        </button>
        <button
          onClick={() => setActiveTab('evals')}
          className={`flex-1 py-2.5 px-2 flex items-center justify-center gap-1.5 transition border-b-2 ${
            activeTab === 'evals'
              ? 'border-amber-600 text-amber-950 bg-white font-bold'
              : 'border-transparent text-amber-800/80 hover:text-amber-900 hover:bg-amber-100/50'
          }`}
        >
          <span>🧪</span> Benchmark Evals
          <span className={`px-1.5 py-0.2 rounded-full text-[10px] font-bold ${
            latestBenchmark 
              ? (latestBenchmark.overall_pass_rate >= 80 ? 'bg-emerald-100 text-emerald-800 border border-emerald-300' : 'bg-amber-100 text-amber-900 border border-amber-300')
              : 'bg-gray-100 text-gray-700'
          }`}>
            {latestBenchmark ? `${latestBenchmark.overall_pass_rate}%` : `${datasetItems.length} tests`}
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
              Đã ghi: <strong className="text-amber-800">{traces.length}</strong> lượt • Active Prompt: <strong className="font-mono text-amber-900">v{activeVersion}</strong>
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

                                  {tc.tool === 'recommend_drink' && (
                                    <div className="bg-emerald-50 border border-emerald-200 rounded p-1.5 flex items-center justify-between text-[10px]">
                                      <span className="font-semibold text-emerald-900 flex items-center gap-1">
                                        🧠 RAG Semantic Engine Active
                                      </span>
                                      <span className="text-emerald-700 font-mono text-[9px]">
                                        all-MiniLM-L6-v2 (Local Free)
                                      </span>
                                    </div>
                                  )}

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

                        {/* 5. ACTIONS: CURATE TO DATASET & COPY RAW JSON */}
                        <div className="grid grid-cols-2 gap-2 pt-1">
                          <button
                            onClick={() => handleAddTraceToDataset(trace)}
                            className="py-1.5 px-2 bg-amber-600 hover:bg-amber-700 text-white rounded font-semibold text-[11px] transition flex items-center justify-center gap-1.5 shadow-2xs"
                          >
                            <span>➕</span> Đưa vào Benchmark Dataset
                          </button>
                          <button
                            onClick={() => handleCopy(trace, `raw-${trace.trace_id}`)}
                            className="py-1.5 px-2 bg-amber-100 hover:bg-amber-200 text-amber-900 rounded font-semibold text-[11px] transition flex items-center justify-center gap-1.5 border border-amber-300"
                          >
                            <span>📋</span> {copiedId === `raw-${trace.trace_id}` ? '✓ Đã chép JSON' : 'Sao chép JSON Trace'}
                          </button>
                        </div>
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
              Quản lý các version của System Prompt theo chuẩn Langfuse Registry. Có thể kích hoạt tức thời để A/B testing tính cách nhân viên pha chế hoặc rollback prompt mà không cần sửa file Python hay restart server.
            </p>
            <div className="flex items-center justify-between pt-1">
              <span className="text-[10px] text-amber-700 italic">
                🔄 Lưu vết hash SHA-256 đối chiếu với Trace Telemetry.
              </span>
              <button
                onClick={() => setShowNewPromptModal(!showNewPromptModal)}
                className="px-3 py-1 bg-amber-600 hover:bg-amber-700 text-white rounded font-semibold text-xs transition shadow-2xs"
              >
                {showNewPromptModal ? 'Đóng tạo mới' : '+ Tạo Version Mới'}
              </button>
            </div>
          </div>

          {/* CREATE NEW PROMPT MODAL / INLINE FORM */}
          {showNewPromptModal && (
            <form
              onSubmit={handleCreatePrompt}
              className="bg-white border border-amber-300 rounded-xl p-3.5 shadow-sm space-y-3 animate-fadeIn"
            >
              <h4 className="font-bold text-amber-950 text-xs">Thêm phiên bản Prompt mới vào Registry</h4>
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-[11px] font-semibold text-gray-700 mb-1">Phiên bản (version):</label>
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

      {/* TAB 3: BENCHMARK EVALS & CENTRALIZED DATASET */}
      {activeTab === 'evals' && (
        <div className="flex-1 overflow-y-auto p-4 space-y-4 text-xs">
          {/* BENCHMARK RUNNER & SUMMARY BANNER */}
          <div className="bg-amber-50 border border-amber-300 rounded-xl p-3.5 space-y-3 text-amber-950">
            <div className="flex items-center justify-between flex-wrap gap-2">
              <div>
                <h3 className="font-bold text-sm text-amber-900 flex items-center gap-1.5">
                  🧪 Centralized Dataset & Automated Benchmark
                </h3>
                <p className="text-[11px] text-amber-800">
                  Chuẩn Langfuse Dataset API • 4 Bộ Evaluators tự động • Hỗ trợ chọn Model & Prompt
                </p>
              </div>
            </div>

            {/* MODEL & PROMPT CONFIGURATION ROW */}
            <div className="bg-white/95 p-2.5 rounded-lg border border-amber-200 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-2.5 shadow-2xs">
              <div className="flex flex-1 items-center gap-2 flex-wrap">
                <div className="flex-1 min-w-[170px]">
                  <label className="block text-[10px] font-bold text-gray-700 mb-0.5">
                    🤖 Model AI cần Benchmark:
                  </label>
                  {useCustomModel ? (
                    <div className="flex items-center gap-1">
                      <input
                        value={customModelInput}
                        onChange={(e) => setCustomModelInput(e.target.value)}
                        placeholder="Nhập tên model..."
                        className="w-full border border-gray-300 rounded px-2 py-1 text-xs font-mono"
                      />
                      <button
                        type="button"
                        onClick={() => setUseCustomModel(false)}
                        className="text-[10px] text-amber-700 hover:underline px-1 whitespace-nowrap"
                      >
                        Chọn list
                      </button>
                    </div>
                  ) : (
                    <div className="flex items-center gap-1">
                      <select
                        value={benchmarkModel}
                        onChange={(e) => setBenchmarkModel(e.target.value)}
                        className="w-full border border-gray-300 rounded px-2 py-1 text-xs font-medium bg-amber-50/40 text-gray-800"
                      >
                        {availableModels.map(m => (
                          <option key={m.id} value={m.id}>{m.name || m.id}</option>
                        ))}
                        {availableModels.length === 0 && (
                          <option value="ag/gemini-3.8-flash-low">Gemini 3.8 Flash (Low Latency)</option>
                        )}
                      </select>
                      <button
                        type="button"
                        onClick={() => setUseCustomModel(true)}
                        className="text-[10px] text-amber-800 hover:underline px-1 font-semibold whitespace-nowrap"
                        title="Nhập tên model khác"
                      >
                        Khác...
                      </button>
                    </div>
                  )}
                </div>

                <div className="min-w-[130px]">
                  <label className="block text-[10px] font-bold text-gray-700 mb-0.5">
                    🏷️ Prompt Version:
                  </label>
                  <select
                    value={benchmarkPromptVersion}
                    onChange={(e) => setBenchmarkPromptVersion(e.target.value)}
                    className="w-full border border-gray-300 rounded px-2 py-1 text-xs font-mono font-bold text-amber-950 bg-amber-50/40"
                  >
                    {prompts.map(p => (
                      <option key={p.version} value={p.version}>
                        v{p.version} {p.version === activeVersion ? '(Active)' : ''}
                      </option>
                    ))}
                    {prompts.length === 0 && (
                      <option value="1.1.0">v1.1.0</option>
                    )}
                  </select>
                </div>
              </div>

              <div className="flex items-center gap-2 self-end sm:self-center pt-1 sm:pt-0">
                <button
                  onClick={() => setShowAddModal(true)}
                  className="px-2.5 py-1.5 bg-amber-100 hover:bg-amber-200 text-amber-900 border border-amber-300 rounded font-semibold text-xs transition whitespace-nowrap"
                >
                  + Test Case
                </button>
                <button
                  onClick={handleRunBenchmark}
                  disabled={isRunningBenchmark}
                  className={`px-3 py-1.5 rounded font-bold text-xs text-white shadow-2xs transition flex items-center gap-1.5 whitespace-nowrap ${
                    isRunningBenchmark
                      ? 'bg-amber-400 cursor-not-allowed'
                      : 'bg-amber-600 hover:bg-amber-700'
                  }`}
                >
                  {isRunningBenchmark ? (
                    <>
                      <span className="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                      Đang Test ({datasetItems.length} ca)...
                    </>
                  ) : (
                    <>🚀 Chạy Benchmark</>
                  )}
                </button>
              </div>
            </div>

            {/* LATEST RUN METRICS CARD */}
            {latestBenchmark ? (
              <div className="bg-white rounded-xl border border-amber-300 p-3 shadow-2xs space-y-2.5">
                <div className="flex items-center justify-between border-b border-amber-100 pb-2 flex-wrap gap-2">
                  <div className="flex items-center gap-1.5 flex-wrap">
                    <span className="font-mono text-xs font-bold text-amber-950">
                      Run #{latestBenchmark.run_id}
                    </span>
                    <span className="px-2 py-0.5 rounded font-mono font-bold text-[10px] bg-blue-100 text-blue-900 border border-blue-300 max-w-[160px] truncate" title={latestBenchmark.model_name}>
                      🤖 {latestBenchmark.model_name || benchmarkModel}
                    </span>
                    <span className="px-2 py-0.5 rounded font-mono font-bold text-[10px] bg-amber-100 text-amber-900 border border-amber-300">
                      v{latestBenchmark.prompt_version}
                    </span>
                    <span className="text-[10px] text-gray-500">
                      {latestBenchmark.timestamp}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] text-gray-600 font-mono">
                      {latestBenchmark.passed_tests}/{latestBenchmark.total_tests} Passed
                    </span>
                    <span className={`px-2 py-0.5 rounded text-xs font-bold ${
                      latestBenchmark.overall_pass_rate >= 80
                        ? 'bg-emerald-100 text-emerald-800 border border-emerald-300'
                        : 'bg-amber-100 text-amber-800 border border-amber-300'
                    }`}>
                      {latestBenchmark.overall_pass_rate}% Pass Rate
                    </span>
                  </div>
                </div>


                {/* 4 EVALUATOR CATEGORY SCORES */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-center text-[11px] font-mono">
                  {/* 1. Allergen Safety */}
                  <div className={`p-2 rounded-lg border ${
                    latestBenchmark.allergen_safety_rate === 100
                      ? 'bg-emerald-50 border-emerald-200 text-emerald-900'
                      : 'bg-red-50 border-red-300 text-red-900'
                  }`}>
                    <div className="text-[9px] font-sans font-semibold text-gray-600 mb-0.5">
                      🛡️ Dị Ứng (An Toàn)
                    </div>
                    <div className="text-sm font-bold">
                      {latestBenchmark.allergen_safety_rate}%
                    </div>
                    <div className="text-[9px] font-sans text-gray-500">
                      {latestBenchmark.allergen_safety_rate === 100 ? '100% An toàn' : 'Cảnh báo vi phạm!'}
                    </div>
                  </div>

                  {/* 2. Menu Groundedness */}
                  <div className="p-2 rounded-lg border bg-blue-50 border-blue-200 text-blue-900">
                    <div className="text-[9px] font-sans font-semibold text-gray-600 mb-0.5">
                      📋 Chống Ảo Giác
                    </div>
                    <div className="text-sm font-bold">
                      {latestBenchmark.hallucination_free_rate}%
                    </div>
                    <div className="text-[9px] font-sans text-gray-500">
                      Grounded Menu
                    </div>
                  </div>

                  {/* 3. Profile Extraction */}
                  <div className="p-2 rounded-lg border bg-purple-50 border-purple-200 text-purple-900">
                    <div className="text-[9px] font-sans font-semibold text-gray-600 mb-0.5">
                      👤 Trích Xuất Profile
                    </div>
                    <div className="text-sm font-bold">
                      {latestBenchmark.extraction_accuracy}%
                    </div>
                    <div className="text-[9px] font-sans text-gray-500">
                      Update Tool Precision
                    </div>
                  </div>

                  {/* 4. Order Accuracy */}
                  <div className="p-2 rounded-lg border bg-amber-50 border-amber-200 text-amber-900">
                    <div className="text-[9px] font-sans font-semibold text-gray-600 mb-0.5">
                      ☕ Độ Chuẩn Đơn
                    </div>
                    <div className="text-sm font-bold">
                      {latestBenchmark.order_accuracy}%
                    </div>
                    <div className="text-[9px] font-sans text-gray-500">
                      Order Tool Calling
                    </div>
                  </div>
                </div>

                {/* COST & LATENCY FOOTER */}
                <div className="flex items-center justify-between text-[10px] text-gray-500 pt-1 font-mono">
                  <span>⏱️ TB Độ trễ: <strong className="text-amber-900">{latestBenchmark.avg_latency_ms}ms</strong>/turn</span>
                  <span>💰 Tổng chi phí: <strong className="text-amber-900">${latestBenchmark.total_cost_usd}</strong></span>
                </div>
              </div>
            ) : (
              <div className="bg-white/80 p-3 rounded-xl border border-amber-200 text-center space-y-1">
                <p className="text-amber-900 font-semibold text-xs">Chưa có kết quả Benchmark nào cho phiên này.</p>
                <p className="text-gray-500 text-[11px]">
                  Bấm <strong>"🚀 Chạy Benchmark Toàn Bộ"</strong> để chạy {datasetItems.length} kịch bản test tự động và tính điểm Pass Rate cho Prompt active (v{activeVersion}).
                </p>
              </div>
            )}
          </div>

          {/* CATEGORY FILTER TABS */}
          <div className="flex items-center gap-1.5 flex-wrap pb-1 border-b border-gray-200">
            {[
              { key: 'all', label: `Tất cả (${datasetItems.length})` },
              { key: 'allergen_safety', label: '🛡️ An Toàn Dị Ứng' },
              { key: 'menu_groundedness', label: '📋 Chống Ảo Giác' },
              { key: 'profile_extraction', label: '👤 Trích Xuất' },
              { key: 'order_accuracy', label: '☕ Đặt Món' },
            ].map(cat => (
              <button
                key={cat.key}
                onClick={() => setFilterCategory(cat.key)}
                className={`px-2.5 py-1 rounded-full text-[11px] font-semibold transition ${
                  filterCategory === cat.key
                    ? 'bg-amber-600 text-white shadow-2xs'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {cat.label}
              </button>
            ))}
          </div>

          {/* ADD TEST CASE MODAL */}
          {showAddModal && (
            <form
              onSubmit={handleAddEvalCase}
              className="bg-white border border-amber-300 rounded-xl p-3.5 shadow-md space-y-3 animate-fadeIn"
            >
              <div className="flex items-center justify-between border-b border-amber-100 pb-2">
                <h4 className="font-bold text-amber-950 text-xs">Thêm Test Case mới vào Centralized Dataset</h4>
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="text-gray-400 hover:text-gray-600 text-sm"
                >
                  ✕
                </button>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-[11px] font-semibold text-gray-700 mb-1">Loại Đánh Giá (Category):</label>
                  <select
                    value={modalCategory}
                    onChange={(e) => setModalCategory(e.target.value)}
                    className="w-full border border-gray-300 rounded px-2 py-1 text-xs"
                  >
                    <option value="allergen_safety">🛡️ An toàn Dị ứng (Allergen Safety)</option>
                    <option value="menu_groundedness">📋 Chống Ảo giác (Menu Groundedness)</option>
                    <option value="profile_extraction">👤 Trích xuất Profile (Profile Extraction)</option>
                    <option value="order_accuracy">☕ Độ chuẩn Đơn hàng (Order Accuracy)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-[11px] font-semibold text-gray-700 mb-1">Tên Kịch Bản:</label>
                  <input
                    value={modalName}
                    onChange={(e) => setModalName(e.target.value)}
                    placeholder="ví dụ: Khách dị ứng dâu tây"
                    className="w-full border border-gray-300 rounded px-2.5 py-1 text-xs"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-gray-700 mb-1">Tin nhắn của User (Input Test):</label>
                <textarea
                  value={modalInput}
                  onChange={(e) => setModalInput(e.target.value)}
                  rows={2}
                  placeholder="ví dụ: Mình bị dị ứng dâu tây, tư vấn món giải khát không có dâu..."
                  className="w-full border border-gray-300 rounded p-2 text-xs"
                  required
                />
              </div>

              <div>
                <label className="block text-[11px] font-semibold text-gray-700 mb-1">Mô tả Tiêu Chí Đạt (Expected Ground Truth):</label>
                <input
                  value={modalExpectedDesc}
                  onChange={(e) => setModalExpectedDesc(e.target.value)}
                  placeholder="ví dụ: AI không được gợi ý món chứa dâu tây"
                  className="w-full border border-gray-300 rounded px-2.5 py-1 text-xs"
                />
              </div>

              <div className="flex justify-end gap-2 pt-1">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-3 py-1 text-gray-600 hover:bg-gray-100 rounded text-xs"
                >
                  Hủy
                </button>
                <button
                  type="submit"
                  className="px-4 py-1 bg-amber-600 hover:bg-amber-700 text-white rounded text-xs font-semibold shadow-xs"
                >
                  Lưu vào Centralized Dataset
                </button>
              </div>
            </form>
          )}

          {/* DATASET ITEMS LIST */}
          <div className="space-y-3">
            {loadingDataset ? (
              <div className="text-center py-8 text-gray-500 text-xs">Đang tải danh sách Test Cases...</div>
            ) : filteredDataset.length === 0 ? (
              <div className="text-center py-8 text-gray-500 text-xs">Không có test case nào trong danh mục này.</div>
            ) : (
              filteredDataset.map((item) => {
                const runResult = resultsByTestId[item.id]
                const isExpanded = expandedResultId === item.id

                return (
                  <div
                    key={item.id}
                    className={`p-3 rounded-xl border transition ${
                      runResult
                        ? runResult.passed
                          ? 'bg-emerald-50/40 border-emerald-300'
                          : 'bg-red-50/40 border-red-300'
                        : 'bg-white border-amber-200'
                    }`}
                  >
                    {/* TOP HEADER */}
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-center gap-1.5 flex-wrap">
                        <span className="font-mono text-[10px] font-bold text-amber-950 bg-amber-100 px-1.5 py-0.5 rounded border border-amber-300">
                          {item.id}
                        </span>
                        <span className={`px-2 py-0.5 rounded-full text-[9px] font-bold uppercase ${
                          item.category === 'allergen_safety'
                            ? 'bg-red-100 text-red-800 border border-red-300'
                            : item.category === 'menu_groundedness'
                            ? 'bg-blue-100 text-blue-800 border border-blue-300'
                            : item.category === 'profile_extraction'
                            ? 'bg-purple-100 text-purple-800 border border-purple-300'
                            : 'bg-amber-100 text-amber-800 border border-amber-300'
                        }`}>
                          {item.category.replace('_', ' ')}
                        </span>
                        <strong className="text-gray-900 text-xs">{item.name}</strong>
                      </div>

                      {/* BENCHMARK RUN STATUS & DELETE BUTTON */}
                      <div className="flex items-center gap-2 flex-shrink-0">
                        {runResult && (
                          <span className={`px-2 py-0.5 rounded text-[10px] font-bold font-mono ${
                            runResult.passed
                              ? 'bg-emerald-600 text-white'
                              : 'bg-red-600 text-white'
                          }`}>
                            {runResult.passed ? `PASS (${runResult.score})` : `FAIL (${runResult.score})`}
                          </span>
                        )}
                        <button
                          onClick={() => handleDeleteEvalCase(item.id)}
                          className="text-gray-400 hover:text-red-600 p-1 transition"
                          title="Xóa test case khỏi Dataset"
                        >
                          🗑️
                        </button>
                      </div>
                    </div>

                    {/* INPUT USER TEXT */}
                    <div className="mt-2 text-xs bg-white/90 p-2 rounded-lg border border-amber-200 text-gray-800 font-sans">
                      <span className="text-amber-900 font-bold">Input:</span> "{item.input_text}"
                    </div>

                    {/* EXPECTED CRITERIA */}
                    <div className="mt-1.5 text-[11px] text-gray-600 italic px-1">
                      🎯 <span className="font-semibold">Tiêu chí:</span> {item.description}
                    </div>

                    {/* RUN DETAILS IF BENCHMARK HAS RUN */}
                    {runResult && (
                      <div className="mt-2.5 pt-2 border-t border-gray-200 text-[11px] space-y-1.5">
                        <div className="flex items-center justify-between text-[10px] text-gray-500 font-mono">
                          <span>⏱️ {runResult.latency_ms}ms • 🪙 {runResult.tokens} tokens</span>
                          <button
                            onClick={() => setExpandedResultId(isExpanded ? null : item.id)}
                            className="text-amber-800 hover:text-amber-950 font-bold underline"
                          >
                            {isExpanded ? '▲ Thu gọn Output' : '▼ Xem phản hồi AI thực tế'}
                          </button>
                        </div>

                        <div className={`p-2 rounded font-sans text-xs ${
                          runResult.passed ? 'bg-emerald-100/70 text-emerald-900' : 'bg-red-100/70 text-red-900'
                        }`}>
                          <strong className="block mb-0.5">Kết luận Evaluator:</strong>
                          {runResult.eval_details}
                        </div>

                        {isExpanded && (
                          <div className="mt-2 p-2 rounded bg-[#0d1117] text-slate-200 font-mono text-[10px] max-h-40 overflow-y-auto whitespace-pre-wrap">
                            <span className="text-emerald-400 block mb-1">🤖 AI Actual Output:</span>
                            {runResult.reply}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )
              })
            )}
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
