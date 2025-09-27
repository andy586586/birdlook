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