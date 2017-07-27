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

import sys
import time
import datetime

import sqlalchemy
import requests

from Database import Base, Route, Trip, WayPoint

class Poller:
    '''Simple class to make an HTTP request
    and store the results in a database.'''

    URL = 'https://realtimebjcta.availtec.com/InfoPoint/rest/Routes/GetAllRoutes'
    SLEEP = 30 # in seconds
    
    def __init__(self):
        #!mwd - TODO: don't hardcode this database
        engine = sqlalchemy.create_engine("sqlite:///poller.db")
        Base.metadata.create_all(engine)

        Session = sqlalchemy.orm.sessionmaker(bind = engine)
        self._session = Session()

        # all ready

    def go(self):
        while True:
            try:
                print('Requesting...')
                r = requests.get(Poller.URL, headers = {'content-type': 'application/json'})

                # get the json
                data = r.json()

                now = datetime.datetime.now()
                
                # iterate
                for route_info in data:
                    # if we don't know about this route yet
                    #  then create it.
                    route = self.get_or_create_route(route_info)
                    
                    if route == None:
                        # We ignore some routes
                        continue

                    for vehicle_info in route_info['Vehicles']:
                        self.add_waypoint(route, vehicle_info, now)

                # commit our changes
                self._session.commit()
                
            except Exception as e:
                print('Error: %s' % e, file = sys.stderr)

            # sleep
            time.sleep(Poller.SLEEP)

    def get_or_create_route(self, route_info):
        try:
            #!mwd Route 999 and 80 is some fake thing,
            #  skip it.
            if route_info.get('RouteId') in (80, 999):
                return None
            
            return self._session.query(Route).filter(Route.rId == str(route_info["RouteId"])).one()
        except sqlalchemy.orm.exc.NoResultFound:
            print('Creating new route: %s' % route_info['RouteId'])
            # create one
            route = Route(rId = str(route_info["RouteId"]),
                          name = route_info["LongName"])
            self._session.add(route)

            return route

    def get_or_create_trip(self, route, vehicle_info):
        try:
            return self._session.query(Trip).filter(sqlalchemy.and_(Trip.tId == str(vehicle_info["TripId"]),
                                                                    Trip.runId == str(vehicle_info["RunId"]),
                                                                    Trip.route_id == route.id)).one()
        except sqlalchemy.orm.exc.NoResultFound:
            print('Creating new trip: %s' % vehicle_info['TripId'])

            trip = Trip(tId = str(vehicle_info['TripId']),
                        name = vehicle_info['Name'],
                        runId = str(vehicle_info['RunId']))
            route.trips.append(trip)

            self._session.add(trip)
            self._session.add(route)

            return trip
        
    def add_waypoint(self, route, vehicle_info, now):
        trip = self.get_or_create_trip(route, vehicle_info)
        if trip:
            waypoint = WayPoint(date = now,
                                latitude = float(vehicle_info['Latitude']),
                                longitude = float(vehicle_info['Longitude']),
                                deviation = int(vehicle_info['Deviation']),
                                opStatus = vehicle_info['OpStatus'],
                                onBoard = int(vehicle_info['OnBoard']),
                                direction = vehicle_info['Direction'])

            trip.waypoints.append(waypoint)

            self._session.add(trip)
            self._session.add(waypoint)

if __name__ == '__main__':
    poller = Poller()
    poller.go()
