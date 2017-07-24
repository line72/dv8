#!/usr/bin/env python3

import sys
import time

import sqlalchemy
import requests

from Database import Base, Route, Trip, WayPoint

class Poller:
    '''Simple class to make an HTTP request
    and store the results in a database.'''

    URL = 'https://realtimebjcta.availtec.com/InfoPoint/rest/Routes/GetAllRoutes'
    SLEEP = 30 # in seconds
    
    def __init__(self):
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

                # iterate
                for routeInfo in data:
                    # if we don't know about this route yet
                    #  then create it.
                    route = self.get_or_create_route(routeInfo)

                # commit our changes
                self._session.commit()
                
            except Exception as e:
                print('Error: %s' % e, file = sys.stderr)

            # sleep
            time.sleep(Poller.SLEEP)

    def get_or_create_route(self, routeInfo):
        try:
            #!mwd Route 999 is some fake thing,
            #  skip it.
            if routeInfo.get('RouteId') == 999:
                return None
            
            print('Checking for route %s' % routeInfo['RouteId'])
            return self._session.query(Route).filter(Route.rId == str(routeInfo["RouteId"])).one()
        except sqlalchemy.orm.exc.NoResultFound:
            print('Creating new route: %s' % routeInfo)
            # create one
            route = Route(rId = str(routeInfo["RouteId"]),
                          name = routeInfo["LongName"])
            self._session.add(route)

            return route

if __name__ == '__main__':
    poller = Poller()
    poller.go()
