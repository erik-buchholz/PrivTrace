"""Evaluation Code."""

import datetime
import multiprocessing
from pathlib import Path
from timeit import default_timer as timer

import pandas as pd

import config.folder_and_file_names as fname
# from tools.object_store import ObjectStore
from config.parameter_carrier import ParameterCarrier
from config.parameter_setter import ParSetter
from data_preparation.data_preparer import DataPreparer
from discretization.get_discretization import DisData
from generator.state_trajectory_generation import StateGeneration
from generator.to_real_translator import RealLocationTranslator
from primarkov.build_markov_model import ModelBuilder
from tools.data_writer import DataWriter
from tools.utils import printc

# CONSTANTS
DATASETS = ["PORTO", "GEOLIFE"]
N_FOLDS = 5
N_TRAJS = 3000
EPSILON = 10.0
epsilons = [10.0]


def run(dataset: str, fold: int, epsilon: float = EPSILON):
    # Copy of main.py

    input_filename = f"{dataset}_{fold}.dat"
    output_filename = f"{dataset}_e{epsilon:.1f}_{fold:02d}_output.dat"

    # Start Timer
    start = timer()

    writer = DataWriter()
    print('begin all')
    print(datetime.datetime.now())
    par = ParSetter().set_up_args(dataset_file_name=input_filename, output_file_name=output_filename,
                                  epsilon=epsilon, out_size=N_TRAJS)
    pc = ParameterCarrier(par)
    data_preparer = DataPreparer(par)
    trajectory_set = data_preparer.get_trajectory_set()
    disdata1 = DisData(pc)
    grid = disdata1.get_discrete_data(trajectory_set)
    mb1 = ModelBuilder(pc)
    mo1 = mb1.build_model(grid, trajectory_set)
    mb1 = ModelBuilder(pc)
    mo1 = mb1.filter_model(trajectory_set, grid, mo1)
    sg1 = StateGeneration(pc)
    st_tra_list = sg1.generate_tra(mo1)
    rlt1 = RealLocationTranslator(pc)
    real_tra_list = rlt1.translate_trajectories(grid, st_tra_list)
    writer.save_trajectory_data_in_list_to_file(real_tra_list, par['output'])
    print('end all')
    print(datetime.datetime.now())

    # Get end time
    end = timer()
    runtime = end - start
    printc("Total Runtime:", f"{runtime // 60 // 60}h {runtime // 60 % 60}m {runtime % 60}s")
    # Write to file
    filepath = Path(fname.OUTPUT_DIR) / f"PrivTrace_{dataset}_e{epsilon:.1f}_runtime.txt"
    df = pd.DataFrame(data={'run_id': [fold], 'runtime': [runtime]})
    if filepath.exists():
        df.to_csv(filepath, mode='a', header=False, index=False)
    else:
        df.to_csv(filepath, mode='w', header=True, index=False)



if __name__ == "__main__":
    processes = []

    for dataset in DATASETS:
        for fold in range(1, N_FOLDS+1):
            for epsilon in epsilons:
                p = multiprocessing.Process(
                    target=run,
                    kwargs={
                        "dataset": dataset,
                        "fold": fold,
                        "epsilon": epsilon,
                    },
                )
                processes.append(p)
                print(f"Starting process for {dataset} fold {fold} with epsilon {epsilon}.")
                p.start()

    for p in processes:
        p.join()
