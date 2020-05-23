"""Tests the cli functionality of the application."""
import re
import json
from click.testing import CliRunner
import pytest
import weather_in


def map_options(options: str) -> list:
    """Map the options passed to the command to expected keys names for
    the dictionary 'msgs' in function 'get_expected_data' """
    regex = [' -temp|--temp', 'feels', 'mood', 'min', 'max', 'cloud',
             'press', 'humid', 'wind', 'sunrise', 'sunset', '-tf|-f', '-u']
    target = ['temp', 'feels-like', 'mood', 'min-temp', 'max-temp',
              'cloudiness', 'pressure', 'humidity', 'wind-speed',
              'sunrise-time', 'sunset-time', 'time-format', 'units']
    mappings = list(zip(regex, target))

    mapped = lambda m: [i[1] for i in m if re.search(i[0], options)]

    return mapped(mappings)


def get_expected_data(options: str) -> str:
    """Returns the expected command output, based on the options passed
    to the command."""
    city_reg = re.search(r"^([\w]+ [\w]+)|^([\w]+)", options).groups()

    city = city_reg[0] if type(city_reg[0]) is str else city_reg[1]
    city_msg = \
        f'\nThe requested current weather data for {city} is as follows:\n\t'

    ftemp = '66.63 Fahrenheit' if 'imperial' in options else '19.24 Celsius'
    ffeels = '62.62 Fahrenheit' if 'imperial' in options else '17.01 Celsius'
    fmin = '66.2 Fahrenheit' if 'imperial' in options else '19 Celsius'
    fmax = '66.99 Fahrenheit' if 'imperial' in options else '19.44 Celsius'
    fwind = '10.29 miles/hour' if 'imperial' in options else '4.6 meter/sec'
    fsunrise = '06:00:23 AM' if '12' in options else '06:00:23'
    fsunset = '08:46:18 PM' if '12' in options else '20:46:18'

    msgs = {
        'temp': f'Current temperature is {ftemp}.',
        'feels-like': f'Feels-like temperature is {ffeels}.',
        'mood': 'Weather mood is Clouds.',
        'min-temp': f'Minimum temperature is {fmin}.',
        'max-temp': f'Maximum temperature is {fmax}.',
        'cloudiness': 'Cloudiness is 100%.',
        'pressure': 'Pressure is 1016hPa.',
        'humidity': 'Humidity is 68%.',
        'wind-speed': f'Wind speed is {fwind}.',
        'sunrise-time': f'Sunrise is at {fsunrise}.',
        'sunset-time': f'Sunset is at {fsunset}.'
    }

    mapped = map_options(options=options)

    if '-v' in options:
        output = ''.join([msgs[key] + '\n\t' for key in msgs.keys()])
    elif '-' not in options or (len(mapped) == 1 and any(list(filter(lambda x: x in 'time-format units', mapped)))):
        keys = ['temp', 'feels-like', 'mood', 'min-temp', 'max-temp']
        output = ''.join([msgs[key] + '\n\t' for key in msgs.keys() if key in keys])
    else:
        output = ''.join([msgs[op] + '\n\t' for op in mapped if op in msgs.keys()])

    return city_msg + output + '\n'


def get_weather_data(units: str = 'metric') -> dict:
    """Deserializes the test json API response, used to mock the usual
    call to the API in weather_in function in weather_in.py"""
    file = 'test_data_imp.json' if units == 'imperial' else 'test_data_met.json'
    with open(file, 'r') as fp:
        content = json.load(fp)
    return content


@pytest.mark.parametrize(
    'argument, options',
    [('Plovdiv', ''), ('sofia', '-temp'),
    ('Sevlievo', '--temperature'), ('cherven bryag', '-feels'),
    ('burgas', '--feels-like'), ('kaspichan', '-mood'),
    ('yambol', '--weather-mood'), ('loVeCh', '-min'),
    ('bear', '--min-temperature'), ('batman', '-max'),
    ('best', '--max-temperature'), ('ham lake', '--cloudiness'),
    ('apriltsi', '--pressure'), ('gabrovo', '--humidity'),
    ('Asenovgrad', '--wind-speed'), ('rila', '-sunrise'),
    ('dupnitsa', '--sunrise-time'), ('dryanovo', '-sunset'),
    ('sapareva banya', '--sunset-time'), ('smolyan', '-v'),
    ('haskovo', '--verbose'), ('plovdiv', '-tf=12'),
    ('sofia', '--time-format=12'), ('Sevlievo', '-tf=24'),
    ('cherven bryag', '--time-format=24'),
    ('yambol', '--units=imperial'), ('lovech', '--units=metric'),
    ('apriltsi', '-v --units=imperial -tf=12'), ('haskovo', '--verbose -tf=24'),
    ('rila', '-temp -min -max -feels -mood --cloudiness' \
     ' --pressure --humidity --wind-speed -sunrise -sunset')])
def test_weather_in(monkeypatch, argument, options):
    """Test the CLI functionalities of the weather_in function."""
    _options = list(options.split(' '))
    expected = get_expected_data(argument + ' ' + options)

    def mock_return(url):
        """Mocks the API call to the openweather API with an already
        prepared test API response."""
        units = 'imperial' if 'imperial' in ' '.join(_options) else 'metric'
        return get_weather_data(units=units)

    monkeypatch.setattr(weather_in, "call_api", mock_return)

    cmd_args = [argument, *_options] if any(_options) else [argument]

    runner = CliRunner()
    result = runner.invoke(weather_in.weather_in, cmd_args)
    assert result.output == expected

