#Import dependencies
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Station = Base.classes.station
Measurement = Base.classes.measurement

session = Session(engine)
    
#################################################
# Flask Setup
#################################################
app = Flask(__name__)

@app.route("/")
def Homepage():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/startend<br/>"
    )
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Perform a query to retrieve the data and precipitation scores
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_year = dt.date(2017,8,23) - dt.timedelta(days= 365)
    prcp_results = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date > last_year).\
    order_by(Measurement.date.desc()).all()

    # Create a dictionary and append for JSON call
    prcp_data = []
    for result in prcp_results:
        data = {result.date: result.prcp}
        prcp_data.append(data)
    return jsonify(prcp_results)

@app.route("/api/v1.0/stations")
def stations(): 
    # Query all stations
    station_results = session.query(Station.station).all()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(station_results))

    # JSON call
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def temperature(): 
    #Query the dates and temperature observations for the most active station for the last year of data.
    results = (session.query(Measurement.station, Measurement.tobs, Measurement.date).\
                       filter(Measurement.station == 'USC00519281').\
                       filter(Measurement.date.between('2016-08-23','2017-08-23'))).all()
    
    # Create a dictionary from the row data and append
    tobs_results = []
    for result in results:
        data = {result.date: result.tobs}
        tobs_results.append(data)
    
    #Return a JSON list of temperature observations (TOBS) for the previous year.   
    return jsonify(tobs_results)

@app.route("/api/v1.0/start")
def start():

    # Query temperature observations from previous year, for dates greater than or equal to trip the planned start date 
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= dt.date(2017,8,10)).all()

    # Create a dictionary from the row data and append    
    start_data = []
    for result in results:
        date_data = {}
        date_data['TMIN'] = result[1]
        date_data['TAVG'] = result[2]
        date_data['TMAX'] = result[3]
        start_data.append(date_data)
    
    # JSON call
    return jsonify(start_data) 

@app.route("/api/v1.0/startend")
def start_end():

    # Query temperature observations from previous year, for dates in the trip range from start to finish dates
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) >= dt.date(2017,8,10)).\
        filter(func.strftime("%Y-%m-%d", Measurement.date) <= dt.date(2017,8,20)).all()

    trip_data = []
    for result in results:
        date_data = {}
        date_data['TMIN'] = result[1]
        date_data['TAVG'] = result[2]
        date_data['TMAX'] = result[3]
        trip_data.append(date_data)
    
    return jsonify(trip_data)

if __name__ == '__main__':
    app.run(debug=True)