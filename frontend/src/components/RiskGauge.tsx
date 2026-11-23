import { useEffect, useRef } from 'react'

interface Props {
  score: number
  label: string
}

const COLORS = {
  'High Risk': '#D64545',
  'Suspicious': '#F28C28',
  'Safe': '#0FA3A3',
}

export default function RiskGauge({ score, label }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const animRef = useRef<number>(0)
  const currentScoreRef = useRef<number>(0)

  const color = COLORS[label as keyof typeof COLORS] || '#0FA3A3'

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    const size = canvas.width
    const cx = size / 2
    const cy = size / 2 + 20
    const radius = size / 2 - 20
    const startAngle = Math.PI * 0.75
    const endAngle = Math.PI * 2.25

    cancelAnimationFrame(animRef.current)

    const animate = () => {
      currentScoreRef.current += (score - currentScoreRef.current) * 0.08

      ctx.clearRect(0, 0, size, size)

      // Background arc
      ctx.beginPath()
      ctx.arc(cx, cy, radius, startAngle, endAngle)
      ctx.strokeStyle = 'rgba(255,255,255,0.1)'
      ctx.lineWidth = 16
      ctx.lineCap = 'round'
      ctx.stroke()

      // Filled arc
      const fillEnd = startAngle + (endAngle - startAngle) * (currentScoreRef.current / 100)
      ctx.beginPath()
      ctx.arc(cx, cy, radius, startAngle, fillEnd)
      ctx.strokeStyle = color
      ctx.lineWidth = 16
      ctx.lineCap = 'round'
      ctx.shadowBlur = 20
      ctx.shadowColor = color
      ctx.stroke()
      ctx.shadowBlur = 0

      // Score text
      ctx.fillStyle = color
      ctx.font = `bold ${size * 0.18}px Inter, sans-serif`
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      ctx.fillText(Math.round(currentScoreRef.current).toString(), cx, cy - 8)

      // /100
      ctx.fillStyle = 'rgba(255,255,255,0.4)'
      ctx.font = `${size * 0.075}px Inter, sans-serif`
      ctx.fillText('/100', cx, cy + size * 0.1)

      if (Math.abs(currentScoreRef.current - score) > 0.5) {
        animRef.current = requestAnimationFrame(animate)
      }
    }

    animRef.current = requestAnimationFrame(animate)
    return () => cancelAnimationFrame(animRef.current)
  }, [score, color])

  const labelColors: Record<string, string> = {
    'High Risk': 'text-alert-red',
    'Suspicious': 'text-saffron',
    'Safe': 'text-teal',
  }

  return (
    <div className="flex flex-col items-center gap-2 animate-fade-in">
      <canvas ref={canvasRef} width={200} height={180} />
      <span className={`text-xl font-bold ${labelColors[label] || 'text-teal'}`}>
        {label === 'High Risk' ? '⚠️ High Risk' : label === 'Suspicious' ? '⚡ Suspicious' : '✅ Safe'}
      </span>
    </div>
  )
}
