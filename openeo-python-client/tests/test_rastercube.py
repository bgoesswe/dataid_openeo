from unittest import TestCase
from openeo.rest.imagecollectionclient import ImageCollectionClient
from openeo.graphbuilder import GraphBuilder


class TestRasterCube(TestCase):

    def setUp(self):
        builder = GraphBuilder()
        id = builder.process("get_collection", {'name': 'S1'})

        self.imagery = ImageCollectionClient(id, builder, None)

    def test_date_range_filter(self):
        new_imagery = self.imagery.date_range_filter("2016-01-01", "2016-03-10")

        graph = new_imagery.graph[new_imagery.node_id]

        self.assertEqual(graph["process_id"], "filter_temporal")
        self.assertIn("data", graph['arguments'])
        self.assertEqual(graph["arguments"]["from"], "2016-01-01")
        self.assertEqual(graph["arguments"]["to"], "2016-03-10")

    def test_bbox_filter(self):
        new_imagery = self.imagery.bbox_filter(left=652000, right=672000,
                                               top=5161000, bottom=5181000,
                                               srs="EPSG:32632")

        graph = new_imagery.graph[new_imagery.node_id]

        self.assertEqual(graph["process_id"], "filter_bbox")
        self.assertIn("data", graph['arguments'])
        self.assertEqual(graph["arguments"]["west"], 652000)
        self.assertEqual(graph["arguments"]["east"], 672000)
        self.assertEqual(graph["arguments"]["north"], 5161000)
        self.assertEqual(graph["arguments"]["south"], 5181000)
        self.assertEqual(graph["arguments"]["crs"], "EPSG:32632")

    def test_min_time(self):
        new_imagery = self.imagery.min_time()

        graph = new_imagery.graph[new_imagery.node_id]

        self.assertEqual(graph["process_id"], "reduce")
        self.assertIn("data", graph['arguments'])

    def test_max_time(self):
        new_imagery = self.imagery.max_time()

        graph = new_imagery.graph[new_imagery.node_id]

        self.assertEqual(graph["process_id"], "reduce")
        self.assertIn("data", graph['arguments'])

    def test_ndvi(self):
        new_imagery = self.imagery.ndvi("B04", "B8A")

        graph = new_imagery.graph[new_imagery.node_id]

        self.assertEqual(graph["process_id"], "NDVI")
        self.assertIn("data", graph['arguments'])

    def test_mask(self):
        from shapely import geometry
        polygon = geometry.Polygon([[0, 0], [1.9, 0], [1.9, 1.9], [0, 1.9]])
        new_imagery = self.imagery.mask(polygon)

        graph = new_imagery.graph[new_imagery.node_id]

        self.assertEqual(graph["process_id"], "mask")
        self.assertEqual(graph["arguments"]["mask_shape"],
                         {'coordinates': (((0.0, 0.0), (1.9, 0.0), (1.9, 1.9), (0.0, 1.9), (0.0, 0.0)),),
                          'crs': {'properties': {'name': 'EPSG:4326'}, 'type': 'name'},
                          'type': 'Polygon'})

    def test_strech_colors(self):
        new_imagery = self.imagery.stretch_colors(-1, 1)

        graph = new_imagery.graph[new_imagery.node_id]

        self.assertEqual(graph["process_id"], "stretch_colors")
        self.assertIn("data", graph['arguments'])
        self.assertEqual(graph["arguments"]["min"], -1)
        self.assertEqual(graph["arguments"]["max"], 1)
