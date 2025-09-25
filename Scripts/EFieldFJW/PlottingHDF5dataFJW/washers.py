import numpy as np
import plotly.graph_objects as go

def make_washer(a, b, n_points=100, n_angles=100):
    """
    Generate coordinates for an annular disk (washer) in the xy-plane.
    a = inner radius
    b = outer radius
    """
    r = np.linspace(a, b, n_points)
    theta = np.linspace(0, 2*np.pi, n_angles)
    R, Theta = np.meshgrid(r, theta)
    X = R * np.cos(Theta)
    Y = R * np.sin(Theta)
    Z = np.zeros_like(X)
    return X, Y, Z

def transform_coords(X, Y, Z, orientation, offset):
    """
    Rotate/translate washer into the given cube face orientation.
    orientation: 'x+', 'x-', 'y+', 'y-', 'z+', 'z-'
    offset: c/2 (half width of cube)
    """
    if orientation == 'z+':   # xy plane at z=+c/2
        return X, Y, Z + offset
    elif orientation == 'z-': # xy plane at z=-c/2
        return X, Y, Z - offset
    elif orientation == 'x+': # yz plane at x=+c/2
        return Z + offset, X, Y
    elif orientation == 'x-': # yz plane at x=-c/2
        return -Z - offset, X, Y
    elif orientation == 'y+': # xz plane at y=+c/2
        return X, Z + offset, Y
    elif orientation == 'y-': # xz plane at y=-c/2
        return X, -Z - offset, Y
    else:
        raise ValueError("Invalid orientation")

def plot_washers(a, b, c):
    fig = go.Figure()

    X0, Y0, Z0 = make_washer(a, b)

    for orient in ['x+','x-','y+','y-','z+','z-']:
        X, Y, Z = transform_coords(X0, Y0, Z0, orient, c/2)
        fig.add_surface(x=X, y=Y, z=Z, colorscale="Viridis", showscale=False, opacity=0.7)

    # Add cube wireframe for reference
    cube_range = [-c/2, c/2]
    for x in cube_range:
        for y in cube_range:
            fig.add_trace(go.Scatter3d(x=[x,x], y=[y,y], z=cube_range,
                                       mode="lines", line=dict(color="black")))
    for x in cube_range:
        for z in cube_range:
            fig.add_trace(go.Scatter3d(x=[x,x], y=cube_range, z=[z,z],
                                       mode="lines", line=dict(color="black")))
    for y in cube_range:
        for z in cube_range:
            fig.add_trace(go.Scatter3d(x=cube_range, y=[y,y], z=[z,z],
                                       mode="lines", line=dict(color="black")))


    fig.update_layout(
        title="Six Washer Disks on Cube Faces",
        scene=dict(aspectmode="cube")
    )
    return fig

# Example usage: inner radius=0.2, outer radius=0.4, cube width=1.0
fig = plot_washers(a=0.2, b=0.4, c=1.0)

fig.show()
