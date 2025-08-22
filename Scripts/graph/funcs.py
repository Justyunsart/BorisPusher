from dataclasses import dataclass
import matplotlib.pyplot as plt

"""
Generic graphic functions and classes.

Classes are means to store meta information on graphs (store settings like titles, labels, etc.)
All functions expect an input of the matplotlib figure object and the axis to draw it to.
"""

@dataclass
class GraphSetting:
    """
    Holds commonly known graph metadata.
    """
    title = 'New Graph'
    x_lab = 'X - axis'
    y_lab = "Y - axis"