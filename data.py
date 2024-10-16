from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd  # Ensure you import pandas


class FlightData:
    def __init__(self, db_uri):
        """
        Initialize a new engine using the given database URI.
        """
        self.engine = create_engine(db_uri)

    def _execute_query(self, query, params=None):
        """
        Execute an SQL query with the params provided in a dictionary,
        and return a list of records (dictionary-like objects).
        If an exception is raised, print the error, and return an empty list.
        """
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(query), params)

                # Convert the result to a list of dictionaries
                return [dict(row._mapping) for row in result]  # Convert each row to dictionary
        except SQLAlchemyError as e:
            print(f"An error occurred: {e.__class__.__name__}: {e}")
            return []

    def get_flight_by_id(self, flight_id):
        """
        Retrieves a flight using only the flight ID.
        """
        query = """
        SELECT flights.*, 
               airlines.airline AS AIRLINE,  
               flights.ID as FLIGHT_ID, 
               flights.DEPARTURE_DELAY as DELAY,
               flights.year AS YEAR,        -- Add year to the result
               flights.month AS MONTH,      -- Add month to the result
               flights.day AS DAY           -- Add day to the result
        FROM flights
        JOIN airlines ON flights.airline = airlines.id
        WHERE flights.ID = :id
        """
        params = {'id': flight_id}
        return self._execute_query(query, params)

    def get_delayed_flights_by_airline(self, airline_name):
        """
        Retrieves delayed flights for a given airline name.
        """
        params = {'airline': airline_name}
        query = """
        SELECT flights.*, airlines.airline, flights.ID as FLIGHT_ID, flights.DEPARTURE_DELAY as DELAY
        FROM flights
        JOIN airlines ON flights.airline = airlines.id
        WHERE airlines.airline = :airline
        AND flights.DEPARTURE_DELAY IS NOT NULL
        AND flights.DEPARTURE_DELAY > 0
        """
        return self._execute_query(query, params)

    def get_delayed_flights_by_airport(self, airport_code):
        """
        Retrieves delayed flights for a given origin airport IATA code.
        """
        params = {'airport': airport_code}
        query = """
        SELECT flights.*, airlines.airline, flights.ID as FLIGHT_ID, flights.DEPARTURE_DELAY as DELAY
        FROM flights
        JOIN airlines ON flights.airline = airlines.id
        WHERE flights.ORIGIN_AIRPORT = :airport
        AND flights.DEPARTURE_DELAY IS NOT NULL
        AND flights.DEPARTURE_DELAY > 0
        """
        return self._execute_query(query, params)

    def get_top_5_delays_by_date(self, day, month, year):
        """
        Retrieve the top 5 delayed flights for a specific date.
        """
        params = {'day': day, 'month': month, 'year': year}
        query = """
        SELECT flights.*, 
                airlines.airline, 
                flights.ID as FLIGHT_ID, 
                flights.DEPARTURE_DELAY as DELAY 
        FROM flights 
        JOIN airlines ON flights.airline = airlines.id 
        WHERE flights.year = :year 
        AND flights.month = :month 
        AND flights.day = :day
        AND flights.DEPARTURE_DELAY IS NOT NULL
        ORDER BY flights.DEPARTURE_DELAY DESC 
        LIMIT 5
        """
        return self._execute_query(query, params)

    def get_top_10_busiest_airlines(self):
        """
        Returns the top 10 busiest airlines based on flight counts.
        """
        query = """
        SELECT airlines.airline AS airline, COUNT(*) AS flight_count
        FROM flights
        JOIN airlines ON flights.airline = airlines.id
        GROUP BY airlines.airline
        ORDER BY flight_count DESC
        LIMIT 10
        """
        return self._execute_query(query)

    def get_average_delay_per_airline(self):
        """
        Fetch the average delay per airline, ignoring negative delays.
        """
        query = """
        SELECT 
            airlines.airline AS AIRLINE,
            AVG(CASE 
                    WHEN flights.DEPARTURE_DELAY >= 0 THEN flights.DEPARTURE_DELAY 
                    ELSE NULL 
                END) AS average_delay 
        FROM 
            flights 
        JOIN airlines ON flights.airline = airlines.id
        WHERE
            flights.DEPARTURE_DELAY IS NOT NULL  -- Ignore NULL delays
        GROUP BY 
            airlines.airline 
        ORDER BY 
            average_delay DESC;
        """
        return self._execute_query(query)

    def get_percentage_delayed_flights_per_airline(self):
        """
        Fetch the percentage of delayed flights per airline.
        """
        query = """
        SELECT 
            airlines.airline AS AIRLINE,
            COUNT(*) AS total_flights,
            SUM(CASE WHEN flights.DEPARTURE_DELAY > 0 THEN 1 ELSE 0 END) AS delayed_flights
        FROM 
            flights 
        JOIN airlines ON flights.airline = airlines.id
        GROUP BY 
            airlines.airline;
        """
        results = self._execute_query(query)

        # Convert the results to a DataFrame for easier manipulation
        df = pd.DataFrame(results)

        # Calculate percentage delays
        df['percentage_delays'] = (df['delayed_flights'] / df['total_flights'] * 100).fillna(0)

        return df[['AIRLINE', 'percentage_delays']]  # Return only the relevant columns

    def get_average_delay_per_origin(self):
        """
        Fetch the average delay per origin airport, ignoring negative delays.
        """
        query = """
        SELECT 
            flights.ORIGIN_AIRPORT AS origin_airport,
            AVG(CASE 
                    WHEN flights.DEPARTURE_DELAY >= 0 THEN flights.DEPARTURE_DELAY 
                    ELSE NULL 
                END) AS average_delay 
        FROM 
            flights 
        WHERE
            flights.DEPARTURE_DELAY IS NOT NULL  -- Ensure there are no NULL values
        GROUP BY 
            flights.ORIGIN_AIRPORT 
        ORDER BY 
            average_delay DESC;
        """
        return self._execute_query(query)

    def get_percentage_delayed_flights_per_hour(self):
        """
        Fetch the percentage of delayed flights per hour of the day.
        """
        query = """
        SELECT 
            strftime('%H', flights.SCHEDULED_DEPARTURE) AS hour,  -- Extract hour from SCHEDULED_DEPARTURE
            COUNT(*) AS total_flights,
            SUM(CASE WHEN flights.DEPARTURE_DELAY > 0 THEN 1 ELSE 0 END) AS delayed_flights
        FROM 
            flights 
        GROUP BY 
            hour;
        """
        results = self._execute_query(query)

        # Convert the results to a DataFrame for easier manipulation
        df = pd.DataFrame(results)

        # Calculate percentage delays
        df['delay_percentage'] = (df['delayed_flights'] / df['total_flights'] * 100).fillna(0)

        # Rename columns to match expected format if necessary
        df.rename(columns={'hour': 'HOUR'}, inplace=True)  # Rename 'hour' to 'HOUR'

        return df[['HOUR', 'delay_percentage']]  # Return only the relevant columns

    def get_percentage_delayed_flights_per_route(self):
        query = """
        SELECT 
            ORIGIN_AIRPORT,
            DESTINATION_AIRPORT,
            AVG(CASE WHEN DELAY > 0 THEN 1 ELSE 0 END) * 100 AS delay_percentage
        FROM 
            flights
        GROUP BY 
            ORIGIN_AIRPORT, DESTINATION_AIRPORT
        """
        result = pd.read_sql(query, self.engine)
        return result

    def __del__(self):
        """
        Closes the connection to the database when the object is about to be destroyed.
        """
        self.engine.dispose()
