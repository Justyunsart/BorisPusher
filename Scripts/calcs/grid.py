import numpy as np

"""
Functions involving meshgrids
"""

def generate_square_meshgrid_3d(lim, nump=100):
    _ = np.linspace(-lim, lim, nump)
    return np.array(np.meshgrid(_,_,_, indexing='ij'))

def index_cross_sections(grid, axis='xy'):
    assert axis in ('xy', 'xz', 'yz')
    ax_dct = {'xy':3, 'xz':2, 'yz':1} # the axis index to zero out in the cross section
    ind = grid.shape[-1] // 2 # assuming mid-index is where the axis is approx. zero

    out =  np.take(grid, ind, axis=ax_dct[axis])
    return np.delete(out, ax_dct[axis]-1, axis=0)    

if __name__ == "__main__":
    grid = generate_square_meshgrid_3d(3)
    grid_ind = index_cross_sections(grid)
    print(grid_ind.shape)