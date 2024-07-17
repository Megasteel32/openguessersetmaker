import argparse
import geopandas as gpd
import random
import json
from shapely.geometry import Point, MultiPolygon, Polygon
import sys
from tqdm import tqdm
import multiprocessing
from functools import lru_cache


@lru_cache(maxsize=1)
def load_countries_from_file(filename='world.txt'):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return frozenset(line.strip() for line in file if line.strip())
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.", file=sys.stderr)
        return frozenset()


@lru_cache(maxsize=1)
def lazy_load_world_dataset(filename='ne_10m_admin_0_countries.shp'):
    try:
        return gpd.read_file(filename)
    except Exception as e:
        print(f"Error loading world dataset: {e}", file=sys.stderr)
        sys.exit(1)


# Load countries from file
all_countries = load_countries_from_file()


def get_random_point_in_polygon(geometry):
    if isinstance(geometry, MultiPolygon):
        areas = [poly.area for poly in geometry.geoms]
        chosen_poly = random.choices(geometry.geoms, weights=areas, k=1)[0]
        return get_random_point_in_polygon(chosen_poly)
    elif isinstance(geometry, Polygon):
        minx, miny, maxx, maxy = geometry.bounds
        while True:
            pnt = Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
            if geometry.contains(pnt):
                return pnt
    else:
        raise ValueError(f"Unsupported geometry type: {type(geometry)}")


def generate_point_for_country(country_data):
    country_name, geometry = country_data
    try:
        point = get_random_point_in_polygon(geometry)
        lat, lon = round(point.y, 4), round(point.x, 4)
        osm_link = f"https://www.openstreetmap.org/#map=10/{lat}/{lon}"
        return [lat, lon], osm_link, country_name
    except Exception as e:
        print(f"Error generating point for {country_name}: {e}", file=sys.stderr)
        return None


def filter_and_validate_countries(input_countries):
    valid_countries = set(country for country in input_countries if country in all_countries)
    return valid_countries, set(input_countries) - valid_countries


def generate_coordinates(locations, num_points=1, feeling_lucky=False):
    if feeling_lucky:
        locations = [random.choice(list(all_countries))]

    valid_locations, invalid_locations = filter_and_validate_countries(locations)

    if not valid_locations:
        print("Error: No valid countries specified.", file=sys.stderr)
        return [], [], valid_locations, invalid_locations

    world = lazy_load_world_dataset()
    countries = world[world['NAME'].isin(valid_locations)]

    if countries.empty:
        print("Error: No matching countries found in the dataset.", file=sys.stderr)
        return [], [], valid_locations, invalid_locations

    country_geometries = list(zip(countries['NAME'], countries['geometry']))

    with multiprocessing.Pool() as pool:
        results = list(tqdm(
            pool.imap(
                generate_point_for_country,
                random.choices(country_geometries, k=num_points)
            ),
            total=num_points,
            desc="Generating coordinates",
            unit="point"
        ))

    results = [r for r in results if r is not None]

    if not results:
        return [], [], set(), invalid_locations

    coordinates, osm_links, generated_countries = zip(*results)

    return list(coordinates), list(osm_links), set(generated_countries), invalid_locations


def process_input(input_item):
    if input_item.endswith('.txt'):
        return load_countries_from_file(input_item)
    else:
        return {input_item}


def get_user_input(parser):
    args = parser.parse_args()

    if not sys.argv[1:]:
        print("1. Enter specific countries")
        print("2. I'm Feeling Lucky (random country/ies)")
        print("3. Use default countries from world.txt")
        choice = input("Enter your choice (1, 2, or 3): ")

        if choice == "1":
            args.input = input("Enter country names or text filenames separated by commas: ").split(',')
            args.lucky = False
        elif choice == "2":
            args.input = []
            args.lucky = True
        elif choice == "3":
            args.input = ['world.txt']
            args.lucky = False
        else:
            print("Invalid choice. Defaulting to world.txt")
            args.input = ['world.txt']
            args.lucky = False

        args.num_points = int(input("Enter the number of points to generate: "))
        args.show_links = input("Do you want to see OpenStreetMap links? (y/n): ").lower() == 'y'
        save_to_file = input("Do you want to save the coordinates to a file? (y/n): ").lower() == 'y'
        if save_to_file:
            args.output = input("Enter the filename to save the coordinates: ")
        else:
            args.output = None

    return args


def save_coordinates_to_file(coordinates, filename):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({"locations": coordinates}, f, indent=4)
        print(f"Coordinates saved to {filename}")
    except IOError as e:
        print(f"Error saving coordinates to file: {e}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Generate random coordinates for specified countries.")
    parser.add_argument("input", nargs='*', help="Country names or text filenames")
    parser.add_argument("-n", "--num_points", type=int, default=1, help="Number of points to generate")
    parser.add_argument("-l", "--lucky", action="store_true", help="I'm Feeling Lucky mode")
    parser.add_argument("-s", "--show_links", action="store_true", help="Show OpenStreetMap links")
    parser.add_argument("-o", "--output", help="Output file to save coordinates")

    args = get_user_input(parser)

    processed_input = set()
    for item in args.input:
        processed_input.update(process_input(item.strip()))

    coordinates, osm_links, valid_locations, invalid_locations = generate_coordinates(
        processed_input, num_points=args.num_points, feeling_lucky=args.lucky
    )

    if coordinates:
        print(json.dumps({"locations": coordinates}, indent=4))

        if args.output:
            save_coordinates_to_file(coordinates, args.output)

        print("", file=sys.stderr)
        if args.show_links:
            print("OpenStreetMap Links:", file=sys.stderr)
            for link in osm_links:
                print(link, file=sys.stderr)
            print("", file=sys.stderr)

        print("Valid countries:", ", ".join(sorted(valid_locations)), file=sys.stderr)

        if invalid_locations:
            print("Invalid countries:", ", ".join(sorted(invalid_locations)), file=sys.stderr)
    else:
        print("No coordinates generated. Please check your input and try again.", file=sys.stderr)


if __name__ == "__main__":
    main()
