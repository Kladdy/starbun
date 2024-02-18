import os
import numpy as np
import matplotlib.pyplot as plt
import openmc
import openmc.stats
import openmc.model
import openmc.deplete
import starbun.materials.fuels
import starbun.materials.claddings
import starbun.materials.moderators
import starbun.geometries.fuel_assemblies

import ba_pin_positions

# Constants
enrichment_pct = 5.0
lattice_pitch = 1.26
fuel_or = 0.45
clad_ir = 0.47
clad_or = 0.55
lattice_size = 10
dt = [60 * 24 * 60 * 60] * 1 # 10 steps of 60 days
power = 4e6 / 400 # MW/cm

def plot_geometry(universe: openmc.Universe, colors: dict, n_ba_pins: int):  
  # Increase font size for better visibility with large pixel counts
  original_font_size = plt.rcParams['font.size']
  plt.rcParams.update({'font.size': 50})

  universe.plot(colors=colors, color_by='material', pixels=(2000,2000), legend=True)
  plt.tight_layout()
  plt.savefig(f'img/{lattice_size}x{lattice_size}_fuel-map_{n_ba_pins}-pins.png')
  plt.close()

  # Restore font size
  plt.rcParams.update({'font.size': original_font_size})

def get_geometry(n_ba_pins: int, ba_pct: float):
  uo2_no_ba = starbun.materials.fuels.uo2(enrichment_pct=enrichment_pct)
  uo2_ba = starbun.materials.fuels.uo2(enrichment_pct=enrichment_pct, gd2o3_pct=ba_pct)
  zircaloy2 = starbun.materials.claddings.zircaloy2()
  water = starbun.materials.moderators.water()

  # Set volumes of fuel as it is needed for depletion calculations
  # TODO: Should this be multiplied by number of pins for each material?
  uo2_no_ba.volume = np.pi * fuel_or**2 * (lattice_size**2 - n_ba_pins)
  uo2_ba.volume = np.pi * fuel_or**2 * n_ba_pins

  ba_positions = ba_pin_positions.get(n_ba_pins, lattice_size)
  fuel_materials = [uo2_ba if (i, j) in ba_positions else uo2_no_ba for i in range(lattice_size) for j in range(lattice_size)]

  universe = starbun.geometries.fuel_assemblies.rectangular_lattice(lattice_size, lattice_pitch, fuel_or, fuel_materials, clad_ir, clad_or, zircaloy2, water, boundary_type='reflective')

  colors = {uo2_no_ba: 'seagreen', uo2_ba: 'firebrick', zircaloy2: 'gray', water: 'cornflowerblue'}
  plot_geometry(universe, colors, n_ba_pins)

  geometry = openmc.Geometry(universe)
  return geometry

def get_settings():
  settings = openmc.Settings()
  settings.particles = 1000
  settings.batches = 100
  settings.inactive = 20
  # settings.source = openmc.IndependentSource(space=openmc.stats.Box((-lattice_pitch*lattice_size/2, -lattice_pitch*lattice_size/2, 0), (lattice_pitch*lattice_size/2, lattice_pitch*lattice_size/2, 0)))
  settings.source = openmc.IndependentSource(space=openmc.stats.Point((0, 0, 0)))
  return settings

def run_depletion(model: openmc.model.Model):
  op = openmc.deplete.CoupledOperator(model, diff_burnable_mats=True, chain_file=os.environ['OPENMC_DEPLETION_CHAIN'])
  cecm = openmc.deplete.CECMIntegrator(op, dt, power)
  os.chdir('cwd')
  cecm.integrate()
  os.chdir('..')

def get_results():
  results = openmc.deplete.Results('cwd/depletion_results.h5')
  time, k = results.get_keff(time_units="d")
  print(k)

  plt.errorbar(time, k[:, 0], yerr=k[:, 1], fmt='o-')
  plt.xlabel('Time (d)')
  plt.ylabel('$k_{\infty}$')
  plt.tight_layout()
  plt.savefig('results/keff.png')

def main():
  os.makedirs('cwd', exist_ok=True)
  os.makedirs('img', exist_ok=True)
  os.makedirs('results', exist_ok=True)

  ba_pin_positions.visualize(lattice_size)

  geometry = get_geometry(16, 5)
  settings = get_settings()

  model = openmc.model.Model(geometry=geometry, settings=settings)
  run_depletion(model)
  
  get_results()

if __name__ == '__main__':
    main()