import openeo
import logging

logging.basicConfig(level=logging.INFO)

''' 1. Researcher A runs an experiment (job A) at the EODC back end  '''
logging.info("1. Researcher A runs an experiment (job A) at the EODC back end")
LOCAL_EODC_DRIVER_URL = "http://openeo.local.127.0.0.1.nip.io"
logging.info("Connecting to the local back end {}...".format(LOCAL_EODC_DRIVER_URL))
con = openeo.connect(LOCAL_EODC_DRIVER_URL)

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
''' 2. Researcher A wants to describe the experiment environment.  '''
logging.info("2. Researcher A wants to describe the experiment environment.")
# Get context model of job A

context_model = jobA.describe_job["context_model"]

# Retrieve the information that Researcher A needs.

interpreter = context_model["interpreter"]
code_env = context_model["code_env"]
input_data = jobA.get_data_pid_url()
backend_version = jobA.get_backend_version()
logging.info("Interpreter: {}".format(interpreter))
logging.info("Code Environment: {}".format(code_env))
logging.info("Input Data PID URL: {}".format(input_data))
logging.info("Back End Version (commit): {}".format(backend_version["commit"]))
logging.info("Finished Use Case 2")