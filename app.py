import numpy as np
import datetime as dt
import sqlalchemy
import pandas as pd
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """Listing all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"List of Stations: /api/v1.0/stations<br/>"
        f"Temperatures for last one year of most active station: /api/v1.0/tobs<br/>"
        f"Temperature stat from the start date(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd<br/>"
        f"Temperature stat from start to end dates(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
    )

@app.route('/api/v1.0/precipitation')
def precipitation():
    session = Session(engine)
    queryresult = session.query(Measurement.date,Measurement.prcp).all()
    session.close()

    precipitation = []
    for date, prcp in queryresult:
        prcp_dict = {}
        prcp_dict["Date"] = date
        prcp_dict["Precipitation"] = prcp
        precipitation.append(prcp_dict)

    return jsonify(precipitation)

@app.route('/api/v1.0/stations')
def stations():
    session = Session(engine)
    queryresult = session.query(Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation).all()
    session.close()

    stations = []
    for station,name,lat,long,elevtn in queryresult:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Lat"] = lat
        station_dict["Long"] = long
        station_dict["Elevation"] = elevtn
        stations.append(station_dict)

    return jsonify(stations)

@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    
    active_statn=session.query(Measurement.station, func.count(Measurement.id))\
                    .group_by(Measurement.station)\
                    .order_by(func.count(Measurement.id).desc()).first()
    lastdate = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    lastdate_ts = dt.datetime.strptime(lastdate[0], '%Y-%m-%d')   #_ts(time stamp)
    yearb4_lastdate_ts = dt.date(lastdate_ts.year -1, lastdate_ts.month, lastdate_ts.day)
    
    queryresult = session.query(Measurement.date, Measurement.tobs)\
                .filter(Measurement.station == active_statn[0])\
                .filter(Measurement.date >= yearb4_lastdate_ts).all()
    
    # getting the station name for active_statn[0][0] 
    station = session.query(Station.name).filter(Station.station==active_statn[0]).first()
    

    tobsall = []
    for date, tobs in queryresult:
        tobs_dict = {}
        tobs_dict["Name"] = station[0]
        tobs_dict["Date"] = date
        tobs_dict["Tobs"] = tobs
        tobsall.append(tobs_dict)

    return jsonify(tobsall)


@app.route('/api/v1.0/<start>')
def get_statrt(start):
# Create our session (link) from Python to the DB
    session = Session(engine)
    queryresult = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()

    tobsall = []
    for min,avg,max in queryresult:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        tobsall.append(tobs_dict)

    return jsonify(tobsall)

@app.route('/api/v1.0/<start>/<end>')
def get_start_end(start,end):
# Create our session (link) from Python to the DB
    session = Session(engine)
    queryresult = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()

    tobsall = []
    for min,avg,max in queryresult:
        tobs_dict = {}
        tobs_dict["Min"] = min
        tobs_dict["Average"] = avg
        tobs_dict["Max"] = max
        tobsall.append(tobs_dict)

    return jsonify(tobsall)


if __name__ == '__main__':
    app.run(debug=True)

           