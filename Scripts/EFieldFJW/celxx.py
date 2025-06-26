import numpy as np
import math as m

def cel_x(k2, q2):
    """
    Modified Bulirsch cel algo. taken from

    "Numerically stable and computationally
    efficient expression for the magnetic field of a current loop.", M.Ortner et al,
    Magnetism 2023, 3(1), 11-31.
    """
    qc = np.sqrt(q2)
    p = 1
    g = qc / p
    cc = qc
    ss = 2 * cc * (qc / (qc + 1))
    em = 1.0
    kk = abs(qc)

    while m.fabs(g - qc) >= g * 1e-8:
        qc = 2 * np.sqrt(kk)
        kk = qc * em
        f = cc
        cc = cc + ss / p
        g = kk / p
        ss = 2 * (ss + f * g)
        p = p + g
        g = em
        em = em + qc

    return 1.5707963267948966 * (ss + cc * em) / (em * (em + p))
