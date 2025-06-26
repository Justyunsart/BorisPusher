import sympy as sp

# Define numeric values
A_val = 3.0
rho_val = 1.0

# Define symbolic variables
theta = sp.Symbol('theta', real=True)
A = sp.Symbol('A', real=True)
rho = sp.Symbol('rho', real=True)

# Define the integrand
integrand = sp.cos(theta) / (A - 2*rho*sp.cos(theta))**(3/2)

# Substitute values
integrand_numeric = integrand.subs({A: A_val, rho: rho_val})

# Compute the integral numerically
numeric_result = sp.N(sp.integrate(integrand_numeric, (theta, 0, sp.pi)))
print(numeric_result)
