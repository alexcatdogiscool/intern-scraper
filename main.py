import scraper
import database
import notify



if __name__ == "__main__":
    
    # get all the jobs from the scraper functions
    funcs = scraper.get_scraper_funcs()
    jobs = []
    for f in funcs:
        jobs.extend(f())
    
    new_jobs = database.get_unique_jobs(jobs)
    
    unmarked_jobs = database.load_unmarked_jobs()
    
    notify.email_jobs(new_jobs, unmarked_jobs)
    
    
    