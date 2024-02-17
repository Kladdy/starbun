import openmc
import openmc.model

def rectangular_lattice(lattice_size: float, lattice_pitch: float, fuel_or: float,
                        fuel_material: openmc.Material | list[openmc.Material], clad_ir: float, clad_or: float,
                        clad_material: openmc.Material, moderator_material: openmc.Material, boundary_type: str):
  """Create a rectangular lattice of fuel pins

  Parameters
  ----------
  lattice_size : int
    Number of pins in the lattice
  lattice_pitch : float
    Distance between pin centers in cm
  fuel_or : float
    Outer radius of the fuel pin in cm
  fuel_material : openmc.Material or list of openmc.Material of size lattice_size^2
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
    fuel_material = [fuel_material]*lattice_size**2

  assert len(fuel_material) == lattice_size**2, "The number of fuel materials must be equal to lattice_size^2, or a single material must be provided"

  # Fuel region
  fuel_or_surf = openmc.ZCylinder(r=fuel_or)
  fuel_region = -fuel_or_surf

  # Gap region
  if clad_ir > fuel_or:
    gap_ir_surf = openmc.ZCylinder(r=fuel_or)
    gap_or_surf = openmc.ZCylinder(r=clad_ir)
    gap_region = +gap_ir_surf & -gap_or_surf

  # Cladding region
  clad_ir_surf = openmc.ZCylinder(r=clad_ir)
  clad_or_surf = openmc.ZCylinder(r=clad_or)
  clad_region = +clad_ir_surf & -clad_or_surf
  

  # Moderator region
  pin_cell_prism = openmc.model.RectangularPrism(width=lattice_pitch, height=lattice_pitch)
  moderator_ir_surf = openmc.ZCylinder(r=clad_or)
  moderator_region = +moderator_ir_surf & -pin_cell_prism
  

  # Prism for moderator only
  moderator_only_region = -pin_cell_prism

  fuel_pin_universes = []

  for fuel_pin_idx, material in enumerate(fuel_material):
    if material is None:
      moderator_only_cell = openmc.Cell(region=moderator_only_region, fill=moderator_material)
      fuel_pin_universe = openmc.Universe(cells=[moderator_only_cell])
      fuel_pin_universes.append(fuel_pin_universe)
      continue
    else:
      fuel_cell = openmc.Cell(region=fuel_region, fill=material)
      clad_cell = openmc.Cell(region=clad_region, fill=clad_material)
      moderator_cell = openmc.Cell(region=moderator_region, fill=moderator_material)

    if clad_ir > fuel_or:
      gap_cell = openmc.Cell(region=gap_region)
      fuel_pin_universe = openmc.Universe(cells=[fuel_cell, gap_cell, clad_cell, moderator_cell])
    else:
      fuel_pin_universe = openmc.Universe(cells=[fuel_cell, clad_cell, moderator_cell])

    fuel_pin_universes.append(fuel_pin_universe)

  lattice = openmc.RectLattice()
  lattice.lower_left = (-lattice_pitch*lattice_size/2, -lattice_pitch*lattice_size/2)
  lattice.pitch = (lattice_pitch, lattice_pitch)
  lattice.universes = [fuel_pin_universes[i*lattice_size:(i+1)*lattice_size] for i in range(lattice_size)]

  lattice_prism = openmc.model.RectangularPrism(width=lattice_pitch*lattice_size, height=lattice_pitch*lattice_size, boundary_type=boundary_type)
  lattice_cell = openmc.Cell(fill=lattice, region=-lattice_prism)
  lattice_universe = openmc.Universe(cells=[lattice_cell])

  return lattice_universe