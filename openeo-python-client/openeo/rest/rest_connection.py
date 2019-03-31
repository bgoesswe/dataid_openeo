from distutils.version import LooseVersion
from urllib.parse import urlparse
import shutil
import os

import requests

from openeo.auth.auth_none import NoneAuth
from openeo.auth.auth_basic import BasicAuth
from openeo.rest.rest_capabilities import RESTCapabilities
from openeo.rest.rest_processes import RESTProcesses
from openeo.rest.job import RESTJob

import json
from openeo.connection import Connection
from datetime import datetime, timedelta
import time

"""
openeo.sessions
~~~~~~~~~~~~~~~~
This module provides a Connection object to manage and persist settings when interacting with the OpenEO API.
"""


class RESTConnection(Connection):


    def __init__(self, url, auth_type=NoneAuth, auth_options={}):
        # TODO: Maybe in future only the endpoint is needed, because of some kind of User object inside of the connection.
        """
        Constructor of RESTConnection, authenticates user.
        :param url: String Backend endpoint url
        :param username: String Username credential of the user
        :param password: String Password credential of the user
        :param auth_class: Auth instance of the abstract Auth class
        :return: token: String Bearer token
        """
        self.root = ""
        self._cached_capabilities = None
        self.connect(url, auth_type, auth_options)

    def connect(self, url, auth_type=NoneAuth, auth_options={}) -> bool:
        """
        Authenticates a user to the backend using auth class.
        :param url: String Backend endpoint url
        :param username: String Username credential of the user
        :param password: String Password credential of the user
        :param auth_class: Auth instance of the abstract Auth class
        :return: token: String Bearer token
        """

        username = None
        password = None

        if 'username' in auth_options:
            username = auth_options['username']

        if 'password' in auth_options:
            password = auth_options['password']

        self.userid = username
        self.endpoint = url

        if auth_type == NoneAuth and username != None and password != None:
            auth_type = BasicAuth

        self.authent = auth_type(username, password, self.endpoint)

        status = self.authent.login()

        return status

    def authenticate_OIDC(self, options={}) -> str:
        """
        Authenticates a user to the backend using OIDC.
        :param options: Authentication options
        """
        return self.not_supported()

    def resetdb(self) -> bool:
        """
        Resets the job, query and process graph database

        :return:
        """

        response1 = self.get(self.root + '/resetjobsdb', auth=False)
        response2 = self.get(self.root + '/resetpgdb', auth=False)

        return True

    def update_file(self, updated=datetime.utcnow(), deleted=False) -> bool:
        """
        Resets the job, query and process graph database

        :return:
        """

        if updated:
            #updated = updated + timedelta(minutes=1)
            time.sleep(10)
            updated = updated.strftime('%Y-%m-%d %H:%M:%S.%f')

        mockupstate = { "process_graph": { "updatetime": updated, "deleted": deleted}}


        job_status = self.post("/updaterecord", mockupstate)

        return True

    def get_mockupstate(self) -> dict:
        """
        Resets the job, query and process graph database

        :return:
        """

        info = self.get(self.root + '/mupdatestate')
        return self.parse_json_response(info)

        return True


    def authenticate_basic(self, username, password):
        """
        Authenticates a user to the backend using HTTP Basic.
        :param username: User name
        :param password: User passphrase
        """

        if username and password:
            self.authent = BasicAuth(username, password, self.endpoint)

        # return self.not_supported()

    def describe_account(self) -> str:
        """
        Describes the currently authenticated user account.
        """
        info = self.get(self.root + '/me')
        return self.parse_json_response(info)

    def user_jobs(self) -> dict:
        #TODO: Create a kind of User class to abstract the information (e.g. userid, username, password from the connection.
        #TODO: Move information to Job class and return a list of Jobs.
        """
        Loads all jobs of the current user.
        :return: jobs: Dict All jobs of the user
        """
        jobs = self.get(self.root + '/users/{}/jobs'.format(self.userid))
        return self.parse_json_response(jobs)

    def list_collections(self) -> dict:
        """
        Loads all available imagecollections types.
        :return: data_dict: Dict All available data types
        """
        data = self.get(self.root + '/collections', auth=False)

        response = self.parse_json_response(data)

        if "collections" in response:
            return response["collections"]

        return response

    def get_processes(self):
        """
        Returns processes of back end.
        :return: data_dict: Dict All available data types
        """
        # TODO return only provided processes of the back end

        return RESTProcesses(self)


    @property
    def capabilities(self) -> 'Capabilities':
        """
        Loads all available capabilities.

        :return: data_dict: Dict All available data types
        """
        if self._cached_capabilities is None:
            data = self.get(self.root + '/', auth=False)
            self._cached_capabilities = RESTCapabilities(self.parse_json_response(data))

        return self._cached_capabilities

    def list_file_types(self) -> dict:
        """
        Loads all available output formats.
        :return: data_dict: Dict All available output formats
        """
        data = self.get(self.root + '/output_formats', auth=False)
        return self.parse_json_response(data)

    def list_service_types(self) -> dict:
        """
        Loads all available service types.
        :return: data_dict: Dict All available service types
        """
        data = self.get(self.root + '/service_types', auth=False)
        return self.parse_json_response(data)

    def list_services(self) -> dict:
        """
        Loads all available services of the authenticated user.
        :return: data_dict: Dict All available service types
        """
        #TODO return service objects
        data = self.get(self.root + '/services', auth=True)
        return self.parse_json_response(data)

    def describe_collection(self, name) -> dict:
        # TODO: Maybe create some kind of Data class.
        """
        Loads detailed information of a specific image collection.
        :param name: String Id of the collection
        :return: data_dict: Dict Detailed information about the collection
        """
        if name:
            data_info = self.get(self.root + '/collections/{}'.format(name), auth=False)
            return self.parse_json_response(data_info)
        else:
            raise ValueError("Invalid argument col_id: {}".format(str(name)))

    def get_filelist(self, data_pid, updated=False) -> dict:
        # TODO: Maybe create some kind of Data class.
        """
        Loads detailed information, including the filelist of a specific data pid.
        :param data_pid: String Id of the collection
        :return: data_dict: Dict Detailed information about the collection
        """
        if data_pid:
            if updated:
                data_info = self.get(self.root + '/collections/{}/updatedresult'.format(data_pid), auth=False)
            else:
                data_info = self.get(self.root + '/collections/{}/result'.format(data_pid), auth=False)
            return self.parse_json_response(data_info)
        else:
            raise ValueError("Invalid argument col_id: {}".format(str(data_pid)))

    def version(self, timestamp=None) -> dict:
        """
        Returns the version of the back end at a given time stamp. If the timestamp is None,
        the current version is returned by the method.

        :param timestamp: Datetime object to get the version of the back end at this time.

        :return: version_dict: Contains the available version information of the back end.
        """


        if timestamp:
            timestamp = timestamp.strftime('%Y%m%d%H%M%S.%f')
            data_info = self.get(self.root + '/version/{}'.format(timestamp), auth=False)
        else:
            data_info = self.get(self.root + '/version', auth=False)

        return self.parse_json_response(data_info)

    def describe_data_pid(self, pid) -> dict:
        """
        Loads detailed information of a specific data pid.
        :param pid: Data PID
        :return: data_dict: Dict Detailed information about the data set represented by the dat pid.
        """
        if pid:
            data_info = self.get(self.root + '/collections/{}'.format(pid), auth=False)
            return self.parse_json_response(data_info)
        else:
            raise ValueError("Invalid argument col_id: {}".format(str(pid)))

    def list_processes(self) -> dict:
        # TODO: Maybe format the result dictionary so that the process_id is the key of the dictionary.
        """
        Loads all available processes of the back end.
        :return: processes_dict: Dict All available processes of the back end.
        """
        processes = self.get('/processes', auth=False)

        response = self.parse_json_response(processes)

        if "processes" in response:
            return response["processes"]

        return response

    def list_jobs(self) -> dict:
        # TODO: Maybe format the result so that there get Job classes returned.
        """
        Lists all jobs of the authenticated user.
        :return: job_list: Dict of all jobs of the user.
        """
        jobs = self.get('/jobs', auth=True)
        return self.parse_json_response(jobs)

    def validate_processgraph(self, process_graph):

        # Endpoint: POST /validate
        return self.not_supported()

    def list_processgraphs(self, process_graph):

        # Endpoint: GET /process_graphs
        return self.not_supported()


    def get_process(self, process_id) -> dict:
        # TODO: Maybe create some kind of Process class.
        """
        Get detailed information about a specifig process.
        :param process_id: String Process identifier
        :return: processes_dict: Dict with the detail information about the
                                 process
        """
        if process_id:
            process_info = self.get('/processes/{}'.format(process_id), auth=False)
            processes_dict = self.parse_json_response(process_info)
        else:
            processes_dict = None

        return processes_dict

    def _isVersion040(self):
        return LooseVersion(self.capabilities.version()) >= LooseVersion("0.4.0")

    def imagecollection(self, image_collection_id) -> 'ImageCollection':
        """
        Get imagecollection by id.
        :param image_collection_id: String image collection identifier
        :return: collection: RestImageCollection the imagecollection with the id
        """
        if self._isVersion040():
            return self._image_040(image_collection_id)
        else:
            from .imagery import RestImagery
            collection = RestImagery({'collection_id': image_collection_id}, self)

            self.fetch_metadata(image_collection_id, collection)
            return collection

    def _image_040(self, image_product_id) -> 'ImageCollection':
        """
        Get imagery by id.
        :param image_collection_id: String image collection identifier
        :return: collection: RestImagery the imagery with the id
        """
        #new implementation: https://github.com/Open-EO/openeo-api/issues/160
        from .imagecollectionclient import ImageCollectionClient
        image = ImageCollectionClient.create_collection(image_product_id, self)
        self.fetch_metadata(image_product_id, image)
        return image

    def image(self, image_product_id) -> 'ImageCollection':
        """
        Get imagery by id.
        :param image_collection_id: String image collection identifier
        :return: collection: RestImagery the imagery with the id
        """
        from .rest_processes import RESTProcesses

        image = RESTProcesses( self)

        self.fetch_metadata(image_product_id, image)
        return image

    def fetch_metadata(self, image_product_id, image_collection):
        # read and format extent, band and date availability information
        data_info = self.describe_collection(image_product_id)
        image_collection.bands = []
        if data_info:
            if 'bands' in data_info:
                for band in data_info['bands']: image_collection.bands.append(band['band_id'])
            image_collection.dates = data_info.get('time',[])
            image_collection.extent = data_info.get('extent',None)
        else:
            image_collection.bands = ['not specified']
            image_collection.dates = ['not specified']
            image_collection.extent = ['not specified']

    def point_timeseries(self, graph, x, y, srs):
        """Compute a timeseries for a given point location."""
        return self.post(self.root + "/timeseries/point?x={}&y={}&srs={}"
                         .format(x,y,srs), graph)

    def create_service(self,graph,**kwargs):
        kwargs["process_graph"] = graph
        return self.parse_json_response(self.post(self.root + "/services",kwargs))

    def job_results(self, job_id):
        response = self.get("/jobs/{}/results".format(job_id))
        return self.parse_json_response(response)

    def list_files(self, user_id=None):
        """
        Lists all files that the logged in user uploaded.
        :param user_id: user id, which files should be listed.
        :return: file_list: List of the user uploaded files.
        """

        if not user_id:
            user_id = self.userid

        files = self.get('/files/{}'.format(user_id))

        #TODO: Create File Objects.

        return self.parse_json_response(files)

    def create_file(self, path, user_id=None):
        """
        Creates virtual file
        :param user_id: owner of the file.
        :return: file object.
        """
        # No endpoint just returns a file object.
        return self.not_supported()

    # TODO: Maybe rename to execute and merge with execute().
    # Depricated function, use download_job instead.
    def download(self, graph, time, outputfile, format_options):
        """
        Downloads a result of a process graph synchronously.
        :param graph: Dict representing a process graph
        :param time: dba
        :param outputfile: output file
        :param format_options: formating options
        :return: job_id: String
        """
        download_url = self.endpoint + self.root + "/execute"

        request = {
            "process_graph": graph,
            "output": format_options
        }
        r = requests.post(download_url, json=request, stream = True, timeout=1000 )
        if r.status_code == 200:
            with open(outputfile, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
        else:
            raise IOError("Received an exception from the server for url: {} and POST message: {}".format(download_url,json.dumps( request ) ) + r.text)

        return

    def execute(self, process_graph, output_format, output_parameters=None, budget=None):
        """
        Execute a process graph synchronously.
        :param process_graph: Dict representing a process graph
        :param output_format: String Output format of the execution
        :param output_parameters: Dict of additional output parameters
        :param budget: Budget
        :return: job_id: String
        """
        # TODO: add output_format to execution
        response = self.post(self.root + "/preview", process_graph)
        return self.parse_json_response(response)

    def create_job(self, process_graph, output_format=None, output_parameters={},
                   title=None, description=None, plan=None, budget=None,
                   additional={}, updated=None, deleted=None):
        """
        Posts a job to the back end.
        :param process_graph: String data of the job (e.g. process graph)
        :return: job_id: String Job id of the new created job
        """

        process_graph = {"process_graph": process_graph}

        # Simulating Changes at the data back end.
        if updated:
            process_graph["updated"] = updated
        if deleted:
            process_graph["deleted"] = deleted

        job_status = self.post("/jobs", process_graph)

        job = None

        if job_status.status_code == 201:
            job_info = job_status.headers._store
            if "openeo-identifier" in job_info:
                job_id = job_info['openeo-identifier'][1]
                job = RESTJob(job_id, self)
            elif "location" in job_info:
                job_id = job_info['location'][1].split("/")[-1]
                job = RESTJob(job_id, self)
        else:
            raise Exception(job_status)


        return job

    def get_job(self, job_id: str):
        """
        Returns job with the given id
        :param job_id: Jpob Id
        :return: job: RESTJob job object with the job id
        """
        job = RESTJob(job_id, self)
        return job

    def parse_json_response(self, response: requests.Response):
        """
        Parses json response, if an error occurs it raises an Exception.
        :param response: Response of a RESTful request
        :return: response: JSON Response
        """
        if response.status_code == 200 or response.status_code == 201:
            return response.json()
        elif response.status_code == 502:
            from requests.exceptions import ProxyError
            raise ProxyError("The proxy returned an error, this could be due to a timeout.")
        else:
            raise ConnectionAbortedError(response.text)

    def post(self, path, postdata):
        """
        Makes a RESTful POST request to the back end.
        :param path: URL of the request (without root URL e.g. "/data")
        :param postdata: Data of the post request
        :return: response: Response
        """

        auth_header = self.authent.get_header()
        auth = self.authent.get_auth()
        test = self.endpoint+path
        return requests.post(self.endpoint+path, json=postdata, headers=auth_header, auth=auth)

    def delete(self, path, postdata):
        """
        Makes a RESTful DELETE request to the back end.
        :param path: URL of the request (without root URL e.g. "/data")
        :param postdata: Data of the post request
        :return: response: Response
        """

        auth_header = self.authent.get_header()
        auth = self.authent.get_auth()
        return requests.delete(self.endpoint+path, json=postdata, headers=auth_header, auth=auth)

    def patch(self, path):
        """
        Makes a RESTful PATCH request to the back end.
        :param path: URL of the request (without root URL e.g. "/data")
        :return: response: Response
        """
        auth_header = self.authent.get_header()
        auth = self.authent.get_auth()
        return requests.patch(self.endpoint+path, headers=auth_header, auth=auth)

    def put(self, path, header={}, data=None):
        """
        Makes a RESTful PUT request to the back end.
        :param path: URL of the request (without root URL e.g. "/data")
        :param header: header that gets added to the request.
        :param data: data that gets added to the request.
        :return: response: Response
        """
        auth_header = self.authent.get_header()

        # Merge headers
        head = auth_header.copy()
        head.update(header)

        auth = self.authent.get_auth()

        if data:
            return requests.put(self.endpoint+path, headers=head, data=data, auth=auth)
        else:
            return requests.put(self.endpoint+path, headers=head, auth=auth)

    def get(self,path, stream=False, auth=True):
        """
        Makes a RESTful GET request to the back end.
        :param path: URL of the request (without root URL e.g. "/data")
        :param stream: True if the get request should be streamed, else False
        :param auth: True if the get request should be authenticated, else False
        :return: response: Response
        """

        if auth:
            auth_header = self.authent.get_header()
            auth = self.authent.get_auth()
        else:
            auth_header = {}
            auth = None



        return requests.get(self.endpoint+path, headers=auth_header, stream=stream, auth=auth)

    def delete(self, path):
        """
        Makes a RESTful DELETE request to the backend

        :param path: URL of the request relative to endpoint url
        """

        auth_header = self.authent.get_header()
        auth = self.authent.get_auth()

        return requests.delete(self.endpoint+path, headers=auth_header, auth=auth)

    def get_outputformats(self) -> dict:
        """
        Loads all available output formats.

        :return: data_dict: Dict All available output formats
        """
        return self.not_supported()

    def not_supported(self):
        not_support = "This function is not supported by the python client yet."
        print(not_support)
        return not_support



def connection(url, auth_type=NoneAuth, auth_options={}):
    """
    This method is the entry point to OpenEO. You typically create one connection object in your script or application, per back-end.
    and re-use it for all calls to that backend.
    If the backend requires authentication, you should set pass your credentials.

    :param endpoint: The http url of an OpenEO endpoint.

    :rtype: openeo.connections.Connection
    """

    return RESTConnection(url, auth_type, auth_options)

def session(userid=None,endpoint:str="https://openeo.org/openeo"):
    """
    Deprecated, use openeo.connect
    This method is the entry point to OpenEO. You typically create one session object in your script or application, per back-end.
    and re-use it for all calls to that backend.
    If the backend requires authentication, you should set pass your credentials.
    :param endpoint: The http url of an OpenEO endpoint.
    :rtype: openeo.sessions.Session
    """
    return connection(url = endpoint)
