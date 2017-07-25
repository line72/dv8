#!/usr/bin/env python3

import itertools
import datetime

import sqlalchemy
import matplotlib.pyplot

from Database import Base, Route, Trip, WayPoint

class Plotter:
    '''Simple class to plot the data.'''
    def __init__(self):
        engine = sqlalchemy.create_engine("sqlite:///poller.db")
        Base.metadata.create_all(engine)

        Session = sqlalchemy.orm.sessionmaker(bind = engine)
        self._session = Session()

    def go(self):
        # make a subplot for each route
        routes = self._session.query(Route).all()

        today = datetime.datetime.now()

        # find the overall max y span, we'll then set up ratios
        #  b/c we want our plots to be different sizes
        # This looks at each routes deviations and finds its span
        # We then find the maximum span, and for each route, we
        #  set a ratio based on its vs the maximum span
        #
        # Also find the min/max date (x)
        spans = []
        xs = []
        for r in routes:
            waypoints = [waypoint for t in r.trips for waypoint in t.waypoints]# if waypoint.date.day == today.day]
            deviations = [x.deviation for x in waypoints]
            xs.extend([x.date for x in waypoints])
            
            if len(deviations) > 0:
                spans.append(max(deviations) - min(deviations))
        max_span = max(spans)

        min_x = min(xs)
        max_x = max(xs)
        xs = None

        # now find the height ratios 
        height_ratios = []
        for r in routes:
            deviations = [waypoint.deviation for t in r.trips for waypoint in t.waypoints]# if waypoint.date.day == today.day]
            if len(deviations) > 0:
                ratio = (max(deviations) - min(deviations)) / max_span
            else:
                ratio = 0.1 # not sure what to do here!
            height_ratios.append(ratio)

        fig, plts = matplotlib.pyplot.subplots(len(routes), 1, sharex = True, sharey = False,
                                               gridspec_kw = {'height_ratios': height_ratios},
                                               figsize = (50, 100))

        for i, route in enumerate(routes):
            # draw a dark black line at 0
            plts[i].plot([min_x, max_x], [0, 0], 'k', linewidth = 4.0, zorder=100)

            self.make_plot(plts[i], route)

        #matplotlib.pyplot.show()
        matplotlib.pyplot.savefig('output.png')
        
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
        tripDeviations = {}
        for trip in route.trips:
            for waypoint in trip.waypoints:
                # Trips restart each day, so we'll need to include
                #  the date as part of the key
                key = '%s_%s_%s_%s%s%s' % (trip.tId, trip.runId, trip.name,
                                           waypoint.date.year, waypoint.date.month, waypoint.date.day)
                #if waypoint.date.day == today.day:
                if True:
                    if key not in tripDeviations:
                        tripDeviations[key] = {'x': [], 'y': [], 'color': next(colors)}
                        
                    tripDeviations[key]['x'].append(waypoint.date)
                    tripDeviations[key]['y'].append(waypoint.deviation)

        if len(tripDeviations) == 0:
            # skip
            return
                    
                    
        flatten = lambda l: [item for sublist in l for item in sublist]
                    
        # find an overall min and max
        all_y = flatten([x['y'] for x in tripDeviations.values()])
        max_y = max(all_y)
        min_y = min(all_y)

        # place colored bars along the bottom, showing the
        #  start and end of each trip
        bars = []
        #bar_size = (max_y - min_y) / 5.0
        bar_size = 2.0
        
        # order our trips based on their start time
        sorted_trips = sorted(tripDeviations.values(), key = lambda x: min(x['x']))

        for tripDeviation in sorted_trips:
            bar_idx = self.find_bar_index(bars, tripDeviation) + 1
            hatch = next(hatches)
            
            # make the background fill
            ax.fill_between(tripDeviation['x'], -(bar_idx * bar_size), -((bar_idx + 1) * bar_size),
                            color = tripDeviation['color'],
                            alpha = 0.3,
                            hatch = hatch)
            # make a line of the actual data
            ax.plot(tripDeviation['x'], tripDeviation['y'], tripDeviation['color'],
                    linewidth = 3.0)
            # fill this line
            ax.fill_between(tripDeviation['x'], tripDeviation['y'], 0,
                            color = tripDeviation['color'],
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

if __name__ == '__main__':
    plotter = Plotter()
    plotter.go()
