import numpy as np

def GraphB(c, fig, root):
    """
    with a mpl subplot as an input, graph the currently selected magnetic coil's B field's cross section.
    """
    l = np.max(c.position) + c.diameter/2 + 1

    # construct grid for the cross section
    x = np.linspace(-l, l, 100)
    z = np.linspace(-l, l, 100)
    y = np.array([0])

    grid = np.array(np.meshgrid(x, y, z)).T  # shape = (100, 100, 3, 1)
    grid = np.moveaxis(grid, 2, 0)[0]  # shape = (100, 100, 3)
    #print(grid.shape)

    X, _, Y = np.moveaxis(grid, 2, 0)  # 3 arrays of shape (100, 100)

    # calculate B field for the entire grid
    Bs = np.array(c.getB(grid))  # [bx, by, bz]
    print(Bs.shape)
    try:
        Bx, _, By = np.moveaxis(Bs, 2, 0)
    except ValueError:
        Bs = Bs[-1]
        Bx, _, By = np.moveaxis(Bs, 2, 0)

    '''
    Bs shape: (step, step, 3)
    '''
    # gather arguments for the streamplot

    stream = fig.streamplot(X, Y, Bx, By, color=np.log(np.linalg.norm(Bs, axis=2)), density=1, cmap='viridis')
    # stream = fig.streamplot(X, Z, U, V, color= Bamp, density=2, norm=colors.LogNorm(vmin = Bamp.min(), vmax = Bamp.max()))
    fig.set_xlabel("X-axis (m)")
    fig.set_ylabel("Z-axis (m)")
    fig.set_title("Magnetic Field Cross Section on the X-Z plane at Y=0", pad=20)

    root.colorbar(stream.lines, ax=fig)