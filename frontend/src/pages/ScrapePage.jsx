import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Loader2, ArrowRight, CheckCircle2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { createScrapeJob } from '@/api/scraper'

export default function ScrapePage() {
  const navigate = useNavigate()
  const [isCreating, setIsCreating] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState(false)

  const [form, setForm] = useState({
    usn_prefix: '',
    usn_sequence: '',
    exam_semester: '',
    result_url: '',
  })

  function handleChange(e) {
    setError('')
    setSuccess(false)
    setForm((f) => ({ ...f, [e.target.name]: e.target.value }))
  }

  function handleSemesterChange(value) {
    setForm((f) => ({ ...f, exam_semester: value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    const { usn_prefix, usn_sequence, exam_semester, result_url } = form
    
    if (!usn_prefix || !usn_sequence || !exam_semester || !result_url) {
      setError('Please fill in all required fields.')
      return
    }

    try {
      setIsCreating(true)
      await createScrapeJob({
        usn_prefix,
        usn_sequence,
        exam_semester: parseInt(exam_semester),
        result_url,
      })
      
      setSuccess(true)
      setForm({ usn_prefix: '', usn_sequence: '', exam_semester: '', result_url: '' })
    } catch (err) {
      setError(err?.response?.data?.message || 'Failed to start job. Please try again.')
    } finally {
      setIsCreating(false)
    }
  }

  return (
    <main className="mt-24 max-h-screen flex flex-col items-center justify-center px-4">
      <div className="w-full max-w-lg animate-fade-in">
        <div className="mb-10 text-center">
          <h1 className="text-3xl font-semibold tracking-tight mb-2">
            Start Scraping Process
          </h1>
          <p className="text-muted-foreground text-sm">
            Fill the form to trigger a new automated background task
          </p>
        </div>

        <form onSubmit={handleSubmit} noValidate className="space-y-4">
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
                    <SelectItem key={sem} value={String(sem)}>Semester {sem}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>

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

          {error && <p className="text-sm text-destructive animate-fade-in">{error}</p>}
          
          {success && (
            <div className="flex items-center gap-2 text-sm text-green-600 bg-green-50/50 p-3 rounded-md border border-green-100 animate-fade-in">
              <CheckCircle2 className="h-4 w-4" />
              Scraping started successfully in the background!
            </div>
          )}

          <div className="flex gap-3 pt-2">
            <Button type="submit" size="lg" className="flex-1" disabled={isCreating}>
              {isCreating ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
              {isCreating ? 'Starting…' : 'Start Scrape Job'}
            </Button>
            
            <Button type="button" variant="secondary" size="lg" onClick={() => navigate('/analyze')}>
              View Dashboard <ArrowRight className="h-4 w-4 ml-2" />
            </Button>
          </div>
        </form>
      </div>
    </main>
  )
}