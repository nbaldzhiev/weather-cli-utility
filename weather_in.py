"""A cli utility for obtaining the current weather in a given city in the world"""
import os
import click
import json
import requests
import time
from operator import add
from functools import lru_cache
from typing import List, Dict, Union, Tuple


# reverses a dict's keys and values
reverse_dict = lambda d: dict(map(reversed, d.items()))

# converts a dict's keys and values to lowercase
lower_dict = lambda d: {k.lower(): v.lower() for k, v in d.items()}

# formats a command output message
fmsg = lambda s: s + '\n\t'


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


def get_city_id(city: str) -> Union[str, int]:
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

    found_cities = \
        [_city for _city in cities if _city['name'].lower() == city.lower()]

    get_city_id_by_name = lambda: \
        [_city['id'] for _city in cities if _city['name'].lower() == city.lower()]

    if len(found_cities) < 1:
        return f'\nError: the city of {city} has not been found!\n'
    elif len(found_cities) == 1:
        city_id = get_city_id_by_name()[0]
    elif len(found_cities) > 1:
        found_countries = [_city['country'] for _city in found_cities]
        if len(set(found_countries)) == 1:
            city_id = get_city_id_by_name()[0]
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


def call_api(url: str) -> Union[str, dict]:
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
    try:
        response = requests.get(url)
    except:
        return '\nError: call to the API service failed.'
    content = json.loads(response.content)
    if response.status_code != 200:
        return '\nError: unsuccessful call to the API service:\n\t' \
               f'{content["cod"]}, {content["message"]}.\n'
    return content


def set_output(vars_msgs: List[Tuple[bool, str]]) -> list:
    '''Creates a list with output messages depending on which options
    are set.

    Parameters
    ----------
    vars_msgs : List[Tuple[bool, str]]
        Each tuple contains a bool, indicating if an option has been set
        and a string, indicating the output message if the option is set

    Returns
    -------
    msgs : list
        Contains all the messages corresponding to the options which
        have been set.
    '''
    msgs = [elem[1] for elem in vars_msgs if elem[0]]
    return msgs


@click.command()
@click.argument('city')
@click.option('-u', '--units',
              help='[=metric, default][=imperial]', default='metric')
@click.option('-tf', '--time-format',
              help='[=12][=24, default]', default=24)
@click.option('-temp', '--temperature',
              help='Show current temperature.', is_flag=True)
@click.option('-feels', '--feels-like',
              help='Show current feels-like temperature.', is_flag=True)
@click.option('-mood', '--weather-mood',
              help='Show current weather mood.', is_flag=True)
@click.option('-min', '--min-temperature',
              help='Show current minimum temperature.', is_flag=True)
@click.option('-max', '--max-temperature',
              help='Show current maximum temperature.', is_flag=True)
@click.option('--cloudiness',
              help='Show current cloudiness.', is_flag=True)
@click.option('--pressure',
              help='Show current pressure level.', is_flag=True)
@click.option('--humidity',
              help='Show current humidity level.', is_flag=True)
@click.option('--wind-speed',
              help='Show current wind speed.', is_flag=True)
@click.option('-sunrise', '--sunrise-time',
              help='Show time of sunrise (city local time).', is_flag=True)
@click.option('-sunset', '--sunset-time',
              help='Show time of sunset (city local time).', is_flag=True)
@click.option('-v', '--verbose',
              help='Show detailed weather information.', is_flag=True)
def weather_in(city: str, units, time_format, temperature, feels_like,
               weather_mood, min_temperature, max_temperature, cloudiness,
               pressure, humidity, wind_speed, sunrise_time, sunset_time,
               verbose):
    """Shows the current weather in a given city in the world."""
    city_id = get_city_id(city)
    if type(city_id) is str:
        click.echo(city_id)
        return city_id

    api_url = build_url(city_id, units)
    result = call_api(api_url)

    if type(result) is str:
        click.echo(result)
        return result

    speed = 'meter/sec' if units == 'metric' else 'miles/hour'
    degrees = 'Celsius' if units == 'metric' else 'Fahrenheit'
    tformat = '%H:%M:%S' if time_format == 24 else '%I:%M:%S %p'

    if not any([temperature, feels_like, weather_mood, min_temperature,
                max_temperature, cloudiness, pressure, humidity, wind_speed,
                sunrise_time, sunset_time, cloudiness, verbose]):
        temperature = feels_like = weather_mood = min_temperature = \
            max_temperature = ' '
    elif verbose:
        temperature = feels_like = weather_mood = min_temperature = \
            max_temperature = cloudiness = pressure = humidity = \
            wind_speed = sunrise_time = sunset_time = ' '

    _sunrise_epoch = add(result['sys']['sunrise'], result['timezone'])
    _sunrise_time = \
        time.strftime(tformat, time.gmtime(_sunrise_epoch))

    _sunset_epoch = add(result['sys']['sunset'], result['timezone'])
    _sunset_time = \
        time.strftime(tformat, time.gmtime(_sunset_epoch))

    messages = set_output(
        [(temperature, fmsg(f"Current temperature is {result['main']['temp']} {degrees}.")),
        (feels_like, fmsg(f"Feels-like temperature is {result['main']['feels_like']} {degrees}.")),
        (weather_mood, fmsg(f"Weather mood is {result['weather'][0]['main']}.")),
        (min_temperature, fmsg(f"Minimum temperature is {result['main']['temp_min']} {degrees}.")),
        (max_temperature, fmsg(f"Maximum temperature is {result['main']['temp_max']} {degrees}.")),
        (cloudiness, fmsg(f"Cloudiness is {result['clouds']['all']}%.")),
        (pressure, fmsg(f"Pressure is {result['main']['pressure']}hPa.")),
        (humidity, fmsg(f"Humidity is {result['main']['humidity']}%.")),
        (wind_speed, fmsg(f"Wind speed is {result['wind']['speed']} {speed}.")),
        (sunrise_time, fmsg(f"Sunrise is at {_sunrise_time}.")),
        (sunset_time, fmsg(f"Sunset is at {_sunset_time}."))])

    click.echo(f'\nThe requested current weather data ' 
               f'for {city} is as follows:\n\t' + ''.join(messages))


if __name__ == '__main__':
    weather_in()
