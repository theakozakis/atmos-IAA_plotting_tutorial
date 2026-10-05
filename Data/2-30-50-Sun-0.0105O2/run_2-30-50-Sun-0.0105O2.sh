#!/bin/bash
# Script to run atmos either uncoupled or coupled
# Written primarily by Jack H. Madden, modified and commented by Thea Kozakis
# This script is started by and takes parameters from run_atmos.sh
# You shouldn't have to change this all only you're doing something fun and new

# Find current time
start=$(date +%s)

# ** Is this one necessary? this is the only time parentdir shows up
parentdir=${PWD%/*}
# Define main working directory (copy of parent_atmos)
workingdir=$PWD
# Extract this script name
scriptname=${BASH_SOURCE[0]}

# Type of run (uncoupled or coupled)
runtype=2
# Name of the specific model run
name=2-30-50-Sun-0.0105O2
# Number of iterations between photochemistry and climate code
iter=30

##########################################################################################
# Only running PHOTOCHEM
##########################################################################################
# This just changes ICOUPLE to 0 in input_photchem.dat, compiles the photochemistry 
# code, and then runs it

if [ $runtype == "0" ]
   then
       perl -pi -e "s/ICOUPLEvar/0/g" PHOTOCHEM/INPUTFILES/input_photchem.dat
       make '-f' 'PhotoMake' 'clean'
       make '-f' 'PhotoMake'
       echo "Make complete"
       echo "Running photo"
       ./'Photo.run'
  fi
  
##########################################################################################
# Only running CLIMA
##########################################################################################
# This just changes ICOUPLE to 0 in input_clima.dat, complies the climate code, and then
# runs it

if [ $runtype == "1" ]
   then
       perl -pi -e "s/ICOUPLEvar/0/g" CLIMA/IO/input_clima.dat
       make '-f' 'ClimaMake' 'clean'
       make '-f' 'ClimaMake'
       echo "Make complete"
       echo "Running clima"
       ./'Clima.run'
  fi

##########################################################################################
# Running PHOTOCHEM and CLIMA coupled together
##########################################################################################
# This part is more ~fancy~ as coupling the codes is less straightforward

if [ $runtype == "2" ]
then
	# Changes ICOUPLE to 0 in input_photchem and compiles the code
    perl -pi -e "s/ICOUPLEvar/0/g" PHOTOCHEM/INPUTFILES/input_photchem.dat
    
    make '-f' 'PhotoMake' 'clean'
    make '-f' 'PhotoMake'
    make '-f' 'ClimaMake' 'clean'
    make '-f' 'ClimaMake'
    echo "Make complete"
    echo "Starting iteration 1"
    echo "running photo iteration 1 of ${iter}"

	# Makes the directory frames to store info from PHOTOCHEM and CLIMA each iteration
    mkdir frames
    
    # Saves original in.dist file in frames
    cp PHOTOCHEM/in.dist frames/in_1.dist
    
    # Runs the first PHOTOCHEM iteration (and keeps track of run time)
    photostart=$(date +%s)
    ./'Photo.run'
    photoend=$(date +%s)
    
    echo "Photo iteration 1 took $((photoend-photostart)) seconds"
    
    # Save the output in.dist file (out.dist) in /frames
    cp PHOTOCHEM/OUTPUT/out.dist frames/out_1.dist
	
	# Changes ICOUPLE to 1 on line 15 on input_photchem.dat
    perl -pi -e 's/0/1/ if $. == 15' PHOTOCHEM/INPUTFILES/input_photchem.dat
    
    # Sets ICOUPLE to 1 in input_clima.dat
    perl -pi -e "s/ICOUPLEvar/1/g" CLIMA/IO/input_clima.dat
    # Changes IUP to 1 on line 17 of input_clima.dat
    perl -pi -e 's/0/1/ if $. == 17' CLIMA/IO/input_clima.dat

	# ** IUP has been set to one so TempIn.dat isn't read in?? also where does TempIn come from
	# ** can I just delete this line?
    cp CLIMA/IO/TempIn.dat frames/Temp_1.dat
    
    echo "running clima iteration 1 of ${iter}"
    
    # Runs the first CLIMA iteration (and keeps track of run time)
    climastart=$(date +%s)
    ./'Clima.run'
    climaend=$(date +%s)
    
    
    echo "Clima iteration 1 took $((climaend-climastart)) seconds"

	# Saves the CLIMA output files in /frames
    cp CLIMA/IO/clima_last.tab  frames/clima_out_1.tab    
    cp CLIMA/IO/clima_allout.tab IO/clima_allout_${name}_all.tab
    
    # Changes IUP to 0 on the 17th line of input_clima.dat
    perl -pi -e 's/1/0/ if $. == 17' CLIMA/IO/input_clima.dat
    
    # for loop begins for the rest of the iterations
    for ((i=2; i<=${iter}; i++)); do
        echo "Starting iteration $i"
	
	# out.dist becomes in.dist, and a copy of in.dist is saved in /frames
	cp PHOTOCHEM/OUTPUT/out.dist PHOTOCHEM/in.dist
	cp PHOTOCHEM/in.dist frames/in_$i.dist

	# PHOTOCHEM runs
	echo "running photo iteration $i of ${iter}"
	photostart=$(date +%s)
        ./'Photo.run'
	photoend=$(date +%s)
	echo "Photo iteration $i took $((photoend-photostart)) seconds"

	# out.dist is saved in /frames
	cp PHOTOCHEM/OUTPUT/out.dist frames/out_$i.dist


    echo "running clima iteration $i of ${iter}"
    
    # TempOut.dat becomes TempIn.dat and TempIn.dat gets saved in /frames
    cp CLIMA/IO/TempOut.dat CLIMA/IO/TempIn.dat
	cp CLIMA/IO/TempIn.dat frames/Temp_$i.dat
	
	# CLIMA runs
	climastart=$(date +%s)
        ./'Clima.run'
	climaend=$(date +%s)
	
	echo "Clima iteration $i took $((climaend-climastart)) seconds"
	
	# The output file clima_last.tab is saved in frames
	cp CLIMA/IO/clima_last.tab  frames/clima_out_${i}.tab
	# The output file clima_allout.tab is constantly built upon itself in /IO
	cat CLIMA/IO/clima_allout.tab >> IO/clima_allout_${name}_all.tab
    done
    
    # All iterations are done, output files are saved in /frames and /IO
    cp CLIMA/IO/TempOut.dat frames/Temp_$i.dat
    cp CLIMA/IO/clima_last.tab  IO/clima_last_${name}.tab
    cp PHOTOCHEM/OUTPUT/PTZ_mixingratios_out.dist  IO/photo_mixings_${name}.tab
    cp CLIMA/IO/clima_allout.tab IO/clima_allout_${name}.tab
fi

end=$(date +%s)
runtime=$((end-start))
echo "Run completed in $runtime seconds"

