import itertools

process_graph = { "process_graph": {"imagery": {"imagery": {"extent": ["2017-01-01", "2017-01-31"],
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
}

process_part = [
     '"north": 49.041469,'
     '"east": 17.171631,'
     '"west": 9.497681,'
     '"south": 46.517296,'
     '"crs": "EPSG:32632"']

result_list = []

for p1 in range(0, len(process_graph)):
    buffer_list = []
    for p2 in range(0, len(process_graph)):
        buffer_list.append(process_graph[p1])



print(result_list)