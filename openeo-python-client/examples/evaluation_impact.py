import openeo
import logging

# west, south, east, north
datasets = [
{"west": 10.288696, "south": 45.935871, "east": 12.189331, "north": 46.905246, "crs": "EPSG:4326", "begin": "2017-05-01", "end": "2017-05-31"}, # running example
{"west": 26.330109, "south": -16.023376, "east": 28.171692, "north": -15.253714, "crs": "EPSG:4326", "begin": "2006-03-30", "end": "2006-03-30"}, # http:// dx.doi.org/ 10.3390/ rs8050402 1
{"west": 26.830673, "south": -15.307366, "east": 27.052460, "north": -15.113227, "crs": "EPSG:4326", "begin": "2007-03-30", "end": "2007-03-30"}, # http:// dx.doi.org/ 10.3390/ rs8050402 2
{"west": 25.563812, "south": -14.429360, "east": 26.092529, "north": -13.980713, "crs": "EPSG:4326", "begin": "2006-03-29", "end": "2006-03-31"}, # http:// dx.doi.org/ 10.3390/ rs8050402 3
{"west": -2.449951, "south": 51.771239, "east": -2.239838, "north": 51.890901, "crs": "EPSG:4326", "begin": "2007-07-23", "end": "2007-07-23"}, # http:// dx.doi.org/ 10.1016/ j.jag.2014.12.001 1
{"west": -2.449951, "south": 51.771239, "east": -2.239838, "north": 51.890901, "crs": "EPSG:4326", "begin": "2005-08-22", "end": "2005-08-22"}, # http:// dx.doi.org/ 10.1016/ j.jag.2014.12.001 2
{"west": -2.449951, "south": 51.771239, "east": -2.239838, "north": 51.890901, "crs": "EPSG:4326", "begin": "2007-07-23", "end": "2007-07-24"}, # http:// dx.doi.org/ 10.1016/j.jag.2016.12.003 1
{"west": 16.506958, "south": 47.529257, "east": 17.188110, "north": 48.022998, "crs": "EPSG:4326", "begin": "2007-07-23", "end": "2007-07-24"}, # Big Data Infrastructures for Processing Sentinel Data, Wolfgang Wagner
{"west": 104.276733, "south": 8.423470, "east": 106.809082, "north": 11.156845, "crs": "EPSG:4326", "begin": "2007-01-01", "end": "2011-01-01"}, # THE USE OF SAR BACKSCATTER TIME SERIES FOR CHARACTERISING RICE PHENOLOGY, DUY NGUYEN
]

logging.basicConfig(level=logging.INFO)
logging.info("--- Data Changes Evaluation ---")
''' 1. Run Job A, which creates query PID-A. Get file list of PID-A '''
logging.info("1. Run Job A, which creates query PID-A. Get file list of PID-A")
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

# re-execute query and get the resulting file list from the back end
pidA = jobA.get_data_pid()
file_list = con.get_filelist(pidA)
logging.info("Query re-execution filelist: {}".format(file_list))

''' 2. Update one of the resulting files of the PID-A query  '''
# Use flag on the back end to switch to the simulation CSW back end.
logging.info("Update one of the resulting files of the PID-A query")
con.set_mockupstate(deleted=True)
file2_list = con.get_filelist(pidA)

''' 3. Researcher A cites the input data in a publication  '''
logging.info("3. Researcher A cites the input data in a publication")
''' 4. Researcher B uses the same input data of job A for job B  '''
logging.info(str(file_list["input_files"] == file2_list["input_files"]))
logging.info("4. Researcher B uses the same input data of job A for job B")
# Take input data of job A by using the input data pid A of job A
pgB = processes.get_collection(data_pid=pidA)

# Choose processes
pgB = processes.ndvi(pgB, nir="B08", red="B04")
pgB = processes.max_time(pgB)
logging.info("Preparing Porcess graph for Job B using data PID from job A {}...".format(pidA))
# Create job B out of the process graph B (pgB)
logging.info("Preparing Porcess graph for Job B using data PID from job A {}...")
jobB = con.create_job(pgB.graph)
logging.info("Creating and starting job B with id {}".format(jobB.job_id))
jobB.start_job()

logging.info("Job A Processing...")
desc = jobB.describe_job
while desc["status"] == "submitted":
    desc = jobB.describe_job
logging.info("Finished processing job B")

logging.info("JobB data pid: {}".format(jobB.get_data_pid_url()))

logging.info("Finished Use Case 1")

