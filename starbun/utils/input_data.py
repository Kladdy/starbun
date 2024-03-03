import os
from dataclasses import dataclass, field
from dataclass_wizard import DumpMeta, LoadMeta, YAMLWizard
import starbun.utils.tracker
import logging

@dataclass
class ExperimentInputData(YAMLWizard, key_transform='SNAKE'):
  experiment: str
  experiment_path: str
  original_cwd_path: str
  cwd_path: str
  results_path: str
  img_path: str

  def __init__(self):
    if self.experiment: 
      is_existing_experiment = True
    else: 
      is_existing_experiment = False

    if not is_existing_experiment: self.experiment = starbun.utils.tracker.get_tracker_value(increase=True)
    self.original_cwd_path = os.getcwd()
    self.experiment_path = os.path.join("experiments", self.experiment)
    self.cwd_path = os.path.join(self.experiment_path, "cwd")
    self.results_path = os.path.join(self.experiment_path, "results")
    self.img_path = os.path.join(self.experiment_path, "img")

    os.makedirs(self.experiment_path, exist_ok=is_existing_experiment)
    os.makedirs(self.cwd_path, exist_ok=is_existing_experiment)
    os.makedirs(self.results_path, exist_ok=is_existing_experiment)
    os.makedirs(self.img_path, exist_ok=is_existing_experiment)