
import './App.css'
import './job.css'
import { useState, useEffect } from 'react'
import { get_jobs } from './job-panel'
import type { Job } from './job-panel'

function App() {

  const [jobs, set_jobs] = useState<Job[]>([])
  
  useEffect(() => {
    fetch('/jobs', {
      headers: { 'Cache-Control': 'no-cache' }
    })
      .then(res => res.json())
      .then(data => set_jobs(data))
  }, [])

  async function update_status(job: Job, status: String) {
      await fetch('/jobs', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ job_name: job.job_name, company: job.company, new_status:  status})
      })
      fetch('/jobs', {
        headers: { 'Cache-Control': 'no-cache' }
      })
        .then(res => res.json())
        .then(data => set_jobs(data))
  }

  console.log(jobs)


  return (
    <>
      <div>
        
        <div className='grid-border'>
          <h1>Unmarked Jobs</h1>

          {get_jobs(jobs, "unmarked", update_status)}
        </div>

        <div className='grid-border'>
          <h1>Applied Jobs</h1>

          {get_jobs(jobs, "applied", update_status)}
        </div>

        <div className='grid-border'>
          <h1>Discarded Jobs</h1>

          {get_jobs(jobs, "discarded", update_status)}
        </div>
        

      </div>
    </>
  )
}

export default App
