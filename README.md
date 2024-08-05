This is a Python based Boris Particle pusher

# TODO:
> Integrate GUI inputs to program
> Write output file functionality

# DESIGN DECISIONS:

## Input files
1. Why are they different from restart files?

     I wanted the input files to be human readable and easily editable, as it's one of the files expected to have lots of human intervention. The idea is that these are strictly used for people to set up initial conditions and nothing more. I might move this functionality to the GUI itself, but that should be easy to integrate with this format anyway.
     
     But because this file would be in a different format than the restart files(output from existing simulation), it did make it necessary for the user to distinguish between them when starting the program. I'm workng on a good UX flow for that right now.
