import os
import sys
import logging
from InquirerPy import inquirer
from InquirerPy.utils import get_style
from rich.console import Console
from rich.table import Table
from art import tprint
import random
from ascii_birds import birds # own other file with ascii birds
from config import CITY_TO_COUNTIES, COUNTIES_TO_CITIES, COLS, COL_COLORS
from functools import lru_cache
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
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

load_dotenv()
API_KEY = os.getenv("EBIRD_API_KEY")

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
DEFAULT_MENU_INSTRUCTION = "Arrow keys to move, enter to submit"
console_lock = threading.Lock() # global lock for console output in multithreaded table action
console = Console()

class gen_ascii_bird():
    # generates an ascii bird
    def __init__(self):
        rand_index = random.randint(0, len(birds)-1)
        self.bird = birds[rand_index]
    
    def get_bird(self):
        return self.bird


@lru_cache(maxsize=None)
def cached_get_regionds(api_key: str, level: str, region_code: str) -> list[str]:
    return get_regions(api_key, level, region_code)


def regions_load(codes_to_counties) -> dict[str,list]: # returns cities to codes hashmap
    relevant = {'Ottawa', 'Waterloo', 'Kings', 'Queens', 'New York', 'Bronx', 'Richmond', 'San Francisco', 'San Mateo', 'Marin', 'Multnomah', 'Washington'}
    cities_to_codes = {city : [] for city in preset_cities_options}

    # get list of relevant US counties
    counties = get_regions(API_KEY, 'subnational2', 'US-OR') + get_regions(API_KEY, 'subnational2', 'US-CA') + get_regions(API_KEY, 'subnational2', 'US-NY')
    for county in counties:
        county_name = county['name']
        code = county['code']
        codes_to_counties[code] = county_name
        if county_name in relevant:
            belong_city = COUNTIES_TO_CITIES[county_name]
            cities_to_codes[belong_city].append(code)

    # get list of subregions in Ontario
    sub_regions = get_regions(API_KEY, 'subnational2', 'CA-ON')
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

# need to split fetching and rendering into 2 diff functions for generate_info
def fetch_area_code_observations(code: str) -> tuple[str, list[list[str]], list[list[str]]]:
    reg_obs = [normalize_observation(obs) for obs in get_observations(API_KEY, code, back=2, max_results=3)]
    notable_obs = [normalize_observation(obs) for obs in get_notable_observations(API_KEY, code, max_results=3)]
    return code, reg_obs, notable_obs

def render_area_code_observations(area_code: str, reg_obs: list[list[str]], notable_obs: list[list[str]]) -> None:
    '''
    Does not return a value, but outputs the pretty tables to terminal display.
    Recovers gracefully if output error.
    '''
    try:
        def build_table(name : str, observations: list[list[str]]) -> Table:
            built_table = Table(title=name)
            for col, color in zip(COLS, COL_COLORS):
                built_table.add_column(col, style=color)
            for row in observations:
                built_table.add_row(
                    row[0],
                    row[1],
                    row[2],
                    str(row[3])
                )
            return built_table

        table_reg_obs = build_table("Regular Observations", reg_obs)
        table_notable_obs = build_table("Notable observations", notable_obs)
        with console_lock:
            console.print(f"Streaming Results for {area_code}")
            console.print(table_reg_obs, table_notable_obs)
    except:
        logging.warning(f"failed to print to output for {area_code}")

def counties_in_city_table(area_codes: list[str]) -> Table:
    # quick FYI to show user what counties are a part of the city
    areas_table = Table(title="EBird Codes for this City")
    areas_table.add_column("County", style="green4")
    for code in area_codes:
        areas_table.add_row(code)
    
    return areas_table


def generate_info(area_codes : list[str]) -> None:
    '''
    args: list of area codes to generate info from
    returns: None
    side effect: writes to console, multiple threads
    '''

    areas_table = counties_in_city_table(area_codes)
    with console_lock:
        console.print(areas_table)

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(fetch_area_code_observations, code) for code in area_codes]
        for future in as_completed(futures):
            code, reg_obs, notable_obs = future.result()
            render_area_code_observations(code, reg_obs, notable_obs)

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
            instruction=DEFAULT_MENU_INSTRUCTION,
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
            user_input = inquirer.select(
                message="Choose another location on exit?",
                choices=end_options,
                instruction=DEFAULT_MENU_INSTRUCTION,
                pointer=">",
                style=default_menu_style
            ).execute()
            
            if user_input == 'Exit':
                break
            else:
                continue

    print("\n Thanks for visitng birdlook. Have a nice day! \n")
    sys.exit()


if __name__ == "__main__":
    main()
