import client from './client'


export async function createScrapeJob(data) {
  const res = await client.post('/scraper/jobs/', data)
  return res.data
}

export async function getScrapeJobStatus(jobId) {
  const res = await client.get(`/scraper/jobs/${jobId}/status/`)
  return res.data
}