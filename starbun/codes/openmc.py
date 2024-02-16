from starbun.models.fuel import CladdingMaterial, FuelAssembly, FuelMaterial, FuelSegment, GapMaterial, ModeratorMaterial
import openmc

def build_fuel_assembly_universe(fuel_assembly: FuelAssembly) -> openmc.Universe:
    universe = openmc.Universe(name=fuel_assembly.name) 

    return universe

def build_segment_universe(fuel_segment: FuelSegment, fuel_assembly: FuelAssembly) -> openmc.Universe:
    universe = openmc.Universe(name=fuel_segment.id)

    fuel_materials = [build_fuel_material(fuel_material) for fuel_material in fuel_segment.fuel_materials]

    return universe

def build_fuel_material(fuel_material: FuelMaterial) -> openmc.Material:
    material = openmc.Material(name=fuel_material.id)

    material.set_density('g/cm3', fuel_material.density)
    for nuclide in fuel_material.nuclides:
      material.add_nuclide(nuclide.nuclide_str, nuclide.percent, nuclide.percent_type)

    return material

def build_gap_material(gap_material: GapMaterial) -> openmc.Material:
    material = openmc.Material(name=gap_material.id)

    material.set_density('g/cm3', gap_material.density)
    for nuclide in gap_material.nuclides:
      material.add_nuclide(nuclide.nuclide_str, nuclide.percent, nuclide.percent_type)

    return material

def build_cladding_material(cladding_material: CladdingMaterial) -> openmc.Material:
    material = openmc.Material(name=cladding_material.id)

    material.set_density('g/cm3', cladding_material.density)
    for nuclide in cladding_material.nuclides:
      material.add_nuclide(nuclide.nuclide_str, nuclide.percent, nuclide.percent_type)

    return material

def build_moderator_material(moderator_material: ModeratorMaterial) -> openmc.Material:
    material = openmc.Material(name=moderator_material.id)

    material.set_density('g/cm3', moderator_material.density)
    for nuclide in moderator_material.nuclides:
      material.add_nuclide(nuclide.nuclide_str, nuclide.percent, nuclide.percent_type)

    return material