import { useTranslation } from 'react-i18next'

interface Props {
  nextSteps: string[]
  label: string
}

export default function WhatToDoCard({ nextSteps, label }: Props) {
  const { t } = useTranslation()
  const isHighRisk = label === 'High Risk'
  const isSuspicious = label === 'Suspicious'

  const borderColor = isHighRisk ? 'border-alert-red/40' : isSuspicious ? 'border-saffron/40' : 'border-teal/40'
  const bgColor = isHighRisk ? 'bg-alert-red/5' : isSuspicious ? 'bg-saffron/5' : 'bg-teal/5'

  return (
    <div className={`rounded-xl border p-5 ${borderColor} ${bgColor} animate-slide-up`}>
      <h3 className="font-semibold text-white mb-3 flex items-center gap-2">
        <span>{isHighRisk ? '🚨' : isSuspicious ? '⚠️' : '✅'}</span>
        {t('home.next_steps')}
      </h3>
      <ul className="space-y-2">
        {nextSteps.map((step, i) => (
          <li key={i} className="flex items-start gap-2 text-sm text-white/80">
            <span className="mt-0.5 text-saffron font-bold">→</span>
            <span>{step}</span>
          </li>
        ))}
      </ul>
      {isHighRisk && (
        <div className="mt-4 flex flex-wrap gap-2">
          <a
            href="https://cybercrime.gov.in"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-alert-red text-white text-xs font-semibold rounded-lg hover:bg-red-600 transition-colors"
          >
            🔗 Report at cybercrime.gov.in
          </a>
          <span className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-saffron/20 text-saffron text-xs font-semibold rounded-lg border border-saffron/40">
            📞 Call 1930
          </span>
        </div>
      )}
    </div>
  )
}
