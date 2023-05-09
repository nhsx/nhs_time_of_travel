from __future__ import annotations
import shapely
import shapely.ops
from shapely.geometry import Point, Polygon, MultiPoint, MultiPolygon
from shapely.strtree import STRtree
from matplotlib import pyplot
from descartes.patch import PolygonPatch
import geopandas as gpd
from haversine import haversine, Unit
import math
import networkx
import osmnx
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
        return GpRegion._from_df(gploader.load_england())

    _df: pd.DataFrame
    _triangulation: list[Polygon]

    def __init__(self, df: pd.DataFrame, triangulation: list[Polygon]):
        self._df = df
        self._triangulation = triangulation

    @classmethod
    def _from_df(cls, df):
        """Construct a region with multiple GP practices from a dataframe.

        :param df: the dataframe which must have the columns:
                   'Name': the name of the practice
                   'latitude': the latitude of the practice
                   'longitude': the longitude of the practice
        """
        # filter any practice without a location
        mydf = df[
            [
                "Name",
                "Postcode",
                "latitude",
                "longitude",
                "National Grouping",
                "High Level Health Geography",
            ]
        ]
        mydf = mydf[pd.notnull(mydf["latitude"])].copy()
        # fill in the location as a shapely point
        mydf["point"] = mydf.apply(_row_to_point, axis=1)
        # Get a set of deduplicated point tuples (as tuples as Point doesn't hash)
        points = {(p.x, p.y) for p in mydf.dropna()["point"]}
        return cls(mydf, shapely.ops.triangulate(MultiPoint(list(points))))

    def get_df(self) -> pd.DataFrame:
        """Gets the internal GP practice dataframe."""
        return self._df

    def find_practices(self, name_substring: str) -> pd.DataFrame:
        """Finds all gp practices with the given substring in the name.

        The argument substring is changed to uppercase as the EPPRACUR dataset has names in uppercase.

        :return: a pandas dataframe with just the rows for matching GP practices
        """
        return self._df[self._df["Name"].str.contains(name_substring.upper())]

    def find_practices_postcode_prefix(self, postcode_prefix: str) -> pd.DataFrame:
        """Finds all gp practices with a postcode that starts with a given prefix.

        :return: a pandas dataframe with just the rows for matching GP practices
        """
        return self._df[self._df["Postcode"].str.startswith(postcode_prefix.upper())]

    def get_practice_area(self, index) -> GpArea:
        """Gets a local catchment area of a GP defined by a polygon out to all the surrounding GP practices.

        Note that this means "catchment areas" overlap - any given location will be in the catchment area of all
        three surrounding GP practice areas in the Delaunay triangulation.

        :param index: the index label for the practice in the dataframe, used for lookup with .loc
        :return: a shapely Polygon for the catchment area
        """
        location: Point = self._df.loc[index]["point"]
        area: Polygon = _find_loop(location, self._triangulation)
        return GpArea(area, self._df.loc[index])

    def get_subregion_by_poly(self, poly: Polygon) -> GpRegion:
        """Creates a new GP Region that includes only the triangles which overlap the given polygon. Note that this
        will include some locations outside the polygon, to produce a surrounding ring, which makes it more likely
        travel times within the polygon will be accurate."""
        subtriangulation = []
        locations = set()
        for triangle in self._triangulation:
            if triangle.intersects(poly):
                subtriangulation.append(triangle)
                for coord in list(triangle.exterior.coords)[0:3]:
                    locations.add((coord[0], coord[1]))
        subdf = self._df.loc[
            self._df["point"].apply(lambda p: (p.x, p.y)).isin(locations)
        ]
        return GpRegion(subdf, subtriangulation)

    def get_subregion_by_filter(self, filter: pd.core.series.Series):
        """Creates a new subregion that uses the same triangles, but filters down to specific GP practices using the
        given filter. This will include any triangle that touches any of the given practices, and any practice from
        one of those triangles. Be aware this means that more practices than expected will be returned, because of the
        extra ones to form the border.

        Example usage:
        england = GpRegion.load_england()
        bath = england.get_subregion(england._df['High Level Health Geography'].isin(['QOX']))

        :param filter a pandas Series that can be used to index _df
        """
        sub_df = self._df.loc[filter]
        locations = set([(p.x, p.y) for p in sub_df["point"].tolist()])
        sub_tr = []
        for triangle in self._triangulation:
            for coord in list(triangle.exterior.coords)[0:3]:
                if coord in locations:
                    sub_tr.append(triangle)
                    break
        return GpRegion(sub_df, sub_tr)

    def pretty_plot(self, poly=None):
        """Plot the triangulation and points, and optionally an overlaying polygon"""
        fig, ax = pyplot.subplots()
        gpd.GeoSeries(self._triangulation).plot(ax=ax)
        if poly is not None:
            gpd.GeoSeries([poly]).plot(ax=ax, ec="black", color="None")
        gpd.GeoDataFrame(self._df, geometry="point").plot(ax=ax, color="green")

    def calculate_walking_distance_polys(
        self,
        triangle: Polygon,
        travel_speed_kmh=4.5,
        radius_minutes=5.0,
        graph: networkx.MultiDiGraph = None,
    ):
        """
        :param triangle: the triangle within this region to calculate the polys for
        :param travel_speed_kmh: the assumed walking speed in km/h
        :param radius_minutes: the time in minutes to put in each polygon. Eg, if 5, the first polygon will be places
               0-5 minutes walk, the second 5-10 minutes walk and so on
        :param graph: optional - a pre-downloaded graph which can be used to get the graph without a network fetch
        :return: A geopandas dataframe with:
           index bucket_dist where 0 is the first bucket of points (eg 0-5 minutes) and so on
           mp a MultiPolygon of areas that are the distance away for that bucket
           area as for mp, but could be a Polygon for areas which are only one polygon
        """
        # Optimization. If the sides of the triangle are less than the bucket size
        # then don't bother calculating walking distance. Just make the return value a single poly of the
        # whole triangle.
        # This isn't strictly correct, as paths could wiggle to increase the distance but saving the osmnx
        # fetches for small areas is probably worth it.
        bucket_distance_m: float = 1000 * travel_speed_kmh * radius_minutes / 60.0
        small: bool = True
        for i in range(3):
            side_length = haversine(
                triangle.exterior.coords[i],
                triangle.exterior.coords[i + 1],
                unit=Unit.METERS,
            )
            if side_length > bucket_distance_m:
                small = False
                break
        if small:
            return _single_bucket_polygon(triangle, 0)

        surrounding_poly = self._polygon_surrounding_triangle(triangle)
        # Load the osm_graph for the area surrounding the triangle
        if graph is not None:
            osmgraph = osmnx.graph_from_polygon(
                polygon=surrounding_poly, simplify=True, network_type="walk"
            )
        else:
            osmgraph = osmnx.truncate.truncate_graph_polygon(
                graph, surrounding_poly, retain_all=True
            )
        corner_a, corner_b, corner_c, ignored = triangle.exterior.coords
        # This could be optimized by only looking at nodes within the triangle
        # networkx does not support this, but it wouldn't be hard to code - just a BFS
        # and stop when all target nodes are reached. Leave the optimization until later,
        node_distances_a: dict[int, float] = _get_all_node_distances(osmgraph, corner_a)
        node_distances_b: dict[int, float] = _get_all_node_distances(osmgraph, corner_b)
        node_distances_c: dict[int, float] = _get_all_node_distances(osmgraph, corner_c)

        # for each node, build a dataframe with the index, a Point, the distance to the GP surgery, and which
        # bucket it is in
        node_data = pd.DataFrame(
            [
                {
                    "node_index": u,
                    "point": Point(node["x"], node["y"]),
                    "dist": min(
                        [node_distances_a[u], node_distances_b[u], node_distances_c[u]]
                    ),
                    "bucket_dist": math.floor(
                        min(
                            [
                                node_distances_a[u],
                                node_distances_b[u],
                                node_distances_c[u],
                            ]
                        )
                        / bucket_distance_m
                    ),
                }
                for u, node in osmgraph.nodes(data=True)
                if triangle.contains(Point(node["x"], node["y"]))
            ]
        )
        if len(node_data.index) == 0:
            # If we have no points, then assume a single triangle. Not perfect, maybe revisit
            return _single_bucket_polygon(triangle, 0)
        return _join_distances_to_polygons(node_data, triangle)

    def _polygon_surrounding_triangle(self, triangle: Polygon):
        triangle_points = list(triangle.exterior.coords)[0:3]
        triangle_points_set = set(triangle_points)
        surrounding_points = set()
        for other_triangle in self._triangulation:
            coords = set(list(other_triangle.exterior.coords)[0:3])
            if not triangle_points_set.isdisjoint(coords):
                surrounding_points.update(coords)
        return MultiPoint(list(surrounding_points)).convex_hull


class GpArea:
    """Class encapsulating the local area around a GP practice"""

    area: Polygon
    row: pd.DataFrame  # a dataframe with a single row representing this practice

    def __init__(self, area: Polygon, row: pd.DataFrame):
        self.area = area
        self.row = row

    def location(self) -> Point:
        return self.row["point"]

    def osm_graph(self) -> networkx.classes.multidigraph.MultiDiGraph:
        """Load the osmnx open streetmap graph for this area."""
        return osmnx.graph_from_polygon(
            polygon=self.area, simplify=True, network_type="walk"
        )

    def calculate_walking_distance_polys(
        self, osmgraph, travel_speed_kmh=4.5, radius_minutes=5.0
    ):
        """

        :param travel_speed_kmh: the assumed walking speed in km/h
        :param radius_minutes: the time in minutes to put in each polygon. Eg, if 5, the first polygon will be places
               0-5 minutes walk, the second 5-10 minutes walk and so on
        :return: A geopandas dataframe with:
           index bucket_dist where 0 is the first bucket of points (eg 0-5 minutes) and so on
           mp a MultiPolygon of areas that are the distance away for that bucket
           area as for mp, but could be a Polygon for areas which are only one polygon
        """
        location = self.row["point"]
        node_distances = _get_all_node_distances(osmgraph, (location.x, location.y))
        bucket_distance_m: float = 1000 * travel_speed_kmh * radius_minutes / 60.0

        # for each node, build a dataframe with the index, a Point, the distance to the GP surgery, and which
        # bucket it is in
        node_data = pd.DataFrame(
            [
                {
                    "node_index": u,
                    "point": Point(node["x"], node["y"]),
                    "dist": node_distances[u],
                    "bucket_dist": math.floor(node_distances[u] / bucket_distance_m),
                }
                for u, node in osmgraph.nodes(data=True)
                if self.area.contains(Point(node["x"], node["y"]))
            ]
        )
        return _join_distances_to_polygons(node_data, self.area)

    def pretty_plot(self):
        blue = "#6699cc"
        grey = "#999999"
        green = "#339933"
        fig = pyplot.figure(1, dpi=90)
        ax = fig.add_subplot(121)
        polygon = self.area
        exterior_x, exterior_y = polygon.exterior.xy
        ax.plot(exterior_x, exterior_y, color=grey, zorder=1, alpha=1)
        patch = PolygonPatch(
            polygon, facecolor=blue, edgecolor=blue, alpha=0.5, zorder=2
        )
        ax.add_patch(patch)
        location = self.location()
        ax.plot(location.x, location.y, "o", color=green, zorder=1, alpha=1)
        for x, y in polygon.exterior.coords:
            ax.plot(
                [location.x, x],
                [location.y, y],
                linestyle="dashed",
                zorder=1,
                color=grey,
            )


def _to_triangles(point: Point, triangulation: list[Polygon]):
    """Get all the triangles with a corner of a particular point

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
                    result.append(
                        (
                            p,
                            coords[(j - 1) % len(coords)],
                            coords[(j + 1) % len(coords)],
                        )
                    )
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
    return Point(row["longitude"], row["latitude"])


def _get_all_node_distances(osmgraph, point) -> dict[int, float]:
    node: int = osmnx.distance.nearest_nodes(osmgraph, point[0], point[1])
    node_distances: dict[int, float] = networkx.shortest_path_length(
        osmgraph, target=node, weight="length"
    )
    return node_distances


def _join_distances_to_polygons(node_data, limit: Polygon):
    # optimization for little spaces. If all of the bucket_dist are the same, just return the limit
    unique_buckets = node_data.bucket_dist.unique()
    if len(unique_buckets) == 1:
        return _single_bucket_polygon(limit, unique_buckets[0])

    # Calculate the little voronoi area around each node
    voronoi = shapely.ops.voronoi_diagram(MultiPoint(node_data["point"].values))
    # trim it so they add up to the original area
    trimmed = [poly.intersection(limit) for poly in voronoi.geoms]
    # Unfortunately voronoi does not keep the output ordering. So we have to (inefficiently)
    # iterate over the nodes to re-order
    diagram = STRtree(trimmed)
    ordered = [diagram.nearest(point) for point in node_data["point"]]
    node_data["area"] = ordered
    geovoronoi = gpd.GeoDataFrame(node_data, geometry="area")
    # dissolve them down to grouped polygons
    result = geovoronoi[["bucket_dist", "area"]].dissolve(by="bucket_dist")
    # Unfortunately geovoronoi isn't consistent about whether it returns MultiPolygons or Polygons,
    # so normalize to MultiPolygons
    result = result.assign(
        mp=result["area"].apply(
            lambda p: p if isinstance(p, MultiPolygon) else MultiPolygon([p])
        )
    )
    result.set_geometry("mp")
    return result


def _single_bucket_polygon(poly, bucket_dist):
    # if you aren't careful, DataFrame is too clever, and unwraps a MultiPolygon to a Polygon
    # so construct with columns, then fill with loc
    mp = MultiPolygon([poly])
    data = pd.DataFrame([{"area": poly, "mp": mp}])
    data.index.name = "bucket_dist"
    result = gpd.GeoDataFrame(data, geometry="mp")
    return result
