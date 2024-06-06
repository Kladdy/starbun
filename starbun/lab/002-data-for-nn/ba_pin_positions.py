def get(n_ba_pins: int, lattice_size: int):
  """Gets the positions of the BA pins in the fuel assembly by placing them 
  one step from the edge of the lattice.
  Assumes lattice_size >= 8 and n_ba_pins <= 16 and n_ba_pins is a multiple of 4"""
  assert lattice_size >= 8, "lattice_size must be at least 8"
  assert n_ba_pins <= 16, "n_ba_pins must be at most 16"
  assert n_ba_pins % 4 == 0, "n_ba_pins must be a multiple of 4"
  n_ba_pins_per_side = n_ba_pins // 4
  ba_pin_positions = []

  # F = fuel, B = BA
  # Add upper left corner positons, then rotate to get all positions
  if n_ba_pins_per_side == 0:
    # F F F F
    # F F F F
    # F F F F
    # F F F F
    pass
  elif n_ba_pins_per_side == 1:
    # F F F F
    # F B F F
    # F F F F
    # F F F F
    ba_pin_positions.append((1, 1))
  elif n_ba_pins_per_side == 2:
    # F F F F
    # F B F F
    # F F F F
    # F F F B
    ba_pin_positions.append((1, 1))
    ba_pin_positions.append((3, 3))
  elif n_ba_pins_per_side == 3:
    # F F F F
    # F B F B
    # F F F F
    # F B F F
    ba_pin_positions.append((1, 1))
    ba_pin_positions.append((3, 1))
    ba_pin_positions.append((1, 3))
  elif n_ba_pins_per_side == 4:
    # F F F F
    # F B F B
    # F F F F
    # F B F B
    ba_pin_positions.append((1, 1))
    ba_pin_positions.append((3, 1))
    ba_pin_positions.append((1, 3))
    ba_pin_positions.append((3, 3))

  # Rotate the upper left corner to get all positions (upper right, lower left, lower right)
  all_ba_pin_positions = []
  for ba_pin_position in ba_pin_positions:
    x, y = ba_pin_position
    all_ba_pin_positions.append((x, y)) # upper left
    all_ba_pin_positions.append((lattice_size - 1 - y, x)) # upper right
    all_ba_pin_positions.append((y, lattice_size - 1 - x)) # lower left
    all_ba_pin_positions.append((lattice_size - 1 - x, lattice_size - 1 - y)) # lower right

  return all_ba_pin_positions
  
def visualize(lattice_size: int, path: str):
  import matplotlib.pyplot as plt
  import numpy as np
  import os
  os.makedirs(path, exist_ok=True)
  for n_ba_pins in [0, 4, 8, 12, 16]:
    ba_pin_positions = get(n_ba_pins, lattice_size)
    lattice = np.zeros((lattice_size, lattice_size))
    for x, y in ba_pin_positions:
      lattice[x, y] = 1
    plt.imshow(lattice, cmap='gray')
    plt.title(f'{n_ba_pins} BA pins, {lattice_size}x{lattice_size} lattice')
    plt.savefig(f'{path}/{lattice_size}x{lattice_size}_ba-pin-positions_{n_ba_pins}-pins.png')
  plt.close() 