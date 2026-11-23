import { useEffect, useRef, useState } from 'react'
import type { LiveEvent } from '../types'
import { useTranslation } from 'react-i18next'

const RISK_COLORS: Record<string, string> = {
  'High Risk': 'text-alert-red',
  'Suspicious': 'text-saffron',
  'Safe': 'text-teal',
}

export default function LiveFeedTicker() {
  const { t } = useTranslation()
  const [events, setEvents] = useState<LiveEvent[]>([])
  const esRef = useRef<EventSource | null>(null)

  useEffect(() => {
    esRef.current = new EventSource('/api/live-feed')
    esRef.current.onmessage = (e) => {
      try {
        const event: LiveEvent = JSON.parse(e.data)
        setEvents(prev => [event, ...prev].slice(0, 20))
      } catch {}
    }
    return () => esRef.current?.close()
  }, [])

  const displayEvents = events.length > 0 ? events : [
    { id: '0', timestamp: new Date().toISOString(), type: 'System', message: 'Live feed connecting...', district: 'Jaipur', risk_level: 'Safe' }
  ]

  return (
    <div className="card p-3">
      <div className="flex items-center gap-2 mb-2">
        <div className="w-2 h-2 rounded-full bg-alert-red animate-pulse" />
        <span className="text-xs font-semibold text-white/70 uppercase tracking-wider">{t('dashboard.live_feed')}</span>
      </div>
      <div className="overflow-hidden h-8">
        <div className="animate-ticker whitespace-nowrap flex gap-8 items-center h-full">
          {displayEvents.map((e) => (
            <span key={e.id} className="inline-flex items-center gap-2 text-sm">
              <span className="text-white/40 text-xs">[{e.district}]</span>
              <span className={`font-medium ${RISK_COLORS[e.risk_level] || 'text-white'}`}>
                {e.type}:
              </span>
              <span className="text-white/80">{e.message}</span>
              <span className="text-white/20">|</span>
            </span>
          ))}
        </div>
      </div>
    </div>
  )
}
