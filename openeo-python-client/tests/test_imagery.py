import unittest
from unittest import TestCase
from openeo.rest.imagery import RestImagery


class TestImagery(TestCase):

    def setUp(self):
        self.processes = RestImagery({},None)


    def test_date_range_filter(self):
        new_imagery = self.processes.date_range_filter("2016-01-01", "2016-03-10")

        graph = new_imagery.graph

        self.assertEqual(graph["process_id"],"filter_daterange")
        self.assertEqual(graph["args"]["imagery"], {})
        self.assertEqual(graph["args"]["from"], "2016-01-01")
        self.assertEqual(graph["args"]["to"], "2016-03-10")

    def test_bbox_filter(self):
        new_imagery = self.processes.bbox_filter(left=652000, right=672000,
                                               top=5161000, bottom=5181000,
                                               srs="EPSG:32632")

        graph = new_imagery.graph

        self.assertEqual(graph["process_id"],"filter_bbox")
        self.assertEqual(graph["args"]["imagery"], {})
        self.assertEqual(graph["args"]["left"], 652000)
        self.assertEqual(graph["args"]["right"], 672000)
        self.assertEqual(graph["args"]["top"], 5161000)
        self.assertEqual(graph["args"]["bottom"], 5181000)
        self.assertEqual(graph["args"]["srs"], "EPSG:32632")


    def test_apply_pixel(self):

        bandFunction = lambda cells,nodata: (cells[3]-cells[2])/(cells[3]+cells[2])
        new_imagery = self.processes.apply_pixel([], bandFunction)

        graph = new_imagery.graph

        self.assertEqual(graph["process_id"],"apply_pixel")
        self.assertEqual(graph["args"]["imagery"], {})
        self.assertEqual(graph["args"]["bands"], [])
        self.assertIsNotNone(graph["args"]["function"])

    def test_min_time(self):
        new_imagery = self.processes.min_time()

        graph = new_imagery.graph

        self.assertEqual(graph["process_id"], "min_time")
        self.assertEqual(graph["args"]["imagery"], {})

    def test_max_time(self):
        new_imagery = self.processes.max_time()

        graph = new_imagery.graph

        self.assertEqual(graph["process_id"], "max_time")
        self.assertEqual(graph["args"]["imagery"], {})

    def test_ndvi(self):
        new_imagery = self.processes.ndvi("B04", "B8A")

        graph = new_imagery.graph

        self.assertEqual(graph["process_id"], "NDVI")
        self.assertEqual(graph["args"]["imagery"], {})
        self.assertEqual(graph["args"]["red"], "B04")
        self.assertEqual(graph["args"]["nir"], "B8A")

    def test_mask(self):
        from shapely import geometry
        polygon = geometry.Polygon([[0, 0], [1.9, 0], [1.9, 1.9], [0, 1.9]])
        new_imagery = self.processes.mask(polygon)

        graph = new_imagery.graph

        self.assertEqual(graph["process_id"], "mask")
        self.assertEqual(graph["args"]["mask_shape"],
                         {'coordinates': (((0.0, 0.0), (1.9, 0.0), (1.9, 1.9), (0.0, 1.9), (0.0, 0.0)),),
                          'crs': {'properties': {'name': 'EPSG:4326'}, 'type': 'name'},
                          'type': 'Polygon'})

    def test_strech_colors(self):
        new_imagery = self.processes.stretch_colors(-1, 1)

        graph = new_imagery.graph

        self.assertEqual(graph["process_id"], "stretch_colors")
        self.assertEqual(graph["args"]["imagery"], {})
        self.assertEqual(graph["args"]["min"], -1)
        self.assertEqual(graph["args"]["max"], 1)
