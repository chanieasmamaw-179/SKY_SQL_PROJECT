Flight Data Management System
Overview

The Flight Data Management System is designed to manage and analyze flight delay data using a SQLite database. It provides a command-line interface for data queries and a RESTful API built with Flask for web access. The system leverages SQLAlchemy for database interactions and Pandas for data manipulation.
Features

    Data Retrieval: Fetch flight details, including delayed flights by airline and airport, top delayed flights by date, and average delays per airline.
    Data Analysis: Analyze flight delays by generating statistics such as percentage of delayed flights per airline and average delays per origin airport.
    Visualizations: Plot graphs to visualize delay percentages and generate heatmaps for flight delays by route.

Installation

    Clone the Repository:

    bash

git clone <repository_url>
cd <repository_directory>

Install Dependencies: Make sure you have Python installed, then install the required packages using:

bash

    pip install -r requirements.txt

    Database Setup: Ensure you have the SQLite database file (flights.sqlite3) located in the specified path.

Usage
Command-Line Interface

Run the command-line interface to interact with the data:

bash

python main.py

Follow the prompts to perform various queries.
RESTful API

    Start the Flask application:

    bash

    python app.py

    Access the API endpoints:
        Get Delayed Flights by Airline:
        GET /flights/delayed_by_airline?airline=<airline_name>
        Get Delayed Flights by Airport:
        GET /flights/delayed_by_airport?airport=<IATA_code>
        Get Flight by ID:
        GET /flights/<flight_id>
        Get Top 5 Delayed Flights by Date:
        GET /flights/delayed_by_date?date=<DD/MM/YYYY>
        Get Average Delay Per Airline:
        GET /flights/average_delay_by_airline
        Get Average Delay Per Origin Airport:
        GET /flights/average_delay_by_origin
        Get Top 10 Busiest Airlines:
        GET /flights/top_busiest_airlines

Dependencies

    SQLAlchemy
    Pandas
    Flask
    Matplotlib
    Seaborn
    Geopandas
    Shapely

License

This project is licensed under the Masterschool,Berlin, software engineering owner, & Asmamaw Y. License - see the LICENSE file for details.
Author
[contact me for collaboration and any issues, Asmamaw Yehun(PhD), chanieasmamaw@yahoo.com or yehunchanieasmamaw@gmail.com and +4917625315666]
