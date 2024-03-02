def get_tracker_value(increase: bool):
  # Open the file in read mode
  try:
    with open("tracker", "r") as file:
      value = int(file.read())
      if increase: value += 1 # Increment the value by 1
  except FileNotFoundError:
    value = 0 # If the file doesn't exist, create it with value 0

  # Open the file in write mode and write the updated value
  with open("tracker", "w") as file:
    file.write(str(value))

  return format_tracker_value(value)

def format_tracker_value(value):
  # Return the padded value with 6 digits
  return str(value).zfill(6)