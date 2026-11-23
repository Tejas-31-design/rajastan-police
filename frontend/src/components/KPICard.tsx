interface Props {
  title: string
  value: string | number
  icon: string
  subtitle?: string
  color?: string
  loading?: boolean
}

export default function KPICard({ title, value, icon, subtitle, color = 'text-saffron', loading }: Props) {
  if (loading) {
    return (
      <div className="kpi-card animate-pulse">
        <div className="h-4 w-20 bg-white/10 rounded mb-2" />
        <div className="h-8 w-16 bg-white/10 rounded" />
      </div>
    )
  }
  return (
    <div className="kpi-card hover:border-saffron/30 transition-colors">
      <div className="flex items-center justify-between">
        <span className="text-white/60 text-xs font-medium uppercase tracking-wide">{title}</span>
        <span className="text-2xl">{icon}</span>
      </div>
      <div className={`text-3xl font-bold ${color}`}>{value}</div>
      {subtitle && <div className="text-white/50 text-xs">{subtitle}</div>}
    </div>
  )
}
