import { useState, useEffect } from 'react'
import {
  Loader2,
  Download,
  BarChart3,
  FileSpreadsheet,
  CheckCircle2,
  XCircle,
  Clock,
  Play,
  ChevronLeft,
  ChevronRight,
  Eye,
  X
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { getScrapeJobs } from '@/api/scraper'
import { startAnalysis, getDownloadExcelUrl, getDownloadChartUrl } from '@/api/analyzer'

export default function AnalyzePage() {
  const [jobs, setJobs] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [triggeringId, setTriggeringId] = useState(null)
  
  const [currentPage, setCurrentPage] = useState(1)
  const [pagination, setPagination] = useState({ count: 0, next: null, previous: null })

  const [viewJobModalId, setViewJobModalId] = useState(null)

  useEffect(() => {
    fetchJobs(currentPage)
    const interval = setInterval(() => fetchJobs(currentPage), 5000)
    return () => clearInterval(interval)
  }, [currentPage])

  async function fetchJobs(page) {
    try {
      const data = await getScrapeJobs(page)
      
      if (data.results) {
        setJobs(data.results)
        setPagination({
          count: data.count,
          next: data.next,
          previous: data.previous
        })
      } else {
        setJobs(data)
        setPagination({ count: data.length, next: null, previous: null })
      }
    } catch (error) {
      console.error("Failed to fetch jobs", error)
    } finally {
      setIsLoading(false)
    }
  }

  async function handleRunAnalysis(jobId) {
    try {
      setTriggeringId(jobId)
      await startAnalysis(jobId)
      await fetchJobs(currentPage)
    } catch (error) {
      console.error("Failed to trigger analysis", error)
      alert("Failed to start analysis. Please try again.")
    } finally {
      setTriggeringId(null)
    }
  }

  function getStatusBadge(status) {
    switch (status) {
      case 'completed':
        return <Badge variant="completed" className="bg-green-100 text-green-800"><CheckCircle2 className="h-3 w-3 mr-1" /> Done</Badge>
      case 'running':
        return <Badge variant="running" className="bg-blue-100 text-blue-800"><Loader2 className="h-3 w-3 mr-1 animate-spin" /> Running</Badge>
      case 'failed':
        return <Badge variant="failed" className="bg-red-100 text-red-800"><XCircle className="h-3 w-3 mr-1" /> Failed</Badge>
      default:
        return <Badge variant="pending" className="bg-gray-100 text-gray-800"><Clock className="h-3 w-3 mr-1" /> Pending</Badge>
    }
  }

  return (
    <main className="min-h-screen py-16 px-4 md:px-8 max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-semibold tracking-tight">Jobs Dashboard</h1>
        <p className="text-muted-foreground">Monitor scraping progress and download analysis reports.</p>
      </div>

      <div className="bg-card border border-border rounded-xl shadow-sm flex flex-col">
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="bg-muted/50 text-muted-foreground uppercase text-xs">
              <tr>
                <th className="px-6 py-4 font-medium whitespace-nowrap">Job ID</th>
                <th className="px-6 py-4 font-medium whitespace-nowrap">Batch Details</th>
                <th className="px-6 py-4 font-medium whitespace-nowrap">Scrape Status</th>
                <th className="px-6 py-4 font-medium text-right whitespace-nowrap">Analysis & Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {isLoading && jobs.length === 0 ? (
                <tr>
                  <td colSpan="4" className="px-6 py-8 text-center text-muted-foreground">
                    <Loader2 className="h-6 w-6 animate-spin mx-auto mb-2" />
                    Loading jobs...
                  </td>
                </tr>
              ) : jobs.length === 0 ? (
                <tr>
                  <td colSpan="4" className="px-6 py-8 text-center text-muted-foreground">
                    No jobs found. Go to the Scrape page to start one.
                  </td>
                </tr>
              ) : (
                jobs.map((job) => (
                  <tr key={job.id} className="hover:bg-muted/20 transition-colors">
                    <td className="px-6 py-4 font-mono font-medium">#{job.id}</td>
                    <td className="px-6 py-4">
                      <div className="font-medium">{job.usn_prefix}</div>
                      <div className="text-xs text-muted-foreground mt-0.5">
                        Sem {job.exam_semester} • Range: {
                          Array.isArray(job.usn_sequence) ? job.usn_sequence.join(', ') : job.usn_sequence
                        }
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center gap-2">
                        {getStatusBadge(job.status)}
                        {job.status === 'running' && (
                          <span className="text-xs font-mono text-muted-foreground">{job.progress}%</span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 flex justify-end items-center gap-2 min-w-[280px]">
                      
                      {job.status !== 'completed' && job.status !== 'failed' && (
                        <span className="text-xs text-muted-foreground italic">Waiting for scrape...</span>
                      )}

                      {job.status === 'failed' && (
                        <span className="text-xs text-red-500 italic truncate max-w-[150px]" title={job.error_log}>
                          Scrape failed
                        </span>
                      )}

                      {job.status === 'completed' && (
                        <>
                          {!job.analysis_status && (
                            <Button 
                              size="sm" 
                              onClick={() => handleRunAnalysis(job.id)}
                              disabled={triggeringId === job.id}
                            >
                              {triggeringId === job.id ? <Loader2 className="h-4 w-4 animate-spin mr-1" /> : <Play className="h-4 w-4 mr-1" />}
                              Run Analysis
                            </Button>
                          )}

                          {job.analysis_status === 'running' && (
                            <div className="flex items-center text-sm text-blue-600 gap-2 px-3 py-1 bg-blue-50 rounded-md">
                              <Loader2 className="h-4 w-4 animate-spin" /> Analyzing...
                            </div>
                          )}

                          {job.analysis_status === 'completed' && (
                            <Button 
                              variant="outline" 
                              size="sm" 
                              onClick={() => setViewJobModalId(job.id)}
                              className="text-muted-foreground hover:text-foreground"
                            >
                              <Eye className="h-4 w-4 mr-1.5" /> View Results
                            </Button>
                          )}

                          {job.analysis_status === 'failed' && (
                            <span className="text-xs text-red-500 italic">Analysis failed</span>
                          )}
                        </>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        <div className="flex items-center justify-between px-6 py-4 border-t border-border bg-muted/10">
          <span className="text-sm text-muted-foreground">
            Total Jobs: {pagination.count}
          </span>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              disabled={!pagination.previous}
              onClick={() => setCurrentPage((p) => p - 1)}
            >
              <ChevronLeft className="h-4 w-4 mr-1" /> Previous
            </Button>
            <Button
              variant="outline"
              size="sm"
              disabled={!pagination.next}
              onClick={() => setCurrentPage((p) => p + 1)}
            >
              Next <ChevronRight className="h-4 w-4 ml-1" />
            </Button>
          </div>
        </div>
      </div>

      {viewJobModalId && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-background/80 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="bg-card border border-border w-full max-w-md rounded-xl shadow-lg relative p-6">
            
            <button 
              onClick={() => setViewJobModalId(null)}
              className="absolute top-4 right-4 rounded-full p-1 hover:bg-muted transition-colors"
            >
              <X className="h-4 w-4 text-muted-foreground" />
            </button>

            <div className="mb-6">
              <h2 className="text-xl font-semibold tracking-tight">Analysis Reports</h2>
              <p className="text-sm text-muted-foreground">
                Download the generated files for Job <span className="font-mono text-foreground">#{viewJobModalId}</span>
              </p>
            </div>

            <div className="grid grid-cols-1 gap-3">
              <a 
                href={getDownloadExcelUrl(viewJobModalId)} 
                download
                className="group flex items-center justify-between p-4 rounded-lg border border-border bg-card hover:bg-muted/50 hover:border-green-300 transition-all cursor-pointer"
              >
                <div className="flex items-center gap-3">
                  <div className="p-2.5 rounded-md bg-green-100 text-green-700">
                    <FileSpreadsheet className="h-5 w-5" />
                  </div>
                  <div>
                    <h3 className="text-sm font-medium">Subject-wise Report</h3>
                    <p className="text-xs text-muted-foreground">Excel Spreadsheet (.xlsx)</p>
                  </div>
                </div>
                <Download className="h-4 w-4 text-muted-foreground group-hover:text-green-600" />
              </a>
              <a 
                href={getDownloadChartUrl(viewJobModalId)} 
                download
                className="group flex items-center justify-between p-4 rounded-lg border border-border bg-card hover:bg-muted/50 hover:border-blue-300 transition-all cursor-pointer"
              >
                <div className="flex items-center gap-3">
                  <div className="p-2.5 rounded-md bg-blue-100 text-blue-700">
                    <BarChart3 className="h-5 w-5" />
                  </div>
                  <div>
                    <h3 className="text-sm font-medium">Pass Percentage</h3>
                    <p className="text-xs text-muted-foreground">Bar Chart Image (.png)</p>
                  </div>
                </div>
                <Download className="h-4 w-4 text-muted-foreground group-hover:text-blue-600" />
              </a>
            </div>

            <div className="mt-6">
              <Button variant="outline" className="w-full" onClick={() => setViewJobModalId(null)}>
                Close
              </Button>
            </div>

          </div>
        </div>
      )}
    </main>
  )
}