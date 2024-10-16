import data
from datetime import datetime
import sqlalchemy
import sys
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import geopandas as gpd
from shapely.geometry import LineString

SQLITE_URI = 'sqlite:////Users/masterschool/Documents/Masterschool_projects_2024/Database_SE106/sky_SQL_codio_project/flights.sqlite3'
IATA_LENGTH = 3

def delayed_flights_by_airline(data_manager):
    airline_input = input("Enter airline name: ")
    results = data_manager.get_delayed_flights_by_airline(airline_input)
    print_results(results)

def delayed_flights_by_airport(data_manager):
    valid = False
    while not valid:
        airport_input = input("Enter origin airport IATA code: ")
        if airport_input.isalpha() and len(airport_input) == IATA_LENGTH:
            valid = True
    results = data_manager.get_delayed_flights_by_airport(airport_input)
    print_results(results)

def flight_by_id(data_manager):
    valid = False
    while not valid:
        try:
            id_input = int(input("Enter flight ID: "))
        except ValueError:
            print("Invalid ID. Try again...")
        else:
            valid = True
    results = data_manager.get_flight_by_id(id_input)
    print_results(results)

def flights_by_date(data_manager):
    valid = False
    while not valid:
        try:
            date_input = input("Enter date in DD/MM/YYYY format: ")
            date = datetime.strptime(date_input, '%d/%m/%Y')
            valid = True
        except ValueError:
            print("Invalid date format. Please use DD/MM/YYYY format. Try again...")

    # Fetch results based on the given date
    results = data_manager.get_top_5_delays_by_date(date.day, date.month, date.year)

    # Check if results are empty and print accordingly
    if not results:
        print("No delayed flights found for this date.")
    else:
        print_results(results)

def top_10_busiest_airlines(data_manager):
    results = data_manager.get_top_10_busiest_airlines()
    print_top_10_busiest_airlines(results)

def print_top_10_busiest_airlines(results):
    print(f"Top 10 Busiest Airlines:")
    if results:  # Check if results are not empty
        print(f"Result keys: {results[0].keys()}")  # Print the keys for debugging
    for idx, result in enumerate(results, start=1):
        airline = result['airline']  # Access the airline field from the result
        flight_count = result['flight_count']  # Access flight count from the result
        print(f"{idx}. {airline}: {flight_count} flights")

def print_results(results):
    print(f"Got {len(results)} results.")
    for result in results:
        try:
            delay = int(result['DELAY']) if result['DELAY'] else 0  # Handle delay
            origin = result['ORIGIN_AIRPORT']
            dest = result['DESTINATION_AIRPORT']
            airline = result['AIRLINE']
            year = result['YEAR']
            month = result['MONTH']
            day = result['DAY']
        except KeyError as e:
            print(f"Missing data for flight record: {e}")
            continue
        except (ValueError, sqlalchemy.exc.SQLAlchemyError) as e:
            print("Error showing results: ", e)
            return

        if delay > 0:
            print(f"{result['FLIGHT_ID']}. {origin} -> {dest}, {airline}, Delay: {delay} minutes, Date: {day}/{month}/{year}")

def average_delay_per_airline(data_manager):
    results = data_manager.get_average_delay_per_airline()
    print_average_delay_per_airline(results)

def print_average_delay_per_airline(results):
    print(f"Average Delay Per Airline:")
    for result in results:
        airline = result['AIRLINE']  # Access the airline field from the result
        average_delay = result['average_delay']
        print(f"{airline}: {average_delay:.2f} minutes")

def average_delay_per_origin(data_manager):
    results = data_manager.get_average_delay_per_origin()
    print_average_delay_per_origin(results)

def print_average_delay_per_origin(results):
    print(f"Average Delays Per Origin Airport:")
    for result in results:
        origin_airport = result['origin_airport']  # Access the origin airport field from the result
        average_delay = result['average_delay']
        print(f"{origin_airport}: {average_delay:.2f} minutes")

def plot_percentage_delay_per_airline(data_manager):
    results = data_manager.get_percentage_delayed_flights_per_airline()

    if results.empty:
        print("No data available to generate the graph.")
        return

    airlines = results['AIRLINE']
    delay_percentages = results['percentage_delays']

    # Plotting the data
    plt.figure(figsize=(10, 6))
    plt.bar(airlines, delay_percentages, color='skyblue')

    # Customizing the graph
    plt.title('Percentage of Delayed Flights Per Airline')
    plt.xlabel('Airlines')
    plt.ylabel('Delay Percentage (%)')
    plt.xticks(rotation=45, ha="right")

    # Display the graph
    plt.tight_layout()
    plt.show()

def plot_percentage_delay_per_hour(data_manager):
    results = data_manager.get_percentage_delayed_flights_per_hour()

    if results.empty:
        print("No data available to generate the graph.")
        return

    hours = results['HOUR']
    delay_percentages = results['delay_percentage']

    # Plotting the data
    plt.figure(figsize=(10, 6))
    plt.bar(hours, delay_percentages, color='lightcoral')

    # Customizing the graph
    plt.title('Percentage of Delayed Flights Per Hour of the Day')
    plt.xlabel('Hour of the Day (24-hour format)')
    plt.ylabel('Delay Percentage (%)')
    plt.xticks(hours)

    # Display the graph
    plt.tight_layout()
    plt.show()

def plot_heatmap_delay_per_route(data_manager):
    results = data_manager.get_percentage_delayed_flights_per_route()

    if results.empty:
        print("No data available to generate the heatmap.")
        return

    # Create a DataFrame from the results
    df = pd.DataFrame(results)

    # Pivot the data to create a matrix of origin -> destination with delay percentage
    heatmap_data = df.pivot("ORIGIN_AIRPORT", "DESTINATION_AIRPORT", "delay_percentage")

    # Plotting the heatmap
    plt.figure(figsize=(12, 8))
    sns.heatmap(heatmap_data, annot=True, fmt=".2f", cmap="YlGnBu", cbar_kws={'label': 'Delay Percentage (%)'})

    plt.title('Heatmap of Delayed Flights (Origin -> Destination)')
    plt.xlabel('Destination Airport')
    plt.ylabel('Origin Airport')

    # Display the heatmap
    plt.tight_layout()
    plt.show()

def plot_delay_map_per_route(data_manager):
    results = data_manager.get_percentage_delayed_flights_for_map()

    if results.empty:
        print("No data available to generate the map.")
        return

    # Load world map data
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

    # Create a GeoDataFrame for flight routes
    routes = []
    for result in results:
        origin = result['ORIGIN_AIRPORT']
        destination = result['DESTINATION_AIRPORT']
        avg_delay = result['avg_delay']

        # Create LineString geometry for route (assuming you have lat/long data)
        origin_coords = get_airport_coordinates(origin)
        destination_coords = get_airport_coordinates(destination)

        if origin_coords and destination_coords:
            route = {
                'geometry': LineString([origin_coords, destination_coords]),
                'delay': avg_delay
            }
            routes.append(route)

    # Convert the list of routes into a GeoDataFrame
    routes_gdf = gpd.GeoDataFrame(routes)

    # Plot the map with routes
    fig, ax = plt.subplots(figsize=(12, 8))
    world.plot(ax=ax, color='lightgray')

    # Plot routes with color based on average delay
    routes_gdf.plot(ax=ax, column='delay', cmap='Reds', legend=True, linewidth=2)

    plt.title('Average Delayed Flights Per Route (Origin <-> Destination)')
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')

    plt.tight_layout()
    plt.show()

def get_airport_coordinates(airport_code):
    # Placeholder function - you need a way to map IATA codes to lat/long coordinates
    airport_coords = {
        'JFK': (-73.7781, 40.6413),
        'LAX': (-118.4085, 33.9416),
        # Add more airport coordinates here...
    }
    return airport_coords.get(airport_code)

def main():
    data_manager = data.FlightData(SQLITE_URI)

    FUNCTIONS = {
        1: (flight_by_id, "Show flight by ID"),
        2: (delayed_flights_by_airline, "Delayed flights by airline"),
        3: (delayed_flights_by_airport, "Delayed flights by origin airport name"),
        4: (flights_by_date, "Top 5 flight delays by date"),
        5: (average_delay_per_airline, "Average Delay Per Airline"),
        6: (average_delay_per_origin, "Average Delay Per Origin Airport"),
        7: (top_10_busiest_airlines, "Top 10 Busiest Airlines"),
        8: (plot_percentage_delay_per_airline, "Plot Percentage of Delayed Flights Per Airline"),
        9: (plot_percentage_delay_per_hour, "Plot Percentage of Delayed Flights Per Hour"),
        10: (quit, "Exit")
    }

    while True:
        print("Please choose an option:")
        for key, (func, description) in FUNCTIONS.items():
            print(f"{key}. {description}")

        try:
            choice = int(input("Your choice: "))
            if choice in FUNCTIONS:
                function, _ = FUNCTIONS[choice]
                function(data_manager)
            else:
                print("Invalid choice, please try again.")
        except ValueError:
            print("Please enter a number corresponding to your choice.")

if __name__ == "__main__":
    main()
