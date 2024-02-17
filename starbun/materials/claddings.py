import openmc

def zircaloy4(density=6.55, temperature=900.0):
  """Create a Zircaloy-4 cladding material

  Parameters
  ----------
  density : float
    Density in g/cm3
  temperature : float
    Temperature in K

  Returns
  -------
  openmc.Material
    The Zircaloy-4 cladding material
  """

  cladding = openmc.Material(name="zircaloy4")
  cladding.add_element('Zr', 1)
  cladding.set_density('g/cm3', density)
  cladding.temperature = temperature

  return cladding

def zircaloy2(density=6.55, temperature=900.0):
  """Create a Zircaloy-2 cladding material

  Parameters
  ----------
  density : float
    Density in g/cm3
  temperature : float
    Temperature in K

  Returns
  -------
  openmc.Material
    The Zircaloy-2 cladding material
  """

  cladding = openmc.Material(name="zircaloy2")
  cladding.add_element('Zr', 1)
  cladding.set_density('g/cm3', density)
  cladding.temperature = temperature

  return cladding