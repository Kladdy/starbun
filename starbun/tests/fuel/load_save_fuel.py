from starbun.models.fuel import CladdingMaterial, FuelAssembly, FuelMaterial, FuelSegment, GapMaterial, Material, ModeratorMaterial, Nuclide
import numpy as np

def test_save_load_fuel():
    # Create a FuelAssembly object
    fuel_assembly = FuelAssembly(
        name='fuel',
        lattice_size=3,
        lattice_pitch=1.0,
        segments=[
            FuelSegment(
                id='segment1',
                height=1.0,
                fuel_rods=['fuel1']*9,
                gap_rods=['gap1']*9,
                cladding_rods=['cladding1']*9
            )
        ],
        fuels=[
            FuelMaterial(
                id='fuel1',
                nuclides=[
                    Nuclide(nuclide_str='U235', percent=3.0, percent_type='wo'),
                    Nuclide(nuclide_str='U238', percent=97.0, percent_type='wo')
                ],
                density=10.0,
                temperature=1000.0,
                inner_radius=0,
                outer_radius=0.3,
                enrichment=5.0,
                ba=1.0,
            )
        ],
        gaps=[
            GapMaterial(
                id='gap1',
                nuclides=[
                    Nuclide(nuclide_str='He4', percent=100.0, percent_type='wo')
                ],
                density=5.0,
                temperature=1000.0,
                inner_radius=0.3,
                outer_radius=0.35
            )
        ],
        claddings=[
            CladdingMaterial(
                id='cladding1',
                nuclides=[
                    Nuclide(nuclide_str='Zr90', percent=100.0, percent_type='wo')
                ],
                density=7.0,
                temperature=1000.0,
                inner_radius=0.35,
                outer_radius=0.45
            )
        ],
        moderators=[
            ModeratorMaterial(
                id='moderator1',
                nuclides=[
                    Nuclide(nuclide_str='H1', percent=2, percent_type='ao'),
                    Nuclide(nuclide_str='O16', percent=1, percent_type='ao')
                ],
                density=1.0,
                temperature=1000.0
            )
        ]
    )

    # Save the FuelAssembly object to a file
    fuel_assembly.save('saved_fuel.yaml')

    # Load the FuelAssembly object from the file
    fuel_assembly_loaded = FuelAssembly.load('saved_fuel.yaml')
    
    # Check if the loaded FuelAssembly object is the same as the original one
    assert fuel_assembly == fuel_assembly_loaded

if __name__ == "__main__":
    test_save_load_fuel()