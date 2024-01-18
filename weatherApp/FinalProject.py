"""
Written By Ori
Check BY Inber
"""


from flask import Flask, request, render_template
import requests
import pycountry                        # Library for mapping country code to country name (IL = Israel)
from countryinfo import CountryInfo     # Brings Me Information About Country(Israel -> Jerusalem)
from datetime import datetime

app = Flask(__name__)

base_url = "http://api.weatherbit.io/v2.0/forecast/daily"
api_key = "82389c58a75047c9bae398983db54710"


@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')


@app.route('/', methods=['POST'])
def get_weather():
    #  Get If The Client Enter City / Country
    location_type = request.form['location_type']
    #  Get The Location Value(City / Country)
    location_name = request.form['location_name']

    #  Create params for Weather API Request
    params = {
        'key': api_key,
        'days': 7
    }

    try:
        #  IF Client Enter City Name
        if location_type == "city":
            params['city'] = location_name

        # IF Client Enter Country Name , Get It's Capital City
        if location_type == "country":
            capital = CountryInfo(location_name).capital()
            params['city'] = capital

    #  Handle CountryInfo Library Exception
    except KeyError:
        return render_template('home.html', error=f"Cannot find {location_name}. Please check the spelling and try again.")

    #  Get Data From Weather Api
    response = requests.get(base_url, params=params)

    #  Handle Failure Status Code
    if response.status_code != 200:
        return render_template('home.html', error="Could not fetch weather data for the provided location.")

    #  Convert Response To Json (Dictionary)
    data = response.json()

    #  Create Data For Client
    country = pycountry.countries.get(alpha_2=data['country_code'])     # Get Country Info
    country_name = country.name if country else data['country_code']    # Set Country Name or Country Code
    country_flag = country.flag

    formatter = {
        'location_type': location_type,
        'city': data['city_name'],
        'country': country_name,
        'flag': country_flag,
        'days_data': []
    }

    #  Filter Relevant Data For Each Day In Forecast
    for day in data['data']:
        my_filter = {
            'datetime': datetime.strptime(day['datetime'], '%Y-%m-%d').strftime('%Y %B %d , %A'),
            'high_temp': day['high_temp'],
            'low_temp': day['low_temp'],
            'rh': day['rh']
        }
        formatter['days_data'].append(my_filter)

    return render_template('home.html', json_filter=formatter)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)
