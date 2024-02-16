from starbun.codes.openmc import build_fuel_assembly_universe
from starbun.models.fuel import FuelAssembly
import openmc

def test_openmc():
  fuel_assembly = FuelAssembly.load('saved_fuel.yaml')

  universe = build_fuel_assembly_universe(fuel_assembly)
  assert isinstance(universe, openmc.Universe)

  universe.plot(basis='xy')


if __name__ == "__main__":
  test_openmc()