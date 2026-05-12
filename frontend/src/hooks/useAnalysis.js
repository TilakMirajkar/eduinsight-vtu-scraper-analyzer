import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { startAnalysis, getAnalysisResult } from '@/api/analyzer'

const TERMINAL = ['completed', 'failed']

/**
 * Returns:
 *   triggerAnalysis(jobId)  — starts analysis for a given job
 *   result                  — live-polled analysis result
 *   isTriggering            — mutation in-flight
 *   triggerError            — error from triggering
 *   reset                   — clear state
 */
export function useAnalysis() {
  const [activeJobId, setActiveJobId] = useState(null)
  const queryClient = useQueryClient()

  const mutation = useMutation({
    mutationFn: startAnalysis,
    onSuccess: (_, jobId) => setActiveJobId(jobId),
  })

  const isTerminal = (data) => TERMINAL.includes(data?.status)

  const { data: result } = useQuery({
    queryKey: ['analysisResult', activeJobId],
    queryFn: () => getAnalysisResult(activeJobId),
    enabled: !!activeJobId,
    refetchInterval: (query) =>
      isTerminal(query.state.data) ? false : 2000,
  })

  function reset() {
    setActiveJobId(null)
    if (activeJobId)
      queryClient.removeQueries({ queryKey: ['analysisResult', activeJobId] })
    mutation.reset()
  }

  return {
    triggerAnalysis: (jobId) => mutation.mutate(jobId),
    activeJobId,
    result,
    isTriggering: mutation.isPending,
    triggerError: mutation.error,
    reset,
  }
}