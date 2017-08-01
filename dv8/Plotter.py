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
import sys

import sqlalchemy
import matplotlib.pyplot

from dv8.Database import Base, Route, Trip, WayPoint

class Plotter:
    '''Simple abstract base class to plot the data.'''
    def __init__(self, start_date = None, end_date = None):
        engine = sqlalchemy.create_engine("sqlite:///poller.db")
        Base.metadata.create_all(engine)

        Session = sqlalchemy.orm.sessionmaker(bind = engine)
        self._session = Session()

        self._start_date = None
        self._end_date = None
        
        if start_date != None:
            try: self._start_date = datetime.datetime.strptime(start_date, '%Y%m%d')
            except ValueError:
                raise Exception('Invalid start date: %s. Please format as YYYYMMDD (20170523)' % start_date)
        if end_date != None:
            try: self._end_date = datetime.datetime.strptime(end_date, '%Y%m%d')
            except ValueError:
                raise Exception('Invalid end date: %s. Please format as YYYYMMDD (20170523)' % end_date)

    ## Callbacks that the sub classes must override ##
    def y_value(self, waypoint):
        raise NotImplementedError

    def output_name(self):
        raise NotImplementedError


    ## Public functions ##
            
    def go(self):
        # make a subplot for each route
        routes = self._session.query(Route).all()

        today = datetime.datetime.now()

        # find the overall max y span, we'll then set up ratios
        #  b/c we want our plots to be different sizes
        # This looks at each routes y-values and finds its span
        # We then find the maximum span, and for each route, we
        #  set a ratio based on its vs the maximum span
        #
        # Also find the min/max date (x)
        spans = []
        xs = []
        for r in routes:
            waypoints = [waypoint for t in r.trips for waypoint in self.waypoints(t)]
            y_values = [self.y_value(x) for x in waypoints]
            xs.extend([x.date for x in waypoints])
            
            if len(y_values) > 0:
                spans.append(max(y_values) - min(y_values))

        if len(xs) == 0:
            print('No data points found in this date range!')
            sys.exit(1);
                
        max_span = max(spans)

        min_x = min(xs)
        max_x = max(xs)
        xs = None

        # now find the height ratios 
        height_ratios = []
        for r in routes:
            y_values = [self.y_value(waypoint) for t in r.trips for waypoint in self.waypoints(t)]
            if len(y_values) > 0:
                ratio = (max(y_values) - min(y_values)) / max_span
            else:
                ratio = 0.1 # not sure what to do here!
            height_ratios.append(ratio)

        fig, plts = matplotlib.pyplot.subplots(len(routes), 1, sharex = True, sharey = False,
                                               gridspec_kw = {'height_ratios': height_ratios},
                                               figsize = (200, 100))

        for i, route in enumerate(routes):
            # draw a dark black line at 0
            plts[i].plot([min_x, max_x], [0, 0], 'k', linewidth = 4.0, zorder=100)

            self.make_plot(plts[i], route)

        ouput = self.output_name()
        matplotlib.pyplot.savefig(ouput)

    ## Internal Functions ##
        
    def make_plot(self, ax, route):
        # just Plot today
        today = datetime.datetime.now()
        # cycle through colors
        colors = itertools.cycle('bgrcmy')
        hatches = itertools.cycle('/\\|-+')

        # add a title
        title = '%s %s' % (route.rId, route.name)
        print('title=%s' % title)
        ax.set_title(title, loc = 'left')

        
        # find all the trips
        trip_y_values = {}
        for trip in route.trips:
            for waypoint in self.waypoints(trip):
                # Trips restart each day, so we'll need to include
                #  the date as part of the key
                key = '%s_%s_%s_%s%s%s' % (trip.tId, trip.runId, trip.name,
                                           waypoint.date.year, waypoint.date.month, waypoint.date.day)
                if self.in_date_range(waypoint.date):
                    if key not in trip_y_values:
                        trip_y_values[key] = {'x': [], 'y': [], 'color': next(colors)}
                        
                    trip_y_values[key]['x'].append(waypoint.date)
                    trip_y_values[key]['y'].append(self.y_value(waypoint))

        if len(trip_y_values) == 0:
            # skip
            return
                    
                    
        flatten = lambda l: [item for sublist in l for item in sublist]
                    
        # find an overall min and max
        all_y = flatten([x['y'] for x in trip_y_values.values()])
        max_y = max(all_y)
        min_y = min(all_y)

        # place colored bars along the bottom, showing the
        #  start and end of each trip
        bars = []
        bar_size = 2.0
        
        # order our trips based on their start time
        sorted_trips = sorted(trip_y_values.values(), key = lambda x: min(x['x']))

        for y_value in sorted_trips:
            bar_idx = self.find_bar_index(bars, y_value) + 1
            hatch = next(hatches)
            
            # make the background fill
            ax.fill_between(y_value['x'], -(bar_idx * bar_size), -((bar_idx + 1) * bar_size),
                            color = y_value['color'],
                            alpha = 0.3,
                            hatch = hatch)
            # make a line of the actual data
            ax.plot(y_value['x'], y_value['y'], y_value['color'],
                    linewidth = 3.0)
            # fill this line
            ax.fill_between(y_value['x'], y_value['y'], 0,
                            color = y_value['color'],
                            alpha = 0.3,
                            hatch = hatch)

    def find_bar_index(self, bars, trip):
        '''
        Find a y location for this bar based
        on this trip.
        '''
        start = min(trip['x'])
        end = max(trip['x'])

        for idx, bar in enumerate(bars):
            taken = False

            for i in bar:
                # Check to make sure our start and end points are not inside
                #  any others. It IS possible for our start and end points
                #  to be outside any single other bar, so we need to do a
                #  reverse check too.
                if ((start >= i[0] and start <= i[1]) or (end >=i[0] and end <= i[1])) or \
                   ((i[0] >= start and i[0] <= end) or (i[1] >= start and i[1] <= end)):
                    taken = True
                    break
                
            if not taken:
                # insert us
                bars[idx].append((start, end))
                return idx

        # add a new index
        bars.append([(start, end)])
        
        return (len(bars) - 1)

    def waypoints(self, trip):
        '''Return all the waypoints of a trip within our date range.'''
        if self._start_date != None and self._end_date != None:
            return trip.waypoints.filter(WayPoint.date >= self._start_date, WayPoint.date <= self._end_date)
        elif self._start_date != None:
            return trip.waypoints.filter(WayPoint.date >= self._start_date)
        elif self._end_date != None:
            return trip.waypoints.filter(WayPoint.date <= self._end_date)
        else:
            return trip.waypoints
    
    def in_date_range(self, d):
        if self._start_date != None and self._end_date != None:
            return d.day >= self._start_date.day and d.day <= self._end_date.day
        elif self._start_date != None:
            return d.day >= self._start_date.day
        elif self._end_date != None:
            return d.day <= self._end_date.day
        else:
            return True
