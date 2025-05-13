"""Evaluation Code."""
import datetime
import logging
import multiprocessing
from pathlib import Path
from timeit import default_timer as timer

import pandas as pd

import config.folder_and_file_names as fname
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
DEBUG = True
DATASETS = ["PORTO", "GEOLIFE"]
N_FOLDS = 5
N_TRAJS = 3000  # Number of trajectories to generate for our evaluation
EPSILON = 10.0
epsilons = [10.0]

# Set up log
logging.basicConfig(
    format="%(asctime)s - [%(levelname)s]: %(message)s",
    level=logging.DEBUG if DEBUG else logging.INFO,
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)


def run(dataset: str, fold: int, epsilon: float = EPSILON) -> None:
    # Copy of main.py

    input_filename = f"{dataset}_{fold}.dat"
    output_filename = f"{dataset}_e{epsilon:.1f}_{fold:02d}_output.dat"

    # Start Timer
    start = timer()

    writer = DataWriter()
    print('begin all')
    print(datetime.datetime.now())
    par = ParSetter().set_up_args(
        dataset_file_name=input_filename,  # Input File
        output_file_name=output_filename,  # Output File
        epsilon=epsilon,  # Final Epsilon (e1 + e2 + e3)
        out_size=N_TRAJS  # Number of trajectories to generate for our evaluation
    )

    pc = ParameterCarrier(par)

    # Load Data
    data_preparer = DataPreparer(par)
    trajectory_set = data_preparer.get_trajectory_set()
    log.info("Preparing data finished")

    # Step 1: Discretisation
    disdata1 = DisData(pc)
    grid = disdata1.get_discrete_data(trajectory_set)
    log.info("Discretization finished")

    # Step 2: Learn Markov Models
    mb1 = ModelBuilder(pc)
    mo1 = mb1.build_model(grid, trajectory_set)
    log.info("Markov model building finished")
    mb1 = ModelBuilder(pc)
    mo1 = mb1.filter_model(trajectory_set, grid, mo1)
    log.info("Markov model filtering finished")

    # Step 3: Generate Trajectories
    sg1 = StateGeneration(pc)
    st_tra_list = sg1.generate_tra(mo1)
    log.info("State trajectory generation finished")
    rlt1 = RealLocationTranslator(pc)
    real_tra_list = rlt1.translate_trajectories(grid, st_tra_list)
    log.info("Real trajectory generation finished")
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
    if DEBUG:
        # Set logging to debug level
        log.setLevel(logging.DEBUG)
        # Only run geolife dataset with fold 1 and epsilon 10.0
        run(dataset="GEOLIFE", fold=1, epsilon=10.0)
    else:
        processes = []
        for dataset in DATASETS:
            for fold in range(1, N_FOLDS + 1):
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
