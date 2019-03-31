""" Job Management """

from os import environ
from nameko.rpc import rpc, RpcProxy
from nameko_sqlalchemy import DatabaseSession

from hashlib import sha256
from uuid import uuid4
import json
from .models import Base, Job, Query, QueryJob
from .schema import JobSchema, JobSchemaFull
# from .exceptions import BadRequest, Forbidden, APIConnectionError
# from .dependencies.task_parser import TaskParser
# from .dependencies.validator import Validator
from .dependencies.api_connector import APIConnector
from .dependencies.template_controller import TemplateController
import time
import random
import datetime
import numpy as np
from git import Repo
import pytz
import logging

service_name = "jobs"

class ServiceException(Exception):
    """ServiceException raises if an exception occured while processing the 
    request. The ServiceException is mapping any exception to a serializable
    format for the API gateway.
    """

    def __init__(self, code: int, user_id: str, msg: str,
                 internal: bool=True, links: list=[]):
        self._service = service_name
        self._code = code
        self._user_id = user_id
        self._msg = msg
        self._internal = internal
        self._links = links

    def to_dict(self) -> dict:
        """Serializes the object to a dict.

        Returns:
            dict -- The serialized exception
        """

        return {
            "status": "error",
            "service": self._service,
            "code": self._code,
            "user_id": self._user_id,
            "msg": self._msg,
            "internal": self._internal,
            "links": self._links
        }

class JobService:
    """Management of batch processing tasks (jobs) and their results.
    """

    name = service_name
    db = DatabaseSession(Base)
    process_graphs_service = RpcProxy("process_graphs")
    data_service = RpcProxy("data")
    api_connector = APIConnector()
    template_controller = TemplateController()

    @rpc
    def get(self, user_id: str, job_id: str):
        user_id = "openeouser"
        try:
            job = self.db.query(Job).filter_by(id=job_id).first()

            valid, response = self.authorize(user_id, job_id, job)
            if not valid: 
                return response

            response = self.process_graphs_service.get(user_id, job.process_graph_id)
            if response["status"] == "error":
               return response
            
            job.process_graph = response["data"]["process_graph"]

            query = self.get_input_pid(job_id)

            result = JobSchemaFull().dump(job).data

            if query:
                result["input_data"] = query.pid

            version_timestamp = datetime.datetime.strptime(result["metrics"]["start_time"], '%Y-%m-%d %H:%M:%S.%f')

            version_timestamp = version_timestamp.strftime('%Y%m%d%H%M%S.%f')

            result["metrics"]["back_end_timestamp"] = version_timestamp

            return {
                "status": "success",
                "code": 200,
                "data": result
            }
        except Exception as exp:
            return ServiceException(500, user_id, str(exp),
                links=["#tag/Job-Management/paths/~1jobs~1{job_id}/get"]).to_dict()

    @rpc
    def modify(self, user_id: str, job_id: str, process_graph: dict, title: str=None, description: str=None, 
               output: dict=None, plan: str=None, budget: int=None):
        user_id = "openeouser"
        try:
            raise Exception("Not implemented yet!")
        except Exception as exp:
            return ServiceException(500, user_id, str(exp),
                links=["#tag/Job-Management/paths/~1jobs~1{job_id}/patch"]).to_dict()
    
    @rpc
    def delete(self, user_id: str, job_id: str):
        user_id = "openeouser"
        try:
            raise Exception("Not implemented yet!")
        except Exception as exp:
            return ServiceException(500, user_id, str(exp),
                links=["#tag/Job-Management/paths/~1jobs~1{job_id}/delete"]).to_dict()

    @rpc
    def get_all(self, user_id: str):
        user_id = "openeouser"
        try:
            jobs = self.db.query(Job).filter_by(user_id=user_id).order_by(Job.created_at).all()

            return {
                "status": "success",
                "code": 200,
                "data": JobSchema(many=True).dump(jobs).data
            }
        except Exception as exp:
            return ServiceException(500, user_id, str(exp),
                links=["#tag/Job-Management/paths/~1jobs/get"]).to_dict()
    @rpc
    def create(self, user_id: str, process_graph: dict, title: str=None, description: str=None, output: dict=None,
                   plan: str=None, budget: int=None):
        user_id = "openeouser"
        try:
            process_response = self.process_graphs_service.create(
                user_id=user_id, 
                **{"process_graph": process_graph})
            
            if process_response["status"] == "error":
               return process_response
            
            process_graph_id = process_response["service_data"]

            job = Job(user_id, process_graph_id, title, description, output, plan, budget)

            job_id = str(job.id)
            self.db.add(job)
            self.db.commit()

            return {
                "status": "success",
                "code": 201,
                "headers": {"Location": "jobs/" + job_id }
            }
        except Exception as exp:
            return ServiceException(500, user_id, str(exp),
                links=["#tag/Job-Management/paths/~1jobs/post"]).to_dict()

    @rpc
    def resetdb(self):
        """ Resets the data base entires of the Jobs, the Queryies and the QueryJobs.
            Used for the Evaluation for testing purposes. Needs to be disabled when going productive
            DELME
        """
        try:
            self.db.query(QueryJob).delete(synchronize_session=False)
            self.db.query(Job).delete(synchronize_session=False)
            self.db.query(Query).delete(synchronize_session=False)
            self.db.commit()
            # self.data_service.resetdb()

        except Exception as exp:
            return ServiceException(500, "openeouser", str(exp))

        return {
            "status": "success",
            "code": 201,
            "headers": {"Location": "Jobs deleted"}
        }


    @rpc
    def updatebackend(self, user_id: str, process_graph: dict):
        user_id = "openeouser"

        logging.info(str(process_graph))

        if "package" in process_graph:
            if process_graph["package"]: # add dependency to req.txt file.
                req_file = open("req.txt", "a")
                req_file.write("{}\n".format(process_graph["package"]))
                req_file.close()
            else: # remove last line of req.txt file.
                req_file = open("file")
                lines = req_file.readlines()
                req_file.close()
                w = open("file", 'w')
                w.writelines([item for item in lines[:-1]])
                w.close()
            logging.info("updatetime")

        git_cmd = "git --git-dir=implementation_backend/.git "



        CMD_GIT_BRANCH = "{0} commit -am \"test\"".format(git_cmd)

        logging.info(CMD_GIT_BRANCH)
        logging.info("Executing Git commit...")
        # Executing the git commit
        self.run_cmd(CMD_GIT_BRANCH)
        logging.info("Executed Git commit !")

        return {
            "status": "success",
            "code": 201,
            "headers": {"Location": ""}
        }


    @rpc
    def process(self, user_id: str, job_id: str):
            """ Execution of the job with the given job_id.
                Including handling of the Query and the context model behaviour.
                :param user_id: String user ID.
                :param job_id: String Identifier of the job.
            """
            # User mockup.json
            user_id = "openeouser"

            message = "started"
            try:
                job = self.db.query(Job).filter_by(id=job_id).first()

                valid, response = self.authorize(user_id, job_id, job)
                if not valid:
                    raise Exception(response)

                job.status = "running " + str(job.process_graph_id)
                self.db.commit()

                # Get process nodes
                response = self.process_graphs_service.get_nodes(
                    user_id=user_id,
                    process_graph_id=job.process_graph_id)

                if response["status"] == "error":
                    raise Exception(response)

                process_nodes = response["data"]

                # Get file_paths
                filter_args = process_nodes[0]["args"]

                now = datetime.datetime.utcnow()
                timestamp = now.strftime('%Y-%m-%d %H:%M:%S.%f')
                logging.info("Now: {}".format(timestamp))
                # If the data pid filter is used: Load filter data of the original query.
                if filter_args["data_pid"]:

                    query = self.get_query_by_pid(filter_args["data_pid"].strip())
                    filter_args_str = query.normalized.replace("'", "\"")
                    filter_args_str = filter_args_str.replace("None", "null")
                    filter_args_buf = json.loads(filter_args_str)
                    if filter_args["data_id"]:
                        filter_args_buf["data_id"] = filter_args["data_id"]
                    if filter_args["extent"]:
                        filter_args_buf["extent"] = filter_args["extent"]
                    if filter_args["time"]:
                        filter_args_buf["time"] = filter_args["time"]
                    filter_args = filter_args_buf
                    timestamp = query.created_at

                # quick fix
                if filter_args["extent"]:
                    spatial_extent = [filter_args["extent"]["extent"]["north"], filter_args["extent"]["extent"]["west"],
                                      filter_args["extent"]["extent"]["south"], filter_args["extent"]["extent"]["east"]]

                temporal = "{}/{}".format(filter_args["time"]["extent"][0], filter_args["time"]["extent"][1])

                # simulating updated records
                updated = self.process_graphs_service.get_updated(user_id=user_id,
                                                                  process_graph_id=job.process_graph_id)

                message = str(updated)
                deleted = self.process_graphs_service.get_deleted(user_id=user_id,
                                                                  process_graph_id=job.process_graph_id)

                message = str(deleted)
                logging.info("Executed Timestamp: {}".format(timestamp))
                response = self.data_service.get_records(
                    detail="file_path",
                    user_id=user_id,
                    name=filter_args["name"],
                    spatial_extent=spatial_extent,
                    temporal_extent=temporal,
                    timestamp=timestamp,
                    updated=updated,
                    deleted=deleted)

                if response["status"] == "error":
                    raise Exception(response)

                # Processing Mockup
                self.processing(filter_args, job_id)

                orig_query = self.data_service.get_query(
                    detail="file_path",
                    user_id=user_id,
                    name=filter_args["name"],
                    spatial_extent=spatial_extent,
                    temporal_extent=temporal,
                    timestamp=timestamp)

                start = datetime.datetime.utcnow()

                # Query Handler, creates a new query or returns an equal old one.
                query = self.handle_query(response["data"], filter_args, orig_query, now)

                # Assignes the Query to the Job
                self.assign_query(query.pid, job_id)
                end = datetime.datetime.utcnow()
                delta = end - start
                message = str(int(delta.total_seconds() * 1000))

                start = datetime.datetime.utcnow()
                # Create Context model and assign it to the Job.
                job.metrics = self.create_context_model(job_id)
                end = datetime.datetime.utcnow()
                delta = end - start

                # debugging output DELME
                message += "## CM: " + str(int(delta.total_seconds() * 1000))

                job.status = "finished " + str(message)
                self.db.commit()
                return
            except Exception as exp:
                job.status = "error: " + exp.__str__() + " " + str(message)
                self.db.commit()
            return

    @rpc
    def create_context_model(self, job_id):
        """ Creates the context model entry of the given job id.
            This method has to be called after the job execution.
            :param job_id: String Identifier of the job.
            :return: context_model: Dict representing the context model entry.
        """
        user_id = "openeouser"
        job = self.db.query(Job).filter_by(id=job_id).first()
        query = self.get_input_pid(job_id)

        context_model = {}
        # MOCK UPs of the Processing
        process_graph = self.process_graphs_service.get(user_id, job.process_graph_id)
        output_hash = sha256(("OUTPUT"+str(process_graph)).encode('utf-8')).hexdigest()

        context_model['output_data'] = output_hash
        context_model['input_data'] = query.pid
        context_model['openeo_api'] = "0.3.1"
        context_model['job_id'] = job_id

        with open("req.txt") as f:
            content = f.readlines()

        code_env = [x.strip() for x in content]

        context_model['code_env'] = code_env

        context_model['interpreter'] = "Python 3.7.1"
        context_model['start_time'] = str(job.created_at)
        context_model['end_time'] = str(job.created_at+datetime.timedelta(1, 30))#datetime.datetime.fromtimestamp(time.time())

        # cm = get_job_cm(job_id)

        return context_model

    @rpc
    def version_current(self):
        """
            Returns the current version of the back end.
            :return: version_info: Dict of the current back end version.
        """
        version_info = self.get_git()
        return {
            "status": "success",
            "code": 200,
            "data": version_info
        }

    def get_commit_by_timestamp(self, timestamp):
        """
            Returns the git commit information of the back end, at the given timestamp
            :param timestamp: String Timestamp of datetime format '%Y%m%d%H%M%S.%f'
            :return: git_info: Dict of the current back end version.
        """

        try:
            repo = Repo("implementation_backend/")

            timestamp = datetime.datetime.strptime(timestamp, '%Y%m%d%H%M%S.%f')
            timestamp = pytz.utc.localize(timestamp)

            date_buffer = None
            git_info = {}
            for commit in repo.iter_commits("master"):
                commit_date = commit.committed_datetime
                if commit_date <= timestamp:
                    if date_buffer:
                        if commit_date > date_buffer:
                            date_buffer = commit_date
                            git_info["branch"] = commit.name_rev.split(" ")[1]
                            git_info["commit"] = commit.name_rev.split(" ")[0]

                    else:
                        date_buffer = commit_date
                        git_info["branch"] = commit.name_rev.split(" ")[1]
                        git_info["commit"] = commit.name_rev.split(" ")[0]

        except(Exception):
            return None

        return git_info


    @rpc
    def version(self, timestamp: str):
        """
            Returns the version of the back end, at the timestamp
            :param timestamp: String Timestamp of datetime format '%Y%m%d%H%M%S.%f'
            :return: version_info: Dict of the current back end version.
        """
        git_info = self.get_commit_by_timestamp(timestamp)

        if not git_info:
            return {
                "status": "error",
                "code": 500,
                "data": "timestamp is not formatted correctly, format e.g. 20180528101608.659892 => %Y%m%d%H%M%S.%f"
            }

        version_info = self.get_git()
        version_info["branch"] = git_info["branch"]
        version_info["commit"] = git_info["commit"]
        #version_info["diff"] = "None"
        version_info["timestamp"] = str(datetime.datetime.strptime(timestamp, '%Y%m%d%H%M%S.%f'))

        return {
            "status": "success ",
            "code": 200,
            "data": version_info
        }

    # TODO: If build should be automated using an endpoint e.g. /build the following can be 
    # activated and adapted
    # @rpc
    # def build(self, user_id: str):
    #     try:
    #         status, log, obj_image_stream = self.template_controller.build(
    #             self.api_connector,
    #             environ["CONTAINER_NAME"],
    #             environ["CONTAINER_TAG"],
    #             environ["CONTAINER_GIT_URI"], 
    #             environ["CONTAINER_GIT_REF"], 
    #             environ["CONTAINER_GIT_DIR"])
    #     except Exception as exp:
    #         return ServiceException(500, user_id, str(exp),
    #             links=["#tag/Job-Management/paths/~1jobs~1{job_id}~1results/delete"]).to_dict()
    
    @rpc
    def cancel_processing(self, user_id: str, job_id: str):
        user_id = "openeouser"
        try:
            raise Exception("Not implemented yet!")
        except Exception as exp:
            return ServiceException(500, user_id, str(exp),
                links=["#tag/Job-Management/paths/~1jobs~1{job_id}~1results/delete"]).to_dict()
    
    @rpc
    def get_results(self, user_id: str, job_id: str):
        user_id = "openeouser"
        try:
            raise Exception("Not implemented yet!")
        except Exception as exp:
            return ServiceException(500, user_id, str(exp),
                links=["#tag/Job-Management/paths/~1jobs~1{job_id}~1results/get"]).to_dict()


    def authorize(self, user_id, job_id, job):
        user_id = "openeouser"
        if job is None:
            return False, ServiceException(400, user_id, "The job with id '{0}' does not exist.".format(job_id), 
                internal=False, links=["#tag/Job-Management/paths/~1data/get"]).to_dict()

        # TODO: Permission (e.g admin)
        if job.user_id != user_id:
            return False, ServiceException(401, user_id, "You are not allowed to access this ressource.", 
                internal=False, links=["#tag/Job-Management/paths/~1data/get"]).to_dict()
        
        return True, None

    # QUERY STORE functionallity

    def order_dict(self, dictionary):
        """
            Sorts the dictionary recursively alphabetically.
            :param dictionary: Dict that has to be sorted.
            :return: sorted_dict: Dict that has been sorted.
        """
        return {k: self.order_dict(v) if isinstance(v, dict) else v
                for k, v in sorted(dictionary.items())}

    def create_result_hash(self, result_files):
        # Remove all characters from the result files list that are not relevant and create a hash.
        result_list = str(result_files).split("]")[0]
        result_list += "]"
        result_list = result_list.replace(" ", "")
        result_list = result_list.replace("\t", "")
        result_list = result_list.replace("\n", "")
        # Mockup for Evaluation TESTCASE1
        # result_list = result_list.replace("S2A_MSIL1C_20170104T101402_N0204_R022_T32TPR_20170104T101405",
        #                                  "S2A_MSIL1C_20170104T101402_N0204_R022_T32TPR_20170104T101405_NEW")
        result_list = result_list.encode('utf-8')
        result_list = result_list.strip()

        result_hash = sha256(result_list).hexdigest()

        return result_hash

    def handle_query(self, result_files, filter_args, orig_query, timestamp):
        """
            Query Handler, creating the Query entry into the QueryStore tables.
            Therefore, calculating the data entries for the RDA recommendations.
            :param result_files: String List of resulting files after executing the query.
            :param filter_args: Query/Filter arguments parsed by the EODC back end from the process graph.
            :param orig_query: Original Query that gets actually executed.
            :param timestamp: Original Query execution timestamp.
            :return: query: Query created, or already existing Query that fits the input.
        """

        # remove query independent filter data
        if "data_pid" in filter_args:
            filter_args.pop("data_pid")


        # normalized query, sorted query...
        normalized = self.order_dict(filter_args)
        normalized = str(normalized)
        normalized = normalized.strip()
        print(normalized)
        norm_hash = sha256(normalized.encode('utf-8')).hexdigest()
        print(norm_hash)

        # Remove all characters from the result files list that are not relevant and create a hash.
        result_hash = self.create_result_hash(result_files)

        # Look for Query entries that have an equal query hash and result hash.
        existing = self.db.query(Query).filter_by(norm_hash=norm_hash, result_hash=result_hash).first()

        if existing:
            return existing

        # extract additional information from the input data.
        dataset_pid = str(filter_args["name"])
        orig_query = str(orig_query)
        #logging.info("RESULTFILES {}".format(result_files))
        metadata = str({"result_files": len(result_files.split("}, {"))})

        new_query = Query(dataset_pid, orig_query, normalized, norm_hash,
                 result_hash, metadata)
        new_query.created_at = timestamp

        self.db.add(new_query)
        self.db.commit()

        return new_query

    def assign_query(self, query_pid, job_id):
        """
            Assign Query to a job, by adding it to the QueryJob table.
            :param query_pid: String Query PID
            :param job_id: String Job ID
        """
        queryjob = QueryJob(query_pid, job_id)
        self.db.add(queryjob)
        self.db.commit()

    def get_input_pid(self, job_id):
        """
            Get query PID that was used by the job with the given job id.
            :param job_id: String job ID
            :return: query: Query that was used by the job with the job_id identifier.
        """
        queryjob = self.db.query(QueryJob).filter_by(job_id=job_id).first()

        return self.db.query(Query).filter_by(pid=queryjob.query_pid).first()

    def get_job_by_query(self, query_pid):
        """
            Get query PID that was used by the job with the given job id.
            :param job_id: String job ID
            :return: query: Query that was used by the job with the job_id identifier.
        """
        queryjob = self.db.query(QueryJob).filter_by(query_pid=query_pid).first()

        return self.db.query(Job).filter_by(id=queryjob.job_id).first()

    @rpc
    def get_query_by_pid(self, query_pid):
        """
            Returns Query object with a given Query PID.
            :param query_pid: String Query PID
            :return: query: Query with the given PID.
        """
        return self.db.query(Query).filter_by(pid=query_pid).first()

    @rpc
    def get_dataset_by_pid(self, query_pid):
        """
            Returns Dataset of the Query object with a given Query PID.
            :param query_pid: String Query PID
            :return: dataset: String dataset identifier
        """
        query = self.db.query(Query).filter_by(pid=query_pid).first()

        dataset = None
        if query:
            dataset = query.dataset_pid

        return dataset

    @rpc
    def get_querydata_by_pid(self, query_pid):
        """
            Returns normalized query of a given Query PID.
            :param query_pid: String Query PID
            :return: query: String of the normalized query.
        """
        query = self.db.query(Query).filter_by(pid=query_pid).first()

        if query:
            query = str(query.normalized)

        return query

    @rpc
    def get_origquerydata_by_pid(self, query_pid):
        """
            Returns original query of a given Query PID.
            :param query_pid: String Query PID
            :return: query: String of the original query.
        """
        query = self.db.query(Query).filter_by(pid=query_pid).first()

        if query:
            query = str(query.original)

        return query

    @rpc
    def get_querytimestamp_by_pid(self, query_pid):
        """
            Returns normalized query of a given Query PID.
            :param query_pid: String Query PID
            :return: query: String of the normalized query.
        """
        query = self.db.query(Query).filter_by(pid=query_pid).first()

        timestamp = None
        if query:
            timestamp = str(query.created_at)

        return timestamp

    @rpc
    def reexecute_query(self, user_id, query_pid, deleted=False):
        """
        Re-executes the Query with the given query pid and returns the resulting files of the query execution.
        It also returns a state of the re-execution where it is stated if the resulting files differ the original
        execution or not.
        :param user_id: String User ID
        :param query_pid: String Query PID
        :return: filelist: Dict of the resulting file list including a state of the re-execution
                                        (DIFF, if the re-execution result in a different filelist and
                                         EQUAL, if the re-execution result is the same as the original execution.)
        """
        user_id = "openeouser"
        query = self.db.query(Query).filter_by(pid=query_pid).first()

        filter_args = query.normalized

        # reading the relevant information out of the original query execution.
        json_acceptable_string = filter_args.replace("'", "\"")
        json_acceptable_string = json_acceptable_string.replace("None", "null")
        filter_args = json.loads(json_acceptable_string)

        # quick fix
        spatial_extent = [filter_args["extent"]["extent"]["north"], filter_args["extent"]["extent"]["west"],
                          filter_args["extent"]["extent"]["south"], filter_args["extent"]["extent"]["east"]]

        temporal = "{}/{}".format(filter_args["time"]["extent"][0], filter_args["time"]["extent"][1])

        timestamp = query.created_at#.split(" ")[0]

        job = self.get_job_by_query(query_pid)

        # simulating updated records
        updated = self.process_graphs_service.get_updated(user_id=user_id,
                                                          process_graph_id=job.process_graph_id)

        deleted_cfg = self.process_graphs_service.get_deleted(user_id=user_id,
                                                          process_graph_id=job.process_graph_id)

        if deleted:
            deleted_cfg = deleted

        # Re-execute the query
        response = self.data_service.get_records(
            detail="file_path",
            user_id=user_id,
            name=filter_args["name"],
            spatial_extent=spatial_extent,
            temporal_extent=temporal,
            timestamp=timestamp,
            updated=updated,
            deleted=deleted_cfg)

        if response["status"] == "error":
            raise Exception(response)


        result_hash = self.create_result_hash(response["data"])

        filter_args["file_paths"] = response["data"]

        # Add resulting files into the response
        output = {
            "file_paths": (str(response["data"]).split("]")[0])+"]"
        }
        # Add state to the response
        if result_hash != query.result_hash:

            new_count = len(response["data"].split("}, {"))
            old_count = int(json.loads(query.meta_data.replace("'", '"'))["result_files"])
            logging.info("OLD_COUNT: {}, NEW_COUNT: {}".format(old_count, new_count))
            if old_count != new_count:
                response2 = self.data_service.get_records(
                    detail="file_path",
                    user_id=user_id,
                    name=filter_args["name"],
                    spatial_extent=spatial_extent,
                    temporal_extent=temporal,
                    timestamp=timestamp,
                    updated=updated,
                    deleted=deleted_cfg)

                if response2["status"] == "error":
                    raise Exception(response2)

                file_diff = []

                for file in response["data"].split("}, {"):
                    found = False
                    for file2 in response2["data"].split("}, {"):
                        if file == file2:
                            found = True
                            break;
                    if not found:
                        file_diff.append(file)

                output["state"] = str(file_diff)
        else:
            output["state"] = "EQUAL"

        return output

    def run_cmd(self, command):
        """
            Executes a shell command
            :param command: String of the shell command
            :return: query: String stdout of the executed command
        """
        import subprocess
        result = subprocess.run(command.split(), stdout=subprocess.PIPE)
        return result.stdout.decode("utf-8")

    def get_git(self):
        """
            Returns the Git url, branch and commit of the local repository.
            :return: git_info: Dict of the git information
        """

        # Used git commands
        git_cmd = "git --git-dir=implementation_backend/.git "

        CMD_GIT_URL = "{0} config --get remote.origin.url".format(git_cmd)
        CMD_GIT_BRANCH = "{0} branch".format(git_cmd)
        CMD_GIT_COMMIT = "{0} log".format(git_cmd)  # first line

        # Executing the git commands
        git_url = self.run_cmd(CMD_GIT_URL).split("\n")[0]
        git_commit = self.run_cmd(CMD_GIT_COMMIT).split("\n")[0].replace("commit", "").strip()

        git_branch = self.run_cmd(CMD_GIT_BRANCH).replace("*", "").strip()

        cm_git = {'url': git_url,
                  'branch': git_branch,
                  'commit': git_commit,
                  }

        return cm_git

    def get_provenance(self):
        """
            Returns the provenance information about the back end. Code environment and back end version.
            :return: context_model:
        """
        context_model = {}

        installed_packages = self.run_cmd("pip freeze")

        context_model["code_env"] = installed_packages

        context_model["backend_env"] = self.get_git("git")

        return context_model

# --- Processing Mockup ---

    def reproject(self, latitude, longitude):
        """Returns the x & y coordinates in meters using a sinusoidal projection"""
        from math import pi, cos, radians
        earth_radius = 6371009 # in meters
        lat_dist = pi * earth_radius / 180.0

        y = [lat * lat_dist for lat in latitude]
        x = [long * lat_dist * cos(radians(lat))
                    for lat, long in zip(latitude, longitude)]
        return x, y


    def area_of_polygon(self, x, y):
        """Calculates the area of an arbitrary polygon given its verticies"""
        area = 0.0
        for i in range(-1, len(x)-1):
            area += x[i] * (y[i+1] - y[i-1])
        return abs(area) / 2.0


    def generate_area(self, lon1, lat1, lon2, lat2, date_start, date_end):
        """Creates mockup.json area related to the given coordinates and daterange"""
        FACTOR_RESOLUTION = 1000

        longitude = [lon1, lon1, lon2, lon2]
        latitude = [lat1, lat2, lat1, lat2]

        # Reprojection of the coordinates
        x, y = self.reproject(longitude, latitude)
        # x2, y2 = reproject(lon2, lat2)

        # NDVI calculation
        width = int((((x[0]-x[1])**2)**0.5)/FACTOR_RESOLUTION)
        height = int((((y[0]-y[3])**2)**0.5)/FACTOR_RESOLUTION)
        # area = area_of_polygon(x, y)

        start = datetime.datetime.strptime(date_start, "%Y-%m-%d")
        end = datetime.datetime.strptime(date_end, "%Y-%m-%d")

        daterange = end-start

        # fill up area with mockup.json values
        area = np.ones((width, height, daterange.days))

        return area

    def set_no_data(self, data, cur, should):
        '''Set no data value'''

        data[data == cur] = should
        return data

    def calc_ndvi(self, red, nir):
        '''Returns ndvi for given red and nir band (no data is set to 2, ndvi in range [-1, 1])'''

        # Calculate NDVI
        ndvi = (nir - red) / (nir + red)
        ndvi = self.set_no_data(ndvi, np.nan, 2)
        return ndvi

    def calc_mintime(self, data):
        '''Returns min time dataset'''
        return np.fmin.reduce(data)

    def calc_maxtime(self, data):
        '''Returns max time dataset'''
        return np.fmax.reduce(data)

    def processing(self, filter_args, job_id):
        '''Returns max time dataset'''

        logging.basicConfig(filename='{}.log'.format(job_id), level=logging.DEBUG)

        logging.info("before spatial")
        west = filter_args["extent"]["extent"]["west"]
        south = filter_args["extent"]["extent"]["south"]
        east = filter_args["extent"]["extent"]["east"]
        north = filter_args["extent"]["extent"]["north"]
        logging.info("after spatial")
        start_date = filter_args["time"]["extent"][0]
        end_date = filter_args["time"]["extent"][1]
        logging.info("after temporal")
        #temporal = "{}/{}".format(filter_args["time"]["extent"][0], filter_args["time"]["extent"][1])
        #daterange = ["2017-05-01", "2017-05-31"]
        # (west, south, east, north)
        #bbox = {"west": 10.288696, "south": 45.935871, "east": 12.189331, "north": 46.905246, "crs": "EPSG:4326"}

        area = self.generate_area(west, south, east, north, start_date, end_date)
        logging.info("after generate area")
        ndvi = self.calc_ndvi(area, area)
        logging.info("after calc ndvi")
        min_time_data = np.fmin.reduce(ndvi)

        logging.info("API-VERSION: 0.3.1")
        logging.info("INTERPRETER: Python 3.7.1")

        #np.savetxt('{}.tif'.format(job_id), min_time_data, delimiter=',')

        logging.info("FINISHED: {}".format(str(datetime.datetime.utcnow())))
