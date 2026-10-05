#!/bin/bash 
# Written by Thea Kozakis, January 2025
# Inspired by trialgen.sh written by Jack H. Madden
# Script to input initial conditions and run models for Atmos IAA
# Values in {} are the defaults for the ModernEarthSimple template from atmos-VPL
# https://github.com/VirtualPlanetaryLaboratory/atmos

# There is the option for using this script to set up multiple runs at once with different
# parameters, i.e., using an array to read in different values for one parameter


# Instructions for using this script:
# - This script assumes it is in the main directory of atmos-IAA with the subdirectory 
#	parent_atmos which contains the atmos code. If this is not the case, you need to 
# 	modify this file!
# - Output directories will all be written in atmos_runs, which is a subdirectory of the 
#	main atmos-IAA directory. If this is not the case you need to modify it!
# - Inputs must be written as strings or they won't be read in properly.

# For the parameter you want to use the array's values for, use ${array[${x}]}
# Example for changing O2 mixing ratios:
# O2MR=${array[${x}]}


echo "*****************************************************"
echo "Running run_atmos.sh"
echo "Setting up input files for new atmos-IAA run..."
echo "*****************************************************"

# Define directories
# Define main directory (where this script is initiated)
maindir=$PWD
# Define directory where atmos code is located
atmosdir=$maindir/parent_atmos
# Define directory where code will be copied to enable parallel runs
newdir=$maindir/atmos_runs

# Define name of this script
scriptname=${BASH_SOURCE[0]}

# If you want to run multiple models in parallel read the instructions below and change
# The necessary parameters

# If you want to use an array of values to cycle through for one parameter, put them in 
# this array (remember to put them in as strings!):
array=("0.0000105" "0.000021" "0.000105" "0.00021" "0.00105" "0.0021" "0.0105" "0.021" "0.0315" "0.042" "0.0525" "0.063" "0.0735" "0.084" "0.0945" "0.105" "0.1155" "0.126" "0.1365" "0.147" "0.1575" "0.168" "0.1785" "0.189" "0.1995" "0.21" "0.315")
len=${#array[@]}


# Change the last number here to reflect the number of values you want to run
# Example for no array and just one value:
#for x in $(seq 0 1 1); do
# Example for array with 5 values:
#for x in $(seq 0 1 4); do 

# right now it's just taking in the length of the array
for x in $(seq 0 1 $len); do 

# Make sure you're back in the main directory at the beginning of each loop
cd ${maindir}


##########################################################################################
# Variables used by both PHOTOCHEM and CLIMA
# Location of files modified:
# PHOTOCHEM/INPUTFILES/TEMPLATES/blanktemplate
# CLIMA/IO/TEMPLATES/blanktemplate
##########################################################################################


# Select host star (key is in starkey.txt)
# Current choices: Sun, GJ876
Star="Sun"

# Select flux scaling ratio
FSCALE="1.00"		# {1.00} Solar Flux Scaling (Seff) - Earth=1.0, Mars=0.43 (PLANET.dat and input_clima.dat - SOLCON in CLIMA)

# Select a coupled or uncoupled run
runtype="2"			# {2} Indicator of uncoupled/coupled run (similar to ICOUPLE in input_photochem.dat and input_clima.dat)
					# [0] Run only PHOTOCHEM
					# [1] Run only CLIMA
					# [2] Run PHOTOCHEM and CLIMA coupled
iter="30"			# {20} Number of iterations between photochemistry and climate models (if coupled)



# Basic planet and code parameters
ZY="60."			# {60.} (deg) Solar zenith angle (in input_photochem.dat and input_clima.dat)
G="980.0"			# {980.7} (cm/s^2) Gravity - Earth=980.7, Mars=373.0 (in PLANET.dat and input_clima.dat)
P0="1.013"			# {1.013} (bars) surface pressure of modern Earth in atm ( 0.0063 for Mars) (PLANET.dat and input_clima.dat - PGO in CLIMA)
SRFALB="0.250"		# {0.250} Surface Albedo - Earth=0.25, Mars=0.215 (PLANET.dat and input_clima.dat - ALB in PHOTOCHEM)
FRAK="0"			# {0} [0] Use Mie scattering for hydrocarbon particles (input_photochem.dat and input_clima.dat)
					# 	  [1] Use Fractal scattering for hydrocarbon particles
monsize="0"			# {0} [0] for 0.05 um monomers for fractal particles (input_photochem.dat and input_clima.dat - ihztype in PHOTOCHEM)
					#	  [1] for 0.01 um monomers for fractal particles
					#	  [2] for 0.02 um monomers for fractal particles
					#	  [3] for 0.07 um monomers for fractal particles
					#	  [4] for 0.10 um monomers for fractal particles
					
# Mixing ratios (species.dat and mixing ratios)
O2MR=${array[${x}]}		# {2.1E-01} (mixing ratio) Molecular oxygen
O3MR="3.000E-08"	# {3.000E-08} (mixing ratio) Ozone
H2MR="5.3E-07"		# {5.3E-07} (mixing ratio) Hydrogen
COMR="1.1E-07"		# {1.1E-07} (mixing ratio) Carbon Monoxide 
CH4MR="1.8E-06"		# {1.8E-06} (mixing ratio) Methane
C2H6MR="8.791E-27"  # {8.792E-27} (mixing ratio) Ethane
N2OMR="3.0E-07"		# {3.0E-07} (mixing ratio) Nitrous Oxide
NO2MR="5.032E-72"	# {5.031E-72} Nitrogen Dioxide 
CO2MR="3.600E-04"		# {4.0E-4} (mixing ratio) Carbon Dioxide
N2MR="0.78"			# {0.78} (mixing ratio) Nitrogen
ArMR="1.000E-02"	# {1.000E-02} (mixing ratio) Argon - check FAR if you change this




##########################################################################################
# Photochemistry code inputs (PHOTOCHEM)
# modifying files in PHOTOCHEM/INPUTFILES/TEMPLATES/blanktemplate
##########################################################################################
# parameters.inc
NZ="200"			# {200} Number of layers in the photochemistry code - currently in.dist assumes 200 layers

# input_photchem.dat
AGL="0.5"			# {0.5} DIURNAL AVERAGING FACTOR FOR PHOTORATES
ISEASON="1"			# {1} TELLS WHETHER P AND T VARY WITH TIME (THEY DON'T FOR ISEASON < 3)
IZYO2="0"			# {0} TELLS WHETHER SOLAR ZENITH ANGLE VARIES WITH TIME (0 SAYS IT DOESN'T; 1 SAYS IT DOES)
LGRID="2"			# {2} [0] USE OLD JPL WAVELENGTH GRID; 
					#	  [1] USE MARK'S NEW HIGH RESOLUTION GRID (SEE ALSO GRID.F) - IF LGRID=1, IO2 and INO should be set to 2
					#	  [2] USE ALINC'S HIGH RESOLUTION GRID AND UPDATED XSEC IF LGRID=2, IO2 and INO should be set to 3
IO2="3"				# {3} [0] FOR ALLEN AND FREDERICK O2 SCHUMANN-RUNGE COEFFICIENTS
					#	  [1] FOR EXPONENTIAL SUM FITS (FOR LOW-O2 ATMOSPHERES)
					#     [2] FOR USING HIGH RESOLUTION CROSS SECTION
					#	  [3] FOR LGRID=2 
INO="3"				# {3} [0] FOR ALLEN AND FREDERICK NO PREDISSOCIATION COEFFICIENTS
					# 	  [1] FOR MODIFIED CIESLIK AND NICOLET FORMULATION
					#     [2] USE OUT.NOPRATES FILE
					#	  [3] USE LGRID=2
EPSJ="1.E-9"		# {1.E-9} AMOUNT BY WHICH TO PERTURB THINGS FOR JACOBIAN CALCULATION
PRONO="1.E9"		# {1.E9} COLUMN-INTEGRATED NO PRODUCTION RATE FROM LIGHTNING IN EARTH'S PRESENT ATMOSPHERE
HCDENS="0.63"		# {0.63} [0.63] (g/cm^3) (Archean hydrocarbon density - Trainer et al 2006)
					# 		 [0.8]  (g/cm^3) (titan tholins - Trainer et al 2006)
					#   	 [1.0]  (g/cm^3) (old suspicious default value)
USOLMIN="1.E-20"	# {1.E-20} Value under which the time stepper no longer considers a species when calculating "max relative change."
KIDA="0"			# {0} [1] if using "kida-style" reactions.rx format
					# 	  [0] if using the code's "old-style" reactions.rx format

# PLANET.dat
ZTROP="1.1E6"		# {1.1E6} (cm) Height of the tropopause - typically Earth=11km, Mars=15km (make sure it agrees with TROPLAYER if coupled)
FAR="0.01"			# {0.1} (bars) Ar partial pressure - check ArMR if you change this
R0="6.371E8"		# {6.371E8} cm Radius of Planet
P0="1.013"			# {1.013} (bars) surface pressure of modern Earth in atm ( 0.0063 for Mars)
PLANET="EARTH"		# {EARTH} string naming the planet for extra changes (MARS is the only other option for the moment)
TIMEGA="0.0"		# {0.0} (Ga) time in Ga, for modifying the solar flux based on Claire et al 2012
IRESET="0"			# {0} Undocumented - VPL notes says probably deprecated
IHZSCALE="0"		# {0} Undocumented
uvscale="1.0"		# {1.0} Apply scale factor to only UV spectrum
JTROP="22"			# {11} Grid layer marking the tropopause height, depends on ZTROP and DELZ
DELZ="0.5E5"		# {1.0E5} (cm) Height of each atm layer - Earth=1.0E5, Mars=2.0E5


# Species.dat
# LBOUND = lower boundary conditions (species.dat)
#	[0] constant deposition velocity (VDEP)
#	[1] constant mixing ratio
#	[2] constant upward flux (SGFLUX)
#	[3] constant vdep + vertically distributed upward flux  (uses SGFLUX and DISTH)
O2LB="1"			# {1} Molecular oxygen lower boundary condition
H2LB="1"			# {0} Hydrogen lower boundary condition
COLB="1"			# {0} Carbon monoxide lower boundary condition
CH4LB="1"			# {2} Methane lower boundary condition
N2OLB="1"			# {2} Nitrous Oxide lower boundary condition
# Ground flux - SGFLUX 
O2SG="0."			# {0.} (molecules/cm^2/s) Molecular Oxygen constant surface flux
H2SG="-3.32E9"			# {0.} (molecules/cm^2/s) Hydrogen constant surface flux
COSG="2.3E11"		# {3.70E+11} (molecules/cm^2/s) Carbon monoxide constant surface flux
CH4SG="1.21E11"	# {1.00E+11} (molecules/cm^2/s) Methane constant surface flux
NOSG="1.000E+09"	# {1.000E+09} (molecules/cm^2/s) Nitric Oxide constant surface flux
H2SSG="2.000E+08"	# {2.000E+08} (molecules/cm^2/s) Hydrogen Sulfide constant surface flux
SO2SG="9.000E+09"	# {9.000E+09} (molecules/cm^2/s) Sulfur Dioxide constant surface flux
N2OSG="6.75E8"	# {1.53E+09} (molecules/cm^2/s) Nitrous Oxide constant surface flux
CO2SG="6.875E+08"	# {6.875E+08} (molecules/cm^2/s) Carbon Dioxide constant surface flux




##########################################################################################
# Climate code inputs (CLIMA)
# Modifying files in CLIMA/IO/TEMPLATES/blanktemplate and CLIMA/INCLUDE
##########################################################################################
# header.inc (in CLIMA/INCLUDE)
ND="101"			# {101} Number of atmospheric layers in the climate code

# input_clima.dat
NSTEPS="50"		# {200} step number (200 recommended for coupling)
IMW="1"				# {2} [0] FOR SATURATED TROPOSPHERE
					#	  [1] FOR MANABE/WETHERALDFIXED RELATIVE HUMIDITY
					#     [2] FOR M/W WITH CONSTANT STRATOSPHERIC H2O CONTENT AND EMPIRICAL TROPOSPHERIC H2O
					#	  [3] for DRY ADIABAT       
RSURF="0.77"			# {0.8} SURFACE RELATIVE HUMIDITY          
DTAU0="0.5"			# {0.5} OPTICAL DEPTH STEP IN SUBLEVEL INTEGRATION
ZCON="20"			# {20} ARBITRARY CONSTANT ADDED TO Z TO KEEP IT POSITIVE
PTOP="3.E-5"  		# {7.E-06} (bar) PRESSURE AT TOP OF GRID - Called P0 in CLIMA
FAC="4.0"			# {4} RATIO OF GRID SPACING AT TOP TO SPACING AT BOTTOM
IO3="1"				# {1} 1 TO INCLUDE O3, 0 TO LEAVE IT OUT BECAUSE YOU'RE A MONSTER WHO HATES OZONE
IUP="1"				# {1} SPECIFIES TYPE OF INITIALIZATION (0 IF YOU WISH TO START FROM AN EXISTING SOLUTION, 1 IF YOU WISH TO SPECIFY A NEW SURFACE TEMPERATURE)
	               	# 	IF OPTION 1 IS SELECTED YOU MUST MAKE SURE THAT THE STARTING TEMPERATURES ABOVE GROUND LEVEL ARE LESS
					# 	THAN TG0, SINCE THE TROPOSPHERIC LAPSE RATE IS INTEGRATED UPWARDS IN THIS CASE.       
TG0="288."			# {288.} INITIAL SURFACE TEMPERATURE (FOR IUP = 1 CASE)
TSTRAT="200."		# {200.} Stratospheric temperature for IUP=1. Suggestion for present Earth 220. 
ICONSERV="1"		# {0} [0] Non strict time-stepping method (faster)
					#	  [1] Each time step conserves energy (better for high CO2) 
dtmax="1.e4"		# {1.E4} Maximum time step in seconds    
CO2MAX="3.55e-2"	# {3.55E-2} Maximum CO2 mixing ratio that RRTM can manage with accuracy (for greater values of CO2 the former IR subroutine is used)
IMET="1"			# {0} Methane flag. If "1" then methane is turned on. (does not turn on ethane)
IMETETH="0"			# {0} ethane flag.  If 1 then both methane and ethane turned on
nga="6"				# {6} number of points in gaussian quadrature for zenith angle
IHAZE="0"			# {0} Turn haze on or off
icealbedo="0"		# {0} Ice-albedo parameterization from Benjamin Charnay that will iteratively update the surface albedo based on your temperature to simulate ice-albedo feedbacks
INVERSE="0"			# {0} This turns on the inverse model if you set it to 1 (you give a temperature and it gives you the necessary flux - only for clima)

# mixing_ratios.dat (the rest are listed with PHOTOCHEM mixing ratios)
TROPLAYER="22"		# {22} Atmospheric Layer of the Tropopause - should make sure this agrees with ZTROP if you change it   



# Name of run for directory labelling - edit this if you want to change naming standard
name="${runtype}-${iter}-${NSTEPS}-${Star}${SOLCON}-${O2MR}O2"


   
##########################################################################################
# END OF INPUT VALUE SECTION
# DO NOT CHANGE BELOW UNLESS YOU ARE MAKING BIG CHANGES TO THE CODE!! THX
##########################################################################################
# Copy atmos code directory into a new directory for this run so that models can run in parallel

# First check if a directory for this model already exists
# If it already exists, stop the script
if [ -d "${newdir}/${name}" ]; then
  echo "A directory for this model already exists. Please change 'name' for this model to avoid overwriting data."
  exit
fi

# Copy the skeleton model of parent_atmos (atmosdir) into atmos_runs (newdir) with "name" as defined earlier
cp -r ${atmosdir} ${newdir}/${name}  
# Copy this setup script into the new directory
cp ${scriptname} ${newdir}/${name}

# Move into new directory
cd ${newdir}/${name}
# Rename script that runs the model
mv run.sh run_$name.sh        

# Use 'star' to pick the appropriate PHOTOCHEM and CLIMA spectra (as determined by starkey.txt)
# Make sure starkey.txt is in top directory OR modify path below
# Star name for PHOTOCHEM
pstar=$(cat starkey.txt | grep -m1 $Star | awk '{print substr($2,1,2)}')
# Star name for CLIMA
STARR=$(cat starkey.txt | grep -m1 $Star | awk '{print substr($3,1,5)}')


# Copy blank template files into proper place
# Go into PHOTOCHEM input file directory
cd PHOTOCHEM/INPUTFILES
# Copy over blank template files
cp TEMPLATES/blanktemplate/input_photchem.dat .
cp TEMPLATES/blanktemplate/parameters.inc .
cp TEMPLATES/blanktemplate/PLANET.dat .
cp TEMPLATES/blanktemplate/species.dat .
cp TEMPLATES/blanktemplate/reactions.rx .
cp TEMPLATES/blanktemplate/in.dist ../

# Edit blank template files
# input_photchem.dat
perl -pi -e "s/AGLvar/$AGL/g" input_photchem.dat
perl -pi -e "s/ISEASONvar/$ISEASON/g" input_photchem.dat
perl -pi -e "s/IZYO2var/$IZYO2/g" input_photchem.dat
perl -pi -e "s/LGRIDvar/$LGRID/g" input_photchem.dat
perl -pi -e "s/IO2var/$IO2/g" input_photchem.dat
perl -pi -e "s/INOvar/$INO/g" input_photchem.dat
perl -pi -e "s/EPSJvar/$EPSJ/g" input_photchem.dat
perl -pi -e "s/PRONOvar/$PRONO/g" input_photchem.dat
perl -pi -e "s/FRAKvar/$FRAK/g" input_photchem.dat
perl -pi -e "s/HCDENSvar/$HCDENS/g" input_photchem.dat
perl -pi -e "s/IHZTYPEvar/$monsize/g" input_photchem.dat
perl -pi -e "s/ZYvar/$ZY/g" input_photchem.dat
perl -pi -e "s/USOLMINvar/$USOLMIN/g" input_photchem.dat
perl -pi -e "s/KIDAvar/$KIDA/g" input_photchem.dat

#echo "input_photchem.dat has been modifed."
echo "                   \       /            _\/_"

# parameters.inc
perl -pi -e "s/NZvar/$NZ/g" parameters.inc

#echo "parameters.inc has been modifed."
echo "                     .-'-.              //o\  _\/_"

# PLANET.dat
perl -pi -e "s/Gvar/$G/g" PLANET.dat
perl -pi -e "s/FSCALEvar/$FSCALE/g" PLANET.dat
perl -pi -e "s/ALBvar/$SRFALB/g" PLANET.dat
perl -pi -e "s/ZTROPvar/$ZTROP/g" PLANET.dat
perl -pi -e "s/FARvar/$FAR/g" PLANET.dat
perl -pi -e "s/R0var/$R0/g" PLANET.dat
perl -pi -e "s/P0var/$P0/g" PLANET.dat
perl -pi -e "s/PLANETvar/$PLANET/g" PLANET.dat
perl -pi -e "s/TIMEGAvar/$TIMEGA/g" PLANET.dat
perl -pi -e "s/IRESETvar/$IRESET/g" PLANET.dat
perl -pi -e "s/IHZSCALEvar/$IHZSCALE/g" PLANET.dat
perl -pi -e "s/UVSCALEvar/$uvscale/g" PLANET.dat
perl -pi -e "s/JTROPvar/$JTROP/g" PLANET.dat
perl -pi -e "s/DELZvar/$DELZ/g" PLANET.dat
perl -pi -e "s/PSTARvar/$pstar/g" PLANET.dat

#echo "PLANET.dat has been modifed."
echo "  _  ___  __  _ --_ /     \ _--_ __  __ _ | __/o\\ _"

# species.dat
perl -pi -e "s/O2LBvarr/$O2LB/g" species.dat
perl -pi -e "s/H2LBvar/$H2LB/g" species.dat
perl -pi -e "s/COLBvar/$COLB/g" species.dat
perl -pi -e "s/CH4LBvar/$CH4LB/g" species.dat
perl -pi -e "s/N2OLBvar/$N2OLB/g" species.dat
perl -pi -e "s/O2MRvarr/$O2MR/g" species.dat
perl -pi -e "s/H2MRvar/$H2MR/g" species.dat
perl -pi -e "s/COMRvar/$COMR/g" species.dat
perl -pi -e "s/CH4MRvar/$CH4MR/g" species.dat
perl -pi -e "s/N2OMRvar/$N2OMR/g" species.dat
perl -pi -e "s/CO2MRvar/$CO2MR/g" species.dat
perl -pi -e "s/N2MRvar/$N2MR/g" species.dat
perl -pi -e "s/O2SGvarr/$O2SG/g" species.dat
perl -pi -e "s/H2SGvar/$H2SG/g" species.dat
perl -pi -e "s/COSGvar/$COSG/g" species.dat
perl -pi -e "s/CH4SGvar/$CH4SG/g" species.dat
perl -pi -e "s/NOSGvar/$NOSG/g" species.dat
perl -pi -e "s/H2SSGvar/$H2SSG/g" species.dat
perl -pi -e "s/SO2SGvar/$SO2SG/g" species.dat
perl -pi -e "s/N2OSGvar/$N2OSG/g" species.dat
perl -pi -e "s/CO2SGvar/$CO2SG/g" species.dat

#echo "species.dat has been modifed."
echo "=-=-_=-=-_=-=_=-_= -=======- = =-=_=-=_,-'|'''-|-,_ "


# Modify in.dist
# Go into PHOTOCHEM
cd ..

# If you are only changing input mixing ratios
# Run Modifyindist.py (if you don't want to change something delete it from the command)
python Modifyindist.py -O2 $O2MR -O3 $O3MR -CH4 $CH4MR -C2H6 $C2H6MR -N2O $N2OMR -NO2 $NO2MR -H2 $H2MR

# If you want to change the input temperature profile
# Include the name/path to the new temperature profile txt file
# NOTE: text file should have one column (no labels) of new temperature profile matching
# up to the atmospheric layers in PHOTOCHEM (first element is the surface)
# python Modifyindist.py -O2 "0.10" -O3 "0.2" -CO2 "0.3" -Temp "TempIn_test.txt"

# If in.dist.new was created correctly, rename files for the code
if [ -f in.dist.new ]
then  
    mv in.dist in.dist.orig  
    mv in.dist.new in.dist
fi

# Go into CLIMA input file directory
cd ../CLIMA/IO
# These files get automatically updated by PHOTOCHEM if coupled
cp TEMPLATES/blanktemplate/coupling_params.out .
cp TEMPLATES/blanktemplate/fromClima2Photo.dat .
cp TEMPLATES/blanktemplate/fromPhoto2Clima.dat .
cp TEMPLATES/blanktemplate/hcaer.climaout.out .
cp TEMPLATES/blanktemplate/hcaer.photoout.out .
# Copy over blank template files to modify
cp TEMPLATES/blanktemplate/input_clima.dat .
cp TEMPLATES/blanktemplate/mixing_ratios.dat .

# Modify header.inc
perl -pi -e "s/NDvar/$ND/g" ../INCLUDE/header.inc

#echo "header.inc has been modifed."
echo " =- _=-=-_=- _=-= _--=====- _=-=_-_,-'         |"

# Edit blank template files
# input_clima.dat
perl -pi -e "s/NSTEPSvar/$NSTEPS/g" input_clima.dat
perl -pi -e "s/IMWvar/$IMW/g" input_clima.dat
perl -pi -e "s/RSURFvar/$RSURF/g" input_clima.dat
perl -pi -e "s/ZYvar/$ZY/g" input_clima.dat
perl -pi -e "s/DTAU0var/$DTAU0/g" input_clima.dat
perl -pi -e "s/ZCONvar/$ZCON/g" input_clima.dat
perl -pi -e "s/P0var/$PTOP/g" input_clima.dat
perl -pi -e "s/PGOvar/$P0/g" input_clima.dat
perl -pi -e "s/Gvar/$G/g" input_clima.dat
perl -pi -e "s/FACvar/$FAC/g" input_clima.dat
perl -pi -e "s/IO3var/$IO3/g" input_clima.dat
perl -pi -e "s/IUPvar/$IUP/g" input_clima.dat
perl -pi -e "s/TG0var/$TG0/g" input_clima.dat
perl -pi -e "s/TSTRATvar/$TSTRAT/g" input_clima.dat
perl -pi -e "s/STARRvar/$STARR/g" input_clima.dat
perl -pi -e "s/ICONSERVvar/$ICONSERV/g" input_clima.dat
perl -pi -e "s/SRFALBvar/$SRFALB/g" input_clima.dat
perl -pi -e "s/SOLCONvar/$FSCALE/g" input_clima.dat
perl -pi -e "s/DTMAXvar/$dtmax/g" input_clima.dat
perl -pi -e "s/CO2MAXvar/$CO2MAX/g" input_clima.dat
perl -pi -e "s/IMETvar/$IMET/g" input_clima.dat
perl -pi -e "s/IMETETHvar/$IMETETH/g" input_clima.dat
perl -pi -e "s/NGAvar/$nga/g" input_clima.dat
perl -pi -e "s/IHAZEvar/$IHAZE/g" input_clima.dat
perl -pi -e "s/MONSIZEvar/$monsize/g" input_clima.dat
perl -pi -e "s/ICEALBEDOvar/$icealbedo/g" input_clima.dat
perl -pi -e "s/INVERSEvar/$INVERSE/g" input_clima.dat
perl -pi -e "s/FRAKvar/$FRAK/g" input_clima.dat

#echo "input_clima.dat has been modifed."
echo "   =- =- =-= =- = -  -===- -= - .'"

# mixing_ratios.dat
perl -pi -e "s/ARMRvar/$ArMR/g" mixing_ratios.dat
perl -pi -e "s/CH4MRvar/$CH4MR/g" mixing_ratios.dat
perl -pi -e "s/C2H6MRvar/$C2H6MR/g" mixing_ratios.dat
perl -pi -e "s/CO2MRvar/$CO2MR/g" mixing_ratios.dat
perl -pi -e "s/N2MRvar/$N2MR/g" mixing_ratios.dat
perl -pi -e "s/O2MRvarr/$O2MR/g" mixing_ratios.dat
perl -pi -e "s/H2MRvar/$H2MR/g" mixing_ratios.dat
perl -pi -e "s/NO2MRvar/$NO2MR/g" mixing_ratios.dat
perl -pi -e "s/TROPLAYERvar/$TROPLAYER/g" mixing_ratios.dat

#echo "mixing_ratios.dat has been modifed."
echo " ~^~^~-~^~~^~-~^~~-~^~^~-~^~~^-~^~^~^-~^~^~^~^~~^~- "



echo "Done setting up input files for run."
echo "Star = ${Star}, runtype = ${runtype}, Seff = ${FSCALE}, O2 MR = ${O2MR}"
echo "*****************************************************"

##########################################################################################
# Running the model with run.sh                                                       
cd $newdir/$name                                            
perl -pi -e "s/runtypevar/$runtype/g" run_$name.sh             
perl -pi -e "s/namevar/$name/g" run_$name.sh                   
perl -pi -e "s/itervar/$iter/g" run_$name.sh                   
##########################################################################################
echo "Attempting to run..."


# Here the model is actually run with run_$name.sh with the new inputs
# The below text writes relevant info out into a log file (run_$name.log) located in the IO
# folder of the new directory for this model.
echo $1

if [ "$1" == "here" ]
	then (nohup ./run_$name.sh | tee IO/run_$name.log) 
	else (nohup ./run_$name.sh > IO/run_$name.log 2>IO/nohuperror_$name.log && \
    (echo "$name"; \
    (tail -n 1 IO/run_*.log | awk '{print substr($0,0,30)}'); \
    (tac IO/run_*.log | grep -m1 'Seff=..' 2>/dev/null | awk '{print "Seff="substr($0,9,7)}'); \
    (tac IO/run_*.log | grep -m1 'Surface temp..' 2>/dev/null | awk '{print "Temp="substr($0,25,6)}'); \
    (tac IO/run_*.log | grep -m1 'PLANETARY ALB..' 2>/dev/null | awk '{print "Albedo="substr($0,28,6)}'); \
    (tac IO/run_*.log | grep -m1 'running photo itera..' 2>/dev/null | awk '{print "Photo iter. "substr($0,25,10)}'); \
    (tac IO/run_*.log | grep -m1 'running clima itera..' 2>/dev/null | awk '{print "Clima iter. "substr($0,25,10)}'); \
    (tac IO/run_*.log | grep -m1 'TIME STEP =..' 2>/dev/null | awk '{print "LastStep="substr($0,31,5)}')) ) &
fi


# Have the script pause for 10 minutes after each run is started to avoid overloading
# the cluster. If doing more steps and the model takes longer this sleep time should be
# increased.
#sleep 10m

done

sleep 12h
















