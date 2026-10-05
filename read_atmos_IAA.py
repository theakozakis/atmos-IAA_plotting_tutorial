#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Written by Thea Kozakis (theakozakis@gmail.com)

"""
A set of functions that read in atmos-IAA FORTRAN output files and load relevant data
into dictionaries to enable easy analysis and data visualization.

Code requirements: Python 3.0+, numpy, matplotlib.pyplot

Currently contains the following functions:

    fixE:
    	"Cleans" and reformats FORTRAN output to readable numerical values
    	
    read_photo_mixings:
    	Reads photo_mixing.tab output files containing chemical profiles and loads them
    	into a dictionary for easy plotting.
    	
    read_outout:
    	Reads out.out, which contains many different outputs from the photochemistry code.
    	
    create_group_table:
    	Takes a list of models and creates a table containing key outputs from the climate
    	and photochemistry codes in order to facilitate plotting similar models. 
    
    read_group_table:
    	Reads the model tables created by create_group_table and converts them into 
    	dictionaries that are easily plot-able.
    	
    check_atmos_convergence:
    	Checks multiple convergence criteria for each atmospheric model and flags where
    	convergence has not been reached.
    	
    plot_frames:
    	Plots a given number of iterations of temperature, ozone, and water profiles in 
    	order to allow the user to visually assess the quality of the model convergence.
    	
    	
All of these functions have highly detailed docstrings, so you can pull up the 
instructions easily for each with help().
    
"""

# Define function to fix values with missing 'E's introduced by FORTRAN
# If an exponent has more than 2 digits it will erase the E and make numbers unreadable
def fixE(line):
    """
    Function that checks a row of FORTRAN numerical values written in scientific
    notation for missing Es (from exponents) and corrects them if necessary. 
    This happens whenever an exponent is more than 2 digits.
    
    This function should be run on ALL lines of numerical output before they can be used
    in any sort of calculations or data visualization.

    Parameters
    ----------
    line : str
        A single row of numerical values read in from a FORTRAN file in 
        scientific notation.

    Returns
    -------
    newline : str
        The same row as the input but missing Es corrected (if need be).

    """
 
    # Split the line
    val = line.split()
    
    # Define list for new corrected line
    newline = []
    
    # Check if there's an E for each element
    for i in range(len(val)):
        
        # Correct value if E is not found
        if val[i].find('E') == -1:
                
            # If it is a positive exponent replace + with E+   
            if val[i].find('+') != -1:
                val[i] = val[i].replace('+','E+')
                
            # If it is a negative exponent replace - with E-
            if val[i].find('-') != -1:
                if val[i][0] == '-':
                    # in case of negative numbers, make sure first character is 
                    # not replaced
                    val[i] = '-' + val[i][1:].replace('-','E-')
                else:
                    val[i] = val[i].replace('-','E-')
        
        # Append original/correct value
        newline.append(val[i])
                
    # Recombine the line after it has been corrected putting spaces back in
    return '   '.join(newline)



def read_photo_mixings(fn):
    """
    Function to extract data from photo_mixings output files from atmos-IAA and 
    read them into a dictionary.
    
    File is in the IO/ directory for each model.
    
    Parameters read into the dictionary are:
        PRESS - pressure at each layer [bars]
        TEMP  - temperature at each layer [K]
        ALT   - altitude at each layer [cm]
        Mixing ratios of these species:
            O, O2, H2O, H, OH, HO2, H2O2, H2, CO, HCO, H2CO, 
            CH4, CH3, C2H6, NO, NO2, HNO, H2S, HS, S, SO, SO2, 
            H2SO4, HSO, S2, S4, S8, SO3, OCS, S3, O3, HNO3, N, 
            NO3, N2O, HO2NO2, N2O5, CO2, SO4AER, S8AER
        

    Parameters
    ----------
    fn : string
        Name of photo_mixings file to be read in.

    
    Returns
    -------
    profiles : dict
        Dictionary contains atmospheric profiles of each key (defined above).

    """

    import numpy as np
    
    # Read in file
    # Read in the out.out file
    fo = open(str(fn),'r')
    # Read each line
    rows = fo.readlines()
    
    fo.close()
    
    # Create data matrix to store values
    row = 200
    col = 43
    f = np.zeros((row,col))
    
    # Loop through each row (skip header)
    for i in range(1,row+1):
    
        # First needs to correct for problem with missing Es when exponent is 
        # more than 2 digits (this is why it's not initially read in as floats)
        # Read row into function to correct for this
        fixedrow = fixE(rows[i])
        
        # Split row
        nrow = fixedrow.split()
        
        # Convert strings to floats
        nrow = [float(j) for j in nrow]
        
        # Load corrected row into PData
        f[i-1,:col] = nrow
    
    
    # Create dictionary and assign the correct array to each key
    profiles = dict(
        PRESS = f[:,0],  TEMP =     f[:,1],  ALT =      f[:,2],  O =    f[:,3], 
        O2 =    f[:,4],  H2O =      f[:,5],  H =        f[:,6],  OH =   f[:,7],
        HO2 =   f[:,8],  H2O2 =     f[:,9],  H2 =       f[:,10], CO =   f[:,11],
        HCO =   f[:,12], H2CO =     f[:,13], CH4 =      f[:,14], CH3 =  f[:,15],
        C2H6 =  f[:,16], NO =       f[:,17], NO2 =      f[:,18], HNO =  f[:,19],
        H2S =   f[:,20], HS =       f[:,21], S =        f[:,22], SO =   f[:,23],
        SO2 =   f[:,24], H2SO4 =    f[:,25], HSO =      f[:,26], S2 =   f[:,27],
        S4 =    f[:,28], S8 =       f[:,29], SO3 =      f[:,30], OCS =  f[:,31],
        S3 =    f[:,32], O3 =       f[:,33], HNO3 =     f[:,34], N =    f[:,35],
        NO3 =   f[:,36], N2O =      f[:,37], HO2NO2 =   f[:,38], N2O5 = f[:,39],
        CO2 =   f[:,40], SO4AER =   f[:,41], S8AER =    f[:,42],
        )

    
    

    return profiles


def read_outout(fn):
    """
    Function that extracts data from out.out, an output file from the
    photochemistry code in atmos-IAA, and reads them into a dictionary.
    
    Also, yes, this code is a mess, but so is out.out. I tried to find a 
    balance between making this code flexible enough to adapt to any changes in 
    out.out, while assuming a certain level of uniformity in format among different
    out.out files. Basically, the goal is that with this function that no human ever
    has to manually pull values from out.out again, because that is a terrible experience
    that is not easily reproducible. 
    
    Parameters read into the dictionary are:
        
        RLIST   - list of all 239 reactions used in this code as strings
        INTRATE - list of the integrated reaction rates for all 239 reactions
                as floats
                
        TIMEY   - length (in years) of the last time step
                
        Energy fluxes at different wavelengths for TOA and surface
        WAV     - list of wavelengths (angstroms)
        EFLUX   - list of TOA fluxes (W/m/m)
        GFLUX   - glist of ground fluxes (W/m/m)
        
        Column depths
        O3COL   - ozone column depth
        O2COL   - O2 column depth
        COCOL   - CO column depth
        CH4COL  - CH4 column depth
        
        Altitude dependent photolysis rates
        PZ     - list of altitudes (cm) corresponding to the photolysis rates
        Photolysis rates of the following reactions (each one has a 'P' preffix):
            PO2_O1D, PO2_O3, P, PH2O_1, PH2O_2, PH2O_3, PO3_O1D, PO3_O, PO3_3O
            PH2O2, PCO2_1, PCO2_2, PH2CO_1, PH2CO_2, PHO2, PCH4_1, PCH4_2
            PCH4_3, PC2H6_1, PC2H6_2, PHNO2_1, PHNO3, PHNO3_3, PHNO3_1, PNO
            PNO2_O1D, PNO2, PCH3_1, PSO, PH2S, PSO2, PSO2_SO21, PSO2_SO23
            PS2, PS4, PS3, PS8L, PS8R, PS8, PSO3, PHSO
            POCS, PNO3_NO, PNO3_NO2, PN2O, PHO2NO2_NO2, PHO2NO2_NO3, PN2O5_NO2, PN2O5_NO
            
        Altitude dependent number densities
        Z_ND    - list of altitudes (cm) corresponding to each number density
        Number densities of the follow species (each has a _ND suffix):
            O_ND, O2_ND, H2O_ND, H_ND, OH_ND, HO2_ND, H2O2_ND, H2_ND, CO_ND, 
            HCO_ND, H2CO_ND, CH4_ND, CH3_ND, C2H6_ND, NO_ND, NO2_ND, HNO_ND, 
            H2S_ND, HS_ND, S_ND, SO_ND, SO2_ND, H2SO4_ND, HSO_ND, S2_ND, S4_ND, 
            S8_ND, SO3_ND, OCS_ND, S3_ND, O3_ND, HNO3_ND, N_ND, NO3_ND, N2O_ND, 
            HO2NO2_ND, N2O5_ND, CO2_ND, SO4AER_ND, S8AER_ND
        
        Altitude dependent fluxes of long-lived species
        Z_FL    - list of altitudes (cm) corresponding to each flux value
        Fluxes of the following species (each has a _FL suffix):
            O_FL, O2_FL, H2O_FL, H_FL, OH_FL, HO2_FL, H2O2_FL, H2_FL, CO_FL, 
            HCO_FL, H2CO_FL, CH4_FL, CH3_FL, C2H6_FL, NO_FL, NO2_FL, HNO_FL, 
            H2S_FL, HS_FL, S_FL, SO_FL, SO2_FL, H2SO4_FL, HSO_FL, S2_FL, S4_FL, 
            S8_FL, SO3_FL, OCS_FL, S3_FL, O3_FL, HNO3_FL, N_FL, NO3_FL, N2O_FL, 
            HO2NO2_FL, N2O5_FL, CO2_FL, SO4AER_FL, S8AER_FL
        
            
    Parameters
    ----------
    fn : string
        The path to the out.out file to be read in.
        

    Returns
    -------
    outout : dictionary
        A dictionary containing the out.out data for all the keys listed 
        above. It's a lot of stuff. That was a lot, Robin.

    """ 
    import numpy as np
    
    # Create the dictionary to hold everything
    outout ={}
    
    # Read in the out.out file
    f = open(str(fn),'r')
    # Read each line
    rows = f.readlines()
    
    f.close()

    ##########################################################################
    # List of reactions - RLIST
    ##########################################################################
    # Save the text of the reactions
    # This version of the code has 239 reactions
    rnamelist = []
    for i in range(239):
        rnamelist.append(rows[i][:-2]) # Remove '\n' at the end
           
    # Add reaction list to dictionary
    outout['RLIST'] = rnamelist
    
    
    ##########################################################################
    # Note about searching out.out for text:
    # To locate different parts of the code it searches for list labels
    # Since we want the final data, the search starts at the end of the file
    # and looks through the rows in reverse, saving the index when it is found
    ##########################################################################
    
    
    
    
    ##########################################################################
    # Integrated reaction rates
    ##########################################################################
    for i in range(len(rows)-1,0,-1):
        if rows[i].find('INTEGRATED REACTION RATES') != -1:
            INTRATEind = i
            break
                
    # Start of final reaction rates will be INTRATEind and then four rows down
    rst = INTRATEind+3
    
    # The integrated reaction rates are stored in a grid of 239 integers
    # (one for each reaction) with 10 columns and 24 rows
    
    # Read in integrated reaction rates
    rlist = [] # list to store all the rates for comparison
    for i in range(rst,rst+24):

        # If there is a negative sign you have to put a space in front of it or
        # else it combines 2 rates and breaks stuff
        rows[i] = rows[i].replace('-',' -')
        
        # If it's an exponent, take the space away again
        rows[i] = rows[i].replace('E ','E')
        col = rows[i].split()

        # For the first 23 rows:
        # The first and last elements are just labels, don't append them
        if i < rst+23:
            for k in range(1,len(col)-1):
                rlist.append(float(col[k]))

        # For the last row only the first element is a label
        if i == rst+23:
            for k in range(1,len(col)):
                rlist.append(float(col[k]))
                
    
    # Add the list of integrated reaction rates to the dictionary
    outout['INTRATE'] = rlist
    
    
    
    
    
    ##########################################################################
    # Length of time photochemistry code ran - TIMEY
    ##########################################################################
    for i in range(len(rows)-1,0,-1):
        if rows[i].find('TIMEY') != -1:
            TIMEYind = i
            break
    
    # Split the row where TIMEY is found
    tline = rows[TIMEYind].split()
    
    # Time (in years) that the code ran will be the second to last element
    ty = float(tline[-2])
    
    # Add to dictionary
    outout['TIMEY'] = ty
        
    
    
    
    ##########################################################################
    # Energy fluxes for each wavelength at the top and bottom of atmosphere
    # WAV, EFLUX, GFLUX
    ##########################################################################   
    for i in range(len(rows)-1,0,-1):
        if rows[i].find('ENERGY FLUXES IN W/m2/nm (NOT DIURNALLY AVERAGED)') != -1:
            EFLUXind = i
            break
        
    # Create the flux lists that we want
    # Column 1: wavelength in angstroms
    wav = []
    # Column 3: Energy that reaches the top of the atmosphere (W/m^2)
    eflux = []
    # Column 4: Energy that reaches the surface of the planet (W/m^2)
    gflux = []
    # Data starts 3 rows down from identifier and will have 750 rows
    efs = EFLUXind+3
    
    # Loop through all the flux data
    for i in range(efs,efs+750):
        # Split each row into the elements of each column
        col = rows[i].split()
        
        # If one of the fluxes is negative, it needs to be corrected or else
        # the values merge together
        # If there are not 6 elements in the list, correct it
        # Yes this is silly but I'm TIRED is this was my idea
        if len(col) != 6:
            # Manually assign the different elements of col based off how 
            # many spaces each value has
            col0 = rows[i][0:4]
            col1 = rows[i][4:11]
            col2 = rows[i][11:22]
            col3 = rows[i][22:32]
            col4 = rows[i][32:42]
            col5 = rows[i][42:52]
            
            # Put the correct values into the list
            col = [col0,col1,col2,col3,col4,col5]
            
        

        # Append wavelength
        wav.append(float(col[1]))

        # Append each column value to the proper list
        # If exponent is greater than 100, there will not be an 'E', so this 
        # part corrects for that
        # Fine if there is an E, just append things normally
        if col[3].find('E') >0:
            eflux.append(float(col[3]))
        if col[4].find('E') > 0:
            gflux.append(float(col[4]))
            
        # If there is no 'E', put it in 
        if col[3].find('E') == -1:
            if col[3].find('-'):
                col[3] = col[3].replace('-', 'E-')
            if col[3].find('+'):
                col[3] = col[3].replace('+', 'E+')
            eflux.append(float(col[3]))
        if col[4].find('E') == -1:
            if col[4].find('-') > 0:
                col[4] = col[4].replace('-', 'E-')
            if col[4].find('+') > 0:
                col[4] = col[4].replace('+', 'E+')
            gflux.append(float(col[4]))
            
    # Add lists to the dictionary
    outout['WAV'] = wav
    outout['EFLUX'] = eflux
    outout['GFLUX'] = gflux
    
    
    
    
    ##########################################################################
    ## Ozone column depth - O3COL
    ##########################################################################
    for i in range(len(rows)-1,0,-1):
        if rows[i].find('OZONE COLUMN DEPTH') != -1:
            O3COLind = i
            break
        
    # Split the row that has the column depth
    col = rows[O3COLind].split()

    # O3 column depth will be the last element of that row
    O3COL = float(col[-1])
    
    # Add to dictionary
    outout['O3COL'] = O3COL
    
    
    
    ##########################################################################
    ## O2, CO, and CH4 column depths - O2COL, COCOL, CH4COL
    ##########################################################################
    for i in range(len(rows)-1,0,-1):
        if rows[i].find('O2, CO, CH4 COLUMN DEPTHs') != -1:
            COLSind = i
            break
    
    # Extract O2, CO, and CH4 column depths
    col = rows[COLSind].split()

    # O2 column depth is the 6th element
    O2COL = float(col[6])
    # CO column depth is the 7th element
    COCOL = float(col[7])
    # CH4 column depth is the 8th element
    CH4COL = float(col[8])
    
    # Add values to dictionary
    outout['O2COL'] = O2COL 
    outout['COCOL'] = COCOL
    outout['CH4COL'] = CH4COL
    
    
    
    ##########################################################################
    ## Altitude dependent photolysis rates - PZ and many reactions
    ##########################################################################
    # There are multiple sets of photolysis rates, need to search for the 
    # beginning of each one
    
    # List for indices
    Pind = []
    
    # Find starting index of each set    
    # First set PO2_O1D 
    for i in range(len(rows)-1,0,-1):
        if rows[i].find('PO2_O1D') != -1:
            Pind.append(i)
            break
      
    # Second set PH2O2
    for i in range(len(rows)-1,0,-1):
        if rows[i].find('PH2O2') != -1:
            Pind.append(i)
            break
    
    # Third set PCH4_3
    for i in range(len(rows)-1,0,-1):
        if rows[i].find('PCH4_3') != -1:
            Pind.append(i)
            break
     
    # Fourth set PNO2_O1D
    for i in range(len(rows)-1,0,-1):
        if rows[i].find('PNO2_O1D') != -1:
            Pind.append(i)
            break
    
    # Fifth set PS2
    for i in range(len(rows)-1,0,-1):
        if rows[i].find('PS2') != -1:
            Pind.append(i)
            break
    
    # Sixth set POCS
    for i in range(len(rows)-1,0,-1):
        if rows[i].find('POCS') != -1:
            Pind.append(i)
            break
        
    # Find number of rows for each set
    prows = Pind[1]-Pind[0]-2
    
    # Cycle through each set of values
    for k in range(len(Pind)):
        # Set starting index
        ind = Pind[k]
        
        # The 0th row has strings of the all the species names
        # Sometimes the reaction names are long enough that the names blend
        # together, so to avoid problems put a space in front of each reaction
        # (every label starts with a P)
        rownames = rows[ind].replace('P',' P')
        names = rownames.split()
        
        # Each set currently 9 columns
        cols = 9
        
        # Create matrix to hold data for this set of rates
        PData = np.zeros((prows,cols))
        
        # Read in each row
        for i in range(ind+1,ind+prows+1):
            
            # Split row
            row = rows[i].split()
            
            # Check if there is a missing 'E' for each element, fix if not
            nrow = []
            for j in range(len(row)):
                
                # Fix E problem, convert to float, add to new row list
                nval = float(fixE(row[j]))
                nrow.append(nval)
                
            # Load corrected row into PData
            PData[i-(ind+1),:cols] = nrow
            
        # For each column read in the profile name and data
        # Only read in the first column (altitude) for the first set
        if k == 0:
            
            # Add altitude data (shared by all sets) to dictionary
            outout['PZ'] = PData[:,0]

            
        # Go through the rest of the columns
        for c in range(1,cols):

            # Extract both name of species and data
            outout[names[c]] = PData[:,c]
            
    
    ##########################################################################
    ## Altitude dependent number densities for long-lived species
    ##########################################################################
    # Find section with number densities
    for i in range(len(rows)-1,0,-1):
        if rows[i].find('NUMBER DENSITIES OF LONG-LIVED SPECIES') != -1:
            NDind = i
            break
   
    # There are 3 sets of profiles after that label, so find the next 3 times
    # a line has a 'Z' to find their indices
    zcont = 0
    NDindlist = []
    for i in range(NDind,len(rows)-1):
        if rows[i].find('Z') != -1:
            NDindlist.append(i)
            zcont = zcont + 1
            
            # Stop the loop when the next 3 rows with a 'Z' are found
            if zcont == 3:
                break

    # Find the number of rows each set has
    ndrows = NDindlist[1]-NDindlist[0]-2
    
    # Cycle through each set of values
    for k in range(len(NDindlist)):
        # Set starting index
        ind = NDindlist[k]
        
        # The 0th row has strings of the all the species names
        names = rows[ind].split()
        
        # The first 2 sets have 19 columns, the third has 5
        if k == 2:
            cols = 5 
        else:
            cols = 19


        # Create matrix to hold data for this set of rates
        NDData = np.zeros((ndrows,cols))
        
        # Read in each row
        for i in range(ind+1,ind+ndrows+1):
            
            # Split row
            row = rows[i].split()
            
            # Check if there is a missing 'E' for each element, fix if not
            nrow = []
            for j in range(len(row)):
                
                # Fix E problem, convert to float, add to new row list
                nval = float(fixE(row[j]))
                nrow.append(nval)
                
            # Load corrected row into NDData
            NDData[i-(ind+1),:cols] = nrow
            
        # For each column read in the profile name and data
        # Only read in the first column (altitude) for the first set
        if k == 0:
            
            # Add altitude data (shared by all sets) to dictionary
            outout['Z_ND'] = NDData[:,0]

            
        # Go through the rest of the columns
        for c in range(1,cols):

            # Extract both name of species and data (name = species + ND)
            outout[names[c]+'_ND'] = NDData[:,c]
    
    
    
    
    ##########################################################################
    ## Altitude dependent fluxes of long-lived species
    ##########################################################################
    # This section is formatted the same as the number densities
    # Find section with number densities
    for i in range(len(rows)-1,0,-1):
        if rows[i].find('FLUXES OF LONG-LIVED SPECIES') != -1:
            Find = i
            break
   
    # There are 3 sets of profiles after that label, so find the next 3 times
    # a line has a 'Z' to find their indices
    zcont = 0
    Findlist = []
    for i in range(Find,len(rows)-1):
        if rows[i].find('Z') != -1:
            Findlist.append(i)
            zcont = zcont + 1
            
            # Stop the loop when the next 3 rows with a 'Z' are found
            if zcont == 3:
                break

    # Find the number of rows each set has
    frows = Findlist[1]-Findlist[0]-2
    
    # Cycle through each set of values
    for k in range(len(Findlist)):
        # Set starting index
        ind = Findlist[k]
        
        # The 0th row has strings of the all the species names
        names = rows[ind].split()
        
        # The first 2 sets have 19 columns, the third has 5
        if k == 2:
            cols = 5 
        else:
            cols = 19


        # Create matrix to hold data for this set of rates
        FData = np.zeros((frows,cols))
        
        # Read in each row
        for i in range(ind+1,ind+frows+1):
            
            # Split row
            row = rows[i].split()
            
            # Check if there is a missing 'E' for each element, fix if not
            nrow = []
            for j in range(len(row)):
                
                # Fix E problem, convert to float, add to new row list
                nval = float(fixE(row[j]))
                nrow.append(nval)
                
            # Load corrected row into NDData
            FData[i-(ind+1),:cols] = nrow
            
        # For each column read in the profile name and data
        # Only read in the first column (altitude) for the first set
        if k == 0:
            
            # Add altitude data (shared by all sets) to dictionary
            outout['Z_FL'] = FData[:,0]

            
        # Go through the rest of the columns
        for c in range(1,cols):

            # Extract both name of species and data (name = species + ND)
            outout[names[c]+'_FL'] = FData[:,c]
        
 
    
    
    
    
    return outout






def create_group_table(datadir,groupfile):
    """
    Function that reads in a text file with the names of atmos-IAA output
    directories and reads in their out.out and photo_mixing files and outputs 
    a single table with multiple useful values. This table can then be easily
    read in with read_group_table for plotting purposes. The output file has 
    the same name as the input file but with _table.txt as a suffix.
    
    NOTE: connected plotting routines often assume that the order of the file
    names is organized by O2 MR, so it is helpful to order your files in that 
    way from most O2 to least.

    Parameters
    ----------
    datdir : String
        Location of models.
    groupfile : String
        Name of text file with model names.

    Returns
    -------
    Writes output file: datadir/namefile_table.txt
    
    Columns in output file (labeled in header):
        0  O2 ground MR
        1  O3 col (cm^-2)
        2  O2 col (cm^-2) 	 
        3  TOA UVA (W/m^2)
        4  Surf UVA (W/m^2)
        5  TOA UVB (W/m^2)
        6  Surf UVB (W/m^2)
        7  TOA UVC (W/m^2)
        8  Surf UVC (W/m^2)
        9  O2 SGFLUX (PU)
        10 CH4 SGFLUX (PU)
        11 CH4 col (cm^-2)
        12 CH4 ground MR
        13 TIMEY (time of last time step)
        14 Surface temperature (K)

    """
    
    # Read in model names from text file
    f = open(datadir+groupfile)
    rows = f.readlines()
    f.close()
    
    # Create text file for output
    fo = open(datadir+groupfile+'_table.txt','w')
    
    # Print header of output file
    fo.write('# O2 MR (ground) \t O3 col (cm^-2) \t O2 col (cm^-2) \t TOA \
             UVA (W/m2) \t Surf UVA \t TOA UVB (W/m2) \t Surf UVB \t TOA UVC \
                 (W/m2) \t Surf UVC \t O2 SGFLUX \t CH4 SGFLUX \t CH4 col \
                     (cm^-2) \t CH4 MR (ground) \t TIMEY \t Surf. Temp \n')
    
    # Loop through each model
    for i in range(len(rows)):
        
        # Remove \n if present
        row = str(rows[i].split('\n')[0])
        print(row)
        
        # Extract info using read_outout
        oo = read_outout(datadir+row+'/PHOTOCHEM_OUTPUT/out.out')
    
        # TOA/ground flux lists
        wav = oo['WAV'] # Wavelength in angstroms
        eflux = oo['EFLUX']
        gflux = oo['GFLUX']
        
        # UVC: 121-280 nm; elements 0-490
        # UVB: 280-315 nm; elements 491-533
        # UVA: 315-400 nm; elements 534-600
        # Set ranges
        UVCi = 0
        UVBi = 491
        UVAi = 534
        UVAf = 600        
        
        # Calculate integrated UVC flux
        uvce = [] # Top of atmosphere
        uvcg = [] # Ground
        for i in range(UVCi,UVBi):
                uvce.append(eflux[i]*(wav[i+1]-wav[i])/10.)
                uvcg.append(gflux[i]*(wav[i+1]-wav[i])/10.)     
        # Sum the amounts
        uvces = sum(uvce)
        uvcgs = sum(uvcg)

        # Calculate integrated UVB flux
        uvbe = [] # Top of atmosphere
        uvbg = [] # Ground
        for i in range(UVBi,UVAi):
                uvbe.append(eflux[i]*(wav[i+1]-wav[i])/10.)
                uvbg.append(gflux[i]*(wav[i+1]-wav[i])/10.)     
        # Sum the amounts
        uvbes = sum(uvbe)
        uvbgs = sum(uvbg)
        
        
        # Calculate integrated UVA flux
        uvae = [] # Top of atmosphere
        uvag = [] # Ground
        for i in range(UVAi,UVAf):
                uvae.append(eflux[i]*(wav[i+1]-wav[i])/10.)
                uvag.append(gflux[i]*(wav[i+1]-wav[i])/10.)     
        # Sum the amounts
        uvaes = sum(uvae)
        uvags = sum(uvag)
        
        
        # Extract other data for output file
        # O3 column depth
        O3col = oo['O3COL']
        # O2 column depth
        O2col = oo['O2COL']
        # CH4 column depth
        CH4col = oo['CH4COL']
        
        # O2 ground flux
        O2sg = oo['O2_FL'][0]
        # CH4 ground flux
        CH4sg = oo['CH4_FL'][0]
        
        
        # Time code ran (for convergence criteria)
        ty = oo['TIMEY']
        
        # From photomixings
        pm = read_photo_mixings(datadir+row+'/IO/photo_mixings_'+row+'.tab')
        # O2 ground MR
        O2MR = pm['O2'][0]

        # CH4 ground MR
        CH4MR = pm['CH4'][0]
        
        # Surface temperature
        Temp = pm['TEMP'][0]
        
        # Write everything to output file
        fo.write(str(O2MR)+'\t'+str(O3col)+'\t'+str(O2col)+'\t'+str(uvaes)+ \
                 '\t'+str(uvags)+'\t'+str(uvbes)+'\t'+str(uvbgs)+'\t'+ \
                 str(uvces)+'\t'+str(uvcgs)+'\t'+str(O2sg)+'\t'+str(CH4sg)+ \
                     '\t'+str(CH4col)+'\t'+str(CH4MR)+'\t'+str(ty)+ \
                         '\t'+str(Temp)+'\n')
        
    
    fo.close()
    


def read_group_table(grouptable):
    """
    Function that reads in a group table created by create_group_table and 
    reads parameters into a dictionary to enable easy plotting.
    
    Here are the parameters in the output dictionary:
        GO2MR - O2 ground mixing ratio
        GCH4MR - CH4 ground mixing ratio
        
        O3COL - O3 column depth (cm^-2)
        O2COL  - O2 column depth 
        CH4COL - CH4 column depth
        
        TUVA  - TOA integrated UVA flux (W/m^2)
        GUVA  - Ground integrated UVA flux (W/m^2)
        
        TUVB  - TOA integrated UVB flux (W/m^2)
        GUVB  - Ground integrated UVB flux (W/m^2)
        
        TUVC  - TOA integrated UVC flux (W/m^2)
        GUVC  - Ground integrated UVC flux (W/m^2)
        
        GO2SG - O2 surface flux (PU)
        GCH4SG - CH4 surface flux (PU)
        
        TIMEY - length of last time step (Gyr)
        
        TEMP - surface temperature of planet (K)
        

    Parameters
    ----------
    grouptable : str
        Name and location of group table created by create_group_table.

    Returns
    -------
    groupdict : dictionary
        Dictionary of all the parameters from the group table, described above.

    """
    
    import numpy as np

    # Read in group table (skipping header)
    f = np.loadtxt(grouptable)
    
    # Read table into dictionary
    grouptable = dict(
        GO2MR = f[:,0],     O3COL = f[:,1], O2COL = f[:,2],     TUVA = f[:,3],  
        GUVA = f[:,4],      TUVB = f[:,5],  GUVB = f[:,6],      TUVC = f[:,7],  
        GUVC = f[:,8],      GO2SG = f[:,9], GCH4SG = f[:,10],   CH4COL = f[:,11],
        GCH4MR = f[:,12],   TIMEY = f[:,13], TEMP = f[:,14]
        )


    return grouptable



def check_atmos_convergence(datadir,groupfile):
    """
    This code is meant to check certain parameters to see if there are any red
    flags for atmos-IAA convergence. Please keep in mind that these are just 
    flags and there may still be problems even if they are okay!!
    
    Right now it is programed to read in a list of names from a text file.
    
    If a value is out the 'acceptable limit' it will be printed out with a 
    warning. If nothing is printed, everything checked was okay.
    
    Photochemistry code convergence:
        Checks TIMEY, the size of the last time step 
        
    Climate code convergence:
        Checks DT, DIVF(1), and DIVFrms to see if they are "small enough",
        with 1e-5 definitely small enough, 1e-3 probably, larger probs not

    Parameters
    ----------
    datadir : string
        The location of where the text file of names is located.
        
    name : string
        The name of the text file with model names.

    Returns
    -------
    Knowledge. Maybe.

    """
    # Define cutoff values for TIMEY and climate code stuff
    Tcut = 1e10
    DIVcut = 1e-3
    
    # Open the text file and read in the names
    f = open(datadir+groupfile,'r')
    names = f.readlines()
    
    # Loop through all models
    for j in range(len(names)):
        
        # Remove \n if present
        name = str(names[j].split('\n')[0])
        
        # Print name of model
        print('---------------------------------------------')
        print('Checking '+name+'...')
        
        
        # Read in out.out file to look for TIMEY
        oo = read_outout(datadir+name+'/PHOTOCHEM_OUTPUT/out.out')
        TIMEY = oo['TIMEY']
        
        # Print warning if TIMEY is less than 1e10
        if TIMEY < Tcut:
            print('WARNING: TIMEY less than ','{:.2e}'.format(Tcut),' years')
            print('TIMEY = ','{:.2e}'.format(TIMEY))
            
            
        # Read in clima_allout for DT, DIVF(1), and DIVFrms
        ca = open(datadir+name+'/IO/clima_allout_'+name+'.tab','r')
        
        # Read each line
        rows = ca.readlines()
        
        ca.close()
        
        # For the last step results are above a line with 'TIME'
        # Search from the end of the file toward the beginning
        for i in range(len(rows)-1,0,-1):
            if rows[i].find('TIME') != -1:
                break
            
        # Two rows down there is the calculated planetary albedo which is 
        # helpful for convergence too, along with surface temperature
        # Split the row with albedo
        albrow = rows[i+2].split()
        # Albedo will be the last element of that row
        alb = albrow[-1]
        
        # Surface temperature can be read in from read_photo_mixings
        pm = read_photo_mixings(datadir+name+'/IO/photo_mixings_'+name+'.tab')
        # Surface temperature is first element of the temperature profile
        Tsurf = pm['TEMP'][0]
        
        # Print surface albedo and temperature
        print('Surf. albedo = '+str(alb)+', Surf. temperature = '+str(Tsurf)+' K')
            
        # Two rows above from i has all the info we need        
        # Split the row
        srow = rows[i-2].split('=')

        # Check DIVF(1) - 5th element of row
        # Remove string from element and convert to absolute value float
        DIVF = abs(float(srow[5].replace('DIVFrms','')))
        if DIVF > DIVcut:
            print('WARNING: DIVF(1) is larger than','{:.2e}'.format(DIVcut))
            print('DIVF(1) = ','{:.2e}'.format(DIVF))
            
        # Check DIVFrms - 6th element of row
        # Remove string from element and convert to absolute value float
        DIVFrms = abs(float(srow[6].replace('DT(ND)','')))
        if DIVFrms > DIVcut:
            print('WARNING: DIVFrms is larger than','{:.2e}'.format(DIVcut))
            print('DIVFrms = ','{:.2e}'.format(DIVFrms))
            
        # Check DT(ND) - 7th element of row
        # Remove string from element and convert to absolute value float
        DT = abs(float(srow[7].replace('T(ND)','')))
        if DT > DIVcut:
            print('WARNING: DT(ND) is larger than','{:.2e}'.format(DIVcut))
            print('DT(ND) = ','{:.2e}'.format(DT))
        
        
        ca.close()
        
        # Read final Seff calculated by Clima from the run*.log file
        # You want Seff to be VERY close to exactly 1
        # Read in clima_allout for DT, DIVF(1), and DIVFrms
        rlog = open(datadir+name+'/IO/run_'+name+'.log','r')
        
        # Read each line
        rows = rlog.readlines()
        
        rlog.close()
        
        # Search for the last occurrence of Seff
        for i in range(len(rows)-1,0,-1):
            if rows[i].find('Seff=') != -1:
                break
            
        # Print that line where Seff was found
        print(rows[i])
        
        
    


def plot_frames(datadir,name,fi,ff):
    """
    Code to plot the outputs stored in /frames for atmos-IAA, so you can 
    look at different parameters and how their profiles changed for each 
    iteration between the photochemistry and climate codes. If the profiles
    have not changed much the last few iterations that is a good sign of 
    convergence.
    
    The last profile plotted will always be colored black to enable easier
    comparison, and the rest of the iterations go in the order of the 
    "rainbow". Checking convergence is difficult, but at least there's a rainbow.

    Parameters
    ----------
    datadir : string
        Path to where the output directory is located (not including name).
    name : string
        Name of the output directory.
    fi : int
        First iteration to plot.
    ff : int
        Last iteration to plot.

    Returns
    -------
    Plots the range of iterations selected.

    """
    import matplotlib.pyplot as plt
    import numpy as np
    
    # Color list for plots
    clist30 = ['pink','lightcoral','firebrick','red','tomato','darkorange',\
            'orange','gold','khaki','greenyellow','springgreen','turquoise',\
            'darkturquoise','deepskyblue','dodgerblue','blue','slateblue',\
            'blueviolet','violet']
    
    # Read in and save relevant values from selected iterations in matrices
    alt = np.zeros((101,ff-fi+1))
    T = np.zeros((101,ff-fi+1))
    H2O = np.zeros((101,ff-fi+1))
    O3 = np.zeros((101,ff-fi+1))
    
    for i in range(fi,ff+1):
        # Load in clima_out data
        co = np.loadtxt(datadir+name+'/frames/clima_out_'+str(i)+'.tab',skiprows=1)
        
        # Save altitude, temperature, H2O, and O3
        alt[:,i-fi] = co[:,0]
        T[:,i-fi] = co[:,2]
        H2O[:,i-fi] = co[:,3]
        O3[:,i-fi] = co[:,4]


    # Plot everything
    f, (ax1,ax2,ax3) = plt.subplots(nrows=1,ncols=3,figsize=(15,5)) 

    f.suptitle(name+': Iterations '+str(fi)+'-'+str(ff))       
     
    # Plot temperature for each iteration
    ax1.set_xlabel('Temperature (K)')
    ax1.set_ylabel('Altitude (km)')
    for i in range(fi,ff):
        # System for looping through colorlist
        c = int(np.mod(i,len(clist30)))
        ax1.plot(T[:,i-fi],alt[:,i-fi],label = i,color=clist30[c])
    # Plot final iteration in black
    ax1.plot(T[:,i-fi],alt[:,i-fi],label = i,color='black')
    
    # Plot H2O for each iteration
    ax2.set_xlabel('H2O mixing ratio')
    ax2.set_ylabel('Altitude (km)')
    for i in range(fi,ff):
        # System for looping through colorlist
        c = int(np.mod(i,len(clist30)))
        ax2.plot(H2O[:,i-fi],alt[:,i-fi],label = i,color=clist30[c])
    ax2.set_xscale('log')
    # Plot final iteration in black
    ax2.plot(H2O[:,i-fi],alt[:,i-fi],label = i,color='black')
    
    # Plot O3 for each iteration
    ax3.set_xlabel('O3 mixing ratio')
    ax3.set_ylabel('Altitude (km)')
    for i in range(fi,ff):
        # System for looping through colorlist
        c = int(np.mod(i,len(clist30)))
        ax3.plot(O3[:,i-fi],alt[:,i-fi],label = i,color=clist30[c])
    ax3.set_xscale('log')
    # Plot final iteration in black
    ax3.plot(O3[:,i-fi],alt[:,i-fi],label = i,color='black')

    
    plt.tight_layout()
    plt.show()
    plt.close()

    




