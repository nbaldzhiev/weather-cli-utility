""""""
from typing import List, Tuple, Dict
import io
import pytest
from weather_in import get_city_id


def input_output_data(test_name: str) -> List[Tuple]:
    """Input and output for the test functions."""
    c_sc_pos_data = [
        ('Sofia', 727011), ('sofia', 727011),
        ('sOfIa', 727011), ('Gorna Oryahovitsa', 731233),
        ('gorna oryahovitsa', 731233), ('gOrNa oRyAhOvItSa', 731233),
        ('newcastle upon tyne', 2641673),
        ('Livarpol',
         '\nError: the city of Livarpol has not been found!\n'),
        ('New iork',
         '\nError: the city of New iork has not been found!\n')
    ]

    c_mc_pos_data = [
        ('Paris', 'France', 2968815),
        ('paris', 'france', 2968815),
        ('pArIs', 'fRaNcE', 2968815),
        ('London', 'United Kingdom', 2643743),
        ('london', 'united kingdom', 2643743),
        ('lOnDon', 'uNiTeD kInGdOm', 2643743),
        ('Paris', 'FR', 2968815), ('paris', 'fr', 2968815),
        ('London', 'GB', 2643743), ('london', 'gb', 2643743),
        ('Paris', 'Bulgaria',
        '\nError: The city of Paris has not been foundin the country of Bulgaria!\n'),
        ('Los Angeles', 'United Kingdom',
        '\nError: The city of Los Angeles has not been foundin the country of United Kingdom!\n'),
        ('liverpool', 'de',
        '\nError: The city of liverpool has not been foundin the country of de!\n')
    ]

    c_sc_neg_data = [
        (' ', '\nError: the city of   has not been found!\n'),
        ('1234567', '\nError: the city of 1234567 has not been found!\n'),
        ('!@#$%^*', '\nError: the city of !@#$%^* has not been found!\n'),
        (' 12$%^Az', '\nError: the city of  12$%^Az has not been found!\n')
    ]

    c_mc_neg_data = [
        ('vienna', ' ', 'Error: Country   not found!'),
        ('London', '1234567', 'Error: Country 1234567 not found!'),
        ('los angeles', '!@#$%^*', 'Error: Country !@#$%^* not found!'),
        ('paris', ' 12$%^Az', 'Error: Country  12$%^Az not found!')
    ]

    data: Dict[str, List[Tuple]] = {
        'c_sc_pos': c_sc_pos_data,
        'c_mc_pos': c_mc_pos_data,
        'c_sc_neg': c_sc_neg_data,
        'c_mc_neg': c_mc_neg_data
    }

    return data[test_name]


@pytest.mark.positives
@pytest.mark.parametrize("city_name, expected",
                         input_output_data('c_sc_pos'))
def test_city_in_single_country_pos(city_name: str, expected: int):
    """Tests get_city_id() with name of cities, which
    exist in only one country, and with name of cities with a typo,
    which do not exist."""
    assert get_city_id(city_name) == expected


@pytest.mark.positives
@pytest.mark.parametrize("city_name, country_name, expected",
                         input_output_data('c_mc_pos'))
def test_city_in_multiple_countries_pos(city_name:str , country_name: str,
                                        expected: int, monkeypatch):
    """Tests get_city_id() with name of cities, which exist in more than
    one countries; verifies that the function works with countries, which
    contain the city, do not contain the city, or do not exist (i.e. due
    to a typo).
    Also tests if get_city_id() can work with both full country names
    and 2-letter country codes, according to ISO 3166-1 standard."""
    monkeypatch.setattr('sys.stdin', io.StringIO(country_name))
    assert get_city_id(city_name) == expected


@pytest.mark.negatives
@pytest.mark.parametrize("city_name, expected",
                         input_output_data('c_sc_neg'))
def test_city_in_single_country_neg(city_name: str, expected: str):
    """Tests get_city_id() with invalid city names."""
    assert get_city_id(city_name) == expected


@pytest.mark.negatives
@pytest.mark.parametrize("city_name, country_name, expected",
                         input_output_data('c_mc_neg'))
def test_city_in_multiple_countries_neg(city_name: str, country_name: str,
                                        expected: str, monkeypatch):
    """Tests get_city_id() with invalid country names."""
    monkeypatch.setattr('sys.stdin', io.StringIO(country_name))
    assert expected in get_city_id(city_name)

