from matplotlib import pyplot as plt
import glob
from run import InputData
import openmc
import pandas as pd
import timeit
import seaborn as sns
import os


import multiprocessing
try:
  CPU_COUNT = multiprocessing.cpu_count()
except NotImplementedError:
  CPU_COUNT = 1   # arbitrary default

def get_results(experiment_path: str):
  inp = InputData.from_yaml_file(f"{experiment_path}/input_data.yaml")

  sp_path = f"{inp.cwd_path}/statepoint.{inp.active_batches+inp.inactive_batches}.h5"
  if not os.path.isfile(sp_path): 
    print(f"WARN: No statepoint file found at '{sp_path}'")
    return

  sp = openmc.StatePoint(filepath=sp_path)
  keff = sp.keff.nominal_value
  
  return inp.n_ba_pins, inp.ba_pct, inp.lattice_size, keff


def main():
  experiment_paths = glob.glob("experiments/*")

  if CPU_COUNT == 1:
    results = [get_results(experiment_path) for experiment_path in experiment_paths]
  else:
    pool = multiprocessing.Pool(processes=CPU_COUNT)
    parallelized = pool.map(get_results, experiment_paths)
    results = [x for x in parallelized if x]

  df = pd.DataFrame(results, columns=["n_ba_pins", "ba_pct", "lattice_size", "keff"])

  # Apply the default theme
  sns.set_style("whitegrid")
  fig = sns.relplot(
    data=df,
    x="ba_pct", y="keff", col="lattice_size",
    hue="n_ba_pins", style="n_ba_pins",
  )

  fig.savefig(f"result.png")
  print(f"Saved figure from {len(df)} experiments")

if __name__ == "__main__":
  run_time = timeit.timeit(main, number=1)
  print(f"Run time with {CPU_COUNT} CPUs: {run_time:.1f} s")