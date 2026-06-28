"""    Calculates the total plasma beta (ratio of kinetic pressure to magnetic pressure), based on:
    p_total = p_electrons + p_ions and p_mag = (B ** 2) / (2 * mu_0)
    Parameters:
    -----------
    B : float
        Magnetic field strength in Tesla (T).
    n_e : float
        Electron density in m^-3.
    T_e : float
        Electron temperature.
    n_i : float, list, or numpy array
        Ion density in m^-3. Can be a single value or a list/array for multiple species.
    T_i : float, list, or numpy array
        Ion temperature. Can be a single value or a list/array matching n_i.
    T_in_ev : bool, optional
        If True (default), temperatures are treated as being in eV.
        If False, temperatures are treated as being in Kelvin (K).

    Returns:
    --------
    beta : float
        The dimensionless total plasma beta parameter.
    FJW 6.28.26
"""
import numpy as np

def calculate_plasma_beta(B, n_e, T_e, n_i, T_i, T_in_ev=True):
    # Physical Constants (SI Units)
    mu_0 = 4 * np.pi * 1e-7  # Vacuum permeability [H/m]
    k_B = 1.380649e-23  # Boltzmann constant [J/K]
    e_charge = 1.602176634e-19  # Elementary charge [C] (Conversion factor for eV to Joules)

    # 1. Convert inputs to numpy arrays for clean handling of multi-species arrays
    n_i = np.atleast_1d(n_i)
    T_i = np.atleast_1d(T_i)

    if len(n_i) != len(T_i):
        raise ValueError("The number of ion density elements must match the number of ion temperature elements.")

    # 2. Determine energy conversion factor based on units
    energy_factor = e_charge if T_in_ev else k_B

    # 3. Calculate Kinetic Pressure (p = sum(n * k_B * T))
    p_electrons = n_e * T_e * energy_factor
    p_ions = np.sum(n_i * T_i * energy_factor)
    p_total = p_electrons + p_ions

    # 4. Calculate Magnetic Pressure (p_mag = B^2 / (2 * mu_0))
    p_mag = (B ** 2) / (2 * mu_0)

    # 5. Total Beta
    beta = p_total / p_mag

    return beta

# --- Example Usage ---
if __name__ == "__main__":
    # Example Parameters (e.g., core plasma conditions)
    B_field = 3.0  # 3 Tesla
    density_e = 1.0e20  # Electron density: 10^20 m^-3
    temp_e = 10000.0  # Electron temperature: 10 keV (10,000 eV)

    # Handling a two-component ion plasma (e.g., 50/50 mix or a fuel/impurity mix)
    densities_i = [0.5e20, 0.5e20]  # Array of ion densities
    temps_i = [10000.0, 10000.0]  # Array of ion temperatures (10 keV)

    total_beta = calculate_plasma_beta(
        B=B_field,
        n_e=density_e,
        T_e=temp_e,
        n_i=densities_i,
        T_i=temps_i,
        T_in_ev=True
    )

    print(f"Total Plasma Beta (β): {total_beta:.5f}")
    print(f"Beta Percentage: {total_beta * 100:.2f}%")