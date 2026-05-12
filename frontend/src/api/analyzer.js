import client from './client'


export async function startAnalysis(jobId) {
  const res = await client.post('/analyzer/analyze/', { job_id: jobId })
  return res.data
}

export async function getAnalysisResult(jobId) {
  const res = await client.get(`/analyzer/results/${jobId}/`)
  return res.data
}

export function getDownloadExcelUrl(jobId) {
  return `/api/v1/analyzer/results/${jobId}/download/excel/`
}

export function getDownloadChartUrl(jobId) {
  return `/api/v1/analyzer/results/${jobId}/download/chart/`
}