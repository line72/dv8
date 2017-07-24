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
    waypoints = relationship("WayPoint", backref="trips", order_by="WayPoint.id")

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

    trip_id = Column(ForeignKey('trips.id'))
