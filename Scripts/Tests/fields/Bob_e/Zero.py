if __name__ == "__main__":
    import numpy as np
    from Alg.polarSpace import *
    def at(coord, q=1, radius=1, resolution=100, convert=True):
        """
        implementation of the function.
        Inputs:
        q: total charge of the ring in Coulombs
        """
        # print(f"q is: {q}")
        # print(f"coord is: {coord}")
        # print(f'FieldMethods_Impl.bob_e_impl.at: bob_e called with charge {q} and radius {radius}')
        # Parameters
        k = 8.99e9  # Coulomb's constant, N * m^2/C^2
        kq_a2 = (k * q) / (radius ** 2)

        # Coordinate Constants
        if convert:
            coord = toCyl(coord)
        zeta = coord[2] / radius
        rho = coord[0] / radius
        if abs(rho) < 1e-10:
            rho = 1e-10

        # Integral Constants - pg.3 of document
        mag = (rho ** 2 + zeta ** 2 + 1)
        mag_3_2 = mag ** (3 / 2)
        ## Fzeta
        Fzeta_c = (zeta) / (mag_3_2 * (radius ** 2))
        ## Frho
        Frho_c = (rho) / (mag_3_2 * (radius ** 2))

        # Integration
        # Circle is broken into {resolution} slices; with each result being appended to the lists below.

        thetas = np.linspace(0, np.pi, resolution,
                             dtype=np.float64)  # np.array of all the theta values used in the integration (of shape {resolution})
        cosines = np.cos(thetas)  # np.array of all the cosine values of the thetas
        denominators = (1 - ((2 * rho * cosines) / mag)) ** (3 / 2)  # shared denominator values of fzeta and frho

        # replace zeros with a really small decimal.
        denominators[denominators == 0] = 1e-20

        fzeta = 1 / denominators
        frho = (1 - cosines / rho) / denominators

        # Final - fzeta, frho is summed, multiplied by the integration constant and kq.a^2.
        zeta = np.asarray(fzeta).sum() * Fzeta_c * kq_a2
        rho = np.asarray(frho).sum() * Frho_c * kq_a2
        return zeta, rho

    z0, r0 = at(coord=[2,2,2], q=1e-4, radius=1)

    print(z0, r0)
    print(type(z0), type(r0))