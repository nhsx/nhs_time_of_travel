from __future__ import annotations
import shapely
import shapely.ops
from shapely.geometry import Point, Polygon, MultiPoint, MultiPolygon
from shapely.strtree import STRtree
import geopandas as gpd
import math
import networkx
import osmnx.distance
import pandas as pd
from nhstravel.loaders import gploader


class GpRegion:
    """Class GpRegion for loading a set of GP practice locations and handling their local geographical area.

    The class keeps an underlying pandas dataframe with the practices, and a Delaunay triangulation of the practices
    to divide the country into a set of area around each practice.

    The dataframe can be accessed with .df() and has columns:
    - Name: the name of the GP practice from the EPPRACUR file
    - latitude: the latitude of the GP practice
    - longitude: the longitude of the GP practice
    - point: the location as a (Longitude, Latitude) shapely point

    Typical usage is:

      area = GpRegion.load_england()
      botley_df = area.find_practices('botley')0
      botley_index = botley_df.index[0]
      botley_area = area.get_practice_area(botley_index)

    """

    @staticmethod
    def load_england():
        """Loads the EPPRACUR GP dataset and precached locations from a defined file path.

        Returns: a GpArea with all English GP practices.
        """
        return GpRegion(gploader.load())

    _df: pd.DataFrame
    _triangulation: list[Polygon]

    def __init__(self, df: pd.DataFrame):
        """ Construct a region with multiple GP practices from a dataframe.

        :param df: the dataframe which must have the columns:
                   'Name': the name of the practice
                   'latitude': the latitude of the practice
                   'longitude': the longitude of the practice
        """
        # filter any practice without a location
        mydf = df[['Name', 'latitude', 'longitude']]
        mydf = mydf[pd.notnull(mydf['latitude'])].copy()
        # fill in the location as a shapely point
        mydf['point'] = mydf.apply(_row_to_point, axis=1)
        # Get a set of deduplicated point tuples (as tuples as Point doesn't hash)
        points = {(p.x, p.y) for p in mydf.dropna()['point']}
        self._df = mydf
        self._triangulation = shapely.ops.triangulate(MultiPoint(list(points)))

    def get_df(self) -> pd.DataFrame:
        """Gets the internal GP practice dataframe.
        """
        return self._df

    def find_practices(self, name_substring: str) -> pd.DataFrame:
        """Finds all gp practices with the given substring in the name.

        The argument substring is changed to uppercase as the EPPRACUR dataset has names in uppercase.

        :return: a pandas dataframe with just the rows for matching GP practices
        """
        return self._df[self._df['Name'].str.contains(name_substring.upper())]

    def get_practice_area(self, index) -> GpArea:
        """ Gets a local catchment area of a GP defined by a polygon out to all the surrounding GP practices.

        Note that this means "catchment areas" overlap - any given location will be in the catchment area of all
        three surrounding GP practice areas in the Delaunay triangulation.

        :param index: the index label for the practice in the dataframe, used for lookup with .loc
        :return: a shapely Polygon for the catchment area
        """
        location: Point = self._df.loc[index]['point']
        area: Polygon = _find_loop(location, self._triangulation)
        return GpArea(area, self._df.loc[index])


class GpArea:
    """Class encapsulating the local area around a GP practice
    """
    area: Polygon
    row: pd.DataFrame  # a dataframe with a single row representing this practice

    def __init__(self, area: Polygon, row: pd.DataFrame):
        self.area = area
        self.row = row

    def osm_graph(self) -> networkx.classes.multidigraph.MultiDiGraph:
        """ Load the osmnx open streetmap graph for this area.
        """
        return osmnx.graph_from_polygon(polygon=self.area, simplify=True, network_type="walk")

    def calculate_walking_distance_polys(self, osmgraph, travel_speed_kmh=4.5, radius_minutes=5.0):
        """

        :param travel_speed_kmh: the assumed walking speed in km/h
        :param radius_minutes: the time in minutes to put in each polygon. Eg, if 5, the first polygon will be places
               0-5 minutes walk, the second 5-10 minutes walk and so on
        :return: A geopandas dataframe with:
           index bucket_dist where 0 is the fist bucket of points (eg 0-5 minutes) and so on
           mp a MultiPolygon of areas that are the distance away for that bucket
           area as for mp, but could be a Polygon for areas which are only one polygon
        """
        practice_node: int = osmnx.distance.nearest_nodes(osmgraph, self.row['longitude'], self.row['latitude'])
        node_distances: dict[int, float] = networkx.shortest_path_length(osmgraph, target=practice_node,
                                                                         weight='length')
        bucket_distance_m: float = 1000 * travel_speed_kmh * radius_minutes / 60.0

        # for each node, build a dataframe with the index, a Point, the distance to the GP surgery, and which
        # bucket it is in
        node_data = pd.DataFrame([
            {
                'node_index': u,
                'point': Point(node['x'], node['y']),
                'dist': node_distances[u],
                'bucket_dist': math.ceil(node_distances[u] / bucket_distance_m),
            }
            for u, node in osmgraph.nodes(data=True) if self.area.contains(Point(node['x'], node['y']))
        ])
        # Calculate the little voronoi area around each node
        voronoi = shapely.ops.voronoi_diagram(MultiPoint(node_data['point'].values))
        # trim it so they add up to the original area
        trimmed = [poly.intersection(self.area) for poly in voronoi.geoms]
        # Unfortunately voronoi does not keep the output ordering. So we have to (inefficiently)
        # iterate over the nodes to re-order
        diagram = STRtree(trimmed)
        ordered = [diagram.nearest(point) for point in node_data['point']]
        node_data['area'] = ordered
        geovoronoi = gpd.GeoDataFrame(node_data, geometry='area')
        # dissolve them down to grouped polygons
        result = geovoronoi[['bucket_dist', 'area']].dissolve(by='bucket_dist')
        # Unfortunately geovoronoi isn't consistent about whether it returns MultiPolygons or Polygons,
        # so normalize to MultiPolygons
        result = result.assign(
            mp=result['area'].apply(lambda p: p if isinstance(p, MultiPolygon) else MultiPolygon([p])))
        result.set_geometry('mp')
        return result


def _to_triangles(point: Point, triangulation: list[Polygon]):
    """ Get all the triangles with a corner of a particular point

    :param point: a point which should be a corner of some triangles
    :param triangulation: the list of all triangles
    :return: all triangles that contain the point, with the point as the first coordinate, maintaining the cyclical
             order of the points
    """
    p = (point.x, point.y)
    result = []
    # This could be faster by preprocessing, but just the loop is quick enough
    # loop over triangles to find first triangle with the point in it
    for i in range(len(triangulation)):
        coords = list(triangulation[i].exterior.coords)[0:3]
        if p in coords:
            for j in range(len(coords)):
                if coords[j] == p:
                    result.append((p, coords[(j - 1) % len(coords)], coords[(j + 1) % len(coords)]))
                    break
    return result


def _find_loop(point: Point, triangulation: list[Polygon]):
    """
    Find the loop around the given point formed by all triangles in the triangulation
    :param point:
    :param triangulation:
    :return:
    """
    triangles = _to_triangles(point, triangulation)
    if len(triangles) == 0:
        raise ValueError("No triangles were found overlapping with point " + str(point))
    # turn into a map from second point to last point
    to_next = {y: z for x, y, z in triangles}
    first_point = triangles[0][1]
    next_point = triangles[0][2]
    result = [Point(first_point)]
    while next_point != first_point:
        result.append(Point(next_point))
        next_point = to_next[next_point]
    return Polygon(result)


def _row_to_point(row):
    return Point(row['longitude'], row['latitude'])
