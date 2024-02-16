from dataclasses import dataclass
from typing import List
import numpy as np
from dataclass_wizard import YAMLWizard

@dataclass
class Nuclide:
  nuclide_str: str
  percent: float
  percent_type: str

@dataclass
class Material:
  id: str
  nuclides: List[Nuclide]
  density: float
  temperature: float  

@dataclass
class FuelMaterial(Material):
  inner_radius: float
  outer_radius: float
  enrichment: float
  ba: float

@dataclass
class GapMaterial(Material):
  inner_radius: float
  outer_radius: float

@dataclass
class CladdingMaterial(Material):
  inner_radius: float
  outer_radius: float

@dataclass
class ModeratorMaterial(Material):
  pass

@dataclass
class FuelSegment:
  id: str
  height: float
  fuel_rods: List[str | None]
  gap_rods: List[str | None]
  cladding_rods: List[str | None]

@dataclass
class FuelAssembly(YAMLWizard, key_transform='SNAKE'):
  name: str
  lattice_size: int
  lattice_pitch: float
  segments: List[FuelSegment]
  fuels: List[FuelMaterial]
  gaps: List[GapMaterial]
  claddings: List[CladdingMaterial]
  moderators: List[ModeratorMaterial]

  @staticmethod
  def load(file_path: str) -> 'FuelAssembly':
    return FuelAssembly.from_yaml_file(file_path)

  def save(self, file_path: str) -> None:
    self.to_yaml_file(file_path)