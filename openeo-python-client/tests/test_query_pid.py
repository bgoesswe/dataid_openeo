
from unittest import TestCase
import openeo
from .testdata.equal_process_graphs import equal_process_graphs, process_graph_filterorder
from .testdata.diff_process_graphs import diff_process_graphs
import time
DRIVER_URL = "http://openeo.local.127.0.0.1.nip.io"

class TestQueryPID(TestCase):

    def setUp(self):
        self.con = openeo.connect(DRIVER_URL, auth_options={})
        self.con.resetdb()
        self.maxDiff=None

    def tearDown(self):
        self.con.resetdb()

    def test_process_graphs_equal(self):
        for pg1 in equal_process_graphs:
            for pg2 in equal_process_graphs:
                self.assertDictEqual(pg1, pg2)

    def test_eq_pgs(self):

        job_list = []
        for graph in equal_process_graphs:
            #print(graph)
            #time.sleep(2)
            job = self.con.create_job(graph)
            job.start_job()
            job_list.append(job)

        for job in job_list:
            desc = job.describe_job
            while desc["status"] == "submitted":
                desc = job.describe_job

        for job1 in job_list:
            for job2 in job_list:
                self.assertEqual(job1.get_data_pid(), job2.get_data_pid())

    def test_filterorder_eq_pgs(self):

        job_list = []
        for graph in process_graph_filterorder:
            #print(graph)
            job = self.con.create_job(graph)
            job.start_job()
            job_list.append(job)

        for job in job_list:
            desc = job.describe_job
            while desc["status"] == "submitted":
                desc = job.describe_job

        for job1 in job_list:
            for job2 in job_list:
                self.assertEqual(job1.get_data_pid(), job2.get_data_pid())

    def test_diff_pgs(self):

        job_list = []
        for graph in diff_process_graphs:
            #print(graph)
            job = self.con.create_job(graph)
            job.start_job()
            job_list.append(job)

        for job in job_list:
            desc = job.describe_job
            while desc["status"] == "submitted":
                desc = job.describe_job

        for job1 in job_list:
            for job2 in job_list:
                if job1.job_id != job2.job_id:
                    self.assertNotEqual(job1.get_data_pid(), job2.get_data_pid())
