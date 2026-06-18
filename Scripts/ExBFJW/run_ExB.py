"""
run_ExB.py

This script did not work as expected which was to call the E and B fields as functions from standalone scripts.

Compute E×B from the six-washer electrostatic solver and six-coil magnetic solver,
and display side-by-side plots:
1) Streamlines of E×B in the XZ plane (y=0)
2) Centerline magnitude |E×B|(0,0,z)
"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize

# ============================================================
# Add Scripts/EfieldFJW to Python path
# ============================================================
SCRIPT_DIR = os.path.join(os.getcwd(), "..", "EfieldFJW")
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

# ============================================================
# Import compute functions from the scripts in that folder
# ============================================================
try:
    from washersPhi import compute_E_field
except ModuleNotFoundError:
    raise ModuleNotFoundError(f"Cannot import 'compute_E_field' from flatEwashersPhi.py. "
                              f"Check that {SCRIPT_DIR}/flatEwashersPhi.py exists.")

try:
    from flatBcoilsVecPot import compute_B_field
except ModuleNotFoundError:
    raise ModuleNotFoundError(f"Cannot import 'compute_B_field' from flatBcoilsVecPot.py. "
                              f"Check that {SCRIPT_DIR}/flatBcoilsVecPot.py exists.")

# ============================================================
# Compute fields
# ============================================================
print("Computing electric field...")
# washersPhi returns 7 items: X, Z, x, z, Ex, Ez, phi
X, Z, _, _, Ex, _, Ez = compute_E_field()

print("Computing magnetic field...")
a, b = 0.25, 0.75

# flatBcoilsVecPot returns 13 items:
# X, Z, x, z, Bx, By, Bz, Bmag, z_line, Bline, t, Bdiag_x, Bdiag_z
_, _, _, _, Bx, _, Bz, _, _, _, _, _, _ = compute_B_field(a, b)

# ============================================================
# Compute E×B in XZ-plane slice (y=0)
# ============================================================
# In the XZ plane, Ey and By are approximately zero in your scripts
# So cross product in 2D (Ex*Bz - Ez*Bx) along y-direction

ExB_y = Ex*Bz - Ez*Bx
ExB_mag = np.abs(ExB_y)   # magnitude for plotting

# ============================================================
# Prepare log-scale for streamlines
# ============================================================
floor = np.exp(-10)
ExB_plot = np.maximum(ExB_mag, floor)
logExB = np.log(ExB_plot)
norm = Normalize(vmin=-10, vmax=np.max(logExB))

# ============================================================
# Extract centerline |E×B|(0,0,z)
# ============================================================
x_vals = X[0,:]
ix0 = np.argmin(np.abs(x_vals - 0.0))
z_line = Z[:,0]
ExB_line = ExB_mag[:, ix0]

# ============================================================
# Create side-by-side figure for E and B Fields
# ============================================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# Calculate magnitudes for log-color scaling
Emag = np.sqrt(Ex**2 + Ez**2)
Bmag = np.sqrt(Bx**2 + Bz**2)

logE = np.log(np.maximum(Emag, np.exp(-10)))
logB = np.log(np.maximum(Bmag, np.exp(-10)))

# -----------------------------
# LEFT PANEL — Electric Field Lines (XZ plane)
# -----------------------------
strm1 = ax1.streamplot(
    X, Z, Ex, Ez,
    color=logE,
    cmap='plasma',
    density=1.4,
    linewidth=1
)
fig.colorbar(strm1.lines, ax=ax1, label=r'$\log|\vec{E}|$')
ax1.set_title("Electric Field lines (XZ Plane, y=0)")
ax1.set_xlabel("x (m)")
ax1.set_ylabel("z (m)")
ax1.set_aspect('equal')
ax1.grid(True)

# -----------------------------
# RIGHT PANEL — Magnetic Field Lines (XZ plane)
# -----------------------------
strm2 = ax2.streamplot(
    X, Z, Bx, Bz,
    color=logB,
    cmap='viridis',  # Different colormap to distinguish fields
    density=1.4,
    linewidth=1
)
fig.colorbar(strm2.lines, ax=ax2, label=r'$\log|\vec{B}|$')
ax2.set_title("Magnetic Field Lines (XZ Plane, y=0)")
ax2.set_xlabel("x (m)")
ax2.set_ylabel("z (m)")
ax2.set_aspect('equal')
ax2.grid(True)

plt.tight_layout()
plt.show()