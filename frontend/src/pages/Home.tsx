import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { checkURL, checkSMS } from '../api/client'
import type { CheckResponse } from '../types'
import RiskGauge from '../components/RiskGauge'
import SignalChart from '../components/SignalChart'
import ReasonChip from '../components/ReasonChip'
import WhatToDoCard from '../components/WhatToDoCard'
import SkeletonLoader from '../components/SkeletonLoader'

const SAMPLES = {
  phishing: 'sbi-kyc-update.xyz',
  safe: 'https://www.google.com',
  sms: 'Aapka SBI account block ho jayega 24 ghante mein, KYC update karein: http://sbi-kyc-update.xyz . Call 9876543210.',
}

export default function Home() {
  const { t } = useTranslation()
  const [tab, setTab] = useState<'url' | 'sms'>('url')
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<CheckResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const analyze = async () => {
    if (!input.trim()) return
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const res = tab === 'url' ? await checkURL(input.trim()) : await checkSMS(input.trim())
      setResult(res)
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Failed to analyze. Is the backend running?')
    } finally {
      setLoading(false)
    }
  }

  const trySample = (key: keyof typeof SAMPLES) => {
    const sample = SAMPLES[key]
    if (key === 'sms') setTab('sms')
    else setTab('url')
    setInput(sample)
    setResult(null)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      analyze()
    }
  }

  const labelBg: Record<string, string> = {
    'High Risk': 'bg-alert-red/10 border-alert-red/30',
    'Suspicious': 'bg-saffron/10 border-saffron/30',
    'Safe': 'bg-teal/10 border-teal/30',
  }

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      {/* Hero */}
      <div className="text-center mb-10">
        <h1 className="text-4xl md:text-5xl font-extrabold text-white mb-2">
          {t('home.title')} <span className="text-saffron">🛡️</span>
        </h1>
        <p className="text-teal font-semibold text-lg mb-1">{t('home.tagline')}</p>
        <p className="text-white/60">{t('home.subtitle')}</p>
      </div>

      {/* Checker card */}
      <div className="card p-6 mb-6 animate-slide-up">
        {/* Tabs */}
        <div className="flex gap-2 mb-5">
          <button
            className={`tab ${tab === 'url' ? 'tab-active' : 'tab-inactive'}`}
            onClick={() => { setTab('url'); setResult(null); setInput('') }}
          >
            🌐 {t('home.tab_url')}
          </button>
          <button
            className={`tab ${tab === 'sms' ? 'tab-active' : 'tab-inactive'}`}
            onClick={() => { setTab('sms'); setResult(null); setInput('') }}
          >
            💬 {t('home.tab_sms')}
          </button>
        </div>

        {/* Input */}
        {tab === 'url' ? (
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={t('home.url_placeholder')}
            className="w-full bg-navy border border-white/20 rounded-lg px-4 py-3 text-white placeholder-white/30 focus:outline-none focus:border-saffron transition-colors font-mono text-sm"
          />
        ) : (
          <textarea
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder={t('home.sms_placeholder')}
            rows={4}
            className="w-full bg-navy border border-white/20 rounded-lg px-4 py-3 text-white placeholder-white/30 focus:outline-none focus:border-saffron transition-colors resize-none text-sm"
          />
        )}

        {/* Actions */}
        <div className="flex flex-wrap gap-2 mt-4">
          <button
            onClick={analyze}
            disabled={loading || !input.trim()}
            className="btn-primary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <>
                <span className="w-4 h-4 border-2 border-navy/40 border-t-navy rounded-full animate-spin" />
                {t('home.analyzing')}
              </>
            ) : (
              <>🔍 {t('home.analyze')}</>
            )}
          </button>

          <div className="flex items-center gap-1 ml-auto">
            <span className="text-xs text-white/40 mr-1">{t('home.try_sample')}:</span>
            <button onClick={() => trySample('phishing')} className="btn-secondary text-xs text-alert-red border-alert-red/30">
              🎣 {t('home.sample_phishing')}
            </button>
            <button onClick={() => trySample('safe')} className="btn-secondary text-xs text-teal border-teal/30">
              ✅ {t('home.sample_safe')}
            </button>
            <button onClick={() => trySample('sms')} className="btn-secondary text-xs text-saffron border-saffron/30">
              💬 {t('home.sample_sms')}
            </button>
          </div>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="card border-alert-red/40 bg-alert-red/10 p-4 mb-6 text-alert-red text-sm">
          ⚠️ {error}
        </div>
      )}

      {/* Loading skeleton */}
      {loading && (
        <div className="grid md:grid-cols-2 gap-6">
          <SkeletonLoader lines={4} />
          <SkeletonLoader lines={5} />
        </div>
      )}

      {/* Result */}
      {result && !loading && (
        <div className="animate-slide-up space-y-5">
          {/* Main result */}
          <div className={`card border p-6 ${labelBg[result.label] || ''}`}>
            <div className="flex flex-col md:flex-row gap-6 items-center">
              {/* Gauge */}
              <div className="flex-shrink-0">
                <RiskGauge score={result.risk_score} label={result.label} />
              </div>

              {/* Info */}
              <div className="flex-1 space-y-4 min-w-0">
                {/* Reasons */}
                <div>
                  <p className="text-xs text-white/50 font-medium uppercase tracking-wider mb-2">{t('home.reasons')}</p>
                  <ReasonChip reasons={result.reasons} />
                </div>

                {/* Indicators */}
                {Object.keys(result.indicators).length > 0 && (
                  <div className="grid grid-cols-2 gap-3">
                    {result.indicators.domain && (
                      <div className="bg-white/5 rounded-lg p-2 text-xs">
                        <div className="text-white/40 mb-0.5">{t('common.domain')}</div>
                        <div className="text-saffron font-mono truncate">{result.indicators.domain}</div>
                      </div>
                    )}
                    {(result.indicators.phones?.length > 0) && (
                      <div className="bg-white/5 rounded-lg p-2 text-xs">
                        <div className="text-white/40 mb-0.5">{t('home.phones_found')}</div>
                        <div className="text-alert-red font-mono">{result.indicators.phones[0]}</div>
                      </div>
                    )}
                    {(result.indicators.urls?.length > 0) && (
                      <div className="bg-white/5 rounded-lg p-2 text-xs">
                        <div className="text-white/40 mb-0.5">{t('home.embedded_links')}</div>
                        <div className="text-saffron font-mono truncate">{result.indicators.urls[0]}</div>
                      </div>
                    )}
                    {(result.indicators.upis?.length > 0) && (
                      <div className="bg-white/5 rounded-lg p-2 text-xs">
                        <div className="text-white/40 mb-0.5">{t('home.upi_found')}</div>
                        <div className="text-purple-400 font-mono">{result.indicators.upis[0]}</div>
                      </div>
                    )}
                    {result.indicators.category && result.indicators.category !== 'Unknown' && (
                      <div className="bg-white/5 rounded-lg p-2 text-xs col-span-2">
                        <div className="text-white/40 mb-0.5">Scam Category</div>
                        <div className="text-saffron">{result.indicators.category}</div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Signal chart + What to do */}
          <div className="grid md:grid-cols-2 gap-5">
            <div className="card p-5">
              <SignalChart signals={result.signals} />
            </div>
            <WhatToDoCard nextSteps={result.next_steps} label={result.label} />
          </div>
        </div>
      )}

      {/* Empty state */}
      {!result && !loading && !error && (
        <div className="text-center text-white/30 py-16">
          <div className="text-5xl mb-3">🔍</div>
          <p>Paste a URL or SMS above to analyze</p>
        </div>
      )}
    </div>
  )
}
