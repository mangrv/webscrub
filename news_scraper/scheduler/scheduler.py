import sys
import os
import time
import datetime
import schedule
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cms_integration.integrator import files_processed, articles_posted, failed_uploads


start_time = time.time()

def job_abc7():
    global files_processed, articles_posted, failed_uploads
    print("Running ABC7 scraper...")
    # Run the scraper and capture the output
    output = os.popen("python3 ../run-abc7-scraper.py").read()  # Adjusted path
    # Parse the output and update the counters
    update_counters(output)
    print("Finished running ABC7 scraper.")
    print_counters()

def job_nbc2():
    global files_processed, articles_posted, failed_uploads
    print("Running NBC2 scraper...")
    # Run the scraper and capture the output
    output = os.popen("python3 ../run-nbc2-scraper.py").read()  # Adjusted path
    # Parse the output and update the counters
    update_counters(output)
    print("Finished running NBC2 scraper.")
    print_counters()

def job_nnw():
    global files_processed, articles_posted, failed_uploads
    print("Running NNW scraper...")
    # Run the scraper and capture the output
    output = os.popen("python3 ../run-nnw-scraper.py").read()  # Adjusted path
    # Parse the output and update the counters
    update_counters(output)
    print("Finished running NNW scraper.")
    print_counters()    

def job_fox4now():
    global files_processed, articles_posted, failed_uploads
    print("Running Fox4Now scraper...")
    # Run the Fox4Now scraper
    output = os.popen("python3 ../run-fox4-scraper.py").read()
    update_counters(output)
    print("Finished running Fox4Now scraper.")
    print_counters()

def update_counters(output):
    global files_processed, articles_posted, failed_uploads
    # This function should parse the output of the scraper scripts
    # and update the files_processed, articles_posted, and failed_uploads variables
    # For now, let's just increment the counters for each run
    files_processed += 1
    articles_posted += 1
    failed_uploads += 1    

def print_counters():
    print(f"Files processed: {files_processed}")
    print(f"Articles posted: {articles_posted}")
    print(f"Failed uploads: {failed_uploads}")
    end_time = time.time()
    print(f"Total elapsed time for the script: {end_time - start_time} seconds")
    next_run_time = datetime.datetime.now() + datetime.timedelta(minutes=60)
    print(f"Next run time: {next_run_time}")

print("Scheduling jobs...")
schedule.every().hour.do(job_abc7)
schedule.every().hour.do(job_nbc2)
schedule.every().hour.do(job_nnw)
schedule.every().hour.do(job_fox4now)
print("Jobs scheduled.")

# Delay start of jobs by 1 hour
# print("Delaying start of jobs by 1 hour...")
# time.sleep(3600)

# Run jobs immediately
job_abc7()
job_nbc2()
job_nnw()

# Then start the regular scheduling
while True:
    schedule.run_pending()
    time.sleep(60)