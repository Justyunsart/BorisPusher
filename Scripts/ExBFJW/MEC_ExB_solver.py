#!/usr/bin/env python3
"""
Self-contained MEC ExB solver
Computes symmetric E, B, and ExB fields and plots maps + lineouts.

No external project modules required.
"""

import numpy as np
import matplotlib.pyplot as plt

# -----------------------------
# Physical / geometry settings
# -----------------------------
mu0 = 4*np.pi*1e-7

coil_radius = 0.25
coil_current = 8e4

# Symmetric 4-coil MEC layout (x–z plane, y=0 slice)
coil_centers = np.array([
    [+0.35, 0.0],
    [-0.35, 0.0],
    [0.0, +0.35],
    [0.0, -0.35],
])

# -----------------------------
# Computational grid
# -----------------------------
N = 140
x = np.linspace(-0.6, 0.6, N)
z = np.linspace(-0.6, 0.6, N)
dx = x[1]-x[0]

X, Z = np.meshgrid(x, z, indexing="ij")

# ============================================================
# ELECTROSTATICS (analytic symmetric potential)
# ============================================================
print("Building electrostatic potential...")

# Quadrupole-like MEC confinement potential
phi = 8e3 * (X**2 - Z**2) * np.exp(-(X**2 + Z**2)/0.18)

# Electric field
Ex = -np.gradient(phi, dx, axis=0)
Ez = -np.gradient(phi, dx, axis=1)

Emag = np.sqrt(Ex**2 + Ez**2)

# ============================================================
# MAGNETOSTATICS (Biot–Savart loop integration)
# ============================================================
print("Computing magnetic field from coils...")

Bx = np.zeros_like(X)
Bz = np.zeros_like(X)

# discretize loop
nseg = 180
theta = np.linspace(0, 2*np.pi, nseg)

dl = 2*np.pi*coil_radius / nseg

for cx, cz in coil_centers:
    for th in theta:
        # current element position
        xs = cx + coil_radius*np.cos(th)
        zs = cz + coil_radius*np.sin(th)

        # tangent vector (current direction)
        dlx = -np.sin(th) * dl
        dlz =  np.cos(th) * dl

        Rx = X - xs
        Rz = Z - zs
        R2 = Rx**2 + Rz**2 + 1e-10
        R32 = R2**1.5

        # Biot–Savart (y-directed current)
        Bx += mu0*coil_current/(4*np.pi) * ( dlz / R32 )
        Bz += mu0*coil_current/(4*np.pi) * (-dlx / R32)

Bmag = np.sqrt(Bx**2 + Bz**2)

# ============================================================
# ExB DRIFT FIELD
# ============================================================
print("Computing ExB drift...")

# Only y-component exists in this slice
Vy = (Ex*Bz - Ez*Bx) / (Bmag**2 + 1e-12)

Vmag = np.abs(Vy)

# ============================================================
# PLOTTING
# ============================================================
print("Rendering plots...")

fig, ax = plt.subplots(4, 2, figsize=(10, 14))

ix0 = N//2   # center lineout

# --- Potential
im0 = ax[0,0].pcolormesh(X, Z, phi, shading='auto')
ax[0,0].set_title("Electrostatic Potential φ")
ax[0,0].set_aspect('equal')
fig.colorbar(im0, ax=ax[0,0])

ax[0,1].plot(z, phi[ix0,:], lw=2)
ax[0,1].set_title("φ lineout (x=0)")
ax[0,1].grid()

# --- Electric field magnitude
im1 = ax[1,0].pcolormesh(X, Z, Emag, shading='auto')
ax[1,0].set_title("|E|")
ax[1,0].set_aspect('equal')
fig.colorbar(im1, ax=ax[1,0])

ax[1,1].plot(z, Emag[ix0,:], lw=2)
ax[1,1].set_title("|E| lineout")
ax[1,1].grid()

# --- Magnetic field magnitude
im2 = ax[2,0].pcolormesh(X, Z, Bmag, shading='auto')
ax[2,0].set_title("|B|")
ax[2,0].set_aspect('equal')
fig.colorbar(im2, ax=ax[2,0])

ax[2,1].plot(z, Bmag[ix0,:], lw=2)
ax[2,1].set_title("|B| lineout")
ax[2,1].grid()

# --- ExB streamlines
im3 = ax[3,0].pcolormesh(X, Z, Vmag, shading='auto')
ax[3,0].streamplot(x, z, Ex*0 + Vy, Ez*0,
                   density=2.0, color='k', linewidth=0.6)
ax[3,0].set_title("|ExB| transport")
ax[3,0].set_aspect('equal')
fig.colorbar(im3, ax=ax[3,0])

ax[3,1].plot(z, Vmag[ix0,:], lw=2)
ax[3,1].set_title("|ExB| lineout")
ax[3,1].grid()

plt.tight_layout()
plt.show()

print("Done.")

# ============================================================
# plt.tight_layout()
# plt.show()
#
#
# # Draw washers
# c = 1.0
# ax1.plot([0.25, 0.75], [c, c], 'green', lw=6)
# ax1.plot([0.25, 0.75], [-c, -c], 'green', lw=6)
# ax1.plot([-0.25, -0.75], [c, c], 'green', lw=6)
# ax1.plot([-0.25, -0.75], [-c, -c], 'green', lw=6)
# ax1.plot([c, c], [0.25, 0.75], 'green', lw=6)
# ax1.plot([c, c], [-0.25, -0.75], 'green', lw=6)
# ax1.plot([-c, -c], [0.25, 0.75], 'green', lw=6)
# ax1.plot([-c, -c], [-0.25, -0.75], 'green', lw=6)


plt.tight_layout()
plt.show()
