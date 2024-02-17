import openmc
import openmc.data

def water(temperature=300.0, pressure=0.1013, use_TSL=True):
  """Create a water moderator material
  
  Parameters
  ----------
  temperature : float
    Temperature in K
  pressure : float
    Pressure in MPa
  use_TSL : bool
    Whether to use the thermal scattering library
    
  Returns
  -------
  openmc.Material
    The water moderator material
  """

  density = openmc.data.water_density(temperature, pressure)

  moderator = openmc.Material(name="water")
  moderator.add_element('H', 2)
  moderator.add_element('O', 1)

  moderator.set_density('g/cm3', density)
  moderator.temperature = temperature

  if use_TSL: moderator.add_s_alpha_beta('c_H_in_H2O')

  return moderator