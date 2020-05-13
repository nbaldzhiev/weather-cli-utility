"""A cli utility for obtaining the current weather in a given city in the world"""
import os
import click
import json
import requests
from functools import lru_cache
from datetime import datetime
from typing import List, Dict


# reverses a dict's keys and values
reverse_dict = lambda _dict: dict(map(reversed, _dict.items()))


# converts a dict's keys and values to lowercase
lower_dict = lambda _dict: {k.lower(): v.lower() for k, v in _dict.items()}


@lru_cache(maxsize=1)
def get_cities() -> List[Dict]:
    """"Opens and deserializes the JSON file with the world cities.

    Returns
    -------
    cities : List[Dict]
        A list containing world cities as dictionaries.
    """
    with open('cities.json', 'r') as fp:
        cities = json.load(fp)
    return cities


@lru_cache(maxsize=1)
def get_country_codes() -> dict:
    """Opens and deserializes the JSON file containing the country names
    and codes in the ISO-3166-1 alpha-2 standard.

    Returns
    -------
    country_codes : dict
        A dict with 2-letter country codes as keys and country names
        as values. Country names and 2-letter codes as based on ISO-3166-1.
    """
    with open('country_codes.json', 'r') as fp:
        country_codes = json.load(fp)
    return country_codes


@lru_cache(maxsize=32)
def get_city_id(city: str) -> int or str:
    """Retrieves the id for a given city or city + country pair.

    Parameters
    ----------
    city : str
        The name ot the city.

    Returns
    -------
    city_id : int
        The id of the city.
    str
        Description of an error message in case id was not retrieved.
    """
    cities = get_cities()

    found_cities = [_city for _city in cities if _city['name'].lower() == city.lower()]

    if len(found_cities) < 1:
        return f'\nError: the city of {city} has not been found!\n'
    elif len(found_cities) == 1:
        for _city in cities:
            if _city['name'].lower() == city.lower():
                city_id = _city['id']
    elif len(found_cities) > 1:
        found_countries = [_city['country'] for _city in found_cities]

        if len(set(found_countries)) == 1:
            for _city in cities:
                if _city['name'].lower() == city.lower():
                    city_id = _city['id']
        elif len(set(found_countries)) > 1:
            country = click.prompt(
                f'\nMultiple cities of {city} have been found.\n'
                'Please specify a country name or 2-letter code '
                'as defined in ISO-3166-1', type=str)

            country_codes = reverse_dict(get_country_codes()) \
                if len(country) > 2 else get_country_codes()
            country_codes_lowered = lower_dict(country_codes)

            if country.lower() not in country_codes_lowered:
                return(f'\nError: Country {country} not found!\n'
                        'Please use country names or 2-letter codes '
                        'as defined in the ISO-3166-1 standard.\n')

            country_code = country_codes_lowered[country.lower()] \
                if len(country) > 2 else country.lower()

            for _city in cities:
                if _city['name'].lower() == city.lower() and \
                        _city['country'].lower() == country_code:
                    city_id = _city['id']
                    break
            else:
                return (f'\nError: The city of {city} has not been found'
                        f'in the country of {country}!\n')

    return int(city_id)


def build_url(city_id: int, units: str = 'metric') -> str:
    """Builds the url for the current weather API call.

    Parameters
    ----------
    city_id : int
        Id of the city retrieved by get_city_id().
    units : str, 'metric'
        The units system to use - 'metric' or 'imperial'.

    Returns
    -------
    str
        The full API url to call.
    """
    base_url = 'https://api.openweathermap.org/data/2.5/weather?'
    app_id_param = '&appid=' + os.environ.get('KEY')
    city_id_param = '&id=' + str(city_id)
    units_param = '&units=' + units

    return base_url + app_id_param + city_id_param + units_param


def call_api(url: str) -> str or dict:
    """Calls the current weather API.

    Parameters
    ----------
    url : str
        API's url.

    Returns
    -------
    dict
        A deserialized JSON with the API's response content.
    str
        An error message in the case of an unsuccessful request.
    """
    response = requests.get(url)
    if response.status_code != 200:
        return 'Error: unsuccessful call to the API service.'
    return json.loads(response.content)


@click.command()
@click.argument('city')
@click.option('-u', '--units',
              help='[=metric][=imperial].', default='metric')
@click.option('-temp', '--temperature',
              help='Show current temperature.', is_flag=True)
@click.option('-feels', '--feels-like',
              help='Show current feels-like temperature.', is_flag=True)
@click.option('-min', '--min-temperature',
              help='Show current minimum temperature.', is_flag=True)
@click.option('-max', '--max-temperature',
              help='Show current maximum temperature.', is_flag=True)
@click.option('--pressure',
              help='Show current pressure level.', is_flag=True)
@click.option('--humidity',
              help='Show current humidity level.', is_flag=True)
@click.option('-sunrise', '--sunrise-time',
              help='Show time of sunrise (city local time).', is_flag=True)
@click.option('-sunset', '--sunset-time',
              help='Show time of sunset (city local time).', is_flag=True)
@click.option('-v', '--verbose',
              help='Show detailed weather information.', is_flag=True)
def weather_in(city: str, units, temperature, feels_like, min_temperature,
               max_temperature, pressure, humidity, sunrise_time,
               sunset_time, verbose):
    """Shows the current weather in a given city in the world."""

    city_id = get_city_id(city)
    if type(city_id) is str:
        click.echo(city_id)
        return

    api_url = build_url(city_id, units)
    result = call_api(api_url)

    if type(result) is str:
        click.echo(result)
        return

    output = f'\nThe requested current weather data (in the {units} system) ' \
             f'for {city} is as follows:\n\t'

    if not any([temperature, feels_like, min_temperature, max_temperature,
                pressure, humidity, sunrise_time, sunset_time, verbose]):
        temperature = feels_like = min_temperature = max_temperature = ' '
    elif verbose:
        temperature = feels_like = min_temperature = max_temperature = \
            pressure = humidity = sunrise_time = sunset_time = ' '

    if temperature:
        output += \
            f"Current temperature is {result['main']['temp']}.\n\t"
    if feels_like:
        output += \
            f"Feels-like temperature is {result['main']['feels_like']}.\n\t"
    if min_temperature:
        output += \
            f"Minimum temperature is {result['main']['temp_min']}.\n\t"
    if max_temperature:
        output += \
            f"Maximum temperature is {result['main']['temp_max']}.\n\t"
    if pressure:
        output += \
            f"Pressure is {result['main']['pressure']}.\n\t"
    if humidity:
        output += \
            f"Humidity is {result['main']['humidity']}.\n\t"
    if sunrise_time:
        _sunrise_epoch = result['sys']['sunrise']
        _sunrise_time = \
            datetime.fromtimestamp(_sunrise_epoch).strftime("%H:%M:%S")
        output += f"Sunrise is at {_sunrise_time}.\n\t"
    if sunset_time:
        _sunset_epoch = result['sys']['sunset']
        _sunset_time = \
            datetime.fromtimestamp(_sunset_epoch).strftime("%H:%M:%S")
        output += f"Sunset is at {_sunset_time}.\n\t"

    click.echo(output)


if __name__ == '__main__':
    weather_in()
