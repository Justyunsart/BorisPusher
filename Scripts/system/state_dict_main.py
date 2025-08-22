"""
state_dict.py holds all the dataclasses that will be organized here.
"""
from system.state_dict import *
from dataclasses import dataclass, field

@dataclass
class AppConfig:
    """
    Combines all relevant dataclasses into one dataclass
    """
    step : DtNpConfig = field(default_factory=DtNpConfig)

    # For the field method configs, make sure you reassign the value itself
    # to the appropriate Config subclass when updating
    #   - (When changing to washer, use the washer config subclass)
    b : object = field(default_factory=FieldConfig)
    e : object = field(default_factory=FieldConfig)

    particle : ParticleData = field(default_factory=ParticleData) #name of particle file

    path : DirData = field(default_factory=DirData) #path of b, e input file

@dataclass
class AppConfigMeta:
    """
    Defines constants about handling AppConfig objects; os level stuff beyond sim. parameter scope.
    """
    filename = "AppConfig.pkl" #what saved instance binary files will be called


if __name__ == "__main__":
    config = AppConfig()
    print(config)