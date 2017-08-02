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

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Float

Base = declarative_base()

class Route(Base):
    __tablename__ = 'routes'

    id = Column(Integer, primary_key = True)
    rId = Column(String)
    name = Column(String)

    trips = relationship("Trip", backref="routes", order_by="Trip.id")
    
class Trip(Base):
    __tablename__ = 'trips'

    id = Column(Integer, primary_key = True)
    tId = Column(String)
    name = Column(String)
    runId = Column(String)

    route_id = Column(ForeignKey('routes.id'))
    waypoints = relationship("WayPoint", backref="trips", order_by="WayPoint.id", lazy="dynamic")

class WayPoint(Base):
    __tablename__ = 'waypoints'

    id = Column(Integer, primary_key = True)
    date = Column(DateTime)
    latitude = Column(Float)
    longitude = Column(Float)
    deviation = Column(Integer)
    opStatus = Column(String)
    onBoard = Column(Integer)
    direction = Column(String)
    driver = Column(String)

    trip_id = Column(ForeignKey('trips.id'))
