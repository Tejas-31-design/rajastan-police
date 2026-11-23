interface Props {
  lines?: number
  className?: string
  type?: 'card' | 'text' | 'circle'
}

export default function SkeletonLoader({ lines = 3, className = '', type = 'card' }: Props) {
  if (type === 'circle') {
    return <div className={`rounded-full bg-white/10 animate-pulse ${className}`} />
  }
  if (type === 'text') {
    return (
      <div className={`space-y-2 ${className}`}>
        {Array.from({ length: lines }).map((_, i) => (
          <div
            key={i}
            className="h-4 bg-white/10 rounded animate-pulse"
            style={{ width: `${100 - i * 15}%` }}
          />
        ))}
      </div>
    )
  }
  return (
    <div className={`card p-5 animate-pulse ${className}`}>
      <div className="h-4 w-1/3 bg-white/10 rounded mb-4" />
      {Array.from({ length: lines }).map((_, i) => (
        <div key={i} className="h-3 bg-white/10 rounded mb-2" style={{ width: `${90 - i * 10}%` }} />
      ))}
    </div>
  )
}
