import argparse
import os
import numpy as np
from .io import read_points, read_yaml
from .mesh import (
    latlon_to_xy,
    latlon_to_xyz,
    generate_delaunay_2d,
    generate_voronoi_2d,
    generate_delaunay_3d,
    convex_hull_triangles,
    spherical_delaunay,
    spherical_voronoi,
    generate_control_grid,
    great_circle_distance_deg,
)
from .plot import plot_2d_delaunay, plot_2d_voronoi, plot_3d_convex_hull, plot_3d_spherical_voronoi

def ensure_outdir(d):
    os.makedirs(d, exist_ok=True)

def cmd_generate(args):
    lat, lon, alt = read_points(args.input)
    cfg = read_yaml(args.input)
    outdir = args.outdir or 'outputs'
    ensure_outdir(outdir)
    scheme = args.scheme.lower()
    dim = int(args.dim)
    if dim == 2:
        pts2 = latlon_to_xy(lat, lon)
        if scheme == 'delaunay':
            tri = generate_delaunay_2d(pts2)
            out = os.path.join(outdir, 'delaunay_2d.html')
            plot_2d_delaunay(pts2, tri, out)
            print('Saved', out)
        elif scheme == 'voronoi':
            vor = generate_voronoi_2d(pts2)
            out = os.path.join(outdir, 'voronoi_2d.html')
            plot_2d_voronoi(pts2, vor, out)
            print('Saved', out)
        else:
            raise SystemExit('Unknown scheme for 2D: '+scheme)
    elif dim == 3:
        # For earth-science use we treat 3D as points on globe surface.
        radius = 1.0
        if scheme == 'delaunay':
            # Optionally add control grid and remove CONTROL points that are
            # within `remove_within_deg` of any original observation. Originals
            # are always kept.
            ctrl_cfg = cfg.get('control') or cfg.get('control_grid')
            original_count = len(lat)
            if ctrl_cfg:
                spacing = float(ctrl_cfg.get('spacing_deg', 20))
                remove_deg = float(ctrl_cfg.get('remove_within_deg', 0.5))
                ctrl_lat, ctrl_lon = generate_control_grid(spacing)
                # compute distances between each control point and each original
                # result shape: (n_ctrl, n_orig). For each control point we
                # determine whether it is farther than `remove_deg` from all
                # originals; if not, the control point is removed.
                dmat = great_circle_distance_deg(ctrl_lat, ctrl_lon, lat, lon)
                keep_ctrl = (dmat > remove_deg).all(axis=1)
                kept_ctrl_lat = ctrl_lat[keep_ctrl]
                kept_ctrl_lon = ctrl_lon[keep_ctrl]
                # original points are kept; original_count is number of originals
                original_count = len(lat)
                # combine originals first, then kept control points
                combined_lat = np.concatenate([lat, kept_ctrl_lat]) if len(kept_ctrl_lat) > 0 else lat
                combined_lon = np.concatenate([lon, kept_ctrl_lon]) if len(kept_ctrl_lon) > 0 else lon
                combined_alt = np.concatenate([alt, np.zeros(len(kept_ctrl_lat))]) if len(kept_ctrl_lat) > 0 else alt
            else:
                combined_lat = lat
                combined_lon = lon
                combined_alt = alt

            pts3, hull = spherical_delaunay(combined_lat, combined_lon, alt=combined_alt, radius=radius)
            out = os.path.join(outdir, 'delaunay_3d_globe.html')

            # Optionally limit connections per node using k-nearest neighbors
            max_conn = None
            if ctrl_cfg:
                max_conn = ctrl_cfg.get('max_connections')
                if max_conn is not None:
                    max_conn = int(max_conn)

            edges_override = None
            if max_conn is not None and max_conn > 0:
                # build full distance matrix (n x n) and take k nearest neighbors per node
                npts = combined_lat.shape[0]
                dmat = great_circle_distance_deg(combined_lat, combined_lon, combined_lat, combined_lon)
                edges = set()
                for i in range(npts):
                    # ignore self (distance zero)
                    idxs = np.argsort(dmat[i])
                    picked = []
                    for j in idxs:
                        if j == i:
                            continue
                        picked.append(int(j))
                        if len(picked) >= max_conn:
                            break
                    for j in picked:
                        edges.add(tuple(sorted((int(i), int(j)))))
                edges_override = list(edges)

            plot_3d_convex_hull(pts3, hull, out, show_sphere=True, original_count=original_count, edges_override=edges_override)
            print('Saved', out)
        elif scheme == 'voronoi':
            sv = spherical_voronoi(lat, lon, radius=radius)
            out = os.path.join(outdir, 'voronoi_3d_globe.html')
            plot_3d_spherical_voronoi(sv, out)
            print('Saved', out)
        else:
            raise SystemExit('Unknown scheme for 3D: '+scheme)
    else:
        raise SystemExit('Only dim 2 or 3 supported')

def main():
    parser = argparse.ArgumentParser(description='Generate 2D/3D meshes from YAML lat/lon')
    sub = parser.add_subparsers(dest='cmd')
    gen = sub.add_parser('generate')
    gen.add_argument('--input', required=True)
    gen.add_argument('--scheme', default='delaunay')
    gen.add_argument('--dim', default='2')
    gen.add_argument('--outdir', default='outputs')
    args = parser.parse_args()
    if args.cmd == 'generate':
        cmd_generate(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
