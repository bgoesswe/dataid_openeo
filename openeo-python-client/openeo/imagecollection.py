from abc import ABC
from typing import List, Dict, Union
from datetime import datetime,date

from openeo.job import Job
from shapely.geometry import Polygon, MultiPolygon


class ImageCollection(ABC):
    """Class representing Processes. """

    def __init__(self):
        pass


    def date_range_filter(self, start_date:Union[str,datetime,date],end_date:Union[str,datetime,date]) -> 'ImageCollection':
        """
        Specifies a date range filter to be applied on the ImageCollection

        :param start_date: Start date of the filter, inclusive, format: "YYYY-MM-DD".
        :param end_date: End date of the filter, exclusive, format e.g.: "2018-01-13".
        :return: An ImageCollection filtered by date.
        """
        pass

    def bbox_filter(self, left:float,right:float,top:float,bottom:float,srs:str) -> 'ImageCollection':
        """
        Specifies a bounding box to filter input image collections.

        :param left:
        :param right:
        :param top:
        :param bottom:
        :param srs:
        :return: An image collection cropped to the specified bounding box.
        """
        pass

    def apply(self,process:str,arguments = {}) -> 'ImageCollection':
        """
        Applies a unary process (a local operation) to each value of the specified or all dimensions in the data cube.
        https://open-eo.github.io/openeo-api/v/0.4.0/processreference/#apply

        :param process: A process (callback) to be applied on each value. The specified process must be unary meaning that it must work on a single value.
        :param dimensions: The names of the dimensions to apply the process on. Defaults to an empty array so that all dimensions are used.
        :return: A data cube with the newly computed values. The resolution, cardinality and the number of dimensions are the same as for the original data cube.
        """
        raise NotImplemented("Apply function not supported by this data cube.")


    def apply_pixel(self, bands: List, bandfunction) -> 'ImageCollection':
        """Apply a function to the given set of bands in this image collection.

        This type applies a simple function to one pixel of the input image or image collection.
        The function gets the value of one pixel (including all bands) as input and produces a single scalar or tuple output.
        The result has the same schema as the input image (collection) but different bands.
        Examples include the computation of vegetation indexes or filtering cloudy pixels.

        :param imagecollection: Imagecollection to apply the process, Instance of ImageCollection
        :param bands: Bands to be used
        :param bandfunction: Band function to be used

        :return: An image collection with the pixel applied function.
        """
        pass

    def apply_tiles(self, code: str) -> 'ImageCollection':
        """Apply a function to the tiles of an image collection.

        This type applies a simple function to one pixel of the input image or image collection.
        The function gets the value of one pixel (including all bands) as input and produces a single scalar or tuple output.
        The result has the same schema as the input image (collection) but different bands.
        Examples include the computation of vegetation indexes or filtering cloudy pixels.

        :param code: Code to apply to the ImageCollection

        :return: An image collection with the tiles applied function.
        """
        pass

    def aggregate_time(self, temporal_window, aggregationfunction) -> 'ImageCollection' :
        """ Applies a windowed reduction to a timeseries by applying a user defined function.
            DEPRECATED: use Aggregate_temporal

            :param temporal_window: The time windows to group by, can be a list of halfopen intervals
            :param aggregationfunction: The function to apply to each time window. Takes a pandas Timeseries as input.

            :return: An ImageCollection containing  a result for each time window
        """
        pass

    def aggregate_temporal(self, intervals:List,labels:List, reducer, dimension:str = None) -> 'ImageCollection' :
        """ Computes a temporal aggregation based on an array of date and/or time intervals.

            Calendar hierarchies such as year, month, week etc. must be transformed into specific intervals by the clients. For each interval, all data along the dimension will be passed through the reducer. The computed values will be projected to the labels, so the number of labels and the number of intervals need to be equal.

            If the dimension is not set, the data cube is expected to only have one temporal dimension.

            :param intervals: Temporal left-closed intervals so that the start time is contained, but not the end time.
            :param labels: Labels for the intervals. The number of labels and the number of groups need to be equal.
            :param reducer: A reducer to be applied on all values along the specified dimension. The reducer must be a callable process (or a set processes) that accepts an array and computes a single return value of the same type as the input values, for example median.
            :param dimension: The temporal dimension for aggregation. All data along the dimension will be passed through the specified reducer. If the dimension is not set, the data cube is expected to only have one temporal dimension.

            :return: An ImageCollection containing  a result for each time window
        """
        pass

    def reduce(self,reducer,dimension):
        """
        Applies a reducer to a data cube dimension by collapsing all the input values along the specified dimension into a single output value computed by the reducer.

        The reducer must accept an array and return a single value (see parameter reducer). Nominal values are possible, but need to be mapped, e.g. band names to wavelengths, date strings to numeric timestamps since 1970 etc.

        https://open-eo.github.io/openeo-api/v/0.4.0/processreference/#reduce

        :param reducer: A reducer to be applied on the specified dimension. The reducer must be a callable process (or a set processes) that accepts an array and computes a single return value of the same type as the input values, for example median.
        :param dimension: The dimension over which to reduce.
        :return: A data cube with the newly computed values. The number of dimensions is reduced, but the resolution and cardinality are the same as for the original data cube.
        """
        raise NotImplemented("This image collection does not support the reduce operation.")

    def reduce_time(self, aggregationfunction) -> 'ImageCollection' :
        """ Applies a windowed reduction to a timeseries by applying a user defined function.

            :param aggregationfunction: The function to apply to each time window. Takes a pandas Timeseries as input.

            :return: An ImageCollection without a time dimension
        """
        pass

    def min_time(self) -> 'ImageCollection':
        """
            Finds the minimum value of time series for all bands of the input dataset.

            :return: An ImageCollection without a time dimension.
        """
        pass

    def max_time(self) -> 'ImageCollection':
        """
            Finds the maximum value of time series for all bands of the input dataset.

            :return: An ImageCollection without a time dimension.
        """
        pass

    def mean_time(self) -> 'ImageCollection':
        """
            Finds the mean value of time series for all bands of the input dataset.

            :return: An ImageCollection without a time dimension.
        """
        pass

    def median_time(self) -> 'ImageCollection':
        """
            Finds the median value of time series for all bands of the input dataset.

            :return: An ImageCollection without a time dimension.
        """
        pass

    def count_time(self) -> 'ImageCollection':
        """
            Counts the number of images with a valid mask in a time series for all bands of the input dataset.

            :return: An ImageCollection without a time dimension.
        """
        pass

    def ndvi(self, red, nir) -> 'ImageCollection':
        """ NDVI

            :param red: Reference to the red band
            :param nir: Reference to the nir band

            :return An ImageCollection instance
        """
        pass


    def stretch_colors(self, min, max) -> 'ImageCollection':
        """ Color stretching

            :param min: Minimum value
            :param max: Maximum value

            :return An ImageCollection instance
        """
        pass

    def band_filter(self, bands) -> 'ImageCollection':
        """Filters the bands in the data cube so that bands that don't match any of the criteria are dropped from the data cube.
        The data cube is expected to have only one spectral dimension.
        The following criteria can be used to select bands:


            :param bands: List of band names or single band name as a string. The order of the specified array defines the order of the bands in the data cube, which can be important for subsequent processes.

            :return An ImageCollection instance
        """
        pass

    def mask(self,polygon: Union[Polygon, MultiPolygon], srs="EPSG:4326") -> 'ImageCollection':
        """
        Mask the image collection using a polygon. All pixels outside the polygon should be set to the nodata value.
        All pixels inside, or intersecting the polygon should retain their original value.

        TODO: Does mask by polygon imply cropping?
        TODO: what about naming? Masking can also be done using a raster mask...
        TODO: what will happen if the intersection between the mask and the imagecollection is empty? Raise an error?

        :param polygon: A polygon, provided as a
        :param srs: The reference system of the provided polygon, provided as an 'EPSG:XXXX' string. By default this is Lat Lon (EPSG:4326).
        :return: A new ImageCollection, with the mask applied.
        """

    ####VIEW methods #######
    def timeseries(self, x, y, srs="EPSG:4326") -> Dict:
        """
        Extract a time series for the given point location.

        :param x: The x coordinate of the point
        :param y: The y coordinate of the point
        :param srs: The spatial reference system of the coordinates, by default this is 'EPSG:4326', where x=longitude and y=latitude.

        :return: Dict: A timeseries
        """
        pass

    def zonal_statistics(self, regions, func, scale=1000, interval="day") -> 'Dict':
        """
        Calculates statistics for each zone specified in a file.

        :param regions: GeoJSON or a path to a GeoJSON file containing the
                        regions. For paths you must specify the path to a
                        user-uploaded file without the user id in the path.
        :param func: Statistical function to calculate for the specified
                     zones. example values: min, max, mean, median, mode
        :param scale: A nominal scale in meters of the projection to work
                      in. Defaults to 1000.
        :param interval: Interval to group the time series. Allowed values:
                        day, wee, month, year. Defaults to day.

        :return A timeseries
        """
        pass

    def polygonal_mean_timeseries(self, polygon: Union[Polygon, MultiPolygon]) -> Dict:
        """
        Extract a mean time series for the given (multi)polygon. Its points are expected to be in the EPSG:4326 coordinate
        reference system.

        :param polygon: The (multi)polygon

        :return: Dict: A timeseries
        """
        pass

    def tiled_viewing_service(self,**kwargs) -> Dict:
        """
        Returns metadata for a tiled viewing service that visualizes this layer.

        :param type: The type of viewing service to create, for instance: 'WMTS'
        :param title: A short description to easily distinguish entities.
        :param description: Detailed description to fully explain the entity. CommonMark 0.28 syntax MAY be used for rich text representation.

        :return: A dictionary object containing the viewing service metadata, such as the connection 'url'.
        """
        pass

    def download(self,outputfile:str, bbox="", time="",**format_options):
        """Extracts a binary raster from this image collection."""
        pass

    def send_job(self) -> Job:
        """Sends the current process to the backend, for batch processing.

            :return: Job: A job object that can be used to query the processing status.
        """
        pass

    def graph_add_process(self, process_id, args) -> 'ImageCollection':
        """
        Returns a new imagecollection with an added process with the given process
        id and a dictionary of arguments

        :param process_id: String, Process Id of the added process.
        :param args: Dict, Arguments of the process.

        :return: imagecollection: Instance of the ImageCollection class
        """
        pass
