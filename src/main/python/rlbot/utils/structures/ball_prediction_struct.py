import ctypes
import math

from rlbot.utils.structures.utils import create_enum_object
from rlbot.utils.structures.game_data_struct import Physics

MAX_SLICES = 3600


class Slices(ctypes.Structure):
    _fields_ = [("physics", Physics)]               # ("physics", Physics),


class BallPrediction(ctypes.Structure):
    _fields_ = [("slices", Slices * MAX_SLICES),    # ("game_cars", PlayerInfo * MAX_PLAYERS),
                ('slices_length', ctypes.c_int)]    # ("num_cars", ctypes.c_int),



