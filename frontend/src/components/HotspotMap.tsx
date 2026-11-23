import { useEffect, useRef } from 'react'
import L from 'leaflet'
import type { DistrictHotspot } from '../types'
import { useTranslation } from 'react-i18next'

interface Props {
  hotspots: DistrictHotspot[]
}

const RISK_COLORS: Record<string, string> = {
  High: '#D64545',
  Medium: '#F28C28',
  Low: '#0FA3A3',
}

export default function HotspotMap({ hotspots }: Props) {
  const { t } = useTranslation()
  const mapRef = useRef<L.Map | null>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return

    mapRef.current = L.map(containerRef.current, {
      center: [26.5, 74.0],
      zoom: 7,
      zoomControl: true,
      scrollWheelZoom: false,
    })

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors',
    }).addTo(mapRef.current)

    return () => {
      mapRef.current?.remove()
      mapRef.current = null
    }
  }, [])

  useEffect(() => {
    if (!mapRef.current || hotspots.length === 0) return

    // Clear existing layers
    mapRef.current.eachLayer((layer) => {
      if (layer instanceof L.CircleMarker) {
        mapRef.current!.removeLayer(layer)
      }
    })

    const maxCount = Math.max(...hotspots.map(h => h.count), 1)

    hotspots.forEach((h) => {
      const radius = Math.max(10, (h.count / maxCount) * 40)
      const color = RISK_COLORS[h.risk_level] || '#0FA3A3'

      L.circleMarker([h.lat, h.lng], {
        radius,
        fillColor: color,
        color: color,
        weight: 2,
        opacity: 0.8,
        fillOpacity: 0.3,
      })
        .addTo(mapRef.current!)
        .bindPopup(
          `<div style="color:#0B1B2B;font-family:Inter,sans-serif">
            <strong>${h.district}</strong><br/>
            ${h.count} ${t('common.reports')}<br/>
            <span style="color:${color}">●</span> ${h.risk_level} Risk
          </div>`,
        )
    })
  }, [hotspots, t])

  return (
    <div ref={containerRef} className="w-full rounded-xl" style={{ height: '400px', zIndex: 1 }} />
  )
}
