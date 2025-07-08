import numpy as np
import matplotlib.pyplot as plt

rho_vals = np.linspace(0.01, 1.5, 200)
z_vals = np.linspace(0.01, 1, 200)
z_lo_vals = np.array([5 * np.min(z_vals), 10 * np.min(z_vals), 50 * np.min(z_vals)])

RHO, Z = np.meshgrid(rho_vals, z_vals)
E_rho = np.zeros_like(RHO)
E_z = np.zeros_like(Z)

for z_lineout in z_lo_vals:
    print(f"Target: {z_lineout}")
    lineout_val = np.argmin(np.abs(z_vals - z_lineout))
    closest_value = z_vals[lineout_val]
    print(f"  Closest value: {closest_value}")
    index = lineout_val  # same as sub_arr is from the beginning
    print(f"  Index in original array: {index}")

fig = plt.figure(figsize=(15, 5))