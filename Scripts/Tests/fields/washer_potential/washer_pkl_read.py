
"""
graph some stuff assuming you made a meshgrid of the washer
potential
"""

if __name__ == "__main__":
    import pickle
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib as mpl

    filename = "mirror_washer_potential.pkl"
    # read pickle file
    with open(filename, 'rb') as f:
        loaded = pickle.load(f)

    # data is (N, N, N, 3)
    data = np.moveaxis(loaded, -1, 0)
    data_mag = np.linalg.norm(data, axis=0)

    # coodinate data that the original pickle file used
    _r_vals = np.linspace(0.01, 1, 200)
    _z_vals = np.linspace(0.01, 1, 200)

    fig, ax = plt.subplots()

    def graph_contour():
        ax.contourf(_r_vals, _z_vals, data_mag[:, 100, :], levels=100, norm=mpl.colors.SymLogNorm(linthresh=0.03, linscale=0.03, vmin=np.min(data_mag), vmax=np.max(data_mag)))

    graph_contour()
    plt.show()
