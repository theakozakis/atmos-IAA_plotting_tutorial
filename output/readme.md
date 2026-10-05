# Example output files

## photo_mixings.tab
- located in the IO/ directory of each model folder
- contains the atmospheric profiles of multiple key species as well as atmospheric altitude, pressure, and temperature
- data is extracted by Python function read_photo_mixings()

## out.out
- located in PHOTOCHEM_OUTPUT/ directory of each model folder
- contains a LOT of different photochemistry code output
- data is extracted by Python function read_outout

## clima_allout.tab
- located in IO/ directory of each model folder
- contains a lot of climate code output
- only used in Python function check_atmos_convergence() to retrieve convergence metrics
