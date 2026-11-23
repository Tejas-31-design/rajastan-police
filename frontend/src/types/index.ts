// Shared TypeScript types

export interface Signal {
  name: string
  weight: number
  triggered: boolean
}

export interface CheckResponse {
  risk_score: number
  label: 'Safe' | 'Suspicious' | 'High Risk'
  reasons: string[]
  indicators: Record<string, any>
  next_steps: string[]
  signals: Signal[]
}

export interface Campaign {
  id: number
  name: string
  created_at: string
  updated_at: string
  report_count: number
  risk_level: string
  status: string
  district: string
  description: string
  indicators: Record<string, string[]>
}

export interface Report {
  id: number
  created_at: string
  source_type: string
  content: string
  risk_score: number
  label: string
  reasons: string[]
  indicators: Record<string, any>
  district: string
  campaign_id: number | null
}

export interface Indicator {
  id: number
  type: string
  value: string
  report_count: number
  first_seen: string
  last_seen: string
}

export interface GraphNode {
  id: string
  label: string
  type: string
  risk_score?: number
  district?: string
  label_risk?: string
  report_count?: number
  x?: number
  y?: number
  vx?: number
  vy?: number
  fx?: number | null
  fy?: number | null
}

export interface GraphLink {
  source: string | GraphNode
  target: string | GraphNode
  label: string
}

export interface CampaignDetail {
  campaign: Campaign
  reports: Report[]
  indicators: Indicator[]
  graph: { nodes: GraphNode[]; links: GraphLink[] }
  timeline: Array<{
    date: string
    event: string
    district: string
    risk_level: string
  }>
}

export interface DashboardStats {
  reports_today: number
  active_campaigns: number
  high_risk_domains: number
  top_district: string
  total_reports: number
  resolved_campaigns: number
}

export interface TrendPoint {
  date: string
  reports: number
  high_risk: number
}

export interface DistrictHotspot {
  district: string
  lat: number
  lng: number
  count: number
  risk_level: string
}

export interface LiveEvent {
  id: string
  timestamp: string
  type: string
  message: string
  district: string
  risk_level: string
}
