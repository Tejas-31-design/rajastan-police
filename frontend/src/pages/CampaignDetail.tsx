import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { getCampaign, exportPDF } from '../api/client'
import type { CampaignDetail as CampaignDetailType } from '../types'
import CampaignGraph from '../components/CampaignGraph'
import SkeletonLoader from '../components/SkeletonLoader'
import SyntheticBadge from '../components/SyntheticBadge'

const LABEL_COLORS: Record<string, string> = {
  'High Risk': 'text-alert-red',
  Suspicious: 'text-saffron',
  Safe: 'text-teal',
}
const IND_ICONS: Record<string, string> = {
  domain: '🌐',
  phone: '📞',
  upi: '💸',
  sender: '📱',
}

export default function CampaignDetail() {
  const { id } = useParams<{ id: string }>()
  const { t } = useTranslation()
  const [data, setData] = useState<CampaignDetailType | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [pdfLoading, setPdfLoading] = useState(false)

  useEffect(() => {
    if (!id) return
    setLoading(true)
    getCampaign(Number(id))
      .then(setData)
      .catch(() => setError('Failed to load campaign'))
      .finally(() => setLoading(false))
  }, [id])

  const handleExportPDF = () => {
    if (!id) return
    setPdfLoading(true)
    exportPDF(Number(id))
    setTimeout(() => setPdfLoading(false), 2000)
  }

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-8 space-y-6">
        <SkeletonLoader lines={2} />
        <div className="grid md:grid-cols-2 gap-6">
          <SkeletonLoader lines={5} />
          <SkeletonLoader lines={5} />
        </div>
      </div>
    )
  }

  if (error || !data) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="card border-alert-red/40 bg-alert-red/10 p-6 text-center">
          <div className="text-4xl mb-3">⚠️</div>
          <p className="text-alert-red">{error || 'Campaign not found'}</p>
          <Link to="/dashboard" className="btn-primary mt-4 inline-block">{t('common.back')}</Link>
        </div>
      </div>
    )
  }

  const { campaign, reports, indicators, graph, timeline } = data

  const riskColor = {
    High: 'text-alert-red border-alert-red/40 bg-alert-red/10',
    Medium: 'text-saffron border-saffron/40 bg-saffron/10',
    Low: 'text-teal border-teal/40 bg-teal/10',
  }[campaign.risk_level] || 'text-white'

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-start justify-between gap-4 mb-8">
        <div>
          <Link to="/dashboard" className="text-white/40 hover:text-white text-sm mb-2 inline-block">{t('common.back')}</Link>
          <h1 className="text-2xl font-bold text-white">{campaign.name}</h1>
          <div className="flex flex-wrap gap-2 mt-2">
            <span className={`text-sm px-3 py-1 rounded-full border font-medium ${riskColor}`}>
              {campaign.risk_level} Risk
            </span>
            <span className="text-sm px-3 py-1 rounded-full border border-white/20 text-white/60">
              📍 {campaign.district}
            </span>
            <span className="text-sm px-3 py-1 rounded-full border border-white/20 text-white/60">
              📋 {campaign.report_count} reports
            </span>
            <span className="text-sm px-3 py-1 rounded-full border border-white/20 text-white/60 capitalize">
              {campaign.status}
            </span>
          </div>
        </div>
        <div className="flex items-center gap-3 flex-shrink-0">
          <SyntheticBadge />
          <button
            onClick={handleExportPDF}
            disabled={pdfLoading}
            className="btn-primary flex items-center gap-2"
          >
            {pdfLoading ? (
              <span className="w-4 h-4 border-2 border-navy/40 border-t-navy rounded-full animate-spin" />
            ) : '📄'}
            {t('campaign.export_pdf')}
          </button>
        </div>
      </div>

      {/* Overview */}
      <div className="grid md:grid-cols-3 gap-4 mb-8">
        <div className="card p-4 md:col-span-2">
          <h2 className="text-sm font-semibold text-white/60 uppercase tracking-wide mb-3">{t('campaign.indicators')}</h2>
          <div className="grid grid-cols-2 gap-3">
            {indicators.slice(0, 8).map(ind => (
              <div key={ind.id} className="flex items-center gap-2 bg-navy rounded-lg p-2.5">
                <span>{IND_ICONS[ind.type] || '•'}</span>
                <div className="min-w-0">
                  <div className="text-xs text-white/40 capitalize">{ind.type}</div>
                  <div className="text-sm font-mono text-white truncate">{ind.value}</div>
                  <div className="text-xs text-white/30">{ind.report_count} reports</div>
                </div>
              </div>
            ))}
            {indicators.length === 0 && (
              <div className="col-span-2 text-white/40 text-sm py-4 text-center">No indicators</div>
            )}
          </div>
        </div>
        <div className="card p-4">
          <h2 className="text-sm font-semibold text-white/60 uppercase tracking-wide mb-3">Summary</h2>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-white/50">First seen</span>
              <span className="text-white">{new Date(campaign.created_at).toLocaleDateString()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-white/50">Last updated</span>
              <span className="text-white">{new Date(campaign.updated_at).toLocaleDateString()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-white/50">Reports</span>
              <span className="text-saffron font-semibold">{campaign.report_count}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-white/50">Indicators</span>
              <span className="text-teal font-semibold">{indicators.length}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Campaign Graph */}
      <div className="card p-5 mb-8">
        <h2 className="font-semibold text-white mb-4">{t('campaign.graph_title')}</h2>
        <CampaignGraph nodes={graph.nodes} links={graph.links} />
      </div>

      {/* Reports + Timeline */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Reports table */}
        <div className="card p-5">
          <h2 className="font-semibold text-white mb-4">{t('campaign.reports')} ({reports.length})</h2>
          <div className="space-y-2 max-h-80 overflow-y-auto pr-1">
            {reports.slice(0, 25).map(r => (
              <div key={r.id} className="flex items-start gap-3 bg-navy rounded-lg p-3">
                <div className="flex-shrink-0 mt-0.5">
                  <span className="text-lg">{r.source_type === 'url' ? '🌐' : '💬'}</span>
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`text-xs font-semibold ${LABEL_COLORS[r.label] || 'text-white'}`}>
                      {r.label}
                    </span>
                    <span className="text-xs text-white/30">{r.district}</span>
                    <span className="text-xs text-white/30 ml-auto">{r.risk_score.toFixed(0)}</span>
                  </div>
                  <p className="text-xs text-white/60 truncate">{r.content}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Timeline */}
        <div className="card p-5">
          <h2 className="font-semibold text-white mb-4">{t('campaign.timeline_title')}</h2>
          <div className="relative max-h-80 overflow-y-auto pr-1">
            <div className="absolute left-3 top-0 bottom-0 w-px bg-white/10" />
            <div className="space-y-3 ml-7">
              {timeline.slice(0, 20).map((ev, i) => (
                <div key={i} className="relative">
                  <div className={`absolute -left-7 top-1 w-2 h-2 rounded-full ${
                    ev.risk_level === 'High Risk' ? 'bg-alert-red' :
                    ev.risk_level === 'Suspicious' ? 'bg-saffron' : 'bg-teal'
                  }`} />
                  <div className="text-xs text-white/30 mb-0.5">
                    {new Date(ev.date).toLocaleDateString()} · {ev.district}
                  </div>
                  <div className={`text-xs font-medium ${LABEL_COLORS[ev.risk_level] || 'text-white'}`}>
                    {ev.event}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
