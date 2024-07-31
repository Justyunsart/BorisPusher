This is a Python based Boris Particle pusher

# TODO:
> Integrate GUI inputs to program
> Write output file functionality

# DESIGN DECISIONS:

## Input files
1. Why are they formatted in a .csv?
     I wanted the input files to be human readable and easily editable, as it's one of the files expected to have lots of human intervention.
     
     But because this file would be in a different format than the restart files(output from existing simulation), it did make it necessary for the user to distinguish between them when starting the program. 
