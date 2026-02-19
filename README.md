meshgen

A small Python utility to generate 2D/3D meshes from lat/lon points stored in a YAML file. Supports Delaunay (2D/3D) and Voronoi (2D). Produces interactive Plotly HTML visualizations that you can pan/zoom/rotate.

Install

Create a venv and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Example input YAML

See `examples/points.yaml`.

Usage

```bash
python -m meshgen.main generate \
  --input examples/points.yaml \
  --scheme delaunay \
  --dim 3 \
  --outdir outputs
```

Options:
- `--scheme`: `delaunay` or `voronoi`
- `--dim`: `2` or `3` (Voronoi only supports 2)

Outputs are saved to `--outdir` as interactive HTML files (and PNG if `kaleido` available).

Notes
- For 2D meshes the code uses (lon, lat) as x/y coordinates.
- For 3D (earth-science) meshes the code maps `(lat, lon)` to a spherical surface (unit radius by default). The surface triangulation is computed from the convex hull of the 3D points (this yields a surface mesh on the globe). Spherical Voronoi is generated using SciPy's `SphericalVoronoi` when available.

Examples for globe outputs:

```bash
python -m meshgen.main generate --input examples/points.yaml --scheme delaunay --dim 3 --outdir outputs
python -m meshgen.main generate --input examples/points.yaml --scheme voronoi --dim 3 --outdir outputs
```
