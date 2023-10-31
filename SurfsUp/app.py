# Import the dependencies.
from flask import Flask, jsonify

import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
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
    return (
        f"<b>Welcome to the Climate App API!</b><br/>"
        f"(This my Bootcamp Module 10 Challenge.)<br/>"
        "<br/>"
        f"Available Routes:<br/>"
        "<br/>"
        f"&nbsp &nbsp/api/v1.0/precipitation&nbsp &nbsp<br/>"
        f"&nbsp &nbsp/api/v1.0/stations<br/>"
        f"&nbsp &nbsp/api/v1.0/tobs<br/>"
        f"&nbsp &nbsp/api/v1.0/<mark><em>&ltstart&gt</em></mark>&nbsp &nbsp***(please use yyyy-mm-dd date format in the <mark><em>&ltstart&gt</em></mark> field.)<br/>"
        f"&nbsp &nbsp/api/v1.0/<mark><em>&ltstart_date&nbsp&gt</em></mark>/<mark><em>&ltend_date&nbsp&gt</em></mark>&nbsp &nbsp***(please use yyyy-mm-dd date format in both <mark><em>&ltstart&gt</em></mark> and <mark><em>&ltend&gt</em></mark> field.)<br/>"
        )


@app.route("/api/v1.0/precipitation")
# Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of only the last 12 months of data"""

    # Query only the last 12 months of data
    import datetime as dt

    date = dt.datetime(2017,8,23)
    query_date = date - dt.timedelta(days=366)
    
    results = session.query(Measurement.date,Measurement.prcp).\
        filter(Measurement.date>=query_date).all()
    
    session.close()

    # Convert list of tuples into dictionary using date as the key and prcp as the value.
    all_precipitation = dict((x,y) for x, y in results)

    return jsonify(all_precipitation)

@app.route("/api/v1.0/stations")
# Return a JSON list of stations from the dataset.
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of stations from the dataset"""
    station_list = session.query(Station.name).all()
    session.close()

    # Convert list
    all_stations = list(np.ravel(station_list))
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
# Query the dates and temperature observations of the most-active station for the previous year of data.
# Return a JSON list of temperature observations for the previous year.
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of only the last 12 months of data"""

    # Query only the last 12 months of data
    import datetime as dt

    date = dt.datetime(2017,8,23)
    query_date = date - dt.timedelta(days=366)

    stations_groupby_sort = session.query(Measurement.station).\
        group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()

    print(stations_groupby_sort[0])

    results_tobs = session.query(Measurement.date,Measurement.tobs).\
        filter(Measurement.date>=query_date).\
        filter(Measurement.station==stations_groupby_sort[0]).\
            all()
    
    session.close()

    # Convert list of tuples into dictionary using date as the key and tobs as the value.
    all_tobs = dict((x,y) for x, y in results_tobs)

    return jsonify(all_tobs)

@app.route("/api/v1.0/<start>")
# Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start-most recent range.
def min_avg_max_temperature_1(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
        
    results_1 = session.query(Measurement.station,func.min(Measurement.tobs),func.round(func.avg(Measurement.tobs),1),func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).group_by(Measurement.station).all()
        
    session.close()
    # Convert list of tuples into dictionary using stations as the key and the tuples of different temperature as the value.
    mix_tobs = dict((x,(y,z,m)) for x, y,z,m in results_1)

    return jsonify(mix_tobs)

    
@app.route("/api/v1.0/<start>/<end>")
# Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start-end range.
def min_avg_max_temperature_2(start,end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    results_2 = session.query(Measurement.station,func.min(Measurement.tobs),func.round(func.avg(Measurement.tobs),1),func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).\
        group_by(Measurement.station).all()
        
    session.close()
    # Convert list of tuples into dictionary using stations as the key and the tuples of different temperature as the value.
    mix_tobs_2 = dict((x,(y,z,m)) for x, y,z,m in results_2)

    return jsonify(mix_tobs_2)


if __name__ == "__main__":
    app.run(debug=True)