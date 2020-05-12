"""A cli utility for obtaining the current weather in a given city in the world"""
import click
import json
import requests
from functools import lru_cache
from typing import List, Dict


# reverses a dict's keys and values
reverse_dict = lambda _dict: dict(map(reversed, _dict.items()))


# converts a dict's keys and values to lowercase
lower_dict = lambda _dict: {k.lower(): v.lower() for k, v in _dict.items()}


@lru_cache(maxsize=1)
def get_cities() -> List[Dict]:
    """"
    Opens and deserializes the JSON file with the world cities.

    :return cities: a list containing world cities as dictionaries
    """
    with open('cities.json', 'r') as fp:
        cities = json.load(fp)
    return cities


@lru_cache(maxsize=1)
def get_country_codes() -> dict:
    """
    Opens and deserializes the JSON file containing the country codes
    in the ISO-3166-1 alpha-2 standard.

    :return country_codes: a dict with keys countries' codes and values
                            countries' names
    """
    with open('country_codes.json', 'r') as fp:
        country_codes = json.load(fp)
    return country_codes


@lru_cache(maxsize=32)
def get_city_id(city: str) -> int or None:
    """"""
    cities = get_cities()

    found_cities = [_city for _city in cities if _city['name'].lower() == city.lower()]

    if len(found_cities) == 1:
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
                f'Multiple cities of {city} have been found.\n'
                f'Please specify a country', type=str)

            country_codes = reverse_dict(get_country_codes()) \
                if len(country) > 2 else get_country_codes()
            country_codes_lowered = lower_dict(country_codes)

            if country.lower() not in country_codes_lowered:
                click.echo(f'\nCountry {country} not found!\n'
                           'Please use country names or 2-letter codes '
                           'as defined in the ISO-3166-1 standard.\n')
                return

            country_code = country_codes_lowered[country.lower()] \
                if len(country) > 2 else country.lower()

            for _city in cities:
                if _city['name'].lower() == city.lower() and \
                        _city['country'].lower() == country_code:
                    city_id = _city['id']
                    break
    return int(city_id)


def build_url(city_id: int, units: str = 'metric') -> str:
    """Builds the url for the API call."""
    base_url = 'https://api.openweathermap.org/data/2.5/weather?'
    app_id_param = '&appid=' + '67ec56915012fdd86c56c64ff55cf048'
    city_id_param = '&id=' + str(city_id)
    units_param = '&units=' + units

    return base_url + app_id_param + city_id_param + units_param


def call_api(url: str) -> str or dict:
    """Calls the current weather API."""
    response = requests.get(url)
    if response.status_code != 200:
        return 'Error: unsuccessful call to the API service.'
    return json.loads(response.content)


@click.command()
@click.argument('city')
def weather_in(city: str):
    """Shows the current weather in a given city in the world."""
    city_id = get_city_id(city)
    if not city_id:
        click.echo(f"Couldn't find city {city}.")
        return

    api_url = build_url(city_id)
    click.echo(call_api(api_url))


if __name__ == '__main__':
    weather_in()
