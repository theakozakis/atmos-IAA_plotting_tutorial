## Data directory

Each atmospheric model computed by atmos-IAA creates a directory with different subdirectories containing lots of output files. 
Since it is incredibly tedious to go through these files by hand, we use the Python functions in read_atmos_IAA.py to clean and extract 
the most relevant data for plotting and other visualizations.

This directory also includes Sun_O2.txt, which contains the names of all the models in the Data directory, which is useful in the plotting 
tutorial contained in test_read_atmos_IAA.py,
