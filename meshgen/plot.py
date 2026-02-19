import os
import numpy as np
import plotly.graph_objects as go

def save_html(fig, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.write_html(path)

def plot_2d_delaunay(points, delaunay, outpath_html):
    x = points[:,0]
    y = points[:,1]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode='markers', marker=dict(size=6)))
    # add triangles
    for tri in delaunay.simplices:
        xs = np.append(x[tri], x[tri[0]])
        ys = np.append(y[tri], y[tri[0]])
        fig.add_trace(go.Scatter(x=xs, y=ys, mode='lines', line=dict(color='blue')))
    fig.update_layout(xaxis_title='lon', yaxis_title='lat', title='2D Delaunay')
    save_html(fig, outpath_html)

def plot_2d_voronoi(points, vor, outpath_html):
    x = points[:,0]
    y = points[:,1]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=y, mode='markers'))
    # finite ridge segments
    for ridge in vor.ridge_vertices:
        if -1 in ridge:
            continue
        v0, v1 = ridge
        xs = [vor.vertices[v0,0], vor.vertices[v1,0]]
        ys = [vor.vertices[v0,1], vor.vertices[v1,1]]
        fig.add_trace(go.Scatter(x=xs, y=ys, mode='lines', line=dict(color='green')))
    fig.update_layout(xaxis_title='lon', yaxis_title='lat', title='2D Voronoi')
    save_html(fig, outpath_html)

def plot_3d_convex_hull(points3d, hull, outpath_html, show_sphere=False, show_faces=False, sphere_resolution=40, original_count=None, edges_override=None):
    x = points3d[:,0]
    y = points3d[:,1]
    z = points3d[:,2]
    # prepare figure
    fig = go.Figure()

    # optionally add a translucent sphere surface for context
    if show_sphere:
        radii = np.sqrt(x**2 + y**2 + z**2)
        r = float(np.mean(radii))
        u = np.linspace(0, 2 * np.pi, sphere_resolution)
        v = np.linspace(0, np.pi, sphere_resolution)
        uu, vv = np.meshgrid(u, v)
        xs = r * np.cos(uu) * np.sin(vv)
        ys = r * np.sin(uu) * np.sin(vv)
        zs = r * np.cos(vv)
        fig.add_trace(go.Surface(x=xs, y=ys, z=zs, colorscale='Blues', opacity=0.2, showscale=False))

    # optionally draw triangular faces as a semi-transparent mesh
    if show_faces:
        i = hull.simplices[:,0]
        j = hull.simplices[:,1]
        k = hull.simplices[:,2]
        mesh = go.Mesh3d(x=x, y=y, z=z, i=i, j=j, k=k, opacity=0.6, color='orange')
        fig.add_trace(mesh)

    # draw edges for each triangle for clearer wireframe
    # use provided edges_override if present, otherwise build unique edges from triangles
    if edges_override is not None:
        edges = set(tuple(sorted((int(a), int(b)))) for (a, b) in edges_override)
    else:
        edges = set()
        for tri in hull.simplices:
            a, b, c = tri
            edges.add(tuple(sorted((int(a), int(b)))))
            edges.add(tuple(sorted((int(b), int(c)))))
            edges.add(tuple(sorted((int(c), int(a)))))

    for (i, j) in edges:
        xs = [x[i], x[j]]
        ys = [y[i], y[j]]
        zs = [z[i], z[j]]
        # determine style: solid for original-original, dashed otherwise
        if original_count is None:
            style = dict(color='black', width=2)
        else:
            if i < original_count and j < original_count:
                style = dict(color='black', width=2)
            else:
                style = dict(color='grey', width=1.5, dash='dash')
        fig.add_trace(go.Scatter3d(x=xs, y=ys, z=zs, mode='lines', line=style, showlegend=False))

    # add points (nodes): original in red, control in yellow
    if original_count is None:
        scatter = go.Scatter3d(x=x, y=y, z=z, mode='markers', marker=dict(size=3, color='red'))
        fig.add_trace(scatter)
    else:
        orig_x = x[:original_count]
        orig_y = y[:original_count]
        orig_z = z[:original_count]
        ctrl_x = x[original_count:]
        ctrl_y = y[original_count:]
        ctrl_z = z[original_count:]
        fig.add_trace(go.Scatter3d(x=orig_x, y=orig_y, z=orig_z, mode='markers', marker=dict(size=4, color='red'), name='original'))
        if len(ctrl_x) > 0:
            fig.add_trace(go.Scatter3d(x=ctrl_x, y=ctrl_y, z=ctrl_z, mode='markers', marker=dict(size=3, color='yellow'), name='control'))

    fig.update_layout(title='3D Globe Mesh', scene=dict(aspectmode='data'))
    save_html(fig, outpath_html)

def plot_3d_spherical_voronoi(sv, outpath_html):
    # sv is a scipy.spatial.SphericalVoronoi instance
    fig = go.Figure()
    # draw vertices
    verts = sv.vertices
    fig.add_trace(go.Scatter3d(x=verts[:,0], y=verts[:,1], z=verts[:,2], mode='markers', marker=dict(size=2)))
    # draw region boundaries
    for region in sv.regions:
        # region is list of vertex indices; draw a closed loop
        coords = verts[region]
        xs = np.append(coords[:,0], coords[0,0])
        ys = np.append(coords[:,1], coords[0,1])
        zs = np.append(coords[:,2], coords[0,2])
        fig.add_trace(go.Scatter3d(x=xs, y=ys, z=zs, mode='lines', line=dict(color='green')))
    fig.update_layout(title='Spherical Voronoi', scene=dict(aspectmode='data'))
    save_html(fig, outpath_html)
