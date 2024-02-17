import openmc
import openmc.data
import openmc.model

def water(boron_ppm=0.0, temperature=300.0, pressure=0.1013):
  """Create a water moderator material
  
  Parameters
  ----------
  boron_ppm : float
    Boron concentration in ppm
  temperature : float
    Temperature in K
  pressure : float
    Pressure in MPa
    
  Returns
  -------
  openmc.Material
    The water moderator material
  """

  moderator = openmc.model.borated_water(boron_ppm, temperature, pressure)

  return moderator