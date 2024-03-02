import os
import numpy as np
import matplotlib.pyplot as plt
import argparse
from dataclasses import dataclass, field
from dataclass_wizard import YAMLWizard
from typing import ClassVar
import openmc
import openmc.stats
import openmc.model
import openmc.deplete
import starbun.materials.fuels
import starbun.materials.claddings
import starbun.materials.moderators
import starbun.geometries.fuel_assemblies
import starbun.utils.tracker

import ba_pin_positions
from starbun.utils.input_data import ExperimentInputData

@dataclass
class InputData(ExperimentInputData, YAMLWizard, key_transform='SNAKE'):

  enrichment_pct: float = 5.0
  lattice_pitch: float = 1.26
  fuel_or: float = 0.45
  clad_ir: float = 0.47
  clad_or: float = 0.55
  lattice_size: int = 10
  dt: ClassVar[list[int]] = [2 * 24 * 60 * 60] * 20 + [100 * 24 * 60 * 60] * 20
  power: float = 4e6 / 400
  n_ba_pins: int = 12
  ba_pct: float = 5.0
  particles: int = 1000
  active_batches: int = 100
  inactive_batches: int = 40
  chain_file: str = os.environ['OPENMC_DEPLETION_CHAIN']
  cross_sections: str = os.environ['OPENMC_CROSS_SECTIONS']

  def __init__(self, experiment=None, *args, **kwargs):
    self.experiment = experiment
    ExperimentInputData.__init__(self)

def plot_geometry(inp: InputData, universe: openmc.Universe, colors: dict):  
  # Increase font size for better visibility with large pixel counts
  original_font_size = plt.rcParams['font.size']
  plt.rcParams.update({'font.size': 50})

  universe.plot(colors=colors, color_by='material', pixels=(2000,2000), legend=True)
  plt.tight_layout()
  plt.savefig(f'{inp.img_path}/{inp.lattice_size}x{inp.lattice_size}_fuel-map_{inp.n_ba_pins}-pins.png')
  plt.close()

  # Restore font size
  plt.rcParams.update({'font.size': original_font_size})

def get_geometry(inp: InputData):
  uo2_no_ba = starbun.materials.fuels.uo2(enrichment_pct=inp.enrichment_pct)
  uo2_ba = starbun.materials.fuels.uo2(enrichment_pct=inp.enrichment_pct, gd2o3_pct=inp.ba_pct)
  zircaloy2 = starbun.materials.claddings.zircaloy2()
  water = starbun.materials.moderators.water()

  # Set volumes of fuel as it is needed for depletion calculations
  # TODO: Should this be multiplied by number of pins for each material?
  uo2_no_ba.volume = np.pi * inp.fuel_or**2 * (inp.lattice_size**2 - inp.n_ba_pins)
  uo2_ba.volume = np.pi * inp.fuel_or**2 * inp.n_ba_pins

  ba_positions = ba_pin_positions.get(inp.n_ba_pins, inp.lattice_size)
  fuel_materials = [uo2_ba if (i, j) in ba_positions else uo2_no_ba for i in range(inp.lattice_size) for j in range(inp.lattice_size)]

  universe = starbun.geometries.fuel_assemblies.rectangular_lattice(inp.lattice_size, inp.lattice_pitch, inp.fuel_or, fuel_materials, inp.clad_ir, inp.clad_or, zircaloy2, water, boundary_type='reflective')

  colors = {uo2_no_ba: 'seagreen', uo2_ba: 'firebrick', zircaloy2: 'gray', water: 'cornflowerblue'}
  plot_geometry(inp, universe, colors)

  geometry = openmc.Geometry(universe)
  return geometry

def get_settings(inp: InputData):
  settings = openmc.Settings()
  settings.particles = inp.particles
  settings.batches = inp.active_batches + inp.inactive_batches
  settings.inactive = inp.inactive_batches
  # settings.source = openmc.IndependentSource(space=openmc.stats.Box((-lattice_pitch*lattice_size/2, -lattice_pitch*lattice_size/2, 0), (lattice_pitch*lattice_size/2, lattice_pitch*lattice_size/2, 0)))
  settings.source = openmc.IndependentSource(space=openmc.stats.Point((0, 0, 0)))
  return settings

def run_depletion(inp: InputData, model: openmc.model.Model):
  op = openmc.deplete.CoupledOperator(model, diff_burnable_mats=False, chain_file=inp.chain_file)
  cecm = openmc.deplete.CECMIntegrator(op, inp.dt, inp.power)
  os.chdir(inp.cwd_path)
  cecm.integrate()
  os.chdir(inp.original_cwd_path)

def get_results(inp: InputData):
  results = openmc.deplete.Results(f'{inp.cwd_path}/depletion_results.h5')

  # Plot the depletion
  time, k = results.get_keff(time_units="d")
  plt.errorbar(time, k[:, 0], yerr=k[:, 1], fmt='o-')
  plt.xlabel('$t$ [d]')
  plt.ylabel('$k_{\infty}$')
  plt.grid()
  plt.tight_layout()
  plt.savefig(f'{inp.results_path}/keff.png')

  # Save the input data as a yaml file
  inp.to_yaml_file(f'{inp.results_path}/input_data.yaml')

def main():
  argparser = argparse.ArgumentParser() # Add argument to specity experiment numbers to get results on, e.g. 1, 2, 7, 928. Could be a list of numbers or a range
  argparser.add_argument("-e", "--experiment_numbers", help="Experiment numbers to get results on, e.g. 1, 2, 7, 928", type=int, nargs='+')
  args = argparser.parse_args()
  experiment_numbers = args.experiment_numbers

  if experiment_numbers is not None:
    print(f"Getting results for experiments: {experiment_numbers}")
    for experiment_number in experiment_numbers:
      inp = InputData(experiment=starbun.utils.tracker.format_tracker_value(experiment_number))
      inp.from_yaml_file(f'experiments/{inp.experiment}/results/input_data.yaml')
      get_results(inp)
    return # Exit the program after getting results

  for depletion_chain in [os.environ['OPENMC_DEPLETION_CHAIN'], "/Users/sigge/nuclear_data/hdf5/Simplified chain/chain_casl_pwr.xml"]:
    inp = InputData()
    inp.chain_file = depletion_chain

    ba_pin_positions.visualize(inp.lattice_size, inp.img_path)

    geometry = get_geometry(inp)
    settings = get_settings(inp)

    model = openmc.model.Model(geometry=geometry, settings=settings)
    model.differentiate_depletable_mats(diff_volume_method="divide equally")
    run_depletion(inp, model)
    
    get_results(inp)

if __name__ == '__main__':
    main()