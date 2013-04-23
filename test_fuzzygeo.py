import fuzzygeo
import pandas as pd

city_db = pd.read_csv('test_city_db.csv')

chicago_addr = '1023 n. clark chicago il'
messy_addr = '1244 helsnky finland'


geocoder = fuzzygeo.fuzzygeo(city_db, 3)

# Illustrate that geocoding works
chicago_latlng = geocoder(chicago_addr, 0.5)
helsinki_latlng = geocoder(messy_addr, 0.5)

# If we set the threshold too tight, nothing comes back
no_return = geocoder(messy_addr, 0.9)

# If we look for a city not in the database, nothing comes
# back
rio_latlng = geocoder('2342 rio de janerio brazil', 0.5)

