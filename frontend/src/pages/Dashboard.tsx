import { useEffect, useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Link } from 'react-router-dom'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { getDashboardStats, getDashboardTrend, getHotspots, getCampaigns } from '../api/client'
import type { DashboardStats, TrendPoint, DistrictHotspot, Campaign } from '../types'
import KPICard from '../components/KPICard'
import HotspotMap from '../components/HotspotMap'
import LiveFeedTicker from '../components/LiveFeedTicker'
import SkeletonLoader from '../components/SkeletonLoader'
import SyntheticBadge from '../components/SyntheticBadge'

const RISK_COLORS: Record<string, string> = {
  High: 'bg-alert-red/20 text-alert-red border-alert-red/30',
  Medium: 'bg-saffron/20 text-saffron border-saffron/30',
  Low: 'bg-teal/20 text-teal border-teal/30',
}
const STATUS_COLORS: Record<string, string> = {
  active: 'text-alert-red',
  monitoring: 'text-saffron',
  resolved: 'text-teal',
}

export default function Dashboard() {
  const { t } = useTranslation()
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [trend, setTrend] = useState<TrendPoint[]>([])
  const [hotspots, setHotspots] = useState<DistrictHotspot[]>([])
  const [campaigns, setCampaigns] = useState<Campaign[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setLoading(true)
    Promise.all([
      getDashboardStats(),
      getDashboardTrend(),
      getHotspots(),
      getCampaigns(),
    ])
      .then(([s, tr, hs, camps]) => {
        setStats(s)
        setTrend(tr)
        setHotspots(hs)
        setCampaigns(camps)
      })
      .catch(() => setError('Failed to load dashboard. Is the backend running?'))
      .finally(() => setLoading(false))
  }, [])

  const takedownCandidates = campaigns.filter(c => c.risk_level === 'High').slice(0, 5)

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white">{t('dashboard.title')}</h1>
          <p className="text-white/40 text-sm mt-1">Rajasthan Cyber Fraud Intelligence</p>
        </div>
        <SyntheticBadge />
      </div>

      {error && (
        <div className="card border-alert-red/40 bg-alert-red/10 p-4 mb-6 text-alert-red">
          ⚠️ {error}
        </div>
      )}

      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
        <KPICard title={t('dashboard.reports_today')} value={stats?.reports_today ?? '—'} icon="📋" loading={loading} color="text-saffron" />
        <KPICard title={t('dashboard.active_campaigns')} value={stats?.active_campaigns ?? '—'} icon="🚨" loading={loading} color="text-alert-red" />
        <KPICard title={t('dashboard.high_risk_domains')} value={stats?.high_risk_domains ?? '—'} icon="🌐" loading={loading} color="text-alert-red" />
        <KPICard title={t('dashboard.top_district')} value={stats?.top_district ?? '—'} icon="📍" loading={loading} color="text-teal" />
        <KPICard title={t('dashboard.total_reports')} value={stats?.total_reports ?? '—'} icon="📊" loading={loading} color="text-white" />
        <KPICard title="Resolved" value={stats?.resolved_campaigns ?? '—'} icon="✅" loading={loading} color="text-teal" />
      </div>

      {/* Trend + Map */}
      <div className="grid lg:grid-cols-2 gap-6 mb-8">
        {/* Trend Chart */}
        <div className="card p-5">
          <h2 className="font-semibold text-white mb-4">{t('dashboard.trend_title')}</h2>
          {loading ? <SkeletonLoader lines={5} /> : (
            <ResponsiveContainer width="100%" height={260}>
              <LineChart data={trend} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
                <XAxis
                  dataKey="date"
                  tickFormatter={d => d.slice(5)}
                  tick={{ fill: 'rgba(255,255,255,0.4)', fontSize: 10 }}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis tick={{ fill: 'rgba(255,255,255,0.4)', fontSize: 10 }} axisLine={false} tickLine={false} />
                <Tooltip
                  contentStyle={{ background: '#12304D', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 8, color: 'white' }}
                  labelStyle={{ color: 'rgba(255,255,255,0.6)' }}
                />
                <Legend wrapperStyle={{ color: 'rgba(255,255,255,0.6)', fontSize: 12 }} />
                <Line type="monotone" dataKey="reports" stroke="#0FA3A3" strokeWidth={2} dot={false} name="Total Reports" />
                <Line type="monotone" dataKey="high_risk" stroke="#D64545" strokeWidth={2} dot={false} name="High Risk" />
              </LineChart>
            </ResponsiveContainer>
          )}
        </div>

        {/* Hotspot Map */}
        <div className="card p-5">
          <h2 className="font-semibold text-white mb-4">{t('dashboard.hotspot_title')}</h2>
          {loading ? <SkeletonLoader lines={5} className="h-64" /> : (
            <HotspotMap hotspots={hotspots} />
          )}
        </div>
      </div>

      {/* Campaigns + Takedown */}
      <div className="grid lg:grid-cols-2 gap-6 mb-6">
        {/* Campaigns Table */}
        <div className="card p-5">
          <h2 className="font-semibold text-white mb-4">{t('dashboard.campaigns_title')}</h2>
          {loading ? <SkeletonLoader lines={6} /> : (
            <div className="space-y-2 max-h-80 overflow-y-auto pr-1">
              {campaigns.slice(0, 10).map(c => (
                <Link
                  key={c.id}
                  to={`/campaign/${c.id}`}
                  className="flex items-center justify-between p-3 rounded-lg bg-navy hover:bg-card-light transition-colors group"
                >
                  <div className="min-w-0">
                    <div className="text-sm font-medium text-white group-hover:text-saffron truncate">{c.name}</div>
                    <div className="text-xs text-white/40">{c.district} · {c.report_count} reports</div>
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0 ml-3">
                    <span className={`text-xs px-2 py-0.5 rounded-full border ${RISK_COLORS[c.risk_level]}`}>
                      {c.risk_level}
                    </span>
                    <span className={`text-xs font-medium ${STATUS_COLORS[c.status] || 'text-white/60'}`}>
                      {c.status}
                    </span>
                  </div>
                </Link>
              ))}
              {campaigns.length === 0 && (
                <div className="text-white/40 text-sm text-center py-8">{t('common.no_data')}</div>
              )}
            </div>
          )}
        </div>

        {/* Takedown Candidates */}
        <div className="card p-5">
          <h2 className="font-semibold text-white mb-4">{t('dashboard.takedown_title')}</h2>
          {loading ? <SkeletonLoader lines={5} /> : (
            <div className="space-y-3">
              {takedownCandidates.map(c => {
                const domains = c.indicators?.domains || []
                return (
                  <div key={c.id} className="rounded-lg bg-alert-red/5 border border-alert-red/20 p-3">
                    <div className="flex items-start justify-between gap-2">
                      <div>
                        <div className="text-sm font-medium text-white">{c.name}</div>
                        <div className="text-xs text-white/50 mt-0.5">{c.report_count} reports · {c.district}</div>
                        {domains.slice(0, 2).map(d => (
                          <div key={d} className="text-xs font-mono text-alert-red mt-1">🌐 {d}</div>
                        ))}
                      </div>
                      <Link to={`/campaign/${c.id}`} className="text-xs btn-secondary flex-shrink-0">
                        {t('dashboard.view_detail')} →
                      </Link>
                    </div>
                  </div>
                )
              })}
              {takedownCandidates.length === 0 && (
                <div className="text-white/40 text-sm text-center py-8">No high-risk campaigns</div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Live Feed */}
      <LiveFeedTicker />
    </div>
  )
}
