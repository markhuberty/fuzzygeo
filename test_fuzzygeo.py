import fuzzygeo
import pandas as pd

#city_db = pd.read_csv('test_city_db.csv')

city_db = pd.read_csv('latlong_dict.csv')
city_db.columns = ['city', 'country', 'lat', 'lng', 'population', 'region']
chicago_addr = '1023 n. clark chacago il'
messy_addr = '1244 helsnky '
helsinki_address = '1244 helsinki'

city_db.population.fillna(0, inplace=True)
city_db['region'] = [r.lower() if isinstance(r, str) else None for r in city_db.region]

us_geocoder = fuzzygeo.fuzzygeo(city_db[city_db.country=='us'])
fi_geocoder = fuzzygeo.fuzzygeo(city_db[city_db.country=='fi'])

# Illustrate that geocoding works
chicago_latlng = us_geocoder(chicago_addr, 'us', 0.7)
helsinki_latlng = fi_geocoder(messy_addr, 'fi', 0.7)

# If we set the threshold too tight, nothing comes back
no_return = geocoder(messy_addr, 0.9)

# If we look for a city not in the database, nothing comes
# back
rio_latlng = geocoder('2342 rio de janero', 'br', 0.5)

