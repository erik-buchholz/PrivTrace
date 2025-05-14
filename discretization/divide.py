import logging

import numpy as np

from config.parameter_carrier import ParameterCarrier

log = logging.getLogger()


class Divide:

    def __init__(self, cc: ParameterCarrier):
        self.cc = cc

    # divide parameter, output is array[x_divide_number, y_divide_number, x_increase, y_increase]
    def level1_divide_parameter(self, total_density, trajectory_number, border2):
        divide_threshold = 60
        initial_parameter = 600
        # This seems initial_parameter to be $c$ in the paper
        # Initial value in Code: c=600
        # In the papers: Brinkhoff: c=5000, Porto: c=1200, GeoLife: c=500
        top = border2[0]
        bot = border2[1]
        lef = border2[2]
        rig = border2[3]
        para = np.floor(np.sqrt(total_density / initial_parameter))
        # This para appears to be $K$ in the paper
        assert para > 1, 'need no dividing'
        if para > divide_threshold:
            para = divide_threshold
        x_divide_number = para
        y_divide_number = para
        x_divide_number = int(x_divide_number)
        y_divide_number = int(y_divide_number)
        x_increase = 1 / x_divide_number * (rig - lef)
        y_increase = 1 / y_divide_number * (top - bot)
        divide_parameter1 = np.array([x_divide_number, y_divide_number, x_increase, y_increase])
        log.debug(f"L1 Divide parameter: {divide_parameter1}")
        return divide_parameter1

    def subdividing_parameter(self, noisy_density):
        initial_parameter = 200
        subdivide_parameter1 = int(np.ceil(np.sqrt(noisy_density / initial_parameter)))
        log.debug(f"Subdivide parameter: {subdivide_parameter1}")
        return subdivide_parameter1




