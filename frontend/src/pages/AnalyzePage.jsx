import { useState, useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import {
  Loader2,
  Download,
  BarChart3,
  FileSpreadsheet,
  CheckCircle2,
  XCircle,
  Clock,
  RefreshCw,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { useAnalysis } from '@/hooks/useAnalysis'
import { getDownloadExcelUrl, getDownloadChartUrl } from '@/api/analyzer'

const STATUS_CONFIG = {
  pending:   { label: 'Pending',    variant: 'pending',   Icon: Clock },
  running:   { label: 'Analyzing…', variant: 'running',   Icon: Loader2 },
  completed: { label: 'Completed',  variant: 'completed', Icon: CheckCircle2 },
  failed:    { label: 'Failed',     variant: 'failed',    Icon: XCircle },
}

function StatusBadge({ status }) {
  const cfg = STATUS_CONFIG[status] ?? STATUS_CONFIG.pending
  const { label, variant, Icon } = cfg
  return (
    <Badge variant={variant}>
      <Icon className={`h-3 w-3 ${status === 'running' ? 'animate-spin' : ''}`} />
      {label}
    </Badge>
  )
}

export default function AnalyzePage() {
  const location = useLocation()
  const { triggerAnalysis, activeJobId, result, isTriggering, triggerError, reset } = useAnalysis()

  const [inputJobId, setInputJobId] = useState(
    location.state?.jobId ? String(location.state.jobId) : ''
  )
  const [formError, setFormError] = useState('')

  // Auto-trigger if navigated here from ScrapePage with a job ID
  useEffect(() => {
    if (location.state?.jobId && !activeJobId) {
      triggerAnalysis(location.state.jobId)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  function handleSubmit(e) {
    e.preventDefault()
    setFormError('')
    const id = parseInt(inputJobId)
    if (!id || isNaN(id) || id < 1) {
      setFormError('Please enter a valid Job ID.')
      return
    }
    triggerAnalysis(id)
  }

  const isDone = result?.status === 'completed'
  const isFailed = result?.status === 'failed'
  const isActive = !!activeJobId

  return (
    <main className="min-h-screen flex flex-col items-center justify-center px-4">
      <div className="w-full max-w-lg animate-fade-in">

        {!isActive ? (
          /* ── FORM STATE ── */
          <>
            <div className="mb-10 text-center">
              <h1 className="text-3xl font-semibold tracking-tight mb-2">
                Analyze Results
              </h1>
              <p className="text-muted-foreground text-sm">
                Enter a completed scrape job ID to generate your report
              </p>
            </div>

            <form onSubmit={handleSubmit} noValidate className="space-y-4">
              <div className="space-y-1.5">
                <Label htmlFor="job_id">Job ID</Label>
                <Input
                  id="job_id"
                  name="job_id"
                  type="number"
                  min="1"
                  placeholder="e.g. 42"
                  value={inputJobId}
                  onChange={(e) => { setFormError(''); setInputJobId(e.target.value) }}
                />
              </div>

              {(formError || triggerError) && (
                <p className="text-sm text-destructive animate-fade-in">
                  {formError || triggerError?.message}
                </p>
              )}

              <Button
                type="submit"
                size="lg"
                className="w-full mt-2"
                disabled={isTriggering}
              >
                {isTriggering ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Starting analysis…
                  </>
                ) : (
                  <>
                    <BarChart3 className="h-4 w-4" />
                    Run Analysis
                  </>
                )}
              </Button>
            </form>

            <p className="mt-6 text-center text-xs text-muted-foreground leading-relaxed">
              Analysis generates a subject-wise Excel report,<br />
              SGPA scores, and a pass-percentage chart
            </p>
          </>
        ) : (
          /* ── RESULTS STATE ── */
          <div className="space-y-6 animate-fade-in">
            <div className="text-center">
              <h1 className="text-2xl font-semibold tracking-tight mb-1.5">
                {isDone ? 'Analysis complete' : isFailed ? 'Analysis failed' : 'Analyzing results'}
              </h1>
              <p className="text-sm text-muted-foreground">
                Job ID <span className="font-mono text-foreground">{activeJobId}</span>
              </p>
            </div>

            {/* Status card */}
            <div className="rounded-xl border border-border p-4 space-y-3">
              <div className="flex items-center justify-between">
                <StatusBadge status={result?.status ?? 'pending'} />
                {!isDone && !isFailed && (
                  <span className="text-xs text-muted-foreground">
                    This may take a minute…
                  </span>
                )}
                {result?.created_at && (
                  <span className="text-xs text-muted-foreground">
                    {new Date(result.created_at).toLocaleTimeString()}
                  </span>
                )}
              </div>
              {/* Indeterminate progress while running */}
              {!isDone && !isFailed && (
                <div className="relative h-2 w-full overflow-hidden rounded-full bg-muted">
                  <div className="absolute inset-y-0 left-0 w-1/3 bg-primary rounded-full animate-[shimmer_1.5s_ease-in-out_infinite]" />
                </div>
              )}
              {isDone && <Progress value={100} />}
            </div>

            {/* Download actions — only when completed */}
            {isDone && (
              <div className="space-y-3 animate-fade-in">
                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  Downloads
                </p>
                <div className="grid grid-cols-2 gap-3">
                  <a
                    href={getDownloadExcelUrl(activeJobId)}
                    download
                    className="block"
                  >
                    <Button variant="outline" size="lg" className="w-full gap-2">
                      <FileSpreadsheet className="h-4 w-4 text-green-600" />
                      Excel Report
                      <Download className="h-3.5 w-3.5 text-muted-foreground ml-auto" />
                    </Button>
                  </a>
                  <a
                    href={getDownloadChartUrl(activeJobId)}
                    download
                    className="block"
                  >
                    <Button variant="outline" size="lg" className="w-full gap-2">
                      <BarChart3 className="h-4 w-4 text-blue-600" />
                      Pass % Chart
                      <Download className="h-3.5 w-3.5 text-muted-foreground ml-auto" />
                    </Button>
                  </a>
                </div>
              </div>
            )}

            {/* Chart preview */}
            {isDone && result?.chart_image && (
              <div className="space-y-1.5 animate-fade-in">
                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  Pass percentage chart
                </p>
                <div className="rounded-xl border border-border overflow-hidden">
                  <img
                    src={result.chart_image}
                    alt="Subject-wise pass percentage chart"
                    className="w-full object-contain"
                  />
                </div>
              </div>
            )}

            {/* Reset */}
            <Button variant="outline" size="lg" className="w-full" onClick={reset}>
              <RefreshCw className="h-4 w-4" />
              Analyze another job
            </Button>
          </div>
        )}
      </div>
    </main>
  )
}