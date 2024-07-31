import magpylib as mp
import numpy as np
from magpy4c1 import c, side

Inp = np.array([[0,0,120],
       [0,0,0]])

def BFields(inp):
    out = []

    for i in inp:
        isBounds = i.any() > side
        Bf = [0.,0.,0.]
        if(not isBounds):
            Bf = c.getB(i, squeeze=True)
        out.append(Bf)
    return np.array(out)

# print(BFields(Inp))