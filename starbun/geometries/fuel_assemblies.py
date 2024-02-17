import openmc
import openmc.model

def rectangular_lattice(n_pins: float, pitch: float, fuel_or: float,
                        fuel_material: openmc.Material | list[openmc.Material], clad_ir: float, clad_or: float,
                        clad_material: openmc.Material, moderator_material: openmc.Material):
  """Create a rectangular lattice of fuel pins

  Parameters
  ----------
  n_pins : int
    Number of pins in the lattice
  pitch : float
    Distance between pin centers in cm
  fuel_or : float
    Outer radius of the fuel pin in cm
  fuel_material : openmc.Material or list of openmc.Material of size n_pins^2
    The fuel material(s)
  clad_ir : float
    Inner radius of the cladding in cm
  clad_or : float 
    Outer radius of the cladding in cm
  clad_material : openmc.Material 
    The cladding material
  moderator_material : openmc.Material
    The moderator material

  Returns
  -------
  openmc.RectangularLattice
    The rectangular lattice of fuel pins
  """

  if isinstance(fuel_material, openmc.Material):
    fuel_material = [fuel_material]*n_pins**2

  assert len(fuel_material) == n_pins**2, "The number of fuel materials must be equal to n_pins^2, or a single material must be provided"

  # Fuel region
  fuel_or_surf = openmc.ZCylinder(r=fuel_or)
  fuel_region = -fuel_or_surf

  # Gap region
  if clad_ir > fuel_or:
    gap_ir_surf = openmc.ZCylinder(r=fuel_or)
    gap_or_surf = openmc.ZCylinder(r=clad_ir)
    gap_region = +gap_ir_surf & -gap_or_surf
    gap_cell = openmc.Cell(region=gap_region)

  # Cladding region
  clad_ir_surf = openmc.ZCylinder(r=clad_ir)
  clad_or_surf = openmc.ZCylinder(r=clad_or)
  clad_region = +clad_ir_surf & -clad_or_surf
  clad_cell = openmc.Cell(region=clad_region, fill=clad_material)

  # Moderator region
  pin_cell_prism = openmc.model.RectangularPrism(width=pitch, height=pitch)
  moderator_ir_surf = openmc.ZCylinder(r=clad_or)
  moderator_region = +moderator_ir_surf & pin_cell_prism
  moderator_cell = openmc.Cell(region=moderator_region, fill=moderator_material)

  # Prism for moderator only
  moderator_only_region = pin_cell_prism
  moderator_only_cell = openmc.Cell(region=moderator_only_region, fill=moderator_material)

  fuel_pin_universes = []

  for fuel_pin_idx, material in enumerate(fuel_material):
    if material is None:
      fuel_pin_universe = openmc.Universe(cells=[moderator_only_cell])
      fuel_pin_universes.append(fuel_pin_universe)
      continue
    else:
      fuel_cell = openmc.Cell(region=fuel_region, fill=material)

    if clad_ir > fuel_or:
      fuel_pin_universe = openmc.Universe(cells=[fuel_cell, gap_cell, clad_cell, moderator_cell])
    else:
      fuel_pin_universe = openmc.Universe(cells=[fuel_cell, clad_cell, moderator_cell])

    fuel_pin_universes.append(fuel_pin_universe)

  lattice = openmc.RectLattice()
  lattice.lower_left = (-pitch*n_pins/2, -pitch*n_pins/2)
  lattice.pitch = (pitch, pitch)
  lattice.universes = [fuel_pin_universes[i*n_pins:(i+1)*n_pins] for i in range(n_pins)]

  return lattice