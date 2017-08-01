#!/usr/bin/env python3
#

##################################################
# DV8 (c) Marcus Dillavou <line72@line72.net
#  https://github.com/line72/dv8
##################################################

# MIT License
#
# Copyright (c) 2017 Marcus Dillavou <line72@line72.net>
# https://github.com/line72/dv8
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import itertools
import datetime

import sqlalchemy
import matplotlib.pyplot

from dv8.Database import Base, Route, Trip, WayPoint
from dv8.Plotter import Plotter

class DeviationPlotter(Plotter):
    '''Simple class to plot the on time performance (deviation)
    for each bus at any given time.'''

    def y_value(self, waypoint):
        if waypoint.deviation > 20:
            return 20
        elif waypoint.deviation < -10:
            return -10
        else:
            return waypoint.deviation

    def output_name(self):
        return 'deviation.pdf'
