import openeo
import logging
import time
from datetime import datetime

logging.basicConfig(level=logging.INFO)


GEE_DRIVER_URL = "http://openeo.local.127.0.0.1.nip.io"

OUTPUT_FILE = "/tmp/openeo_gee_output.png"

user = "group1"
password = "test123"

#connect with GEE backend
#session = openeo.session("nobody", GEE_DRIVER_URL)


con = openeo.connect(GEE_DRIVER_URL, auth_options={})

timestamp = datetime.now()

version = con.version(timestamp)

#date = datetime.strptime('2019-03-15 15:44:25.410621', '%Y-%m-%d %H:%M:%S.%f')

#Test Connection
print(con.list_processes())
print(con.list_collections())
#print(con.describe_collection("s2a_prd_msil1c"))


# Test Capabilities
cap = con.capabilities

print(cap.version())
print(cap.list_features())
print(cap.currency())
print(cap.list_plans())

# Test Processes

processes = con.get_processes()
pg = processes.get_collection(name="s2a_prd_msil1c")
print(pg.graph)
pg = processes.filter_daterange(pg, extent=["2017-01-01", "2017-01-31"])
print(pg.graph)
pg = processes.filter_bbox(pg, west=9.497682, south=46.517296, east=17.171631, north=49.041469, crs="EPSG:4326")
print(pg.graph)
pg = processes.ndvi(pg, nir="B08", red="B04")
print(pg.graph)
pg = processes.min_time(pg)
print(pg.graph)


# Test Job

job = con.create_job(pg.graph)

#job2 = con.create_job(pg.graph)
print(job.job_id)
print(job.start_job())
time.sleep(5)
#job2.start_job()
time.sleep(5)
#job_comp = job.diff(job2)
#job_desc = job.get_data_pid()
#job_desc = job.get_backend_version()
job_desc = job.describe_job()
print(job_desc)

#job.download_results("/tmp/testfile")
