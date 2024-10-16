from flask import Flask, jsonify, request
from datetime import datetime
import data

# Initialize Flask app
app = Flask(__name__)

# Database URI
SQLITE_URI = 'sqlite:////Users/masterschool/Documents/Masterschool_projects_2024/Database_SE106/sky_SQL_codio_project/flights.sqlite3'

# Initialize data manager (assuming 'data.FlightData' is your data manager class)
data_manager = data.FlightData(SQLITE_URI)

@app.route('/')
def home():
    return "Welcome to the Flight API!"

# Endpoint: Get delayed flights by airline
@app.route('/flights/delayed_by_airline', methods=['GET'])
def delayed_flights_by_airline():
    airline = request.args.get('airline')
    if not airline:
        return jsonify({"error": "Airline parameter is required."}), 400

    results = data_manager.get_delayed_flights_by_airline(airline)
    return jsonify(results)

# Endpoint: Get delayed flights by airport
@app.route('/flights/delayed_by_airport', methods=['GET'])
def delayed_flights_by_airport():
    airport = request.args.get('airport')
    if not airport or len(airport) != 3:
        return jsonify({"error": "Valid IATA airport code is required."}), 400

    results = data_manager.get_delayed_flights_by_airport(airport)
    return jsonify(results)

# Endpoint: Get flight by ID
@app.route('/flights/<int:flight_id>', methods=['GET'])
def flight_by_id(flight_id):
    result = data_manager.get_flight_by_id(flight_id)
    if not result:
        return jsonify({"error": "Flight not found."}), 404
    return jsonify(result)

# Endpoint: Get top 5 delayed flights by date
@app.route('/flights/delayed_by_date', methods=['GET'])
def flights_by_date():
    date_input = request.args.get('date')
    try:
        date = datetime.strptime(date_input, '%d/%m/%Y')
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid date format. Use DD/MM/YYYY."}), 400

    results = data_manager.get_top_5_delays_by_date(date.day, date.month, date.year)
    if not results:
        return jsonify({"message": "No delayed flights found for this date."}), 404
    return jsonify(results)

# Endpoint: Get average delay per airline
@app.route('/flights/average_delay_by_airline', methods=['GET'])
def average_delay_per_airline():
    results = data_manager.get_average_delay_per_airline()
    return jsonify(results)

# Endpoint: Get average delay per origin airport
@app.route('/flights/average_delay_by_origin', methods=['GET'])
def average_delay_per_origin():
    results = data_manager.get_average_delay_per_origin()
    return jsonify(results)

# Endpoint: Get top 10 busiest airlines
@app.route('/flights/top_busiest_airlines', methods=['GET'])
def top_10_busiest_airlines():
    results = data_manager.get_top_10_busiest_airlines()
    return jsonify(results)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
