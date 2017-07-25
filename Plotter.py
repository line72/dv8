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
        # just Plot today for the Route 44
        today = datetime.datetime.now()
        # cycle through colors
        colors = itertools.cycle('bgrcmy')
        hatches = itertools.cycle('/\\|-+')
        
        route = self._session.query(Route).filter(Route.rId == "902").one()
        # find all the trips

        tripDeviations = {}
        for trip in route.trips:
            key = '%s_%s_%s' % (trip.tId, trip.runId, trip.name)
            for waypoint in trip.waypoints:
                if waypoint.date.day == today.day:
                    if key not in tripDeviations:
                        tripDeviations[key] = {'x': [], 'y': [], 'color': next(colors)}
                        
                    tripDeviations[key]['x'].append(waypoint.date.timestamp())
                    tripDeviations[key]['y'].append(waypoint.deviation)

                    
        flatten = lambda l: [item for sublist in l for item in sublist]
                    
        ## Try 1
        ## This didn't look good
        
        # # create a nice tuple of all the data
        # t = flatten([[x['x'], x['y'], x['color']] for x in tripDeviations.values()])
        # print('t=%s' % t)
                    
        # # plot this
        # fig, ax = matplotlib.pyplot.subplots()
        # ax.fill(*t, alpha=0.3)
        # matplotlib.pyplot.show()
        
        ##
        ## Try 1 - End
        
        # find an overall min and max
        all_y = flatten([x['y'] for x in tripDeviations.values()])
        max_y = max(all_y)
        min_y = min(all_y)

        all_x = flatten([x['x'] for x in tripDeviations.values()])
        max_x = max(all_x)
        min_x = min(all_x)

        
        # place colored bars along the bottom, showing the
        #  start and end of each trip
        bars = []
        #bar_size = (max_y - min_y) / 5.0
        bar_size = 2.0
        
        fix, ax = matplotlib.pyplot.subplots()

        # order our trips based on their start time
        sorted_trips = sorted(tripDeviations.values(), key = lambda x: min(x['x']))

        # draw a black line at 0
        ax.plot([min_x, max_x], [0, 0], 'k', linewidth = 4.0, zorder=100)
        
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

        matplotlib.pyplot.show()

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
