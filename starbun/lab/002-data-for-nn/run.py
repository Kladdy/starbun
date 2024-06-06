import os
import numpy as np
import matplotlib.pyplot as plt
import argparse
from dataclasses import dataclass, field
from dataclass_wizard import DumpMeta, YAMLWizard
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
class InputData(ExperimentInputData):
  enrichment_pct: float = 5.0
  lattice_pitch: float = 1.26
  fuel_or: float = 0.45
  clad_ir: float = 0.47
  clad_or: float = 0.55
  lattice_size: int = 10
  n_ba_pins: int = 12
  ba_pct: float = 5.0
  particles: int = 1000
  active_batches: int = 100
  inactive_batches: int = 40
  cross_sections: str = os.environ['OPENMC_CROSS_SECTIONS']

  def __init__(self, experiment=None, *args, **kwargs):
    self.experiment = experiment

    # Check if kwargs is an empty dictionary
    if kwargs:
      for key, value in kwargs.items():
        setattr(self, key, value)

    super().__init__()

def get_geometry(inp: InputData):
  uo2_no_ba = starbun.materials.fuels.uo2(enrichment_pct=inp.enrichment_pct)
  uo2_ba = starbun.materials.fuels.uo2(enrichment_pct=inp.enrichment_pct, gd2o3_pct=inp.ba_pct)
  zircaloy2 = starbun.materials.claddings.zircaloy2()
  water = starbun.materials.moderators.water()

  ba_positions = ba_pin_positions.get(inp.n_ba_pins, inp.lattice_size)
  fuel_materials = [uo2_ba if (i, j) in ba_positions else uo2_no_ba for i in range(inp.lattice_size) for j in range(inp.lattice_size)]

  universe = starbun.geometries.fuel_assemblies.rectangular_lattice(inp.lattice_size, inp.lattice_pitch, inp.fuel_or, fuel_materials, inp.clad_ir, inp.clad_or, zircaloy2, water, boundary_type='reflective')

  colors = {uo2_no_ba: 'seagreen', uo2_ba: 'firebrick', zircaloy2: 'gray', water: 'cornflowerblue'}
  plot_geometry(inp, universe, colors)

  geometry = openmc.Geometry(universe)
  return geometry

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

def get_settings(inp: InputData):
  settings = openmc.Settings()
  settings.particles = inp.particles
  settings.batches = inp.active_batches + inp.inactive_batches
  settings.inactive = inp.inactive_batches
  # settings.source = openmc.IndependentSource(space=openmc.stats.Box((-lattice_pitch*lattice_size/2, -lattice_pitch*lattice_size/2, 0), (lattice_pitch*lattice_size/2, lattice_pitch*lattice_size/2, 0)))
  settings.source = openmc.IndependentSource(space=openmc.stats.Point((0, 0, 0)))
  return settings

def main():
  for n_ba_pins in [0, 4, 8, 12, 16]:
    for ba_pct in np.linspace(0, 8, 17):
      for lattice_size in [8, 10, 12]:
        inp = InputData(n_ba_pins=n_ba_pins, ba_pct=float(ba_pct), lattice_size=lattice_size)

        # Save the input data as a yaml file
        inp.to_yaml_file(f'{inp.experiment_path}/input_data.yaml')

        # ba_pin_positions.visualize(inp.lattice_size, inp.img_path)

        geometry = get_geometry(inp)
        settings = get_settings(inp)

        model = openmc.model.Model(geometry=geometry, settings=settings)

        model.run(cwd=inp.cwd_path)

if __name__ == '__main__':
    main()