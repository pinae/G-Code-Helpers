# G-Code-Helpers
Generate G-Code with python.

## Installation
Clone the repository:
```bash
git clone https://github.com/pinae/G-Code-Helpers.git
```
Create a virtualenv:
```bash
python3 -m venv env
source env/bin/activate
```
Install the requirements:
```bash
pip install --upgrade pip
pip install wheel
pip install -r requirements.txt
```

## Usage
**Important: Adjust `start_sequence()` and `stop_sequence()` to your 
3D-printer. The default values may be harmful for your machine!**

The module `gcodehelpers.py` contains useful functions to create scripts 
which produce G-Code. They base mainly on `print_move()` which accepts a
position for start and destination and usually a current position for
the extruder. It returns a modified extruder position which can be used 
as input for the next `print_move()`. The second return value is a string 
with G-Code commands. A typical sequence of commands looks like this:

```python
from gcodehelpers import print_move, start_sequence, stop_sequence

with open("test.gcode", 'w') as f:
    f.write(start_sequence() + "\n")
    e = 0.0
    e, command = print_move((0, 0, 0.3), (10, 0, 0.3), old_e=e)
    f.write(command + "\n")
    e, command = print_move((10, 0, 0.3), (10, 10, 0.3), old_e=e)
    f.write(command + "\n")
    f.write(stop_sequence())
```

## Example scripts
There are four scripts for generating G-Code for test prints (`generate_*.py`). Use these
as a reference on how to write your own scripts.

Let me know if you create useful scripts for calibrating your own printer.
