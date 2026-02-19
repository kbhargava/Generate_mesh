import numpy as np
from scipy.spatial import Delaunay, Voronoi, ConvexHull
try:
    from scipy.spatial import SphericalVoronoi
except Exception:
    SphericalVoronoi = None

def latlon_to_xy(lat_deg, lon_deg):
    # simple equirectangular projection (lon,lat)
    x = lon_deg.astype(float)
    y = lat_deg.astype(float)
    return np.vstack([x, y]).T


def generate_control_grid(spacing_deg):
    """Generate a simple lat/lon control grid with given spacing in degrees.

    This produces a regular lat/lon grid (not equal-area) which is sufficient
    for coarse control points. Returns (lat_array, lon_array).
    """
    spacing = float(spacing_deg)
    lats = np.arange(-90, 90 + 1e-6, spacing)
    lons = np.arange(-180, 180 + 1e-6, spacing)
    lat_list = []
    lon_list = []
    for la in lats:
        for lo in lons:
            lat_list.append(la)
            lon_list.append(lo)
    return np.array(lat_list), np.array(lon_list)


def great_circle_distance_deg(lat1_deg, lon1_deg, lat2_deg, lon2_deg):
    """Compute great-circle angular distance in degrees between arrays of points.

    lat1, lon1 may be scalars or 1D arrays; lat2, lon2 similarly. This function
    returns a matrix of distances when both are arrays, or a vector when one is array.
    """
    # convert to radians
    lat1 = np.deg2rad(np.asarray(lat1_deg))
    lon1 = np.deg2rad(np.asarray(lon1_deg))
    lat2 = np.deg2rad(np.asarray(lat2_deg))
    lon2 = np.deg2rad(np.asarray(lon2_deg))

    # use spherical law of cosines (numerically stable for our sizes)
    sin1 = np.sin(lat1)
    sin2 = np.sin(lat2)
    cos1 = np.cos(lat1)
    cos2 = np.cos(lat2)

    # Broadcast to 2D arrays
    s1 = sin1.reshape(-1, 1) if sin1.ndim == 1 else sin1
    s2 = sin2.reshape(1, -1) if sin2.ndim == 1 else sin2
    c1 = cos1.reshape(-1, 1) if cos1.ndim == 1 else cos1
    c2 = cos2.reshape(1, -1) if cos2.ndim == 1 else cos2
    dlon = (lon1.reshape(-1, 1) - lon2.reshape(1, -1)) if lon1.ndim == 1 and lon2.ndim == 1 else (lon1 - lon2)

    cos_angle = (s1 * s2) + (c1 * c2 * np.cos(dlon))
    # clip
    cos_angle = np.clip(cos_angle, -1.0, 1.0)
    angle = np.arccos(cos_angle)
    return np.rad2deg(angle)

def latlon_to_xyz(lat_deg, lon_deg, alt=None, radius=1.0):
    # Map latitude/longitude to 3D Cartesian coordinates on a sphere of given radius.
    lat = np.deg2rad(lat_deg)
    lon = np.deg2rad(lon_deg)
    x = np.cos(lat) * np.cos(lon)
    y = np.cos(lat) * np.sin(lon)
    z = np.sin(lat)
    if alt is not None:
        r = radius + alt.astype(float)
    else:
        r = radius
    x = x * r
    y = y * r
    z = z * r
    return np.vstack([x, y, z]).T

def generate_delaunay_2d(points2d):
    tri = Delaunay(points2d)
    return tri

def generate_voronoi_2d(points2d):
    vor = Voronoi(points2d)
    return vor

def generate_delaunay_3d(points3d):
    # 3D Delaunay (tetrahedra). For surface triangulation on sphere use ConvexHull instead.
    tri = Delaunay(points3d)
    return tri

def convex_hull_triangles(points3d):
    hull = ConvexHull(points3d)
    return hull

def spherical_delaunay(lat_deg, lon_deg, alt=None, radius=1.0):
    # Map to 3D on sphere and return points and surface hull triangulation
    pts3 = latlon_to_xyz(lat_deg, lon_deg, alt=alt, radius=radius)
    hull = convex_hull_triangles(pts3)
    return pts3, hull

def spherical_voronoi(lat_deg, lon_deg, radius=1.0, center=None):
    if SphericalVoronoi is None:
        raise RuntimeError('SphericalVoronoi not available in this SciPy version')
    pts3 = latlon_to_xyz(lat_deg, lon_deg, alt=None, radius=radius)
    if center is None:
        center = np.array([0.0, 0.0, 0.0])
    sv = SphericalVoronoi(pts3, radius=radius, center=center)
    sv.sort_vertices_of_regions()
    return sv
