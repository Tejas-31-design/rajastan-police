import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'
import type { Signal } from '../types'
import { useTranslation } from 'react-i18next'

interface Props {
  signals: Signal[]
}

export default function SignalChart({ signals }: Props) {
  const { t } = useTranslation()
  const data = signals
    .filter(s => s.weight > 0)
    .sort((a, b) => b.weight - a.weight)
    .slice(0, 10)
    .map(s => ({
      name: s.name.length > 22 ? s.name.slice(0, 22) + '…' : s.name,
      fullName: s.name,
      weight: s.weight,
      triggered: s.triggered,
    }))

  return (
    <div className="animate-fade-in">
      <h3 className="text-sm font-semibold text-white/70 mb-3">{t('home.signals')}</h3>
      <ResponsiveContainer width="100%" height={data.length * 36 + 20}>
        <BarChart
          data={data}
          layout="vertical"
          margin={{ top: 0, right: 10, left: 0, bottom: 0 }}
        >
          <XAxis type="number" domain={[0, 25]} hide />
          <YAxis
            type="category"
            dataKey="name"
            width={160}
            tick={{ fill: 'rgba(255,255,255,0.7)', fontSize: 11 }}
            axisLine={false}
            tickLine={false}
          />
          <Tooltip
            formatter={(value: number, _name: string, props: any) => [
              `Weight: ${value}`,
              props.payload.fullName,
            ]}
            contentStyle={{
              background: '#12304D',
              border: '1px solid rgba(255,255,255,0.1)',
              borderRadius: 8,
              color: 'white',
              fontSize: 12,
            }}
          />
          <Bar dataKey="weight" radius={[0, 4, 4, 0]}>
            {data.map((entry, i) => (
              <Cell
                key={i}
                fill={entry.triggered ? '#F28C28' : 'rgba(255,255,255,0.1)'}
                opacity={entry.triggered ? 1 : 0.4}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
