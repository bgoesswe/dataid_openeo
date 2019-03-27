""" Query Handler """

from models import Query
from hashlib import sha256
from uuid import uuid4
#TODO: Move to own file...

EXAMPLE_GRAPH = {
    "process_id": "min_time",
    "process_description": "Deriving minimum NDVI measurements over pixel time series of Sentinel 2 imagery.",
    "imagery": {
      "process_id": "NDVI",
      "imagery": {
        "process_id": "filter_daterange",
        "imagery": {
          "process_id": "get_collection",
          "name": "Sentinel2A-L1C"
        },
        "extent": [
          "2017-01-01T00:00:00Z",
          "2017-01-31T23:59:59Z"
        ]
      },
      "red": "4",
      "nir": "8"
    }
  }

EXAMPLE_FILE_LIST = ["TESTFILE1", "TESTFILE2", "TESTFILE3", "TESTFILE4"]

FILTER_ARGS = {'data_id': None, 'time': {'extent': ['2017-01-01', '2017-01-05']}, 'bands': None, 'extent': {'extent': {'crs': 'EPSG:32632', 'east': 17.2, 'north': 46.3, 'south': 49.02, 'west': 9.4}}, 'derived_from': None, 'license': None, 'name': 's2a_prd_msil1c'}

def order_dict(dictionary):
    return {k: order_dict(v) if isinstance(v, dict) else v
            for k, v in sorted(dictionary.items())}

def handle_query(process_graph, result_files, filter_args, job_id):

    # normalized query, sorted query...
    normalized = order_dict(filter_args)
    normalized = str(normalized)
    normalized = normalized.encode('utf-8')
    norm_hash = sha256(normalized).hexdigest()

    result_list = str(result_files)
    result_list = result_list.encode('utf-8')

    result_hash = sha256(result_list).hexdigest()

    #existing = self.db.query(Query).filter_by(norm_hash=norm_hash, result_hash=result_hash).first()

    #if existing:
    #    return existing

    pid = "qu-"+str(uuid4())
    dataset_pid = filter_args["name"]
    orig_query = filter_args

    #TODO data_pid --> get by filter_args name

    #TODO maybe add metadata...
    metadata = { "number_of_files": len(result_files)}

    #print(result)

#handle_query(EXAMPLE_GRAPH, EXAMPLE_FILE_LIST, FILTER_ARGS, "test")