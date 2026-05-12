import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Loader2, ArrowRight, RotateCcw, CheckCircle2, XCircle, Clock } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useScrapeJob } from '@/hooks/useScrapeJob'

const STATUS_CONFIG = {
  pending:   { label: 'Pending',   variant: 'pending',   Icon: Clock },
  running:   { label: 'Scraping…', variant: 'running',   Icon: Loader2 },
  completed: { label: 'Completed', variant: 'completed', Icon: CheckCircle2 },
  failed:    { label: 'Failed',    variant: 'failed',    Icon: XCircle },
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

export default function ScrapePage() {
  const navigate = useNavigate()
  const { createJob, jobId, jobStatus, isCreating, createError, resetJob } = useScrapeJob()

  const [form, setForm] = useState({
    usn_prefix: '',
    usn_sequence: '',
    exam_semester: '',
    result_url: '',
  })
  const [formError, setFormError] = useState('')

  function handleChange(e) {
    setFormError('')
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }))
  }

  function handleSemesterChange(value) {
    setForm((f) => ({ ...f, exam_semester: value }))
  }

  function handleSubmit(e) {
    e.preventDefault()
    setFormError('')
    const { usn_prefix, usn_sequence, exam_semester, result_url } = form
    if (!usn_prefix || !usn_sequence || !exam_semester || !result_url) {
      setFormError('Please fill in all required fields.')
      return
    }
    createJob({
      usn_prefix,
      usn_sequence,
      exam_semester: parseInt(exam_semester),
      result_url,
    })
  }

  const isJobActive = !!jobId
  const isDone = jobStatus?.status === 'completed'
  const isFailed = jobStatus?.status === 'failed'
  const progress = jobStatus?.progress ?? 0

  return (
    <main className="min-h-screen flex flex-col items-center justify-center px-4">
      <div className="w-full max-w-lg animate-fade-in">

        {!isJobActive ? (
          /* ── FORM STATE ── */
          <>
            <div className="mb-10 text-center">
              <h1 className="text-3xl font-semibold tracking-tight mb-2">
                Welcome to EduInsight
              </h1>
              <p className="text-muted-foreground text-sm">
                Fill the form to start the automated scraping process
              </p>
            </div>

            <form onSubmit={handleSubmit} noValidate className="space-y-4">
              {/* Row 1: Prefix + Semester */}
              <div className="grid grid-cols-2 gap-3">
                <div className="space-y-1.5">
                  <Label htmlFor="usn_prefix">Prefix USN</Label>
                  <Input
                    id="usn_prefix"
                    name="usn_prefix"
                    placeholder="2AG21CS"
                    value={form.usn_prefix}
                    onChange={handleChange}
                    autoComplete="off"
                    spellCheck={false}
                    style={{ textTransform: 'uppercase' }}
                  />
                </div>
                <div className="space-y-1.5">
                  <Label htmlFor="exam_semester">Semester</Label>
                  <Select onValueChange={handleSemesterChange} value={form.exam_semester}>
                    <SelectTrigger id="exam_semester">
                      <SelectValue placeholder="Select…" />
                    </SelectTrigger>
                    <SelectContent>
                      {Array.from({ length: 8 }, (_, i) => i + 1).map((sem) => (
                        <SelectItem key={sem} value={String(sem)}>
                          Semester {sem}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              {/* Row 2: Range */}
              <div className="space-y-1.5">
                <Label htmlFor="usn_sequence">Range</Label>
                <Input
                  id="usn_sequence"
                  name="usn_sequence"
                  placeholder="1-60  or  1,2,5-10"
                  value={form.usn_sequence}
                  onChange={handleChange}
                  autoComplete="off"
                />
              </div>

              {/* Row 3: URL */}
              <div className="space-y-1.5">
                <Label htmlFor="result_url">Result URL</Label>
                <Input
                  id="result_url"
                  name="result_url"
                  type="url"
                  placeholder="https://results.vtu.ac.in/DJcbcs25/index.php"
                  value={form.result_url}
                  onChange={handleChange}
                  autoComplete="off"
                  spellCheck={false}
                />
              </div>

              {/* Error */}
              {(formError || createError) && (
                <p className="text-sm text-destructive animate-fade-in">
                  {formError || createError?.message}
                </p>
              )}

              <Button
                type="submit"
                size="lg"
                className="w-full mt-2"
                disabled={isCreating}
              >
                {isCreating ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Starting…
                  </>
                ) : (
                  'Start the automated process'
                )}
              </Button>
            </form>

            <p className="mt-6 text-center text-xs text-muted-foreground leading-relaxed">
              Once the process is finished, your Excel file<br />will be ready to download
            </p>
          </>
        ) : (
          /* ── PROGRESS STATE ── */
          <div className="space-y-6 animate-fade-in">
            <div className="text-center">
              <h1 className="text-2xl font-semibold tracking-tight mb-1.5">
                {isDone ? 'Scraping complete' : isFailed ? 'Scraping failed' : 'Scraping in progress'}
              </h1>
              <p className="text-sm text-muted-foreground">
                Job ID <span className="font-mono text-foreground">{jobId}</span>
                {jobStatus?.usn_prefix && (
                  <> · <span className="font-mono">{jobStatus.usn_prefix}</span></>
                )}
              </p>
            </div>

            {/* Status + Progress */}
            <div className="rounded-xl border border-border p-4 space-y-3">
              <div className="flex items-center justify-between">
                <StatusBadge status={jobStatus?.status ?? 'pending'} />
                <span className="text-sm font-mono text-muted-foreground">
                  {progress}%
                </span>
              </div>
              <Progress value={progress} />
            </div>

            {/* Log */}
            {jobStatus?.error_log && (
              <div className="space-y-1.5">
                <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  Log
                </p>
                <pre className="rounded-xl border border-border bg-muted/40 p-3.5 text-xs font-mono text-foreground leading-relaxed overflow-y-auto max-h-52 whitespace-pre-wrap break-words">
                  {jobStatus.error_log}
                </pre>
              </div>
            )}

            {/* Actions */}
            <div className="flex gap-2">
              {isDone && (
                <Button
                  size="lg"
                  className="flex-1"
                  onClick={() => navigate('/analyze', { state: { jobId } })}
                >
                  Analyze Results
                  <ArrowRight className="h-4 w-4" />
                </Button>
              )}
              <Button
                variant={isDone ? 'outline' : 'secondary'}
                size={isDone ? 'lg' : 'lg'}
                className={isDone ? '' : 'flex-1'}
                onClick={resetJob}
              >
                <RotateCcw className="h-4 w-4" />
                {isDone ? 'New job' : 'Cancel'}
              </Button>
            </div>

            {isDone && (
              <p className="text-center text-xs text-muted-foreground">
                Click <strong>Analyze Results</strong> to generate your Excel report and charts
              </p>
            )}
          </div>
        )}
      </div>
    </main>
  )
}