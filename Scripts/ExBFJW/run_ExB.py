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
    raise ModuleNotFoundError(f"Cannot import 'compute_E_field' from washersPhi.py. "
                              f"Check that {SCRIPT_DIR}/washersPhi.py exists.")

try:
    from flatcoilsVecPot import compute_B_field
except ModuleNotFoundError:
    raise ModuleNotFoundError(f"Cannot import 'compute_B_field' from flatcoilsVecPot.py. "
                              f"Check that {SCRIPT_DIR}/flatcoilsVecPot.py exists.")

# ============================================================
# Compute fields
# ============================================================
print("Computing electric field...")
X, Z, Ex, Ez = compute_E_field()   # y=0 plane

print("Computing magnetic field...")
_, _, Bx, Bz = compute_B_field()   # y=0 plane

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
# Create side-by-side figure
# ============================================================
fig, (ax1, ax2) = plt.subplots(
    1, 2, figsize=(13,5),
    gridspec_kw={'width_ratios':[1.25, 1]}
)

# -----------------------------
# LEFT PANEL — Streamlines (XZ plane)
# -----------------------------
strm = ax1.streamplot(
    X, Z, ExB_y*0+1, ExB_y,   # pseudo vector: all along y (vertical in 2D)
    color=logExB,
    cmap='plasma',
    norm=norm,
    density=1.4,
    linewidth=1
)

cbar = fig.colorbar(strm.lines, ax=ax1)
cbar.set_label(r'$\log|\vec{E}\times\vec{B}|$')

ax1.set_title("E×B Streamlines (XZ Plane, y=0)")
ax1.set_xlabel("x (m)")
ax1.set_ylabel("z (m)")
ax1.set_aspect('equal')
ax1.grid(True)

# -----------------------------
# RIGHT PANEL — Centerline |E×B|(0,0,z)
# -----------------------------
ax2.plot(z_line, ExB_line, color='navy', lw=2)
ax2.set_title("On-Axis E×B Magnitude")
ax2.set_xlabel("z (m)")
ax2.set_ylabel(r'$|\vec{E}\times\vec{B}|$')
ax2.grid(True)

# Optional log-scale twin axis
ax2b = ax2.twinx()
ax2b.plot(z_line, np.log(np.maximum(ExB_line,1e-30)),
          color='darkred', ls='--', lw=1.5)
ax2b.set_ylabel(r'$\log|\vec{E}\times\vec{B}|$', color='darkred')
ax2b.tick_params(axis='y', colors='darkred')

plt.tight_layout()
plt.show()
