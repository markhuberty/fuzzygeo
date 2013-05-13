import fuzzygeo
import pandas as pd

#city_db = pd.read_csv('test_city_db.csv')

city_db = pd.read_csv('latlong_dict.csv')
city_db.columns = ['country', 'city', 'lat', 'lng', 'population']
chicago_addr = '1023 n. clark chacago il'
messy_addr = '1244 helsnky '

city_db.population.fillna(0, inplace=True)

city_us = city_db[city_db.country=='us']
city_fi = city_db[city_db.country=='fi']
us_geocoder = fuzzygeo.fuzzygeo(city_us, 4)
fi_geocoder = fuzzygeo.fuzzygeo(city_fi, 4)

# Illustrate that geocoding works
chicago_latlng = us_geocoder(chicago_addr, 0.7)
helsinki_latlng = fi_geocoder(messy_addr, 0.7)

# If we set the threshold too tight, nothing comes back
no_return = geocoder(messy_addr, 0.9)

# If we look for a city not in the database, nothing comes
# back
rio_latlng = geocoder('2342 rio de janerio brazil', 0.5)

