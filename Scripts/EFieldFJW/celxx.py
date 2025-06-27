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

def cel(kc, p=1.0, a=1.0, b=1.0):
    """
    Computes the complete elliptic integral using Bulirsch's CEL algorithm.

    cel(kc, p, a, b) ≡ ∫₀^{π/2} (a·cos²φ + b·sin²φ) / ((cos²φ + p·sin²φ)·√(cos²φ + kc²·sin²φ)) dφ

    Parameters:
    kc: float - complementary modulus (kc² = 1 - k²)
    p: float
    a: float
    b: float

    Returns:
    float - value of the elliptic integral
    """

    if kc == 0.0:
        raise ValueError("kc cannot be zero.")

    errtol = 1e-8
    k = abs(kc)
    pp = p
    aa = a
    bb = b
    em = 1.0

    if p > 0.0:
        pp = np.sqrt(p)
        b = b / pp
    else:
        f = k * k
        q = 1.0 - f
        g = 1.0 - pp
        f = f - pp
        q = (b - a * pp) * q / (g * g) + a * f / g
        pp = np.sqrt(f / g)
        a = (a - b) / g + a
        b = q

    f = aa
    aa = a
    cc = a
    dd = b
    ee = pp

    while True:
        f = cc
        cc = (aa + bb) / 2.0
        g = ee / (bb + aa)
        bb = np.sqrt(bb * aa)
        ee = g * ee
        aa = cc
        if abs(f - cc) <= errtol * f:
            break

    result = (np.pi / 2.0) * (aa * dd + bb * ee) / (aa * (aa + pp))
    return result