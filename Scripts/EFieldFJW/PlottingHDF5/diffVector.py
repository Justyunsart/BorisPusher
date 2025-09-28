import numpy as np
import plotly.graph_objects as go

def plot_difference_vectors_lines(df1, df2, step=10, colorscale="Viridis"):
    idx = range(0, len(df1), step)

    x_lines, y_lines, z_lines = [], [], []
    colors = []

    for i in idx:
        x0, y0, z0 = df2.loc[i, ["px", "py", "pz"]]
        x1, y1, z1 = df1.loc[i, ["px", "py", "pz"]]

        x_lines += [x0, x1, np.nan]   # use np.nan as separator (not None)
        y_lines += [y0, y1, np.nan]
        z_lines += [z0, z1, np.nan]

        mag = np.linalg.norm([x1 - x0, y1 - y0, z1 - z0])
        colors.append(mag)

    # Expand colors for each vertex in the trace (same value for start and end)
    colors_expanded = np.repeat(np.array(colors, dtype=float), 3)  # each segment -> [c,c,?]
    colors_expanded[-1] = np.nan  # final NaN color for the trailing separator (safe)

    fig = go.Figure()

    # Scatter3d line with per-point color (colors_expanded numeric, np.nan allowed)
    fig.add_trace(go.Scatter3d(
        x=x_lines, y=y_lines, z=z_lines,
        mode="lines",
        line=dict(width=4, color=colors_expanded, colorscale=colorscale),
        name="Difference Vectors (lines)",
        showlegend=True
    ))

    # Optional: show endpoints and starts (small markers)
    fig.add_trace(go.Scatter3d(x=df1["px"], y=df1["py"], z=df1["pz"],
                               mode="markers", marker=dict(size=2, color="red"), name="Q1"))
    fig.add_trace(go.Scatter3d(x=df2["px"], y=df2["py"], z=df2["pz"],
                               mode="markers", marker=dict(size=2, color="green"), name="Q2"))

    fig.update_layout(title=f"Difference vectors colored by magnitude (step={step})",
                      scene=dict(aspectmode="cube"))
    fig.show()