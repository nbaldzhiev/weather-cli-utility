$ weather\_in
=============
.. image:: https://github.com/nbaldzhiev/weather-cli-utility/blob/master/docs/interrogate_badge.svg
 :target: https://github.com/econchick/interrogate
 :alt: Documentation Coverage

(project is used for coding practice purposes and is in no way, shape, or form finished!)

weather_in is a simple command-line interface (CLI) utility for checking current weather status
in a given city in the world. It is based on Python 3.8 and `click`_. The API service used for the
current weather data is `OpenWeatherMap`_.

.. _click: https://github.com/pallets/click
.. _OpenWeatherMap: https://openweathermap.org/current

Installing
----------
Install project's  package requirements via freeze into a virtual environment.
In order to avoid invoking the command via 'python weather_in.py' syntax each time, create a
directory-wise alias, such as:

.. code-block:: text

        alias weather_in='python3.8 weather_in.py'

In order to avoid setting this alias each time, a .env file can be incorporated using, for instance,
`autoenv`_.

.. _autoenv: https://github.com/inishchith/autoenv

An OpenWeatherMap API key is required and it must be set as an environment variable named **KEY**.
It can be obtained through a registration and a request for OpenWeatherMap's Current weather data API service (link is above).

Example usage
-------------
.. note::
    The command works with country names and 2-letter country codes based on the ISO-3166-1 standard.


.. code-block:: text

        $ weather_in sofia

    The requested current weather data for sofia is as follows:
	    Current temperature is 21.82 Celsius.
	    Feels-like temperature is 17.95 Celsius.
	    Weather mood is Rain.
	    Minimum temperature is 21.67 Celsius.
	    Maximum temperature is 22 Celsius.


.. code-block:: text

        $ weather_in 'los angeles' --units=imperial --verbose

    Multiple cities of los angeles have been found.
    Please specify a country name or 2-letter code as defined in ISO-3166-1: us

    The requested current weather data for los angeles is as follows:
        Current temperature is 64.99 Fahrenheit.
        Feels-like temperature is 60.78 Fahrenheit.
        Weather mood is Clouds.
        Minimum temperature is 59 Fahrenheit.
        Maximum temperature is 70 Fahrenheit.
        Cloudiness is 40%.
        Pressure is 1015hPa.
        Humidity is 49%.
        Wind speed is 5.55 miles/hour.
        Sunrise is at 05:48:27.
        Sunset is at 19:50:46.

Available options:

.. code-block:: text

       $ weather_in --help
    Usage: weather_in.py [OPTIONS] CITY

    Shows the current weather in a given city in the world.

    Options:
      -u, --units TEXT            [=metric, default][=imperial]
      -tf, --time-format INTEGER  [=12][=24, default]
      -temp, --temperature        Show current temperature.
      -feels, --feels-like        Show current feels-like temperature.
      -mood, --weather-mood       Show current weather mood.
      -min, --min-temperature     Show current minimum temperature.
      -max, --max-temperature     Show current maximum temperature.
      --cloudiness                Show current cloudiness.
      --pressure                  Show current pressure level.
      --humidity                  Show current humidity level.
      --wind-speed                Show current wind speed.
      -sunrise, --sunrise-time    Show time of sunrise (city local time).
      -sunset, --sunset-time      Show time of sunset (city local time).
      -v, --verbose               Show detailed weather information.
      --help                      Show this message and exit.
