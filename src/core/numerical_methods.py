import numpy as np
from scipy.integrate import solve_ivp


def get_pursuit_state(t, D_0, v1, v_p, alpha):
    def system(t, state):
        rho, phi = state

        if rho <= 0:
            return [0, 0]

        rho_dot = (v1 ** 2 * t + D_0 * v1 * np.cos(alpha - phi)) / rho

        under_sqrt = v_p ** 2 - rho_dot ** 2
        if under_sqrt < 0:
            under_sqrt = 0
        phi_dot = (1 / rho) * np.sqrt(under_sqrt)

        return [rho_dot, phi_dot]

    state0 = [D_0, 0.0]
    solution = solve_ivp(system, [0, t], state0, method='RK45', dense_output=True)

    rho_t, phi_t = solution.y[:, -1]

    return rho_t, phi_t