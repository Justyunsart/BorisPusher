#
#
import magpylib as magpy
import plotly.graph_objects as go
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation as R
from scipy.interpolate import griddata
from mpl_toolkits.mplot3d import Axes3D

#
#
# Construct two coils from windings
coil1 = magpy.Collection(style_label="coil1")
for z in np.linspace(-0.0005, 0.0005, 3):
    coil1.add(magpy.current.Circle(current=-1, diameter=1, position=(0, 0, z)))
coil1.position = (0, 0, -1.4)
#
coil2 = magpy.Collection(style_label="coil2")
for z in np.linspace(-0.0005, 0.0005, 3):
    coil2.add(magpy.current.Circle(current=1, diameter=1, position=(0, 0, z)))
coil2.position = (0, 0, 1.4)

# SPINDLECUSP consists of two coils
spindle = coil1 + coil2

# Move the spindle
#spindle.position = np.linspace((0, 0, 0), (0.05, 0.05, 0.05), 15)
spindle.rotate_from_angax(54.8, "y", start=0)
#spindle.rotate_from_angax(45, "x", start=0)
spindle.rotate_from_angax(45, "z", start=0)

# Move the coils
#coil1.move(np.linspace((0, 0, 0), (0.005, 0, 0), 15))
#coil2.move(np.linspace((0, 0, 0), (-0.005, 0, 0), 15))

# Move the windings
#for coil in [coil1, coil2]:
#    for i, wind in enumerate(coil):
#        wind.move(np.linspace((0, 0, 0), (0, 0, (2 - i) * 0.001), 15))

# Display as animation
#fig = go.Figure()
#fig.add_trace(go.Scatter3d( x=(-0.03,0.03), y=(-0.03,0.03), z=(-0.03,0.03) ))
#fig.show()
#magpy.show(*spindle, animation=True, style_path_show=False)
#how to combine the show of Fig and *spindle together !!!

def GraphB(c, fig, root):
    """
    with a mpl subplot as an input, graph the currently selected magnetic coil's B field's cross section.
    """
    l = np.max(c[0][0].position) + c[0][0].diameter/2 + 2.5

    # construct grid for the cross section
    x = np.linspace(-l, l, 100)
    z = np.linspace(-l, l, 100)
    #y = np.zeros(100)

    _x, _z = np.array(np.meshgrid(x, z, indexing='ij'))
    points = np.column_stack([_x.ravel(), np.zeros(10000), _z.ravel()])

    #_x, _y, _z = np.moveaxis(grid, 2, 0)[0]  # shape = (100, 100, 3)
    #_grid_rot = np.column_stack(([_x.ravel(), _y.ravel(), _z.ravel()]))

    rot_1 = R.from_euler('y', 45, degrees=True)
    rot_2 = R.from_euler('z', 45, degrees=True)

    rotated_points = rot_1.apply(points)
    rotated_points = rot_2.apply(rotated_points)

    X = rotated_points[:, 0].reshape(_x.shape)
    Y = rotated_points[:, 1].reshape(_x.shape)
    Z = rotated_points[:, 2].reshape(_z.shape)

    grid = np.stack((X, Y, Z), axis=-1)
    print(grid.shape)

    # calculate B field for the entire grid
    Bs = np.array(c.getB(grid))  # [bx, by, bz]
    print(Bs.shape)
    Bmag = np.linalg.norm(Bs, axis=2)
    Bx, By, Bz = np.moveaxis(Bs, -1, 0)
    print(Bx.shape)
    # gather arguments for the streamplot
    xi, zi = np.meshgrid(np.linspace(X.min(), X.max(), 100),
                         np.linspace(Z.min(), Z.max(), 100))
    coords = np.column_stack([X.ravel(), Z.ravel()])
    Bx_i = griddata(coords, Bx.ravel(), (xi, zi), method='linear')
    Bz_i = griddata(coords, Bz.ravel(), (xi, zi), method='linear')
    Bmag_i = griddata(coords, Bmag.ravel(), (xi, zi), method='linear')


    stream = fig.streamplot(xi, zi, Bx_i, Bz_i, color=np.log(Bmag_i + 1e-12), density=1, cmap='viridis')
    # stream = fig.streamplot(X, Z, U, V, color= Bamp, density=2, norm=colors.LogNorm(vmin = Bamp.min(), vmax = Bamp.max()))
    fig.set_xlabel("X-axis (interpolated) (m)")
    fig.set_ylabel("Z-axis (interpolated) (m)")
    fig.set_title("Magnetic Field Cross Section, rotated", pad=20)

    root.colorbar(stream.lines, ax=fig)

def cir(a, dia, d, gap):
    # current Loop creation, superimpose Loops and their fields
    s1 = magpy.current.Circle(current=a, diameter=dia).move([-(d)-gap,0,0]).rotate_from_angax(90, [0, 1, 0])
    s2 = magpy.current.Circle(current=-a, diameter=dia).move([(d)+gap,0,0]).rotate_from_angax(90, [0, 1, 0])
    s3 = magpy.current.Circle(current=-a, diameter=dia).move([0,-(d)-gap,0]).rotate_from_angax(-90, [1, 0, 0])
    s4 = magpy.current.Circle(current=a, diameter=dia).move([0,(d)+gap,0]).rotate_from_angax(-90, [1, 0, 0])
    s5 = magpy.current.Circle(current=a, diameter=dia).move([0,0,-(d)-gap]).rotate_from_angax(90, [0, 0, 1])
    s6 = magpy.current.Circle(current=-a, diameter=dia).move([0,0,(d)+gap]).rotate_from_angax(90, [0, 0, 1])

    c = magpy.Collection(s1,s2,s3,s4,s5,s6, style_color='black')
    return c


if __name__ == '__main__':
    fig = plt.figure()
    #ax = fig.add_subplot(121)
    ax1 = fig.add_subplot(111, projection='3d')
    #GraphB(spindle, ax, fig)
    # Prepare some coordinates for the cube
    # This creates a 3x3x3 grid of indices (0-2)
    x, y, z = np.indices((3, 3, 3))

    magpy.show(*spindle, canvas=ax1)

    # create visual reference hex
    hex = cir(100, 2, 1.1, 0)

    magpy.show(hex, canvas=ax1)

    plt.show()

