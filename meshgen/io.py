import yaml
import numpy as np

def _as_floats(seq):
    out = []
    for v in seq:
        try:
            out.append(float(v))
        except Exception:
            # Skip non-convertible values
            raise ValueError(f'Cannot convert value to float: {v}')
    return out


def read_points(yaml_path):
    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f) or {}

    # Support two formats:
    # 1) points: - lat: ... / lon: ... (list of dicts)
    # 2) lats: [...], lons: [...], optional alts: [...] (parallel lists)

    if 'lats' in data or 'lons' in data:
        lats = data.get('lats', [])
        lons = data.get('lons', [])
        alts = data.get('alts', None)
        if not lats or not lons:
            raise ValueError('Both "lats" and "lons" lists must be present and non-empty')
        lat = _as_floats(lats)
        lon = _as_floats(lons)
        if len(lat) != len(lon):
            raise ValueError('Length mismatch between "lats" and "lons"')
        if alts is None:
            alt = [0.0] * len(lat)
        else:
            alt = _as_floats(alts)
            if len(alt) != len(lat):
                raise ValueError('Length mismatch between "alts" and "lats"/"lons"')
        return np.array(lat), np.array(lon), np.array(alt)

    pts = data.get('points') or []
    if isinstance(pts, dict):
        # points: { lats: [...], lons: [...] }
        if 'lats' in pts or 'lons' in pts:
            lats = pts.get('lats', [])
            lons = pts.get('lons', [])
            alts = pts.get('alts', None)
            if not lats or not lons:
                raise ValueError('Both "lats" and "lons" lists must be present and non-empty')
            lat = _as_floats(lats)
            lon = _as_floats(lons)
            if len(lat) != len(lon):
                raise ValueError('Length mismatch between "lats" and "lons"')
            if alts is None:
                alt = [0.0] * len(lat)
            else:
                alt = _as_floats(alts)
                if len(alt) != len(lat):
                    raise ValueError('Length mismatch between "alts" and "lats"/"lons"')
            return np.array(lat), np.array(lon), np.array(alt)

    lat = []
    lon = []
    alt = []
    for p in pts:
        if not isinstance(p, dict):
            raise ValueError('Each entry in "points" must be a mapping with "lat" and "lon"')
        lat.append(float(p.get('lat', 0.0)))
        lon.append(float(p.get('lon', 0.0)))
        alt.append(float(p.get('alt', 0.0)))
    return np.array(lat), np.array(lon), np.array(alt)


def read_yaml(yaml_path):
    """Return the raw YAML as a Python dict for configuration access."""
    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f) or {}
    return data
