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


def cel(kc, p=1.0, a=1.0, b=1.0, debug=False):
    """
    Computes the complete elliptic integral using Bulirsch's CEL algorithm.

    cel(kc, p, a, b) ≡ ∫₀^{π/2} (a·cos²φ + b·sin²φ) / ((cos²φ + p·sin²φ)·√(cos²φ + kc²·sin²φ)) dφ

    Parameters:
    kc: float - complementary modulus (kc² = 1 - k²)
    p: float
    a: float
    b: float
    debug: bool - if True, print internal values at each iteration

    Returns:
    float - value of the elliptic integral
    """
    if kc == 0.0:
        raise ValueError("kc cannot be zero.")
    if not np.isfinite(kc) or not np.isfinite(a) or not np.isfinite(b):
        raise ValueError(f"Non-finite input: kc={kc}, a={a}, b={b}")

    errtol = 1e-8
    k = abs(kc)
    pp = p
    aa = a
    bb = b

    if p > 0.0:
        pp = np.sqrt(p)
        bb = bb / pp
    else:
        f = k * k
        q = 1.0 - f
        g = 1.0 - pp
        f = f - pp
        q = (b - a * pp) * q / (g * g) + a * f / g
        pp = np.sqrt(f / g)
        aa = (a - b) / g + a
        bb = q

    f = aa
    cc = aa
    dd = bb
    ee = pp

    iter_count = 0
    while True:
        iter_count += 1
        f = cc
        cc = (aa + bb) / 2.0
        denom = bb + aa
        if denom == 0 or not np.isfinite(denom):
            raise ValueError("Unstable iteration: denominator (bb + aa) is zero or NaN.")
        g = ee / denom

        product = bb * aa
        if product < 0 or not np.isfinite(product):
            raise ValueError(
                f"Numerical instability at iteration {iter_count}: "
                f"bb * aa = {product} (bb={bb}, aa={aa})"
            )

        bb = np.sqrt(product)
        ee = g * ee
        aa = cc

        if debug:
            print(f"Iteration {iter_count}:")
            print(f"  aa = {aa}")
            print(f"  bb = {bb}")
            print(f"  cc = {cc}")
            print(f"  ee = {ee}")
            print(f"  g = {g}")
            print(f"  product = {product}")
            print()

        if abs(f - cc) <= errtol * abs(f):
            break

    result = (np.pi / 2.0) * (aa * dd + bb * ee) / (aa * (aa + pp))
    if not np.isfinite(result):
        raise ValueError(f"Final result is not finite: {result}")
    return result