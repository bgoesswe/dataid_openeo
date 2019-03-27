equal_process_graphs = [

{"imagery": {"imagery": {"extent": ["2017-01-01", "2017-01-31"],
   "imagery": {"extent": {
     "north": 49.041469,
     "east": 17.171631,
     "west": 9.497681,
     "south": 46.517296,
     "crs": "EPSG:32632"},
    "imagery": {"process_id": "get_collection", "name": "s2a_prd_msil1c"},
    "process_id": "filter_bbox"},
   "process_id": "filter_daterange"},
  "nir": "B08",
  "process_id": "NDVI",
  "red": "B04"},
 "process_id": "min_time"}
,

{"imagery": {"imagery": {"extent": ["2017-01-01", "2017-01-31"],
   "imagery": {"extent": {
     "east": 17.171631,
     "north": 49.041469,
     "west": 9.497681,
     "south": 46.517296,
     "crs": "EPSG:32632"},
    "imagery": {"process_id": "get_collection", "name": "s2a_prd_msil1c"},
    "process_id": "filter_bbox"},
   "process_id": "filter_daterange"},
  "nir": "B08",
  "process_id": "NDVI",
  "red": "B04"},
 "process_id": "min_time"}
,

{"imagery": {"imagery": {"extent": ["2017-01-01", "2017-01-31"],
   "imagery": {"extent": {
     "east": 17.171631,
     "west": 9.497681,
     "north": 49.041469,
     "south": 46.517296,
     "crs": "EPSG:32632"},
    "imagery": {"process_id": "get_collection", "name": "s2a_prd_msil1c"},
    "process_id": "filter_bbox"},
   "process_id": "filter_daterange"},
  "nir": "B08",
  "process_id": "NDVI",
  "red": "B04"},
 "process_id": "min_time"
},
 {"imagery": {"imagery": {"extent": ["2017-01-01", "2017-01-31"],
   "imagery": {"extent": {
     "east": 17.171631,
     "west": 9.497681,
     "south": 46.517296,
     "north": 49.041469,
     "crs": "EPSG:32632"},
    "imagery": {"process_id": "get_collection", "name": "s2a_prd_msil1c"},
    "process_id": "filter_bbox"},
   "process_id": "filter_daterange"},
  "nir": "B08",
  "process_id": "NDVI",
  "red": "B04"},
 "process_id": "min_time"
},

{"imagery": {"imagery": {"extent": ["2017-01-01", "2017-01-31"],
   "imagery": {"extent": {
     "east": 17.171631,
     "west": 9.497681,
     "south": 46.517296,
     "crs": "EPSG:32632",
     "north": 49.041469},
    "imagery": {"process_id": "get_collection", "name": "s2a_prd_msil1c"},
    "process_id": "filter_bbox"},
   "process_id": "filter_daterange"},
  "nir": "B08",
  "process_id": "NDVI",
  "red": "B04"},
 "process_id": "min_time"
},

{"imagery": {"imagery": {"extent": ["2017-01-01", "2017-01-31"],
   "imagery": {"extent": {
     "east": 17.171631,
     "west": 9.497681,
     "south": 46.517296,
     "crs": "EPSG:32632",
     "north": 49.041469},
    "imagery": {"process_id": "get_collection", "name": "s2a_prd_msil1c"},
    "process_id": "filter_bbox"},
   "process_id": "filter_daterange"},
  "nir": "B08",
  "red": "B04",
  "process_id": "NDVI"
  },
 "process_id": "min_time"
},


 {"imagery": {"imagery": {
   "imagery": {"extent": {
     "east": 17.171631,
     "west": 9.497681,
     "south": 46.517296,
     "crs": "EPSG:32632",
     "north": 49.041469},
    "imagery": {"process_id": "get_collection", "name": "s2a_prd_msil1c"},
    "process_id": "filter_bbox"},
   "process_id": "filter_daterange",
   "extent": ["2017-01-01", "2017-01-31"]},
  "red": "B04",
  "nir": "B08",
  "process_id": "NDVI"
  },
 "process_id": "min_time"
}
]

process_graph_filterorder = [

 {"imagery": {"imagery": {
   "imagery": {"extent": {
     "east": 17.171631,
     "west": 9.497681,
     "south": 46.517296,
     "crs": "EPSG:32632",
     "north": 49.041469},
    "imagery": {"name": "s2a_prd_msil1c", "process_id": "get_collection"},
    "process_id": "filter_bbox"},
   "process_id": "filter_daterange",
   "extent": ["2017-01-01", "2017-01-31"]},
  "red": "B04",
  "nir": "B08",
  "process_id": "NDVI"
  },
 "process_id": "min_time"
},
 {"imagery": {"imagery": {
   "imagery": {
    "imagery": {"process_id": "get_collection", "name": "s2a_prd_msil1c"},
    "process_id": "filter_daterange",
    "extent": ["2017-01-01", "2017-01-31"]},
   "process_id": "filter_bbox",
     "extent": {
     "east": 17.171631,
     "west": 9.497681,
     "south": 46.517296,
     "crs": "EPSG:32632",
     "north": 49.041469}},
  "red": "B04",
  "nir": "B08",
  "process_id": "NDVI"
  },
 "process_id": "min_time"
},
{"imagery": {"imagery": {"extent": ["2017-01-01", "2017-01-31"],
   "imagery": {"extent": {
     "north": 49.041469,
     "east": 17.171631,
     "west": 9.497681,
     "south": 46.517296,
     "crs": "EPSG:32632"},
    "imagery": {"process_id": "get_collection", "name": "s2a_prd_msil1c"},
    "process_id": "filter_bbox"},
   "process_id": "filter_daterange"},
  "nir": "B08",
  "process_id": "NDVI",
  "red": "B04"},
 "process_id": "min_time"
}
]