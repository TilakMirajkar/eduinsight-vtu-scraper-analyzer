import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { createScrapeJob, getScrapeJobStatus } from '@/api/scraper'

const TERMINAL = ['completed', 'failed']

/**
 * Returns:
 *   createJob(formData)  — fire-and-forget mutation
 *   jobId                — set once job is created
 *   status               — live-polled job object
 *   isPending            — mutation in-flight
 *   error                — creation error
 *   resetJob             — clear state to go back to the form
 */
export function useScrapeJob() {
  const [jobId, setJobId] = useState(null)
  const queryClient = useQueryClient()

  const mutation = useMutation({
    mutationFn: createScrapeJob,
    onSuccess: (data) => setJobId(data.id),
  })

  const isTerminal = (data) => TERMINAL.includes(data?.status)

  const { data: jobStatus } = useQuery({
    queryKey: ['scrapeJob', jobId],
    queryFn: () => getScrapeJobStatus(jobId),
    enabled: !!jobId,
    refetchInterval: (query) =>
      isTerminal(query.state.data) ? false : 2000,
  })

  function resetJob() {
    setJobId(null)
    if (jobId) queryClient.removeQueries({ queryKey: ['scrapeJob', jobId] })
    mutation.reset()
  }

  return {
    createJob: mutation.mutate,
    jobId,
    jobStatus,
    isCreating: mutation.isPending,
    createError: mutation.error,
    resetJob,
  }
}