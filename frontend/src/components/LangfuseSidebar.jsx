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

  // Model Registry & Retrain State
  const [modelsList, setModelsList] = useState([])
  const [loadingModelsList, setLoadingModelsList] = useState(false)
  const [activeChatModelKey, setActiveChatModelKey] = useState('')
  const [activeEmbedModelKey, setActiveEmbedModelKey] = useState('')
  const [activatingModelKey, setActivatingModelKey] = useState(null)

  // SLM LoRA Fine-tune state (Gemma 2 2B Base)
  const [isTrainingSLM, setIsTrainingSLM] = useState(false)
  const [slmMetrics, setSlmMetrics] = useState(null)
  const [slmEpochs, setSlmEpochs] = useState(3)
  const [slmRank, setSlmRank] = useState(8)
  const [slmAlpha, setSlmAlpha] = useState(16)

  // RAG Embedding Retrain state
  const [isTrainingEmbed, setIsTrainingEmbed] = useState(false)
  const [embedMetrics, setEmbedMetrics] = useState(null)
  const [embedEpochs, setEmbedEpochs] = useState(5)

  // Intent NER test state
  const [nerInputText, setNerInputText] = useState('Giao cho anh Nam số 0912345678 đến 45 Lê Duẩn 2 ly Bạc xỉu ít đường nhé')
  const [nerResult, setNerResult] = useState(null)
  const [isParsingNER, setIsParsingNER] = useState(false)

  // Sub-tabs in Tab 4: 'registry' | 'experiments' | 'datasets'
  const [modelSubTab, setModelSubTab] = useState('registry')

  // Experiment Tracking & Hyperparameters State
  const [experimentRuns, setExperimentRuns] = useState([])
  const [loadingRuns, setLoadingRuns] = useState(false)
  const [selectedRunIds, setSelectedRunIds] = useState([])
  const [comparisonResult, setComparisonResult] = useState(null)
  const [loadingComparison, setLoadingComparison] = useState(false)

  // Centralized Training Data State
  const [datasetsList, setDatasetsList] = useState([])
  const [loadingDatasets, setLoadingDatasets] = useState(false)
  const [selectedDatasetName, setSelectedDatasetName] = useState('drinkbot-slm-finetune-dataset')
  const [selectedDatasetVersion, setSelectedDatasetVersion] = useState('')
  const [currentDatasetDetail, setCurrentDatasetDetail] = useState(null)
  const [loadingDatasetDetail, setLoadingDatasetDetail] = useState(false)
  const [sampleSearchQuery, setSampleSearchQuery] = useState('')
  const [showAddSampleForm, setShowAddSampleForm] = useState(false)
  const [showSnapshotForm, setShowSnapshotForm] = useState(false)
  const [sampleField1, setSampleField1] = useState('')
  const [sampleField2, setSampleField2] = useState('')
  const [sampleCategory, setSampleCategory] = useState('coffee')
  const [sampleLabel, setSampleLabel] = useState(1.0)
  const [isSubmittingSample, setIsSubmittingSample] = useState(false)
  const [newVersionTag, setNewVersionTag] = useState('')
  const [newVersionDesc, setNewVersionDesc] = useState('')
  const [isSubmittingVersion, setIsSubmittingVersion] = useState(false)

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
      fetchModelRegistry()
      fetchExperimentRuns()
      fetchDatasetsList()
    }
  }, [isOpen, onRefreshTrigger])

  useEffect(() => {
    if (selectedDatasetName) {
      fetchDatasetDetail(selectedDatasetName, selectedDatasetVersion)
    }
  }, [selectedDatasetName, selectedDatasetVersion])

  async function fetchExperimentRuns() {
    setLoadingRuns(true)
    try {
      const data = await api.experimentRuns()
      setExperimentRuns(data.runs || [])
    } catch (err) {
      console.error('Failed to load experiment runs:', err)
    } finally {
      setLoadingRuns(false)
    }
  }

  async function handleCompareRuns() {
    if (selectedRunIds.length < 2) {
      alert('Vui lòng chọn ít nhất 2 runs để so sánh!')
      return
    }
    setLoadingComparison(true)
    try {
      const data = await api.compareRuns(selectedRunIds)
      setComparisonResult(data.comparison || [])
    } catch (err) {
      alert(`Lỗi so sánh thực nghiệm: ${err.message}`)
    } finally {
      setLoadingComparison(false)
    }
  }

  async function fetchDatasetsList() {
    setLoadingDatasets(true)
    try {
      const data = await api.trainingDatasets()
      setDatasetsList(data.datasets || [])
      if (!selectedDatasetName && data.datasets?.length > 0) {
        setSelectedDatasetName(data.datasets[0].name)
      }
    } catch (err) {
      console.error('Failed to load training datasets:', err)
    } finally {
      setLoadingDatasets(false)
    }
  }

  async function fetchDatasetDetail(name, version) {
    if (!name) return
    setLoadingDatasetDetail(true)
    try {
      const data = await api.datasetDetails(name, version)
      setCurrentDatasetDetail(data.dataset || null)
    } catch (err) {
      console.error('Failed to load dataset details:', err)
    } finally {
      setLoadingDatasetDetail(false)
    }
  }

  async function handleAddSample() {
    if (!sampleField1.trim() || !sampleField2.trim()) {
      alert('Vui lòng nhập đầy đủ các trường dữ liệu!')
      return
    }
    setIsSubmittingSample(true)
    try {
      let samplePayload = {}
      if (selectedDatasetName === 'drinkbot-slm-finetune-dataset') {
        samplePayload = {
          user_input: sampleField1.trim(),
          model_output: sampleField2.trim(),
          category: sampleCategory,
          verified: true
        }
      } else {
        samplePayload = {
          query_slang: sampleField1.trim(),
          target_drink_flavor: sampleField2.trim(),
          label: Number(sampleLabel) || 1.0,
          category: sampleCategory
        }
      }
      await api.addDatasetSample(selectedDatasetName, samplePayload)
      setSampleField1('')
      setSampleField2('')
      setShowAddSampleForm(false)
      setFeedbackMsg('✓ Đã thêm mẫu vào tập dữ liệu tập trung thành công!')
      setTimeout(() => setFeedbackMsg(null), 3500)
      await fetchDatasetsList()
      await fetchDatasetDetail(selectedDatasetName, selectedDatasetVersion)
    } catch (err) {
      alert(`Lỗi thêm mẫu: ${err.message}`)
    } finally {
      setIsSubmittingSample(false)
    }
  }

  async function handleCreateVersionSnapshot() {
    if (!newVersionTag.trim()) {
      alert('Vui lòng nhập định danh version (ví dụ: v1.1.0)!')
      return
    }
    setIsSubmittingVersion(true)
    try {
      await api.createDatasetVersion(selectedDatasetName, newVersionTag.trim(), newVersionDesc.trim())
      setSelectedDatasetVersion(newVersionTag.trim())
      setNewVersionTag('')
      setNewVersionDesc('')
      setShowSnapshotForm(false)
      setFeedbackMsg(`✓ Đã tạo snapshot phiên bản ${newVersionTag} thành công!`)
      setTimeout(() => setFeedbackMsg(null), 3500)
      await fetchDatasetsList()
      await fetchDatasetDetail(selectedDatasetName, newVersionTag.trim())
    } catch (err) {
      alert(`Lỗi tạo snapshot version: ${err.message}`)
    } finally {
      setIsSubmittingVersion(false)
    }
  }

  async function fetchModelRegistry() {
    setLoadingModelsList(true)
    try {
      const data = await api.modelRegistry()
      setModelsList(data.models || [])
      setActiveChatModelKey(data.active_chat_model || '')
      setActiveEmbedModelKey(data.active_embedding_model || '')
    } catch (err) {
      console.error('Failed to load model registry:', err)
    } finally {
      setLoadingModelsList(false)
    }
  }

  async function handleActivateModel(modelKey) {
    setActivatingModelKey(modelKey)
    try {
      await api.activateModel(modelKey)
      await fetchModelRegistry()
      setFeedbackMsg(`✓ Đã hot-swap model '${modelKey}' thành công!`)
      setTimeout(() => setFeedbackMsg(null), 3500)
    } catch (err) {
      alert(`Lỗi kích hoạt model: ${err.message}`)
    } finally {
      setActivatingModelKey(null)
    }
  }

  async function handleRunSLMFineTune() {
    setIsTrainingSLM(true)
    setSlmMetrics(null)
    try {
      const res = await api.retrainSLM({
        epochs: Number(slmEpochs),
        r: Number(slmRank),
        lora_alpha: Number(slmAlpha),
      })
      setSlmMetrics(res.metrics)
      await fetchModelRegistry()
      await fetchExperimentRuns()
      setFeedbackMsg('✓ Huấn luyện LoRA thành công! Đã ghi nhận thông số thực nghiệm & Checkpoint.')
      setTimeout(() => setFeedbackMsg(null), 4000)
    } catch (err) {
      alert(`Lỗi huấn luyện SLM: ${err.message}`)
    } finally {
      setIsTrainingSLM(false)
    }
  }

  async function handleRunEmbeddingRetrain() {
    setIsTrainingEmbed(true)
    setEmbedMetrics(null)
    try {
      const res = await api.retrainEmbeddings({
        epochs: Number(embedEpochs),
      })
      setEmbedMetrics(res.metrics)
      await fetchModelRegistry()
      await fetchExperimentRuns()
      setFeedbackMsg('✓ Tái huấn luyện RAG Embedding thành công! Đã ghi nhận thông số thực nghiệm & Adapter.')
      setTimeout(() => setFeedbackMsg(null), 4000)
    } catch (err) {
      alert(`Lỗi tái huấn luyện Embeddings: ${err.message}`)
    } finally {
      setIsTrainingEmbed(false)
    }
  }

  async function handleParseNER() {
    if (!nerInputText.trim()) return
    setIsParsingNER(true)
    try {
      const res = await api.parseNER(nerInputText)
      setNerResult(res.extracted)
    } catch (err) {
      alert(`Lỗi bóc tách thực thể: ${err.message}`)
    } finally {
      setIsParsingNER(false)
    }
  }

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
        <button
          onClick={() => setActiveTab('models')}
          className={`flex-1 py-2.5 px-2 flex items-center justify-center gap-1.5 transition border-b-2 ${
            activeTab === 'models'
              ? 'border-amber-600 text-amber-950 bg-white font-bold'
              : 'border-transparent text-amber-800/80 hover:text-amber-900 hover:bg-amber-100/50'
          }`}
        >
          <span>🤖</span> Models & Retrain
          <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-purple-600 text-white font-bold">
            Gemma 2B
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

      {/* TAB 4: MODEL REGISTRY & RETRAINING */}
      {activeTab === 'models' && (
        <div className="flex-1 overflow-y-auto p-4 space-y-5 bg-gradient-to-b from-white to-amber-50/20 text-left">
          {/* HEADER INTRO */}
          <div className="p-3 bg-gradient-to-r from-purple-50 via-amber-50 to-emerald-50 rounded-xl border border-purple-200 shadow-sm flex items-center justify-between">
            <div>
              <h3 className="text-xs font-bold text-purple-950 flex items-center gap-1.5">
                <span>🤖</span> Model Versioning & Dual Retraining Engine
              </h3>
              <p className="text-[11px] text-purple-800/80 mt-0.5">
                Quản lý Foundation Models, Fine-Tuned SLM LoRA (Gemma 2 2B), và Domain RAG Embeddings.
              </p>
            </div>
            <button
              onClick={fetchModelRegistry}
              disabled={loadingModelsList}
              className="px-2.5 py-1 bg-white hover:bg-purple-100 text-purple-900 border border-purple-200 rounded text-[11px] font-semibold transition"
            >
              {loadingModelsList ? 'Đang tải...' : '↻ Làm mới'}
            </button>
          </div>

          {/* SUB-TABS NAVIGATION: 1) Registry & Pipelines | 2) Experiment Runs | 3) Centralized Data Hub */}
          <div className="flex gap-1.5 p-1 bg-purple-100/70 rounded-xl border border-purple-200 text-xs font-semibold">
            <button
              onClick={() => setModelSubTab('registry')}
              className={`flex-1 py-1.5 px-2 rounded-lg text-center transition flex items-center justify-center gap-1 ${
                modelSubTab === 'registry'
                  ? 'bg-white text-purple-950 font-bold shadow-xs'
                  : 'text-purple-800/80 hover:text-purple-950 hover:bg-white/50'
              }`}
            >
              <span>📦</span> Checkpoints & Retrain
            </button>
            <button
              onClick={() => {
                setModelSubTab('experiments')
                fetchExperimentRuns()
              }}
              className={`flex-1 py-1.5 px-2 rounded-lg text-center transition flex items-center justify-center gap-1 ${
                modelSubTab === 'experiments'
                  ? 'bg-white text-purple-950 font-bold shadow-xs'
                  : 'text-purple-800/80 hover:text-purple-950 hover:bg-white/50'
              }`}
            >
              <span>📊</span> Lịch Sử Thực Nghiệm
              <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-purple-200 text-purple-900 font-mono">
                {experimentRuns.length}
              </span>
            </button>
            <button
              onClick={() => {
                setModelSubTab('datasets')
                fetchDatasetsList()
              }}
              className={`flex-1 py-1.5 px-2 rounded-lg text-center transition flex items-center justify-center gap-1 ${
                modelSubTab === 'datasets'
                  ? 'bg-white text-purple-950 font-bold shadow-xs'
                  : 'text-purple-800/80 hover:text-purple-950 hover:bg-white/50'
              }`}
            >
              <span>📚</span> Quản Lý Dữ Liệu
              <span className="px-1.5 py-0.2 rounded-full text-[10px] bg-emerald-200 text-emerald-900 font-mono">
                {datasetsList.length}
              </span>
            </button>
          </div>

          {/* SUB-TAB 1: CHECKPOINTS & RETRAINING */}
          {modelSubTab === 'registry' && (
            <div className="space-y-4">
              {/* ACTIVE STATUS BANNER */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
            <div className="p-3 bg-white rounded-xl border border-amber-200 shadow-xs">
              <div className="flex items-center justify-between">
                <span className="text-gray-500 text-[10px] font-medium uppercase tracking-wider">Active Chat Model</span>
                <span className="px-1.5 py-0.5 bg-emerald-100 text-emerald-800 text-[10px] font-bold rounded">Live Serving</span>
              </div>
              <div className="mt-1 font-mono font-bold text-amber-950 text-xs truncate">
                {activeChatModelKey || 'ag/gemini-3.8-flash-low'}
              </div>
              <div className="mt-0.5 text-[10px] text-gray-500">
                Được kích hoạt trực tiếp trong Agent Chat
              </div>
            </div>

            <div className="p-3 bg-white rounded-xl border border-amber-200 shadow-xs">
              <div className="flex items-center justify-between">
                <span className="text-gray-500 text-[10px] font-medium uppercase tracking-wider">Active RAG Embedding</span>
                <span className="px-1.5 py-0.5 bg-purple-100 text-purple-800 text-[10px] font-bold rounded">Projection Adapter</span>
              </div>
              <div className="mt-1 font-mono font-bold text-purple-950 text-xs truncate">
                {activeEmbedModelKey || 'all-MiniLM-L6-v2'}
              </div>
              <div className="mt-0.5 text-[10px] text-gray-500">
                Không gian vector ngữ nghĩa 384 chiều
              </div>
            </div>
          </div>

          {/* MODEL REGISTRY TABLE */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <h4 className="text-xs font-bold text-gray-900 flex items-center gap-1.5">
                <span>📦</span> Danh mục Model Versions (Langfuse Tracked)
              </h4>
              <span className="text-[10px] text-gray-500 font-mono">{modelsList.length} checkpoints</span>
            </div>

            <div className="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-xs divide-y divide-gray-100">
              {modelsList.map((m) => {
                const key = `${m.name}@${m.version}`
                const isActive = m.is_active_chat || m.is_active_embedding
                const isActivating = activatingModelKey === key
                return (
                  <div key={key} className={`p-3 text-xs transition ${isActive ? 'bg-emerald-50/40' : 'hover:bg-gray-50'}`}>
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <div className="flex items-center gap-1.5 flex-wrap">
                          <span className="font-mono font-bold text-gray-950">{m.name}</span>
                          <span className="font-mono text-[10px] px-1.5 py-0.5 bg-gray-100 rounded text-gray-700 border border-gray-200">
                            {m.version}
                          </span>
                          <span className={`text-[9px] px-1.5 py-0.5 rounded font-bold uppercase ${
                            m.model_type === 'foundation' ? 'bg-blue-100 text-blue-800' :
                            m.model_type === 'fine-tuned-slm' ? 'bg-purple-100 text-purple-800' :
                            'bg-emerald-100 text-emerald-800'
                          }`}>
                            {m.model_type}
                          </span>
                          {isActive && (
                            <span className="text-[9px] px-1.5 py-0.5 bg-emerald-600 text-white rounded font-bold">
                              ✓ ACTIVE
                            </span>
                          )}
                        </div>
                        <div className="text-[11px] text-gray-600 mt-1">
                          {m.description}
                        </div>
                        <div className="text-[10px] text-gray-400 mt-0.5 font-mono flex items-center gap-2">
                          <span>Base: <strong>{m.base_model}</strong></span>
                          <span>•</span>
                          <span>Hash: {m.sha256_hash}</span>
                          {m.eval_pass_rate != null && (
                            <>
                              <span>•</span>
                              <span className="text-emerald-700 font-bold">Eval: {m.eval_pass_rate}%</span>
                            </>
                          )}
                        </div>
                      </div>

                      <div className="flex items-center gap-1.5 flex-shrink-0">
                        {isActive ? (
                          <span className="text-[10px] font-bold text-emerald-700 px-2 py-1 bg-emerald-100/80 rounded-md">
                            Đang phục vụ
                          </span>
                        ) : (
                          <button
                            onClick={() => handleActivateModel(key)}
                            disabled={isActivating}
                            className="px-2.5 py-1 bg-amber-600 hover:bg-amber-700 text-white rounded text-[11px] font-bold transition shadow-xs disabled:opacity-50"
                          >
                            {isActivating ? 'Đang bật...' : '⚡ Hot-Swap'}
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>

          {/* PIPELINE 1: SLM FINE-TUNING (GEMMA 2 2B) */}
          <div className="p-3.5 bg-purple-50/60 rounded-xl border border-purple-200 space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-xs font-bold text-purple-950 flex items-center gap-1.5">
                  <span>🚀</span> Pipeline 1: SLM LoRA Fine-Tuning (Gemma 2 2B Base)
                </h4>
                <p className="text-[11px] text-purple-900/80 mt-0.5">
                  Huấn luyện checkpoint <strong>drinkbot-slm-lora-v1.0</strong> từ base <code>google/gemma-2-2b-it</code> với Gemma Chat Template & Eval Gate.
                </p>
              </div>
              <span className="text-[10px] font-mono px-2 py-0.5 bg-purple-200 text-purple-900 rounded font-bold">
                LoRA r=8, α=16
              </span>
            </div>

            {/* HYPERPARAMS */}
            <div className="grid grid-cols-3 gap-2 text-xs">
              <div className="bg-white p-2 rounded-lg border border-purple-100">
                <span className="text-[10px] text-gray-500 block">Epochs</span>
                <input
                  type="number"
                  min="1"
                  max="10"
                  value={slmEpochs}
                  onChange={(e) => setSlmEpochs(e.target.value)}
                  className="w-full font-mono text-xs font-bold text-purple-950 bg-transparent outline-none"
                />
              </div>
              <div className="bg-white p-2 rounded-lg border border-purple-100">
                <span className="text-[10px] text-gray-500 block">Rank (r)</span>
                <input
                  type="number"
                  value={slmRank}
                  onChange={(e) => setSlmRank(e.target.value)}
                  className="w-full font-mono text-xs font-bold text-purple-950 bg-transparent outline-none"
                />
              </div>
              <div className="bg-white p-2 rounded-lg border border-purple-100">
                <span className="text-[10px] text-gray-500 block">LoRA Alpha</span>
                <input
                  type="number"
                  value={slmAlpha}
                  onChange={(e) => setSlmAlpha(e.target.value)}
                  className="w-full font-mono text-xs font-bold text-purple-950 bg-transparent outline-none"
                />
              </div>
            </div>

            <button
              onClick={handleRunSLMFineTune}
              disabled={isTrainingSLM}
              className="w-full py-2 bg-gradient-to-r from-purple-700 to-indigo-700 hover:from-purple-800 hover:to-indigo-800 text-white rounded-lg text-xs font-bold transition shadow-sm flex items-center justify-center gap-2 disabled:opacity-50"
            >
              {isTrainingSLM ? (
                <>
                  <span className="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                  Đang chạy Gemma 2B LoRA Gradient Descent & Eval Gate...
                </>
              ) : (
                '▶ Bắt Đầu Pipeline Fine-Tune LoRA (drinkbot-slm-lora-v1.0)'
              )}
            </button>

            {/* METRICS RESULT CARD */}
            {slmMetrics && (
              <div className="p-3 bg-white rounded-lg border border-purple-200 text-xs space-y-1.5 animate-fadeIn">
                <div className="flex items-center justify-between text-[11px] font-bold text-purple-950">
                  <span>✓ Checkpoint Huấn Luyện Thành Công!</span>
                  <span className="text-emerald-700 font-mono">Eval: {slmMetrics.eval_pass_rate}%</span>
                </div>
                <div className="text-[11px] text-gray-700 font-mono grid grid-cols-2 gap-1">
                  <span>Initial Loss: <strong>{slmMetrics.initial_loss}</strong></span>
                  <span>Final Loss: <strong className="text-emerald-600">{slmMetrics.final_loss}</strong></span>
                  <span>Duration: {slmMetrics.duration_seconds}s</span>
                  <span>Dataset: {slmMetrics.total_samples} traces</span>
                </div>
                <div className="text-[10px] text-gray-500 font-mono truncate">
                  Output: {slmMetrics.checkpoint_path}
                </div>
              </div>
            )}
          </div>

          {/* PIPELINE 2: DOMAIN RAG EMBEDDING RETRAINING */}
          <div className="p-3.5 bg-emerald-50/60 rounded-xl border border-emerald-200 space-y-3">
            <div className="flex items-center justify-between">
              <div>
                <h4 className="text-xs font-bold text-emerald-950 flex items-center gap-1.5">
                  <span>⚡</span> Pipeline 2: Domain RAG Embedding Retraining (384d)
                </h4>
                <p className="text-[11px] text-emerald-900/80 mt-0.5">
                  Tái huấn luyện Adapter trên 35+ cặp từ lóng F&B Việt Nam (bạc xỉu, say cà phê, giải ngấy, đẹp da, keto...).
                </p>
              </div>
              <span className="text-[10px] font-mono px-2 py-0.5 bg-emerald-200 text-emerald-900 rounded font-bold">
                Contrastive Loss
              </span>
            </div>

            <div className="flex items-center gap-2">
              <div className="bg-white p-2 rounded-lg border border-emerald-100 flex-1">
                <span className="text-[10px] text-gray-500 block">Số Epochs</span>
                <input
                  type="number"
                  min="1"
                  max="15"
                  value={embedEpochs}
                  onChange={(e) => setEmbedEpochs(e.target.value)}
                  className="w-full font-mono text-xs font-bold text-emerald-950 bg-transparent outline-none"
                />
              </div>
              <button
                onClick={handleRunEmbeddingRetrain}
                disabled={isTrainingEmbed}
                className="flex-2 py-2 px-3 bg-emerald-700 hover:bg-emerald-800 text-white rounded-lg text-xs font-bold transition shadow-sm flex items-center justify-center gap-2 disabled:opacity-50"
              >
                {isTrainingEmbed ? (
                  <>
                    <span className="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                    Đang huấn luyện...
                  </>
                ) : (
                  '⚡ Tái Huấn Luyện Adapter & Hot-Reload'
                )}
              </button>
            </div>

            {embedMetrics && (
              <div className="p-3 bg-white rounded-lg border border-emerald-200 text-xs space-y-1 animate-fadeIn">
                <div className="flex items-center justify-between font-bold text-emerald-950">
                  <span>✓ Checkpoint drinkbot-embed-adapted-v1.0</span>
                  <span className="text-emerald-600">+{embedMetrics.accuracy_improvement}% Độ chính xác</span>
                </div>
                <div className="text-[11px] text-gray-600 font-mono">
                  Loss: {embedMetrics.initial_loss} → <strong className="text-emerald-700">{embedMetrics.final_loss}</strong> ({embedMetrics.duration_seconds}s)
                </div>
              </div>
            )}
          </div>

          {/* TOOL 3: INTENT & NER EXTRACTION (LEVEL 3) */}
          <div className="p-3.5 bg-amber-50/60 rounded-xl border border-amber-200 space-y-2.5">
            <h4 className="text-xs font-bold text-amber-950 flex items-center gap-1.5">
              <span>🎯</span> Intent & Entity Extraction (Tên, SĐT, Địa chỉ)
            </h4>
            <p className="text-[11px] text-amber-900/80">
              Kiểm tra khả năng bóc tách thông tin giao hàng tự động trực tiếp từ câu chat của khách hàng:
            </p>
            <div className="flex gap-2">
              <input
                type="text"
                value={nerInputText}
                onChange={(e) => setNerInputText(e.target.value)}
                placeholder="Nhập tin nhắn đặt hàng có địa chỉ..."
                className="flex-1 px-2.5 py-1.5 bg-white border border-amber-300 rounded-lg text-xs text-gray-900 outline-none focus:ring-1 focus:ring-amber-500"
              />
              <button
                onClick={handleParseNER}
                disabled={isParsingNER}
                className="px-3 py-1.5 bg-amber-800 hover:bg-amber-900 text-white rounded-lg text-xs font-bold transition disabled:opacity-50"
              >
                {isParsingNER ? 'Đang trích xuất...' : 'Bóc tách'}
              </button>
            </div>

            {nerResult && (
              <div className="p-2.5 bg-white rounded-lg border border-amber-200 text-xs space-y-1 animate-fadeIn font-mono">
                <div className="text-[11px] font-bold text-amber-950">Kết quả bóc tách (Confidence: {nerResult.confidence * 100}%):</div>
                <div className="text-gray-700">👤 Khách hàng: <strong className="text-amber-900">{nerResult.customer_name || 'N/A'}</strong></div>
                <div className="text-gray-700">📞 SĐT: <strong className="text-emerald-700">{nerResult.phone_number || 'N/A'}</strong></div>
                <div className="text-gray-700">📍 Địa chỉ: <strong className="text-indigo-700">{nerResult.shipping_address || 'N/A'}</strong></div>
                {nerResult.items && nerResult.items.length > 0 && (
                  <div className="text-gray-700">
                    🥤 Món: {nerResult.items.map(it => `${it.quantity}x ${it.item}`).join(', ')}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}

          {/* SUB-TAB 2: EXPERIMENT RUNS (LƯU THÔNG SỐ MODEL & COMPARISON) */}
          {modelSubTab === 'experiments' && (
            <div className="space-y-4">
              {/* INTRO & ACTIONS */}
              <div className="p-3 bg-white rounded-xl border border-purple-200 shadow-xs space-y-2">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-xs font-bold text-purple-950 flex items-center gap-1.5">
                      <span>📊</span> Lịch Sử Thực Nghiệm & Lưu Trữ Hyperparameters
                    </h4>
                    <p className="text-[11px] text-gray-600 mt-0.5">
                      MLOps Level 2: Ghi nhận đầy đủ thông số r, α, LR, Epochs, Loss curve, Phần cứng GPU RTX 3060 vs CPU, và Eval Gate.
                    </p>
                  </div>
                  <button
                    onClick={fetchExperimentRuns}
                    disabled={loadingRuns}
                    className="px-2.5 py-1 bg-purple-50 hover:bg-purple-100 text-purple-900 border border-purple-200 rounded text-[11px] font-semibold transition"
                  >
                    {loadingRuns ? 'Đang tải...' : '↻ Làm mới'}
                  </button>
                </div>

                {/* COMPARE ACTION BAR */}
                <div className="flex items-center justify-between pt-2 border-t border-gray-100">
                  <div className="text-[11px] text-gray-500">
                    Đã chọn <strong className="text-purple-900">{selectedRunIds.length}</strong> runs để so sánh
                  </div>
                  <div className="flex gap-2">
                    {selectedRunIds.length > 0 && (
                      <button
                        onClick={() => setSelectedRunIds([])}
                        className="text-[11px] text-gray-500 hover:text-gray-800 underline"
                      >
                        Bỏ chọn
                      </button>
                    )}
                    <button
                      onClick={handleCompareRuns}
                      disabled={selectedRunIds.length < 2 || loadingComparison}
                      className="px-3 py-1 bg-purple-700 hover:bg-purple-800 text-white rounded text-xs font-bold transition shadow-xs disabled:opacity-40"
                    >
                      {loadingComparison ? 'Đang so sánh...' : `⚡ So sánh ${selectedRunIds.length >= 2 ? selectedRunIds.length : ''} Runs`}
                    </button>
                  </div>
                </div>
              </div>

              {/* SIDE-BY-SIDE COMPARISON MODAL/BOX */}
              {comparisonResult && (
                <div className="p-3.5 bg-gradient-to-r from-purple-50 via-white to-amber-50 rounded-xl border-2 border-purple-300 shadow-md space-y-3 animate-fadeIn">
                  <div className="flex items-center justify-between">
                    <h5 className="text-xs font-bold text-purple-950 flex items-center gap-1.5">
                      <span>⚖️</span> Bảng So Sánh Thực Nghiệm ({comparisonResult.length} runs)
                    </h5>
                    <button
                      onClick={() => setComparisonResult(null)}
                      className="text-gray-400 hover:text-gray-700 font-bold text-sm px-1.5"
                    >
                      ✕
                    </button>
                  </div>

                  <div className="overflow-x-auto">
                    <table className="w-full text-[11px] border-collapse bg-white rounded-lg border border-gray-200 overflow-hidden">
                      <thead>
                        <tr className="bg-purple-900 text-white text-left font-semibold">
                          <th className="p-2 border-b border-purple-800">Thông Số / Metric</th>
                          {comparisonResult.map((c) => (
                            <th key={c.run_id} className="p-2 border-b border-purple-800 font-mono">
                              {c.run_id}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200">
                        <tr>
                          <td className="p-2 font-semibold bg-gray-50">Model Checkpoint</td>
                          {comparisonResult.map((c) => (
                            <td key={c.run_id} className="p-2 font-mono font-bold text-purple-950">
                              {c.model_name}
                            </td>
                          ))}
                        </tr>
                        <tr>
                          <td className="p-2 font-semibold bg-gray-50">Pipeline Type</td>
                          {comparisonResult.map((c) => (
                            <td key={c.run_id} className="p-2 font-mono text-[10px]">
                              {c.pipeline_type}
                            </td>
                          ))}
                        </tr>
                        <tr>
                          <td className="p-2 font-semibold bg-gray-50">Base Model</td>
                          {comparisonResult.map((c) => (
                            <td key={c.run_id} className="p-2 font-mono text-gray-600">
                              {c.base_model}
                            </td>
                          ))}
                        </tr>
                        <tr>
                          <td className="p-2 font-semibold bg-gray-50">LoRA Rank (r) / Alpha</td>
                          {comparisonResult.map((c) => (
                            <td key={c.run_id} className="p-2 font-mono text-amber-900 font-bold">
                              r={c.hyperparameters?.r ?? 'N/A'}, α={c.hyperparameters?.lora_alpha ?? 'N/A'}
                            </td>
                          ))}
                        </tr>
                        <tr>
                          <td className="p-2 font-semibold bg-gray-50">Epochs / Batch Size</td>
                          {comparisonResult.map((c) => (
                            <td key={c.run_id} className="p-2 font-mono">
                              {c.hyperparameters?.epochs ?? 'N/A'} eps / batch {c.hyperparameters?.batch_size ?? 'N/A'}
                            </td>
                          ))}
                        </tr>
                        <tr>
                          <td className="p-2 font-semibold bg-gray-50">Phần cứng (Hardware)</td>
                          {comparisonResult.map((c) => (
                            <td key={c.run_id} className="p-2 font-mono text-[10px] text-emerald-800">
                              {c.hardware?.device_name || 'GPU RTX 3060'} ({c.hardware?.vram_total_gb || 12}GB)
                            </td>
                          ))}
                        </tr>
                        <tr>
                          <td className="p-2 font-semibold bg-gray-50">Loss Ban Đầu → Cuối</td>
                          {comparisonResult.map((c) => (
                            <td key={c.run_id} className="p-2 font-mono">
                              <span className="text-gray-500">{c.initial_loss}</span> → <strong className="text-emerald-700">{c.final_loss}</strong>
                            </td>
                          ))}
                        </tr>
                        <tr>
                          <td className="p-2 font-semibold bg-gray-50">Eval Gate Pass Rate</td>
                          {comparisonResult.map((c) => (
                            <td key={c.run_id} className="p-2 font-bold text-emerald-700">
                              {c.eval_metrics?.overall_pass_rate != null ? `${c.eval_metrics.overall_pass_rate}%` : 'N/A'}
                            </td>
                          ))}
                        </tr>
                        <tr>
                          <td className="p-2 font-semibold bg-gray-50">Data Lineage</td>
                          {comparisonResult.map((c) => (
                            <td key={c.run_id} className="p-2 text-[10px] font-mono text-gray-600">
                              {c.dataset_lineage?.dataset_name || 'N/A'}@{c.dataset_lineage?.version || 'N/A'} ({c.dataset_lineage?.sample_count} mẫu)
                            </td>
                          ))}
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* RUNS LIST */}
              <div className="space-y-2.5">
                {experimentRuns.length === 0 ? (
                  <div className="p-6 text-center text-gray-500 bg-white rounded-xl border border-gray-200 text-xs">
                    Chưa có lịch sử thực nghiệm nào được ghi nhận.
                  </div>
                ) : (
                  experimentRuns.map((run) => {
                    const isSelected = selectedRunIds.includes(run.run_id)
                    const isSlm = run.pipeline_type === 'slm_lora_finetune'
                    return (
                      <div
                        key={run.run_id}
                        className={`p-3.5 bg-white rounded-xl border transition shadow-xs space-y-2 ${
                          isSelected ? 'border-purple-500 ring-1 ring-purple-400 bg-purple-50/20' : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        {/* HEADER: Checkbox, Run ID, Status, Pipeline Badge */}
                        <div className="flex items-start justify-between gap-2">
                          <div className="flex items-center gap-2">
                            <input
                              type="checkbox"
                              checked={isSelected}
                              onChange={(e) => {
                                if (e.target.checked) {
                                  setSelectedRunIds([...selectedRunIds, run.run_id])
                                } else {
                                  setSelectedRunIds(selectedRunIds.filter((id) => id !== run.run_id))
                                }
                              }}
                              className="w-4 h-4 text-purple-600 rounded border-gray-300 focus:ring-purple-500"
                            />
                            <div>
                              <div className="flex items-center gap-1.5 flex-wrap">
                                <span className="font-mono font-bold text-gray-950 text-xs">{run.run_id}</span>
                                <span className={`text-[9px] px-1.5 py-0.5 rounded font-bold uppercase ${
                                  isSlm ? 'bg-purple-100 text-purple-800' : 'bg-emerald-100 text-emerald-800'
                                }`}>
                                  {isSlm ? 'SLM LoRA' : 'RAG Adapter'}
                                </span>
                                <span className="text-[9px] px-1.5 py-0.5 rounded font-bold bg-emerald-100 text-emerald-800">
                                  ✓ {run.status}
                                </span>
                              </div>
                              <div className="text-[10px] text-gray-500 mt-0.5 font-mono">
                                Target: <strong className="text-gray-800">{run.model_name}</strong> • Base: {run.base_model}
                              </div>
                            </div>
                          </div>

                          <div className="text-right text-[10px] text-gray-400 font-mono">
                            <div>{run.created_at ? new Date(run.created_at).toLocaleTimeString() : ''}</div>
                            {run.duration_seconds && <div>⏱️ {run.duration_seconds}s</div>}
                          </div>
                        </div>

                        {/* HARDWARE BANNER */}
                        <div className="p-1.5 bg-gray-50 rounded-lg border border-gray-200 flex items-center justify-between text-[10px] font-mono text-gray-700">
                          <div className="flex items-center gap-1">
                            <span>🖥️</span>
                            <strong>{run.hardware?.device_name || 'NVIDIA GeForce RTX 3060'}</strong>
                          </div>
                          <span>VRAM: {run.hardware?.vram_total_gb || 12}GB (Utilization: {run.hardware?.vram_utilization_pct || 28}%)</span>
                        </div>

                        {/* HYPERPARAMETERS GRID */}
                        <div className="grid grid-cols-2 sm:grid-cols-4 gap-1.5 text-[11px] font-mono">
                          <div className="p-1.5 bg-purple-50/50 rounded border border-purple-100">
                            <span className="text-[9px] text-gray-500 block">LoRA Rank (r)</span>
                            <strong className="text-purple-950">{run.hyperparameters?.r ?? 'N/A'}</strong>
                          </div>
                          <div className="p-1.5 bg-purple-50/50 rounded border border-purple-100">
                            <span className="text-[9px] text-gray-500 block">Alpha (α)</span>
                            <strong className="text-purple-950">{run.hyperparameters?.lora_alpha ?? 'N/A'}</strong>
                          </div>
                          <div className="p-1.5 bg-purple-50/50 rounded border border-purple-100">
                            <span className="text-[9px] text-gray-500 block">Learning Rate</span>
                            <strong className="text-purple-950">{run.hyperparameters?.learning_rate ?? '0.0002'}</strong>
                          </div>
                          <div className="p-1.5 bg-purple-50/50 rounded border border-purple-100">
                            <span className="text-[9px] text-gray-500 block">Epochs / Batch</span>
                            <strong className="text-purple-950">{run.hyperparameters?.epochs ?? '3'} eps / {run.hyperparameters?.batch_size ?? '2'} bsz</strong>
                          </div>
                        </div>

                        {/* LOSS TRAJECTORY & EVAL METRICS */}
                        <div className="flex items-center justify-between pt-1 text-[11px] font-mono border-t border-gray-100">
                          <div className="flex items-center gap-1.5">
                            <span className="text-gray-500 text-[10px]">Loss:</span>
                            <span className="text-gray-600">{run.initial_loss}</span>
                            <span>→</span>
                            <strong className="text-emerald-700">{run.final_loss}</strong>
                          </div>
                          {run.eval_metrics?.overall_pass_rate != null && (
                            <div className="flex items-center gap-1">
                              <span className="text-gray-500 text-[10px]">Eval Gate:</span>
                              <span className="px-1.5 py-0.5 bg-emerald-100 text-emerald-800 rounded font-bold">
                                {run.eval_metrics.overall_pass_rate}% Pass
                              </span>
                            </div>
                          )}
                        </div>

                        {/* STEP LOSS CURVE PILLS */}
                        {run.loss_history && run.loss_history.length > 0 && (
                          <div className="flex items-center gap-1 overflow-x-auto text-[9px] font-mono text-gray-600 pt-0.5">
                            <span className="text-gray-400">Steps:</span>
                            {run.loss_history.map((step, idx) => (
                              <span key={idx} className="px-1.5 py-0.5 bg-gray-100 rounded border border-gray-200 whitespace-nowrap">
                                Ep {step.epoch}: <strong>{step.loss}</strong>
                              </span>
                            ))}
                          </div>
                        )}

                        {/* DATASET LINEAGE FOOTER */}
                        {run.dataset_lineage && (
                          <div className="text-[10px] text-gray-500 font-mono pt-1 border-t border-dashed border-gray-200 flex items-center justify-between flex-wrap gap-1">
                            <div>
                              📚 Dataset Lineage: <strong className="text-purple-900">{run.dataset_lineage.dataset_name}</strong>@{run.dataset_lineage.version}
                            </div>
                            <div>
                              {run.dataset_lineage.sample_count} mẫu • Hash: {run.dataset_lineage.sha256_hash}
                            </div>
                          </div>
                        )}
                      </div>
                    )
                  })
                )}
              </div>
            </div>
          )}

          {/* SUB-TAB 3: CENTRALIZED TRAINING DATA HUB (QUẢN LÝ DỮ LIỆU TẬP TRUNG) */}
          {modelSubTab === 'datasets' && (
            <div className="space-y-4">
              {/* INTRO & DATASET PICKER */}
              <div className="p-3 bg-white rounded-xl border border-emerald-200 shadow-xs space-y-3">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="text-xs font-bold text-emerald-950 flex items-center gap-1.5">
                      <span>📚</span> Trung Tâm Dữ Liệu Huấn Luyện Tập Trung (Data Hub)
                    </h4>
                    <p className="text-[11px] text-gray-600 mt-0.5">
                      Quản lý mẫu dữ liệu, đánh nhãn (annotation), snapshot các version (v1.0, v1.1...), và liên kết Data Lineage đến model checkpoints.
                    </p>
                  </div>
                  <button
                    onClick={fetchDatasetsList}
                    disabled={loadingDatasets}
                    className="px-2.5 py-1 bg-emerald-50 hover:bg-emerald-100 text-emerald-900 border border-emerald-200 rounded text-[11px] font-semibold transition"
                  >
                    {loadingDatasets ? 'Đang tải...' : '↻ Làm mới'}
                  </button>
                </div>

                {/* DATASET SELECTOR PILLS */}
                <div className="flex gap-2">
                  {datasetsList.map((ds) => (
                    <button
                      key={ds.name}
                      onClick={() => {
                        setSelectedDatasetName(ds.name)
                        setSelectedDatasetVersion('')
                      }}
                      className={`flex-1 p-2.5 rounded-lg border text-left transition ${
                        selectedDatasetName === ds.name
                          ? 'border-emerald-600 bg-emerald-50/50 shadow-xs'
                          : 'border-gray-200 hover:border-gray-300 bg-white'
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-mono font-bold text-xs text-gray-900">{ds.name}</span>
                        <span className="text-[10px] px-1.5 py-0.2 bg-emerald-100 text-emerald-800 rounded font-mono font-bold">
                          {ds.current_version}
                        </span>
                      </div>
                      <div className="text-[10px] text-gray-500 mt-1 flex items-center justify-between">
                        <span>{ds.dataset_type === 'slm_dialogues' ? 'Mẫu hội thoại SLM' : 'Cặp từ lóng RAG'}</span>
                        <strong className="text-emerald-900">{ds.sample_count} mẫu</strong>
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              {/* ACTIVE DATASET DETAIL CARD */}
              {currentDatasetDetail && (
                <div className="p-3.5 bg-white rounded-xl border border-gray-200 shadow-xs space-y-3">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <div className="flex items-center gap-2">
                        <h5 className="font-mono font-bold text-gray-950 text-xs">
                          {currentDatasetDetail.name}
                        </h5>
                        <span className="text-[10px] px-2 py-0.5 bg-emerald-100 text-emerald-900 rounded-full font-mono font-bold">
                          Version: {selectedDatasetVersion || currentDatasetDetail.current_version}
                        </span>
                      </div>
                      <p className="text-[11px] text-gray-600 mt-1">
                        {currentDatasetDetail.description}
                      </p>
                    </div>
                    <div className="text-right text-[10px] font-mono text-gray-400">
                      <div>Tổng: <strong className="text-emerald-800 text-xs">{currentDatasetDetail.sample_count}</strong> mẫu</div>
                      <div>Hash: {currentDatasetDetail.sha256_hash}</div>
                    </div>
                  </div>

                  {/* VERSION SELECTOR PILLS */}
                  {currentDatasetDetail.versions_available && currentDatasetDetail.versions_available.length > 1 && (
                    <div className="flex items-center gap-1.5 text-[11px] font-mono">
                      <span className="text-gray-500">Lịch sử version:</span>
                      {currentDatasetDetail.versions_available.map((v) => (
                        <button
                          key={v}
                          onClick={() => setSelectedDatasetVersion(v)}
                          className={`px-2 py-0.5 rounded text-[10px] border font-bold transition ${
                            (selectedDatasetVersion || currentDatasetDetail.current_version) === v
                              ? 'bg-emerald-700 text-white border-emerald-700'
                              : 'bg-gray-100 text-gray-700 border-gray-300 hover:bg-gray-200'
                          }`}
                        >
                          {v}
                        </button>
                      ))}
                    </div>
                  )}

                  {/* ACTION BUTTONS */}
                  <div className="flex gap-2 pt-1 border-t border-gray-100">
                    <button
                      onClick={() => {
                        setShowAddSampleForm(!showAddSampleForm)
                        setShowSnapshotForm(false)
                      }}
                      className="flex-1 py-1.5 px-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-xs font-bold transition shadow-xs flex items-center justify-center gap-1"
                    >
                      <span>+</span> Thêm mẫu huấn luyện (Annotation)
                    </button>
                    <button
                      onClick={() => {
                        setShowSnapshotForm(!showSnapshotForm)
                        setShowAddSampleForm(false)
                      }}
                      className="flex-1 py-1.5 px-3 bg-purple-700 hover:bg-purple-800 text-white rounded-lg text-xs font-bold transition shadow-xs flex items-center justify-center gap-1"
                    >
                      <span>🏷️</span> Snapshot Version Mới
                    </button>
                  </div>

                  {/* FORM 1: ADD SAMPLE */}
                  {showAddSampleForm && (
                    <div className="p-3 bg-emerald-50/60 rounded-xl border border-emerald-200 space-y-2.5 animate-fadeIn text-xs">
                      <div className="font-bold text-emerald-950 flex items-center justify-between">
                        <span>✍️ Thêm Mẫu Mới Vào {selectedDatasetName}</span>
                        <button
                          onClick={() => setShowAddSampleForm(false)}
                          className="text-gray-400 hover:text-gray-600"
                        >
                          ✕
                        </button>
                      </div>

                      <div className="space-y-2">
                        <div>
                          <label className="text-[10px] font-semibold text-gray-600 block mb-0.5">
                            {selectedDatasetName === 'drinkbot-slm-finetune-dataset'
                              ? 'Câu hỏi / Yêu cầu của khách (User Prompt):'
                              : 'Từ lóng / Khẩu vị tiếng Việt (Vietnamese F&B Slang):'}
                          </label>
                          <textarea
                            rows="2"
                            value={sampleField1}
                            onChange={(e) => setSampleField1(e.target.value)}
                            placeholder={
                              selectedDatasetName === 'drinkbot-slm-finetune-dataset'
                                ? 'Ví dụ: Cho 1 ly Bạc xỉu ít ngọt nhiều béo nha em'
                                : 'Ví dụ: Bạc xỉu sài gòn thơm béo ngậy'
                            }
                            className="w-full p-2 bg-white border border-emerald-300 rounded-lg text-xs outline-none focus:ring-1 focus:ring-emerald-500"
                          />
                        </div>

                        <div>
                          <label className="text-[10px] font-semibold text-gray-600 block mb-0.5">
                            {selectedDatasetName === 'drinkbot-slm-finetune-dataset'
                              ? 'Câu trả lời chuẩn mực của Barista (Model Barista Output):'
                              : 'Món nước & Sắc thái hương vị mục tiêu (Target Drink & Flavor):'}
                          </label>
                          <textarea
                            rows="2"
                            value={sampleField2}
                            onChange={(e) => setSampleField2(e.target.value)}
                            placeholder={
                              selectedDatasetName === 'drinkbot-slm-finetune-dataset'
                                ? 'Ví dụ: Dạ quán em có Caramel Latte ngọt béo nhiều sữa tươi thơm nồng sốt caramel chuẩn vị bạc xỉu cho mình ạ!'
                                : 'Ví dụ: Caramel Latte béo ngọt nhiều sữa ít đắng'
                            }
                            className="w-full p-2 bg-white border border-emerald-300 rounded-lg text-xs outline-none focus:ring-1 focus:ring-emerald-500"
                          />
                        </div>

                        <div className="grid grid-cols-2 gap-2">
                          <div>
                            <label className="text-[10px] font-semibold text-gray-600 block mb-0.5">Phân loại (Category):</label>
                            <input
                              type="text"
                              value={sampleCategory}
                              onChange={(e) => setSampleCategory(e.target.value)}
                              placeholder="coffee / tea / allergy / mood"
                              className="w-full p-1.5 bg-white border border-emerald-300 rounded-lg text-xs outline-none"
                            />
                          </div>
                          {selectedDatasetName !== 'drinkbot-slm-finetune-dataset' && (
                            <div>
                              <label className="text-[10px] font-semibold text-gray-600 block mb-0.5">Độ tương đồng (Label):</label>
                              <select
                                value={sampleLabel}
                                onChange={(e) => setSampleLabel(e.target.value)}
                                className="w-full p-1.5 bg-white border border-emerald-300 rounded-lg text-xs outline-none"
                              >
                                <option value="1.0">+1.0 (Cực kỳ tương đồng)</option>
                                <option value="0.8">+0.8 (Tương đồng cao)</option>
                                <option value="-0.8">-0.8 (Đối lập / Negative)</option>
                                <option value="-1.0">-1.0 (Trái ngược hoàn toàn)</option>
                              </select>
                            </div>
                          )}
                        </div>

                        <div className="flex justify-end gap-2 pt-1">
                          <button
                            onClick={() => setShowAddSampleForm(false)}
                            className="px-3 py-1 text-gray-600 hover:text-gray-800 text-xs"
                          >
                            Hủy
                          </button>
                          <button
                            onClick={handleAddSample}
                            disabled={isSubmittingSample}
                            className="px-4 py-1.5 bg-emerald-700 hover:bg-emerald-800 text-white rounded-lg text-xs font-bold transition shadow-xs disabled:opacity-50"
                          >
                            {isSubmittingSample ? 'Đang lưu...' : 'Lưu mẫu vào tập dữ liệu'}
                          </button>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* FORM 2: SNAPSHOT VERSION */}
                  {showSnapshotForm && (
                    <div className="p-3 bg-purple-50/60 rounded-xl border border-purple-200 space-y-2.5 animate-fadeIn text-xs">
                      <div className="font-bold text-purple-950 flex items-center justify-between">
                        <span>🏷️ Tạo Snapshot Phiên Bản Mới (Data Versioning)</span>
                        <button
                          onClick={() => setShowSnapshotForm(false)}
                          className="text-gray-400 hover:text-gray-600"
                        >
                          ✕
                        </button>
                      </div>

                      <div className="space-y-2">
                        <div>
                          <label className="text-[10px] font-semibold text-gray-600 block mb-0.5">
                            Tên phiên bản mới (Version Tag):
                          </label>
                          <input
                            type="text"
                            value={newVersionTag}
                            onChange={(e) => setNewVersionTag(e.target.value)}
                            placeholder="Ví dụ: v1.1.0"
                            className="w-full p-1.5 bg-white border border-purple-300 rounded-lg text-xs outline-none font-mono focus:ring-1 focus:ring-purple-500"
                          />
                        </div>

                        <div>
                          <label className="text-[10px] font-semibold text-gray-600 block mb-0.5">
                            Mô tả thay đổi (Changelog):
                          </label>
                          <input
                            type="text"
                            value={newVersionDesc}
                            onChange={(e) => setNewVersionDesc(e.target.value)}
                            placeholder="Ví dụ: Bổ sung 15 mẫu trà đào cam sả và xử lý dị ứng sữa hạt"
                            className="w-full p-1.5 bg-white border border-purple-300 rounded-lg text-xs outline-none focus:ring-1 focus:ring-purple-500"
                          />
                        </div>

                        <div className="flex justify-end gap-2 pt-1">
                          <button
                            onClick={() => setShowSnapshotForm(false)}
                            className="px-3 py-1 text-gray-600 hover:text-gray-800 text-xs"
                          >
                            Hủy
                          </button>
                          <button
                            onClick={handleCreateVersionSnapshot}
                            disabled={isSubmittingVersion}
                            className="px-4 py-1.5 bg-purple-800 hover:bg-purple-900 text-white rounded-lg text-xs font-bold transition shadow-xs disabled:opacity-50"
                          >
                            {isSubmittingVersion ? 'Đang snapshot...' : 'Khóa Version Snapshot'}
                          </button>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* SAMPLES BROWSER */}
                  <div className="space-y-2 pt-2 border-t border-gray-100">
                    <div className="flex items-center justify-between gap-2">
                      <h6 className="font-bold text-gray-900 text-xs flex items-center gap-1">
                        <span>🔍</span> Danh Sách Mẫu ({currentDatasetDetail.samples?.length || 0})
                      </h6>
                      <input
                        type="text"
                        value={sampleSearchQuery}
                        onChange={(e) => setSampleSearchQuery(e.target.value)}
                        placeholder="Tìm kiếm mẫu dữ liệu..."
                        className="px-2.5 py-1 bg-gray-50 border border-gray-200 rounded-lg text-xs outline-none focus:bg-white focus:ring-1 focus:ring-emerald-500 font-sans"
                      />
                    </div>

                    <div className="space-y-2 max-h-96 overflow-y-auto pr-1">
                      {(currentDatasetDetail.samples || [])
                        .filter((s) => {
                          if (!sampleSearchQuery) return true
                          const q = sampleSearchQuery.toLowerCase()
                          return (
                            (s.user_input && s.user_input.toLowerCase().includes(q)) ||
                            (s.model_output && s.model_output.toLowerCase().includes(q)) ||
                            (s.query_slang && s.query_slang.toLowerCase().includes(q)) ||
                            (s.target_drink_flavor && s.target_drink_flavor.toLowerCase().includes(q)) ||
                            (s.category && s.category.toLowerCase().includes(q))
                          )
                        })
                        .map((s, idx) => (
                          <div
                            key={s.id || idx}
                            className="p-2.5 bg-gray-50/70 hover:bg-white rounded-lg border border-gray-200 text-xs space-y-1.5 transition"
                          >
                            {/* SLM SAMPLE */}
                            {s.user_input ? (
                              <>
                                <div className="flex items-start gap-1.5">
                                  <span className="text-gray-400 text-[10px] font-mono mt-0.5">👤</span>
                                  <div className="text-gray-900 font-medium">{s.user_input}</div>
                                </div>
                                <div className="flex items-start gap-1.5 bg-white p-2 rounded border border-gray-100">
                                  <span className="text-purple-600 text-[10px] font-mono mt-0.5">🤖</span>
                                  <div className="text-gray-700 text-[11px] leading-relaxed">{s.model_output}</div>
                                </div>
                                <div className="flex items-center justify-between text-[10px] text-gray-400 font-mono pt-1">
                                  <span className="px-1.5 py-0.2 bg-gray-100 rounded text-gray-600">
                                    #{s.category || 'general'}
                                  </span>
                                  <span className="text-emerald-700 font-bold">✓ Đã kiểm định Barista</span>
                                </div>
                              </>
                            ) : (
                              /* RAG SLANG PAIR */
                              <>
                                <div className="flex items-center justify-between text-xs">
                                  <div className="flex items-center gap-1.5">
                                    <span className="text-gray-400">💬</span>
                                    <strong className="text-gray-900">"{s.query_slang}"</strong>
                                  </div>
                                  <span
                                    className={`text-[10px] font-mono px-1.5 py-0.2 rounded font-bold ${
                                      s.label > 0 ? 'bg-emerald-100 text-emerald-800' : 'bg-red-100 text-red-800'
                                    }`}
                                  >
                                    Label: {s.label > 0 ? `+${s.label}` : s.label}
                                  </span>
                                </div>
                                <div className="flex items-start gap-1.5 text-[11px] text-gray-700 bg-white p-1.5 rounded border border-gray-100">
                                  <span>☕</span>
                                  <div>Target: <strong>{s.target_drink_flavor}</strong></div>
                                </div>
                                <div className="text-[10px] text-gray-400 font-mono">
                                  #{s.category || 'general'}
                                </div>
                              </>
                            )}
                          </div>
                        ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
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
