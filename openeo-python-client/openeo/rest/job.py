from openeo.connection import Connection
from openeo.processgraph import ProcessGraph
from openeo.job import Job, JobResult
from typing import List
import urllib.request
import requests
from datetime import datetime


class DictDiffer(object):
    """
    Calculate the difference between two dictionaries as:
    (1) items added
    (2) items removed
    (3) keys same in both but changed values
    (4) keys same in both and unchanged values
    """
    def __init__(self, current_dict, past_dict):
        self.current_dict, self.past_dict = current_dict, past_dict
        self.set_current, self.set_past = set(current_dict.keys()), set(past_dict.keys())
        self.intersect = self.set_current.intersection(self.set_past)
    def added(self):
        return self.set_current - self.intersect
    def removed(self):
        return self.set_past - self.intersect
    def changed(self):
        return set(o for o in self.intersect if self.past_dict[o] != self.current_dict[o])
    def unchanged(self):
        return set(o for o in self.intersect if self.past_dict[o] == self.current_dict[o])

class RESTJobResult(JobResult):
    def __init__(self, url):
        self.url = url

    def save_as(self, target_file):
        urllib.request.urlretrieve(self.url, target_file)


class RESTJob(Job):

    def __init__(self, job_id: str, connection: Connection):
        super().__init__(job_id)
        self.connection = connection
        self._cached_desc = None


    def get_remote_desc(self):
        request = self.connection.get("/jobs/{}".format(self.job_id))
        if request.status_code == 200 or request.status_code == 201:
            response = self.connection.parse_json_response(request)

            if "metrics" in response:
                if response["metrics"]["input_data"] in str(response["process_graph"]):
                    if "data_pid" in str(response["process_graph"]):
                        response["logs"] = "Warning: data PID changed"
                        response["status"] = "finished with warnings"

                response["context_model"] = response["metrics"]
            return response
        #elif request.status_code == 500:
        #    return {"status": "error"}
        else:
            return {"status": "submitted"}

    @property
    def describe_job(self):
        """ Get all job information."""
        # GET /jobs/{job_id}

        if self._cached_desc is None:
            self._cached_desc = self.get_remote_desc()

        else:
            if self._cached_desc["status"] == "submitted":
                self._cached_desc = self.get_remote_desc()

        return self._cached_desc

    def update_job(self, process_graph=None, output_format=None,
                   output_parameters=None, title=None, description=None,
                   plan=None, budget=None, additional=None):
        """ Update a job."""
        # PATCH /jobs/{job_id}
        pass

    def delete_job(self):
        """ Delete a job."""
        # DELETE /jobs/{job_id}
        request = self.connection.delete("/jobs/{}".format(self.job_id), postdata=None)

        return request.status_code

    def estimate_job(self):
        """ Calculate an time/cost estimate for a job."""
        # GET /jobs/{job_id}/estimate
        request = self.connection.get("/jobs/{}/estimate".format(self.job_id), postdata=None)

        return self.connection.parse_json_response(request)

    def start_job(self):
        """ Start / queue a job for processing."""
        # POST /jobs/{job_id}/results
        request = self.connection.post("/jobs/{}/results".format(self.job_id), postdata=None)

        return request.status_code

    def stop_job(self):
        """ Stop / cancel job processing."""
        # DELETE /jobs/{job_id}/results
        request = self.connection.delete("/jobs/{}/results".format(self.job_id), postdata=None)

        return request.status_code
        pass

    def list_results(self, type=None):
        """ Get document with download links."""
        # GET /jobs/{job_id}/results
        pass

    def get_data_pid_url(self):
        """ Returns resolvable data PID of the job."""

        desc = self.describe_job

        input_data = ""

        if "input_data" in desc:
            input_data = desc["input_data"]

        input_data = self.connection.endpoint+"/collections/"+input_data

        return input_data

    def get_data_pid(self):
        """ Returns resolvable data PID of the job."""

        desc = self.describe_job

        input_data  = None
        if "input_data" in desc:
            input_data = desc["input_data"]

        return input_data

    def get_backend_version(self):
        """ Returns back end version dict at the time of the execution."""
        desc = self.describe_job

        backend_version = None

        if "metrics" in desc:
            if "start_time" in desc["metrics"]:
                start_time = desc["metrics"]["start_time"]
                timestamp = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S.%f')
                backend_version = self.connection.version(timestamp)

        return backend_version

    def describe_input_data(self):
        """ Returns resolvable dict about the input data PID of the job."""

        desc = self.describe_job

        if "input_data" in desc:
            input_data = desc["input_data"]
        else:
            return None

        if input_data and self.connection:
            return self.connection.describe_data_pid(input_data)
        else:
            return None

    def diff(self, target_job):
        """ Compare job context model."""

        self_cm = self.describe_job
        if "metrics" in self_cm:
            if "process_graph" in self_cm:
                self_cm["metrics"]["process_graph"] = self_cm["process_graph"]
                self_cm = self_cm["metrics"]
        else:
            return None

        target_cm = target_job.describe_job
        if "metrics" in target_cm:
            if "process_graph" in target_cm:
                target_cm["metrics"]["process_graph"] = target_cm["process_graph"]
                target_cm = target_cm["metrics"]
        else:
            return None

        job_comp = DictDiffer(self_cm, target_cm)

        output_dict = {}

        added = job_comp.added()
        removed = job_comp.removed()
        changed = job_comp.changed()
        unchanged = job_comp.unchanged()

        for elem in unchanged:
            output_dict[elem] = "EQUAL"
        for elem in added:
            if not "added" in output_dict:
                output_dict["added"] = {}
            output_dict["added"][elem] = target_cm[elem]
        for elem in removed:
            if not "removed" in output_dict:
                output_dict["removed"] = {}
            output_dict["removed"] = elem
        for elem in changed:
            if not "different" in output_dict:
                output_dict["different"] = {}
            output_dict["different"][elem] = target_cm[elem]

        return output_dict

    def download_results(self, target):
        """ Download job results."""
        # GET /jobs/{job_id}/results > ...


        download_url = "/jobs/{}/results".format(self.job_id)
        r = self.connection.get(download_url, stream = True)

        if r.status_code == 200:

            url = r.json()
            if "links" in url:
                download_url = url["links"][0]
                if "href" in download_url:
                    download_url = download_url["href"]

            auth_header = self.connection.authent.get_header()

            with open(target, 'wb') as handle:
                response = requests.get(download_url, stream=True, headers=auth_header)

                if not response.ok:
                    print (response)

                for block in response.iter_content(1024):

                    if not block:
                        break

                    handle.write(block)
        else:
            raise ConnectionAbortedError(r.text)
        return r.status_code

# TODO: All below methods are depricated (at least not specified in the coreAPI)
    def download(self, outputfile:str, outputformat=None):
        """ Download the result as a raster."""
        try:
            return self.connection.download_job(self.job_id, outputfile, outputformat)
        except ConnectionAbortedError as e:
            return print(str(e))

    def status(self):
        """ Returns the status of the job."""
        return self.connection.job_info(self.job_id)['status']

    def queue(self):
        """ Queues the job. """
        return self.connection.queue_job(self.job_id)

    def results(self) -> List[RESTJobResult]:
        """ Returns this job's results. """
        return [RESTJobResult(link['href']) for link in self.connection.job_results(self.job_id)['links']]
