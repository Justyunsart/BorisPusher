
"""

"""
import mpmath
import numpy as np
import matplotlib.pyplot as plt
import scipy
from Alg.polarSpace import *
from magpylib.current import Circle

def mpmath_denominator(rho, theta, zeta):
    # convert rho and theta to high precision floats
    _r = mpmath.mpf(rho)
    _th = mpmath.mpf(theta)
    _m = mpmath.mpf((rho ** 2 + zeta ** 2 + 1))

    # compute then return the value
    return (1 - ((2 * _r * mpmath.cos(_th)) / _m)) ** (3 / 2)

def mpmath_frho(rho, theta, zeta):
    denominator = mpmath_denominator(rho, theta, zeta)
    return (1 - mpmath.cos(mpmath.mpf(theta)) / mpmath.mpf(rho)) / mpmath.mpf(denominator)

def estimate_denominator(rho, theta, zeta):
    return (1 - ((2 * rho * np.cos(theta)) / (rho ** 2 + zeta ** 2 + 1))) ** (3 / 2)

def estimate_frho(rho, theta, zeta):
    denominator = estimate_denominator(rho, theta, zeta)
    return (1 - np.cos(theta) / rho) / denominator

circle = Circle(position=(0,0,0), current=1000)
circle.rotate_from_angax(90, 'x')
inv = circle.orientation.inv()
# Generate values
rng = 100
lim = 3
x = np.linspace(-lim, lim, rng)
y = np.linspace(-lim, lim, rng)
thetas = np.linspace(0, np.pi, rng)

# Create 2D grids
_x, _y = np.meshgrid(x, y, indexing='ij')

rel_errors = np.zeros((rng, rng))  # Pre-allocate for speed
rel_errors_unrotated = np.zeros((rng, rng))  # Pre-allocate for speed

# Compute errors
for i in range(rng):
    for j in range(rng):
        x = _x[i, j]
        y = _y[i, j]
        z = 0.1
        _coord = np.array((x, y, z))

        # simulate inverse rotation with circle
        coord = inv.apply(_coord)
        # convert to cyl
        coord = toCyl(coord)

        zeta, theta, rho = coord
        # estimate the rotated ver.
        est = estimate_frho(rho, theta, zeta)
        real = mpmath_frho(rho, theta, rho)
        rel_error = abs(real - est) / abs(real)
        rel_errors[i, j] = rel_error

        # estimate the unrotated ver.
        _coord = toCyl(_coord)
        zeta, theta, rho = _coord
        est = estimate_frho(rho, theta, zeta)
        real = mpmath_frho(rho, theta, rho)
        rel_error = abs(real - est) / abs(real)
        rel_errors_unrotated[i, j] = rel_error

_rhos = np.linspace(-lim, lim, 1000)
_zs = sorted([0.001, 0.1, 1, 10, 100])
rel_errors_cyl = np.zeros((len(_zs), 1000))  # Pre-allocate for speed

# Compute errors
for i in range(1000):
    for z in range(len(_zs)):
        rho = _rhos[i]
        #theta = _th[i, j]
        zeta = _zs[z]

        est = estimate_frho(rho, 0, zeta)
        #real = mpmath_denominator(rho, theta, rho)
        #rel_error = abs(real - est) / abs(real)

        rel_errors_cyl[z, i] = est

# Plotting
fig = plt.figure(figsize=(15, 5))
ax1 = fig.add_subplot(131)
ax2 = fig.add_subplot(132)
ax3 = fig.add_subplot(133)
axes = [ax1, ax2, ax3]
for ax in axes:
    ax.set_box_aspect(1)
    ax.grid(True, which="both", ls="--")
#plt.loglog(x_vals, abs_error, label='Absolute Error')
contour = ax1.contourf(_x, _y, rel_errors)
contour_unrotated = ax2.contourf(_x, _y, rel_errors_unrotated)
for i in range(len(_zs)):
    val = _zs[i]
    contour_cyl = ax3.plot(_rhos , rel_errors_cyl[i], label=str(val))
fig.colorbar(contour, ax=ax1)
fig.colorbar(contour_unrotated, ax=ax2)

fig.suptitle("Bob_E Frho Relative Errors")

ax1.set_title("Cartesian w/ rotation")
ax1.set_xlabel('x')
ax1.set_ylabel('y')

ax2.set_title("Cartesian w/o rotation")
ax2.set_xlabel('x')
ax2.set_ylabel('y')

ax3.set_title("Generated Cyl")
ax3.set_xlabel('rho')
ax3.set_ylabel('V/m')
ax3.legend()
plt.show()