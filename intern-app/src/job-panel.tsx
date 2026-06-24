
import './job.css'

export interface Job {
    company: string,
    job_name: string,
    status: string,
    url: string
}




export function get_jobs(jobs: Job[], status: string, update_status: (job: Job, status: string) => void) {
    return (
        <>
        <div className='job-grid'>
            {jobs.filter(job => job.status === status).map(job => (
                <div className='job'>
                    <div className='job-title'>
                        <p><a href={job.url}>{job.job_name}</a></p>
                    </div>
                    <div className='job-company'>
                        <p>{job.company}</p>
                    </div>
                    <div className='buttons-div'>
                        <div className='button-applied' onClick={() => update_status(job, "applied")}>
                            Applied
                        </div>
                        <div className='button-discarded' onClick={() => update_status(job, "discarded")}>
                            Discard
                        </div>                        
                    </div>
                    <div className='button-unmark' onClick={() => update_status(job, "unmarked")}>
                        Unmark Job
                    </div>
                </div>
            ))}
            
        </div>
        
        </>
    )
}