import { useState, useEffect, useCallback } from 'react'
import { Users, LogIn, LogOut, Activity } from 'lucide-react'

import StatCard from '../components/StatCard'
import OccupancyChart from '../components/OccupancyChart'
import CapacityRing from '../components/CapacityRing'
import { useWebSocket } from '../hooks/useWebSocket'
import { useFlash } from '../hooks/useFlash'

const API_BASE = import.meta.env.VITE_API_BASE || ''

function formatNumber(n) {
    return n.toLocaleString('en-US')
}

function useClock() {
    const [time, setTime] = useState(new Date())
    useEffect(() => {
        const id = setInterval(() => setTime(new Date()), 1000)
        return () => clearInterval(id)
    }, [])
    return time.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
}

export default function DashboardPage() {
    const [stats, setStats] = useState({ people_inside: 0, entries_today: 0, exits_today: 0 })
    const [chartData, setChartData] = useState([])
    const [loading, setLoading] = useState(true)
    const clock = useClock()
    const heroFlashing = useFlash(stats.people_inside)

    // Fetch initial data
    useEffect(() => {
        const fetchAll = async () => {
            try {
                const [statsRes, histRes] = await Promise.all([
                    fetch(`${API_BASE}/api/stats`),
                    fetch(`${API_BASE}/api/history`),
                ])
                if (statsRes.ok) setStats(await statsRes.json())
                if (histRes.ok) setChartData(await histRes.json())
            } catch (e) {
                console.warn('Initial fetch failed:', e)
            } finally {
                setLoading(false)
            }
        }
        fetchAll()
    }, [])

    // Handle WebSocket messages
    const handleMessage = useCallback((msg) => {
        if (msg.event === 'stats_update' && msg.data) {
            setStats(msg.data)

            // Update chart: add a data point for the current minute
            setChartData((prev) => {
                const now = new Date()
                const minute = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}T${String(now.getHours()).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}`
                const last = prev[prev.length - 1]
                if (last && last.minute === minute) {
                    // Increment the last bucket
                    const direction = (msg.data.entries_today - (prev.reduce((a, b) => a + b.entries, 0))) >= 0 ? 'entries' : 'exits'
                    return prev.map((pt, i) =>
                        i === prev.length - 1
                            ? {
                                ...pt, entries: msg.data.entries_today > (prev.reduce((a, b) => a + b.entries, 0)) ? pt.entries + 1 : pt.entries,
                                exits: msg.data.exits_today > (prev.reduce((a, b) => a + b.exits, 0)) ? pt.exits + 1 : pt.exits
                            }
                            : pt
                    )
                } else {
                    // New minute bucket — keep last 60
                    const newPoint = { minute, entries: 0, exits: 0 }
                    return [...prev.slice(-59), newPoint]
                }
            })
        }
    }, [])

    const { connected } = useWebSocket(handleMessage)

    if (loading) {
        return (
            <div className="dashboard" style={{ alignItems: 'center', justifyContent: 'center', minHeight: '100vh' }}>
                <div style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
                    <Activity size={40} style={{ margin: '0 auto 12px', display: 'block', color: 'var(--primary)' }} />
                    <p style={{ fontWeight: 600 }}>Connecting to dashboard…</p>
                </div>
            </div>
        )
    }

    return (
        <div className="dashboard">
            {/* ── Header ── */}
            <header className="header">
                <div className="header-brand">
                    <div className="header-icon">
                        <Users size={20} />
                    </div>
                    <div>
                        <div className="header-title">Stadium People Counter</div>
                        <div className="header-subtitle">Real-time occupancy dashboard</div>
                    </div>
                </div>

                <div className="header-right">
                    <span className="header-time">🕐 {clock}</span>
                    <div className={`connection-badge ${connected ? 'connected' : 'disconnected'}`}>
                        <span className="connection-dot" />
                        {connected ? 'Live' : 'Reconnecting…'}
                    </div>
                </div>
            </header>

            {/* ── Main ── */}
            <main className="main">
                {/* Hero panel */}
                <section className="hero-panel">
                    <div className="hero-left">
                        <div className="hero-label">Stadium Occupancy</div>
                        <div className={`hero-number${heroFlashing ? ' updating' : ''}`}>
                            {formatNumber(stats.people_inside)}
                        </div>
                        <div className="hero-sub">People currently inside the stadium</div>
                    </div>
                    <div className="hero-right">
                        <CapacityRing peopleInside={stats.people_inside} />
                    </div>
                </section>

                {/* Stat cards */}
                <div className="cards-grid">
                    <StatCard
                        label="Current Occupancy"
                        value={stats.people_inside}
                        icon={Users}
                        iconClass="icon-blue"
                        footer="People inside right now"
                    />
                    <StatCard
                        label="Entries Today"
                        value={stats.entries_today}
                        icon={LogIn}
                        iconClass="icon-green"
                        footer="Total entries since midnight"
                    />
                    <StatCard
                        label="Exits Today"
                        value={stats.exits_today}
                        icon={LogOut}
                        iconClass="icon-red"
                        footer="Total exits since midnight"
                    />
                </div>

                {/* Chart */}
                <section className="chart-section">
                    <div className="chart-header">
                        <div>
                            <div className="chart-title">Activity — Last 60 Minutes</div>
                            <div className="chart-subtitle">Entries and exits per minute</div>
                        </div>
                        <div className="chart-legend">
                            <div className="legend-item">
                                <div className="legend-dot" style={{ background: '#024ddf' }} />
                                Entries
                            </div>
                            <div className="legend-item">
                                <div className="legend-dot" style={{ background: '#10b981' }} />
                                Exits
                            </div>
                        </div>
                    </div>
                    <OccupancyChart data={chartData} />
                </section>
            </main>

            {/* ── Footer ── */}
            <footer className="footer">
                Stadium People Counter Dashboard · Real-time via WebSocket ·{' '}
                <span style={{ color: connected ? 'var(--green)' : 'var(--red)' }}>
                    {connected ? '● Live' : '○ Offline'}
                </span>
            </footer>
        </div>
    )
}
