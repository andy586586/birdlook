import os
import sys
from InquirerPy import inquirer
from InquirerPy.utils import get_style
from rich.console import Console
from rich.table import Table
from art import tprint
import random
from ascii_birds import birds # own other file with ascii birds
from config import CITY_TO_COUNTIES, COUNTIES_TO_CITIES

from ebird.api.requests import (
    get_observations, # returns all records, too much data
    get_nearby_observations, # returns all records, too much data
    get_notable_observations,
    get_nearby_notable,
    get_species_observations,
    get_nearby_species,
    get_regions, 
    get_adjacent_regions, 
    get_region
)

from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("EBIRD_API_KEY")

preset_cities_options = ['Ottawa', 'Waterloo', 'New York City', 'San Francisco', 'Portland', 'Exit']
end_options = ['Other city', 'Exit']
default_menu_style = get_style(
    {
    "checkbox": "#99dd99",            # unchecked color
    "checkbox-selected": "#2cec12",   # checked color
    "selected": "#42eb20",            # highlight when navigating
    "pointer": "#21e04a",             # arrow pointer color
    "marker": "#ffffff",              # checkbox border color
    }
)
default_menu_instruction = "Arrow keys to move, enter to submit"


class gen_ascii_bird():
    # generates an ascii bird
    def __init__(self):
        rand_index = random.randint(0, len(birds)-1)
        self.bird = birds[rand_index]
    
    def get_bird(self):
        return self.bird



def regions_load(codes_to_counties) -> dict[str,list]: # returns cities to codes hashmap
    relevant = {'Ottawa', 'Waterloo', 'Kings', 'Queens', 'New York', 'Bronx', 'Richmond', 'San Francisco', 'San Mateo', 'Marin', 'Multnomah', 'Washington'}
    cities_to_codes = {city : [] for city in preset_cities_options}

    # get list of relevant US counties
    counties = get_regions(api_key, 'subnational2', 'US-OR') + get_regions(api_key, 'subnational2', 'US-CA') + get_regions(api_key, 'subnational2', 'US-NY')
    for county in counties:
        county_name = county['name']
        code = county['code']
        codes_to_counties[code] = county_name
        if county_name in relevant:
            belong_city = COUNTIES_TO_CITIES[county_name]
            cities_to_codes[belong_city].append(code)

    # get list of subregions in Ontario
    sub_regions = get_regions(api_key, 'subnational2', 'CA-ON')
    for county in sub_regions:
        county_name = county['name']
        code = county['code']
        if county_name in relevant:
            belong_city = COUNTIES_TO_CITIES[county_name]
            cities_to_codes[belong_city].append(code)

    print(cities_to_codes)

    return cities_to_codes



def normalize_observation(obs: dict) -> list[str]:
    '''
    Convert raw API observation dict into normalized list for display.
    '''
    return [
        obs.get("comName", "Unknown"),
        obs.get("sciName", "Unknown"),
        obs.get("locName", "Unknown"),
        str(obs.get("howMany", "No Data"))
    ]

def generate_info(area_codes):
    # generates the bird info, given the area

    # quick FYI to show user what counties are a part of the city
    areas_table = Table(title="EBird Codes")
    areas_table.add_column("County", style="green4")
    for code in area_codes:
        areas_table.add_row(code)
    console = Console()
    console.print(areas_table)

    cols = ['Name', 'Scientific Name', 'Location', 'Number']
    col_colors = ["green", "yellow", "yellow", "cyan"]
    for code in area_codes:
        reg_obs = [normalize_observation(obs) for obs in get_observations(api_key, code, back=2, max_results=3)]

        notable_obs = [normalize_observation(obs) for obs in get_notable_observations(api_key, code, max_results=3)]
    
        # pretty print tables
        table_reg_obs = Table(title="Regular Observations")
        for col, color in zip(cols, col_colors):
            table_reg_obs.add_column(col, style=color)
        for row in reg_obs:
            table_reg_obs.add_row(
                row[0],
                row[1],
                row[2],
                str(row[3])
            )

        table_notable_obs = Table(title="Notable")
        for col, color in zip(cols, col_colors):
            table_notable_obs.add_column(col, style=color)
        for row in notable_obs:
            table_notable_obs.add_row(
                row[0],
                row[1],
                row[2],
                str(row[3])
            )

        console = Console()
        console.print(table_reg_obs, table_notable_obs)
    # TODO multithread


def main():
    codes_to_counties = {} # dict to translate county codes to county names, for display later
    region_hashmap = regions_load(codes_to_counties)

    tprint("BirdLook", "big") 

    print_bird = gen_ascii_bird()
    print(print_bird.get_bird())

    while True: 
        # main interactive loop for user
        selected_option = inquirer.select(
            message="Please choose your location:",
            choices=preset_cities_options,
            instruction=default_menu_instruction,
            pointer=">",
            style=default_menu_style
        ).execute()

        if selected_option not in preset_cities_options or selected_option == 'Exit':
            print("Goodbye")
            break
        else:
            print("Another beautiful day in " + selected_option  + "\n")
            area_codes = region_hashmap[selected_option]
            generate_info(area_codes) # fn to gen bird info
            input = inquirer.select(
                message="Choose another location on exit?",
                choices=end_options,
                instruction=default_menu_instruction,
                pointer=">",
                style=default_menu_style
            ).execute()
            
            if input == 'Exit':
                break
            else:
                continue

    print("\n Thanks for visitng birdlook. Have a nice day! \n")
    sys.exit()


if __name__ == "__main__":
    main()
