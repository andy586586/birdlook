CITY_TO_COUNTIES = {
    "Ottawa": ["Ottawa"],
    "Waterloo": ["Waterloo"],
    "New York City": ["Kings", "Queens", "New York", "Bronx", "Richmond"],
    "San Francisco": ["San Francisco", "San Mateo", "Marin"],
    "Portland": ["Multnomah", "Washington"]
}

COUNTIES_TO_CITIES = {
     county: city for city, counties in CITY_TO_COUNTIES.items() for county in counties
}


# for printing tables with colours:
COLS = ['Name', 'Scientific Name', 'Location', 'Number']
COL_COLORS = ["green", "yellow", "yellow", "cyan"]

RELEVANT_COUNTIES = {'Ottawa', 'Waterloo', 'Kings', 'Queens', 'New York', 'Bronx', 'Richmond', 'San Francisco', 'San Mateo', 'Marin', 'Multnomah', 'Washington'}

HIDDEN_REGION_1 = 'US-OR'
HIDDEN_REGION_2 = 'US-CA'
HIDDEN_REGION_3 = 'US-NY'
HIDDEN_REGION_4 = 'CA-ON'


PRESET_CITIES_OPTIONS = ['Ottawa', 'Waterloo', 'New York City', 'San Francisco', 'Portland', 'Exit']
END_MENU_OPTIONS = ['Other city', 'Exit']

set_ver_num = "0.1.2"
