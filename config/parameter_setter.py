import argparse

import config.folder_and_file_names as fname
import numpy as np

from tools.utils import printc


class ParSetter:

    def __init__(self):
        pass

    def set_up_args(self, dataset_file_name=None, epsilon=False, epsilon_partition=False, level1_parameter=False,
                    level2_parameter=False, out_size: int = -1, output_file_name=None):
        parser = argparse.ArgumentParser()
        parser.add_argument('--dataset_file_name', type=str, default=fname.dataset_file_name, help="Input File")
        parser.add_argument('-o', '--output' , type=str, default=None, help="Output File. Default is input file name + '_output.dat'")
        parser.add_argument('--subdividing_inner_parameter', type=float, default=200)
        parser.add_argument('--total_epsilon', type=float, default=2.0)
        # regularly, partition solution is suggested to be np.array([0.2, 0.52, 0.28]))
        parser.add_argument('--epsilon_partition', type=np.ndarray, default=np.array([0.2, 0.4, 0.4]))
        # this parameter indicates how many trajectories to generate
        parser.add_argument('--trajectory_number_to_generate', type=int, default=-1)
        args = vars(parser.parse_args())
        if epsilon is not False:
            args['total_epsilon'] = epsilon
        if epsilon_partition is not False:
            args['epsilon_partition'] = epsilon_partition
        if level1_parameter is not False:
            args['level1_divide_inner_parameter'] = level1_parameter
        if level2_parameter is not False:
            args['subdividing_inner_parameter'] = level2_parameter
        if dataset_file_name is not None:
            args['dataset_file_name'] = dataset_file_name
        if args['output'] is None:
            # Write to input file
            args['output'] = fname.OUTPUT_DIR + args['dataset_file_name'].split('/')[-1].split('.')[0] + '_output.dat'
        if out_size != -1:
            args['trajectory_number_to_generate'] = out_size
        if output_file_name is not None:
            args['output'] = output_file_name

        # Print Parameters
        printc("Input file name:", args['dataset_file_name'])
        printc("Output file name:", args['output'])
        printc("Total epsilon:", args['total_epsilon'])
        printc("Epsilon partition:", args['epsilon_partition'])
        printc("Trajectory number to generate:", args['trajectory_number_to_generate'])
        printc("Subdividing inner parameter:", args['subdividing_inner_parameter'])
        # printc("Level 1 divide inner parameter:", args['level1_divide_inner_parameter'])

        return args




