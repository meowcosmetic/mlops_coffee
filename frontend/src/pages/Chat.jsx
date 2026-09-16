import { useEffect, useRef, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { api, clearToken } from '../api'
import LangfuseSidebar from '../components/LangfuseSidebar'

function money(value) {
  return Number(value || 0).toFixed(2)
}

function RecommendationCard({ rec, onFavorite }) {
  return (
    <div className="bg-white border border-amber-200 rounded-xl p-3 mt-2 shadow-sm relative overflow-hidden">
      <div className="flex justify-between items-start gap-2">
        <div className="flex items-center gap-2 flex-wrap">
          <h3 className="font-semibold text-amber-800">{rec.name}</h3>
          {rec.match_score && (
            <span className="px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-300 text-[10px] font-bold">
              🧠 RAG Match: {rec.match_score}%
            </span>
          )}
        </div>
        <span className="text-sm font-bold text-gray-700 whitespace-nowrap">${money(rec.price)}</span>
      </div>
      <p className="text-sm text-gray-600 mt-1">{rec.description}</p>
      {rec.tasting_notes && (
        <p className="text-xs text-slate-700 mt-1.5 bg-amber-50/70 p-2 rounded border border-amber-200/60 leading-relaxed">
          <span className="font-semibold text-amber-900">🍵 Hương vị:</span> {rec.tasting_notes}
        </p>
      )}
      <p className="text-xs text-amber-800 mt-1.5 italic">
        💡 {rec.reason}
      </p>
      <button
        type="button"
        onClick={() => onFavorite(rec.name)}
        className="text-xs text-amber-600 hover:text-amber-800 mt-2 inline-flex items-center gap-1 font-medium"
      >
        ♥ Lưu món yêu thích
      </button>
    </div>
  )
}

function OrderCard({ order, busy, error, onDecision }) {
  return (
    <div className="bg-amber-50 border border-amber-300 rounded-xl p-3 mt-3">
      <div className="flex justify-between items-start">
        <h3 className="font-semibold text-amber-900">Order #{order.id}</h3>
        <span className="text-sm font-bold text-gray-700">${money(order.total_price)}</span>
      </div>
      <ul className="text-sm text-gray-700 mt-2 space-y-1">
        {order.items.map((item) => (
          <li key={`${order.id}-${item.name}`}>
            {item.quantity} × {item.name} (${money(item.unit_price)} each)
          </li>
        ))}
      </ul>
      {order.status === 'pending' ? (
        <div className="flex gap-2 mt-3">
          <button
            type="button"
            disabled={busy}
            onClick={() => onDecision(order.id, true)}
            className="bg-amber-600 hover:bg-amber-700 disabled:opacity-50 text-white text-sm font-semibold px-3 py-1.5 rounded-lg"
          >
            Xác nhận đơn
          </button>
          <button
            type="button"
            disabled={busy}
            onClick={() => onDecision(order.id, false)}
            className="border border-gray-300 hover:bg-white disabled:opacity-50 text-gray-700 text-sm px-3 py-1.5 rounded-lg"
          >
            Hủy đơn
          </button>
        </div>
      ) : (
        <p className="text-sm font-semibold text-amber-800 mt-3">
          {order.status === 'placed' ? 'Đơn hàng đã được đặt.' : 'Đơn hàng đã được hủy.'}
        </p>
      )}
      {error && <p className="text-sm text-red-600 mt-2">{error}</p>}
    </div>
  )
}

export default function Chat() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [busy, setBusy] = useState(false)
  const [menu, setMenu] = useState([])
  const [showSidebar, setShowSidebar] = useState(false)
  const [sidebarTrigger, setSidebarTrigger] = useState(0)
  const bottomRef = useRef(null)
  const navigate = useNavigate()

  useEffect(() => {
    Promise.allSettled([api.history(), api.menu(), api.pendingOrders()])
      .then(([historyResult, menuResult, pendingResult]) => {
        const history = historyResult.status === 'fulfilled' ? historyResult.value : []
        const menuItems = menuResult.status === 'fulfilled' ? menuResult.value : []
        const pendingOrders = pendingResult.status === 'fulfilled' ? pendingResult.value : []
        const restored = pendingOrders.map((order) => ({
          role: 'assistant',
          content: 'Please review your order and confirm it when ready.',
          pendingOrder: order,
        }))
        setMessages([
          ...history.map((m) => ({ role: m.role, content: m.content })),
          ...restored,
        ])
        setMenu(menuItems)
      })
  }, [])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, busy])

  async function send(e) {
    e.preventDefault()
    const text = input.trim()
    if (!text || busy) return
    setInput('')
    setMessages((m) => [...m, { role: 'user', content: text }])
    setBusy(true)
    try {
      const res = await api.chat(text)
      setMessages((m) => [
        ...m,
        {
          role: 'assistant',
          content: res.reply,
          recommendations: res.recommendations,
          pendingOrder: res.pending_order || (res.order?.status === 'pending' ? res.order : null),
          orderError: null,
        },
      ])
      // Kích hoạt cập nhật sidebar log
      setSidebarTrigger((t) => t + 1)
    } catch (err) {
      setMessages((m) => [...m, { role: 'assistant', content: `⚠️ ${err.message}` }])
    } finally {
      setBusy(false)
    }
  }

  async function decideOrder(messageIndex, orderId, confirmed) {
    if (busy) return
    setBusy(true)
    try {
      const order = await api.confirmOrder(orderId, confirmed)
      setMessages((current) => current.map((message, index) => (
        index === messageIndex ? { ...message, pendingOrder: order, orderError: null } : message
      )))
    } catch (err) {
      setMessages((current) => current.map((message, index) => (
        index === messageIndex ? { ...message, orderError: err.message } : message
      )))
    } finally {
      setBusy(false)
    }
  }

  async function favoriteByName(name) {
    const item = menu.find((i) => i.name === name)
    if (!item) return
    try {
      await api.addFavorite(item.id)
    } catch {
      /* already favorited */
    }
  }

  async function handleNewChat() {
    if (busy) return
    const confirmed = window.confirm('Bạn có muốn xóa toàn bộ lịch sử và bắt đầu cuộc hội thoại mới không?')
    if (!confirmed) return

    setBusy(true)
    try {
      const res = await api.clearHistory()
      setMessages([
        {
          role: 'assistant',
          content: res.welcome_message || 'Welcome! I am your drink assistant — how can I help you today?',
        },
      ])
      setInput('')
    } catch (err) {
      alert(`Lỗi khi làm mới cuộc hội thoại: ${err.message}`)
    } finally {
      setBusy(false)
    }
  }

  function logout() {
    clearToken()
    navigate('/')
  }

  return (
    <div className="h-screen bg-amber-50 flex flex-col overflow-hidden">
      {/* HEADER */}
      <header className="bg-white shadow-xs px-4 py-3 flex justify-between items-center z-20 flex-shrink-0 border-b border-amber-100">
        <div className="flex items-center gap-2.5 sm:gap-3 flex-wrap">
          <h1 className="font-bold text-amber-900 flex items-center gap-1.5 text-base">
            🍹 Drink Bot
          </h1>

          {/* NÚT CUỘC HỘI THOẠI MỚI */}
          <button
            type="button"
            onClick={handleNewChat}
            disabled={busy}
            className="flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-amber-50 hover:bg-amber-100 text-amber-900 border border-amber-300 transition shadow-2xs hover:shadow-sm"
            title="Xóa lịch sử chat và bắt đầu cuộc hội thoại mới"
          >
            <span>✨</span> Cuộc hội thoại mới
          </button>

          {/* NÚT LANGFUSE INSPECTOR */}
          <button
            type="button"
            onClick={() => setShowSidebar((s) => !s)}
            className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold border transition ${
              showSidebar
                ? 'bg-amber-600 text-white border-amber-600 shadow-sm'
                : 'bg-amber-100 hover:bg-amber-200 text-amber-900 border-amber-300'
            }`}
            title="Bật/Tắt bảng giám sát Langfuse"
          >
            <span className={`w-2 h-2 rounded-full ${showSidebar ? 'bg-white' : 'bg-amber-600'}`}></span>
            📊 {showSidebar ? 'Đóng Log Langfuse' : 'Mở Log Langfuse'}
          </button>
        </div>
        <nav className="flex gap-4 text-sm items-center">
          <Link to="/profile" className="text-amber-700 hover:underline font-medium">Profile</Link>
          <button onClick={logout} className="text-gray-500 hover:underline">Log out</button>
        </nav>
      </header>

      {/* WORKSPACE: CHAT AREA + SIDEBAR CO-EXIST (CO GIÃN TRANG) */}
      <div className="flex-1 flex overflow-hidden">
        {/* MAIN CHAT COLUMN */}
        <div className="flex-1 flex flex-col h-full overflow-hidden transition-all duration-300">
          <main className="flex-1 overflow-y-auto p-4 max-w-2xl w-full mx-auto">
            {messages.map((m, i) => (
              <div key={i} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'} mb-3`}>
                <div
                  className={`max-w-[85%] rounded-2xl px-4 py-2.5 ${
                    m.role === 'user'
                      ? 'bg-amber-600 text-white rounded-br-sm shadow-sm'
                      : 'bg-white shadow border border-amber-100 text-gray-800 rounded-bl-sm'
                  }`}
                >
                  <p className="whitespace-pre-wrap leading-relaxed">{m.content}</p>
                  {m.recommendations?.map((rec) => (
                    <RecommendationCard key={rec.name} rec={rec} onFavorite={favoriteByName} />
                  ))}
                  {m.pendingOrder && (
                    <OrderCard
                      order={m.pendingOrder}
                      busy={busy}
                      error={m.orderError}
                      onDecision={(orderId, confirmed) => decideOrder(i, orderId, confirmed)}
                    />
                  )}
                </div>
              </div>
            ))}
            {busy && (
              <div className="flex justify-start mb-3">
                <div className="bg-white shadow rounded-2xl px-4 py-2 text-amber-700/60 border border-amber-100 animate-pulse text-sm">
                  ☕ Đang suy nghĩ gợi ý...
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </main>

          <form onSubmit={send} className="bg-white border-t border-amber-100 p-3 flex-shrink-0">
            <div className="max-w-2xl mx-auto flex gap-2">
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="e.g. I want something refreshing and not too sweet"
                className="flex-1 border border-gray-300 rounded-full px-4 py-2 focus:outline-none focus:ring-2 focus:ring-amber-400 text-sm"
              />
              <button
                type="submit"
                disabled={busy || !input.trim()}
                className="bg-amber-600 hover:bg-amber-700 disabled:opacity-50 text-white font-semibold px-5 rounded-full transition text-sm shadow-sm"
              >
                Send
              </button>
            </div>
          </form>
        </div>

        {/* SIDEBAR COMPONENT (NẰM TRONG FLOW, CO TRANG LẠI CHỨ KHÔNG ĐÈ LÊN) */}
        <LangfuseSidebar
          isOpen={showSidebar}
          onClose={() => setShowSidebar(false)}
          onRefreshTrigger={sidebarTrigger}
        />
      </div>
    </div>
  )
}
