import os
from dataclasses import dataclass, field
from dataclass_wizard import YAMLWizard
import starbun.utils.tracker

@dataclass
class ExperimentInputData(YAMLWizard, key_transform='SNAKE'):
  experiment: str
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
    self.cwd_path = self.get_cwd_path()
    self.results_path = self.get_results_path()
    self.img_path = self.get_img_path()

    os.makedirs(self.cwd_path, exist_ok=is_existing_experiment)
    os.makedirs(self.results_path, exist_ok=is_existing_experiment)
    os.makedirs(self.img_path, exist_ok=is_existing_experiment)

  def get_cwd_path(self):
    return os.path.join("experiments", self.experiment, "cwd")

  def get_results_path(self):
    return os.path.join("experiments", self.experiment, "results")

  def get_img_path(self):
    return os.path.join("experiments", self.experiment, "img")