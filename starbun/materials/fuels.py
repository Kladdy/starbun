import openmc

def uo2(density=10.0, temperature=900.0, enrichment_pct=5.0, gd2o3_pct=0.0):
  """Create a UO2 fuel material

  Parameters
  ----------
  density : float
    Density in g/cm3
  temperature : float
    Temperature in K
  enrichment_pct : float
    U235 enrichment in percent
  gd2o3_pct : float
    Gd2O3 in percent

  Returns
  -------
  openmc.Material
    The UO2 or UO2+Gd2O3 fuel material
  """

  fuel = openmc.Material(name="uo2")
  fuel.add_element('U', 1, enrichment=enrichment_pct)
  fuel.add_element('O', 2)

  fuel.set_density('g/cm3', density)
  fuel.temperature = temperature

  if gd2o3_pct > 0.0:
    ba = gd2o3(density, temperature)
    gd2o3_frac = gd2o3_pct/100
    fuel = fuel.mix_materials(ba, [1 - gd2o3_frac, gd2o3_frac], 'wo')
    fuel.name = "uo2_gd2o3"

  return fuel

def gd2o3(density=7.4, temperature=900.0):
  """Create a Gd2O3 burnable absorber material

  Parameters
  ----------
  density : float
    Density in g/cm3
  temperature : float
    Temperature in K

  Returns
  -------
  openmc.Material
    The Gd2O3 burnable absorber material
  """

  ba = openmc.Material(name="gd2o3")
  ba.add_element('Gd', 2)
  ba.add_element('O', 3)

  ba.set_density('g/cm3', density)
  ba.temperature = temperature

  return ba