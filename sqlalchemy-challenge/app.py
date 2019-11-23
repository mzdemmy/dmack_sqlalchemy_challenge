import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc

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

# Return the JSON representation of the dictionary
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date/<start_date><br/>"
        f"/api/v1.0/start_date/end_date/<start_date>/<end_date>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    
    """Return a list of precipation scores for the previous year."""
    
    # Query all measurements
    prcp_results = session.query(Measurement.date, Measurement.prcp).\
    filter(Measurement.date <= '2017-08-23').filter(Measurement.date >= '2016-08-23').\
    group_by(Measurement.date).order_by(desc(Measurement.date)).all()

    session.close()
    
    # Convert the query results to a Dictionary using `date` as the key and `prcp` as the value
    prcp_data = []
    for prcp_rcd in prcp_results:
        prcp_dict = {}
        prcp_dict[prcp_rcd.date] = prcp_rcd.prcp
        prcp_data.append(prcp_dict)

    return jsonify(prcp_data)

@app.route("/api/v1.0/stations")
def stations():
    # return a JSON list of stations from the dataset.

    """Return a list of stations"""
    # Query all stations
    station_results = session.query(Station.name).all()

    session.close()
    
    list_stations = list(np.ravel(station_results))

    return jsonify(list_stations)
   
@app.route("/api/v1.0/tobs")
def tobs():
    # query for the dates and temperature observations from a year from the last data point.

    """Return a JSON list of Temperature Observations (tobs) for the previous year."""
    # Query all temps from the previous year
    tobs_results = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.date <= '2017-08-23').filter(Measurement.date >= '2016-08-23').\
    group_by(Measurement.date).order_by(desc(Measurement.date)).all()

    session.close()
    
    tobs_data = []
    for tobs_rcd in tobs_results:
        tobs_dict = {}
        tobs_dict[tobs_rcd.date] = tobs_rcd.tobs
        tobs_data.append(tobs_dict)

    return jsonify(tobs_data)   

@app.route("/api/v1.0/start_date/<start_date>")
def temp_norms(start_date):
    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start date.

    """When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date."""
    # Query temps from the start date
    tnorms_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(func.strftime("%Y-%m-%d", Measurement.date) >= start_date).all()
    #filter(Measurement.date >= start_date).all()

    session.close()
    
    tnorms_data = []
    for temps_rcd in tnorms_results:
        (min_tobs, avg_tobs, max_tobs) = temps_rcd
        tnorms_dict = {}
        tnorms_dict["min"] = min_tobs
        tnorms_dict["avg"] = avg_tobs
        tnorms_dict["max"] = max_tobs
        tnorms_data.append(tnorms_dict)

    return jsonify(tnorms_data)

@app.route("/api/v1.0/start_date/end_date/<start_date>/<end_date>")
def calc_temps(start_date, end_date):
    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.

    """When given the start and end date, calculate `TMIN`, `TAVG`, and `TMAX` for all dates between the start and end date."""
    # Query temps from the start and end dates
    stat_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    #filter(func.strftime("%Y-%m-%d", Measurement.date) >= start_date).\
    #filter(func.strftime("%Y-%m-%d", Measurement.date) <= end_date).all()
    
    session.close()
    
    stat_data = []
    for stat_rcd in stat_results:
        (min_tobs, avg_tobs, max_tobs) = stat_rcd
        stat_dict = {}
        stat_dict["min"] = min_tobs
        stat_dict["avg"] = avg_tobs
        stat_dict["max"] = max_tobs
        stat_data.append(stat_dict)

    return jsonify(stat_data)

if __name__ == '__main__':
    app.run(debug=True)
