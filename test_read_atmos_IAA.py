#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Written by Thea Kozakis (theakozakis@gmail.com)

"""
A test script to learn how to use the functions of read_atmos_IAA to plot 
the output of atmos-IAA atmospheric models.

This tutorial shows how to plot models as a group or indiviually.

The example files provided are for a planet orbiting the Sun with varying 
# levels of oxygen.

"""

# Import atmos-IAA and other packages
from read_atmos_IAA import *
import numpy as np
import matplotlib.pyplot as plt

# INSERT YOUR DATA DIRECTORY PATH HERE 
# - the directory containing the atmos-IAA output folders
datadir = '/Users/thkoz/Documents/Research_IAA/atmos-IAA/Python_read_atmos_test/Data/'


##########################################################################
# Group models together and check validity
##########################################################################
# This requires a text file containing the names of the directories containing
# each output file. 
# The provided example is 'Sun_O2.txt' (in the Data folder)

# Identify the file with the directory names
groupfile = 'Sun_O2.txt'

# Use create_group_table(datadir,groupfile)
create_group_table(datadir,groupfile)

# Output: If the models ran correctly  a file will be created called
# 'Sun_O2.txt_table.txt' in the Data directory and that each model
# name will be printed out as it is verified and added to the table

# If there are problems, either the directory path is incorrect, or the model
# did not run to completion


##########################################################################
# Test model convergence
##########################################################################

# You can check the convergence of multiple models at once with the function
# check_atmos_convergence(datadir,groupfile) using the groupfile that was 
# created in the previous step

check_atmos_convergence(datadir,groupfile)

# Output: For each model it will print the basic parameters (suface albedo, 
# etc) and also print any flags if convergence criteria are not reached. 
# If any flags are printed, there may be convergence issues


# An additional test for convergence is to plot the last few iterations of 
# each model for the water, ozone, and temperature profiles. If there is 
# Signficant variation in the last few steps, that means the model was not 
# converged

# Plotting is done with plot_frames(datadir,name,fi,ff), where name is the 
# indiviual model name, fi is the first frame iterationplotted, and ff is the  
# final iteration plotted. This is useful for testing individual models, but \
# we will plot all in the group here.

# If the model is well converged, ideally the last few frames will overlap 
# with the final iteration, which is always plotted in black

# For this example, we will plot iterations 25-30
fi = 25
ff = 30

# Loop through every model in the groupfile (Sun_O2.txt)
# Read in each name
name = np.loadtxt(datadir+groupfile,dtype=str)

# Read in each model 
for i in range(len(name)):
    # Plot the frames for the selected model
    plot_frames(datadir,name[i],fi,ff)
    
    
# Output: for the example models, you can see that the two lowest O2 mixing ratio models
# there were flags, but they look fairly normal when the individual frames are plotted.



########################################################################
# Plotting the models
########################################################################

# NOTE: all plots for the example data are located in the 'Plots' directory,
# so you can check against them



#######################
# Plotting with model groups
#######################

# To plot models as a group you need to read in the table created several
# steps ago with the function read_group_table(grouptable)
# By default these group tables are named as the original file name with all
# the model names with the suffix '_table.txt'

grouptable = datadir+groupfile+'_table.txt'

models = read_group_table(grouptable)

# The table is read in as a dictionary so to pick which parameters you wish
# to plot you must specify the keyword (type 'help(read_group_table)) to 
# see a list of all available parameters

# Plot example: ground oxygen mixing ratios (GO2MR) versus ozone column (O3COL)
plt.plot(models['GO2MR'],models['O3COL'])
plt.xscale('log')
plt.xlabel('O$_2$ mixing ratio')
plt.ylabel('Int. O$_3$ column density (cm$^{-2}$)')
plt.savefig(datadir+'../Plots/Sun_group_O2MR_v_O3COL.pdf')
plt.show()
plt.close()


# Plot example: ground oxygen mixing ratios (GO2MR) versus UVC flux reaching
# the planetary surface as a scatter plot
plt.scatter(models['GO2MR'],models['GUVC'],marker='o')
plt.yscale('log')
plt.xlabel('O$_2$ mixing ratio')
plt.ylabel('UVC surface flux (W/m$^2$)')
plt.savefig(datadir+'../Plots/Sun_group_O2MR_v_GUVC.pdf')
plt.show()
plt.close()

# Plot example: ground oxygen mixing ratios (GO2MR) versus UVC flux reaching
# the planetary surface as a scatter plot with ozone abundance represented by
# color
plt.scatter(models['GO2MR'],models['GUVC'],marker='o',c=models['O3COL'])
plt.yscale('log')
plt.xlabel('O$_2$ mixing ratio')
plt.ylabel('UVC surface flux (W/m$^2$)')
plt.colorbar(label='Int. O$_3$ column density (cm$^{-2}$)')
plt.savefig(datadir+'../Plots/Sun_group_O2MR_v_GUVC_O3COL.pdf')
plt.show()
plt.close()


#######################
# Plotting models individually
#######################

# Say we want to compare atmospheric profiles for O2 values of 100, 10, 1, and
# 1% the Present Atmospheric Level (PAL) of O2 (which is 0.21)

# Read in the photochemical mixing ratio profiles from photo_mixings_*.dat
# using the function read_photo_mixings(filename)

# Read in all other relevant atmospheric data from out.out using the function
# read_outout(filename)

# NOTE: use the help() function or read the descriptions of read_photo_mixings
# and read_outout for lists of the parameters that can be plotted with each


# 100% PAL O2 (0.21)
# Model name
n = '2-30-50-Sun-0.21O2'
# photo_mixings files are in the IO directory of each model
Sun100p = read_photo_mixings(datadir+n+'/IO/photo_mixings_'+n+'.tab')
# out.out is in the PHOTOCHEM_OUTPUT directory
Sun100o = read_outout(datadir+n+'/PHOTOCHEM_OUTPUT/out.out')

# 10% PAL O2 (0.021)
# Model name
n = '2-30-50-Sun-0.021O2'
Sun10p = read_photo_mixings(datadir+n+'/IO/photo_mixings_'+n+'.tab')
Sun10o = read_outout(datadir+n+'/PHOTOCHEM_OUTPUT/out.out')

# 1% PAL O2 (0.0021)
# Model name
n = '2-30-50-Sun-0.0021O2'
Sun1p = read_photo_mixings(datadir+n+'/IO/photo_mixings_'+n+'.tab')
Sun1o = read_outout(datadir+n+'/PHOTOCHEM_OUTPUT/out.out')

# 0.1% PAL O2 (0.00021)
# Model name
n = '2-30-50-Sun-0.00021O2'
Sun01p = read_photo_mixings(datadir+n+'/IO/photo_mixings_'+n+'.tab')
Sun01o = read_outout(datadir+n+'/PHOTOCHEM_OUTPUT/out.out')



# Colorblind friendly template
c100 = '#000000' #black
c10 = '#CCBB44'#yellow
c1 = '#EE6677'#red
c01 = '#AA3377'#purple

############
# Plotting profiles from photo_mixings.dat
############

# Plot example: O3 mixing ratio profiles plotting using atmospheric altitude
# Dividing the ALT keyword by 1e5 converts it to km
plt.plot(Sun100p['O3'],Sun100p['ALT']/1e5,color=c100,label='100% PAL O$_2$')
plt.plot(Sun10p['O3'],Sun10p['ALT']/1e5,color=c10,label='10% PAL O$_2$')
plt.plot(Sun1p['O3'],Sun1p['ALT']/1e5,color=c1,label='1% PAL O$_2$')
plt.plot(Sun01p['O3'],Sun01p['ALT']/1e5,color=c01,label='0.1% PAL O$_2$')
plt.xscale('log')
plt.xlabel('O$_2$ mixing ratio')
plt.ylabel ('Altitude (km)')
plt.legend(frameon=False)
#plt.savefig(datadir+'../Plots/Sun_O2MR_v_ALT.pdf')
plt.show()
plt.close()


# Plot example: H2O mixing ratio profiles plotting using atmospheric altitude
# Dividing the ALT keyword by 1e5 converts it to km
plt.plot(Sun100p['H2O'],Sun100p['ALT']/1e5,color=c100,label='100% PAL O$_2$')
plt.plot(Sun10p['H2O'],Sun10p['ALT']/1e5,color=c10,label='10% PAL O$_2$')
plt.plot(Sun1p['H2O'],Sun1p['ALT']/1e5,color=c1,label='1% PAL O$_2$')
plt.plot(Sun01p['H2O'],Sun01p['ALT']/1e5,color=c01,label='0.1% PAL O$_2$')
plt.xscale('log')
plt.xlabel('H$_2$O mixing ratio')
plt.ylabel ('Altitude (km)')
plt.legend(frameon=False)
plt.savefig(datadir+'../Plots/Sun_H2OMR_v_ALT.pdf')
plt.show()
plt.close()


# Plot example: Temperature profiles plotting using atmospheric altitude
# Dividing the ALT keyword by 1e5 converts it to km
plt.plot(Sun100p['TEMP'],Sun100p['ALT']/1e5,color=c100,label='100% PAL O$_2$')
plt.plot(Sun10p['TEMP'],Sun10p['ALT']/1e5,color=c10,label='10% PAL O$_2$')
plt.plot(Sun1p['TEMP'],Sun1p['ALT']/1e5,color=c1,label='1% PAL O$_2$')
plt.plot(Sun01p['TEMP'],Sun01p['ALT']/1e5,color=c01,label='0.1% PAL O$_2$')
plt.xlabel('Temperature (K)')
plt.ylabel ('Altitude (km)')
plt.legend(frameon=False)
plt.savefig(datadir+'../Plots/Sun_TEMP_v_ALT.pdf')
plt.show()
plt.close()


############
# Plotting data from out.out
############

# Example plot: plotting both the flux arriving at the top of the atmosphere
# (which is the same for all models) and the amount of flux reaching the 
# surface of the planet. This is most interesting in UV wavelengths, so we
# restrict the range there

# Top of atmosphere (TOA) flux (EFLUX)
plt.plot(Sun100o['WAV'],Sun100o['EFLUX'],color='grey',linestyle='dashed',label='TOA flux')
# Surface fluxes (GFLUX)
plt.plot(Sun100o['WAV'],Sun100o['GFLUX'],color=c100,label='100% PAL O$_2$')
plt.plot(Sun10o['WAV'],Sun10o['GFLUX'],color=c10,label='10% PAL O$_2$')
plt.plot(Sun1o['WAV'],Sun1o['GFLUX'],color=c1,label='1% PAL O$_2$')
plt.plot(Sun01o['WAV'],Sun01o['GFLUX'],color=c01,label='0.1% PAL O$_2$')
plt.yscale('log')
plt.xlim([1900,3500])
plt.ylim([1e-30,1])
plt.xlabel('Wavelength (angstroms)')
plt.ylabel ('Ground flux (W/m/m)')
plt.legend(frameon=False)
plt.savefig(datadir+'../Plots/Sun_WAV_v_GFLUX.pdf')
plt.show()
plt.close()

# Plot example: photolysis rate profiles of Reaction 23 (listed in out.out)
#  O2  +  HV ->   O  +  O(1D)  (a very important ozone reaction)
plt.plot(Sun100o['PO2_O1D'],Sun100o['PZ']/1e5,color=c100,label='100% PAL O$_2$')
plt.plot(Sun10o['PO2_O1D'],Sun10o['PZ']/1e5,color=c10,label='10% PAL O$_2$')
plt.plot(Sun1o['PO2_O1D'],Sun1o['PZ']/1e5,color=c1,label='1% PAL O$_2$')
plt.plot(Sun01o['PO2_O1D'],Sun01o['PZ']/1e5,color=c01,label='0.1% PAL O$_2$')
plt.xscale('log')
#plt.xlim([1900,3500])
#plt.ylim([1e-30,1])
plt.xlabel('Rate of O$_2$ + hv --> O + O($^1$D) [/s]')
plt.ylabel ('Altitude (km)')
plt.legend(frameon=False)
plt.savefig(datadir+'../Plots/Sun_PO2_O1D_v_ALT.pdf')
plt.show()
plt.close()





















