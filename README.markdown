# Random Coordinate Generator

This Python script generates random geographic coordinates for specified countries or a randomly selected country.

## Features

- Generate random coordinates for specific countries
- "I'm Feeling Lucky" mode for random selection of a single country
- Pass list of countries for custom groupings
- OpenStreetMap links for generated coordinates
- Option to save coordinates to a JSON file
- Command-line interface and interactive mode

## Prerequisites

Before running the script, ensure you have the following installed:

- Python 3.x
- Required Python packages:
  - geopandas
  - shapely
  - tqdm

You can install the required packages using pip:

```
pip install geopandas shapely tqdm
```

## Usage

### Command-line Interface

```
python script_name.py [countries...] [-n NUM_POINTS] [-l] [-s] [-o OUTPUT_FILE]
```

- `[countries...]`: Optional. Specify country names or text files containing country names.
- `-n, --num_points`: Number of points to generate (default: 1).
- `-l, --lucky`: Enable "I'm Feeling Lucky" mode to select a random country.
- `-s, --show_links`: Show OpenStreetMap links for generated coordinates.
- `-o, --output`: Specify an output file to save the coordinates as JSON.

### Interactive Mode

If no command-line arguments are provided, the script will run in interactive mode, prompting you for input.

## Examples

1. Generate 3 random coordinates for France and Germany:
   ```
   python openguessersetmaker.py France Germany -n 3
   ```

2. Generate 5 random coordinates for countries listed in a file:
   ```
   python openguessersetmaker.py countries.txt -n 5
   ```

3. Use "I'm Feeling Lucky" mode to generate 2 coordinates for a randomly selected country:
   ```
   python openguessersetmaker.py -l -n 2
   ```

4. Generate a coordinate from the included world set and save it to a file:
   ```
   python openguessersetmaker.py world.txt -o coordinates.json
   ```
## Notes

- Ensure that the `world.txt` file and the shapefile are in the same directory as the script.
- I have also included several other textfiles with template groupings, for all the continents, certain areas such as Oceania, and the European Union.
- When passing countries manually, or creating your own groupings template, ensure they're spelled exactly as found in `world.txt` 
- The script uses the Natural Earth 1:10m Admin 0 Countries shapefile (and supporting files) 
- In "I'm Feeling Lucky" mode, the script selects one random country and generates the specified number of points within that country.

## License

## Acknowledgements
Made with Natural Earth. Free vector and raster map data @ naturalearthdata.com

Wrote all of this (both the code and most of this README) using Claude Sonnet 3.5