interface Props {
  reasons: string[]
}

const CHIP_COLORS = [
  'bg-alert-red/20 border-alert-red/40 text-alert-red',
  'bg-saffron/20 border-saffron/40 text-saffron',
  'bg-teal/20 border-teal/40 text-teal',
  'bg-purple-500/20 border-purple-400/40 text-purple-300',
]

export default function ReasonChip({ reasons }: Props) {
  return (
    <div className="flex flex-wrap gap-2 animate-fade-in">
      {reasons.map((reason, i) => (
        <span
          key={i}
          className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium border ${CHIP_COLORS[i % CHIP_COLORS.length]}`}
        >
          <span>⚡</span>
          {reason}
        </span>
      ))}
    </div>
  )
}
