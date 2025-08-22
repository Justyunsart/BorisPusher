
"""
Moving from keeping a state dictionary in a tempfile
and instead putting it in a regular dictionary held in memory.

Does not make sense to keep reading and writing to a file when
we want it to function like something in memory.

Will define a class here to maintain the key and default values and type of
each parameter.
"""

from dataclasses import dataclass, field
from typing import Optional
from magpylib import Collection
import pandas as pd

# PARTICLE DATACLASSES
@dataclass
class ParticleData:
    name : Optional[str] = None #name of the particle file chosen
    count : Optional[int] = None #number of tracked particles
    dataframe : Optional[pd.DataFrame] = field(default_factory=pd.DataFrame)

# DIRECTORY DATACLASSES
@dataclass
class DirData:
    # Although you can always create the path by reading the configuration .ini (to get path)
    # and joining the filename at the end, storing it here saves some repetition.
    b : str = None
    e : str = None
    particle : str = None

    output_name : str = None
    output : str = None # PATH + FILE NAME AT THE END
    output_absolute : str = None # JUST THE PATH TO THE FILE's PARENT DIR

    hdf5 : str = None

# TIME STEP DATACLASSES
#   - atop the timestep and numsteps parameters, we also need to store the dt scaling params if that method is chosen.

@dataclass
class DynB0Consts:
    """
    Things we track about the reference particle B0
    """
    position : list[float] = field(default_factory=list)
    b : list[float] = field(default_factory=list)
    b_norm : float = None

@dataclass
class DynDtConsts:
    """
    These values are calculated based on the geometry and referenced when scaling the timestep.
    Therefore, they do not have a default value.
    """
    dt_min : float = None
    dt_max : float = None
    dt0 : float = None
    f0 : float = None
    B0 : DynB0Consts = field(default_factory=DynB0Consts)

@dataclass
class DynDtConfig:
    proportion : float = 0.5
    dynamic_range : int = 10
    consts : DynDtConsts = field(default_factory=DynDtConsts)
    on : bool = False # scaling is off by default.

@dataclass
class DtNpConfig:
    dt : float = 2e-9
    numsteps : int = 30000
    dynamic : DynDtConfig = field(default_factory=DynDtConfig)

# FIELD METHOD DATACLASSES
#    - Universal class for every method, then subclasses for any variations.
#    - This way, we can see what parameters to expect for each option by dataclass attributes.
@dataclass
class FieldConfig:
    """
    Holds universal params for B, E-field solver methods.

    :params:
    method: the name of the method
    collection: the magpylib Collection object
    gridding: 0, 1 = determines whether the solver will precompute a grid and interpolate
    """
    method : str = ""
    collection : object = Collection()
    gridding : int = 0
    name : Optional[str] = None #name of the particle file chosen

@dataclass
class ResFieldConfig(FieldConfig):
    """
    For any field solver that relies on a linspace for integration.
    This parameter represents the num of points on that linspace.
    """
    res : int = 100

@dataclass
class WasherFieldConfig(ResFieldConfig):
    """
    Washer fields also need to know its inner washer radii.
    """
    inner_r : list[float] = field(default_factory=list)
