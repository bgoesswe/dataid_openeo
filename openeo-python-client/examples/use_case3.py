import openeo
import logging
import time
logging.basicConfig(level=logging.INFO)

''' 1. Researcher A runs an experiment (job A) at the EODC back end  '''
logging.info("1. Researcher A runs an experiment (job A) at the EODC back end")
LOCAL_EODC_DRIVER_URL = "http://openeo.local.127.0.0.1.nip.io"
logging.info("Connecting to the local back end {}...".format(LOCAL_EODC_DRIVER_URL))
con = openeo.connect(LOCAL_EODC_DRIVER_URL)

con.update_file(None, False)
# Choose dataset
processes = con.get_processes()
pgA = processes.get_collection(name="s2a_prd_msil1c")
pgA = processes.filter_daterange(pgA, extent=["2017-05-01", "2017-05-31"])
pgA = processes.filter_bbox(pgA, west=10.288696, south=45.935871, east=12.189331, north=46.905246, crs="EPSG:4326")

# Choose processes
pgA = processes.ndvi(pgA, nir="B08", red="B04")
pgA = processes.min_time(pgA)
logging.info("Preparing Porcess graph for Job A...")
# Create job A out of the process graph A (pgA)
logging.info("Creating Job A and retrieving Job A ID...")
jobA = con.create_job(pgA.graph)
logging.info("Job A with ID {} created...".format(jobA.job_id))
logging.info("Starting Job A...")
jobA.start_job()

# Wait until the job execution was finished
logging.info("Job A Processing...")
desc = jobA.describe_job
while desc["status"] == "submitted":
    desc = jobA.describe_job


''' 2. Researcher B re-runs the same experiment (job B).  '''
logging.info("2. Researcher B re-runs the same experiment (job B).")
# Get the already executed job A by Id
from openeo.rest.job import RESTJob

jobA_new = RESTJob(jobA.job_id, con)

# Get process graph of job A and create new job B with it
pgA = jobA_new.describe_job["process_graph"]

logging.info("Creating Job B and retrieving Job B ID...")
jobB = con.create_job(pgA)
logging.info("Job B with ID {} created...".format(jobB.job_id))
logging.info("Starting Job B...")
jobB.start_job()


''' 3. Researcher runs a different experiment (job C).  '''
logging.info("3. Researcher runs a different experiment (job C).")
# Choose dataset
processes = con.get_processes()
pgC = processes.get_collection(name="s2a_prd_msil1c")
pgC = processes.filter_daterange(pgC, extent=["2017-05-01", "2017-05-31"])
pgC = processes.filter_bbox(pgC, west=10.288696, south=45.935871, east=12.189331, north=46.905246, crs="EPSG:4326")

# Choose processes
pgC = processes.ndvi(pgC, nir="B08", red="B04")
pgC = processes.max_time(pgC)
logging.info("Preparing Porcess graph for Job C...")
# Create job C out of the process graph C (pgC)

logging.info("Creating Job C and retrieving Job C ID...")
jobC = con.create_job(pgC.graph) # differs from job A
logging.info("Job C with ID {} created...".format(jobC.job_id))
logging.info("Starting Job C...")
time.sleep(2)
jobC.start_job()

# Wait until the job execution was finished
logging.info("Job C Processing...")
desc = jobC.describe_job
while desc["status"] == "submitted":
    time.sleep(2)
    desc = jobC.describe_job

''' 4. Researcher wants to compare the jobs by their environment and outcome. '''
logging.info("4. Researcher wants to compare the jobs by their environment and outcome.")
diffAB = jobA.diff(jobB)
diffAC = jobA.diff(jobC)
logging.info("diffAB: ")
logging.info(diffAB)
logging.info("diffAB: Only Differences")
logging.info(diffAB["different"])
logging.info("diffAC: ")
logging.info(diffAC)
logging.info("diffAC: Only Differences")
logging.info(diffAC["different"])
logging.info("Finished Use Case 3")
