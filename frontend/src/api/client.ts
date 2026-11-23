import axios from 'axios'
import type { Campaign, CampaignDetail, CheckResponse, DashboardStats, DistrictHotspot, TrendPoint } from '../types'

const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
})

export const checkURL = (url: string): Promise<CheckResponse> =>
  api.post('/check/url', { url }).then(r => r.data)

export const checkSMS = (text: string): Promise<CheckResponse> =>
  api.post('/check/sms', { text }).then(r => r.data)

export const getDashboardStats = (): Promise<DashboardStats> =>
  api.get('/dashboard/stats').then(r => r.data)

export const getDashboardTrend = (): Promise<TrendPoint[]> =>
  api.get('/dashboard/trend').then(r => r.data)

export const getHotspots = (): Promise<DistrictHotspot[]> =>
  api.get('/dashboard/hotspots').then(r => r.data)

export const getCampaigns = (): Promise<Campaign[]> =>
  api.get('/campaigns').then(r => r.data)

export const getCampaign = (id: number): Promise<CampaignDetail> =>
  api.get(`/campaigns/${id}`).then(r => r.data)

export const exportPDF = (id: number): void => {
  window.open(`/api/campaigns/${id}/export-pdf`, '_blank')
}

export default api
