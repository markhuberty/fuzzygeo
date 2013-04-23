fuzzygeo
========

`fuzzygeo` provides a fuzzy geocoding routine for geocoding at the named entity (city or similar) level. It has been built to resolve messy address and address-in-name data supplied in the [PATSTAT](http://www.epo.org/searching/subscription/raw/product-14-24.html) international patent file. It computes edit distances between city names and parsed addresses to find appropriate matches. To keep search times reasonable on long city lists, it first tries to intelligently restrict the set of possible cities using phonetic hashing. 

`fuzzygeo` requires a database of named entities matched to their latitudes and longitudes. For PATSTAT, we used the [Maxmind](http://www.maxmind.com/en/worldcities) database. But any database that can be coerced to a form `city`:`lat`:`lng` will work. 

Use
------

    import pandas as pd
    import fuzzygeo
    
    # Assumes city_db has columns city, lat, lng
    city_db = pd.read_csv('city_database.csv')
    
    geocoder = fuzzygeo.fuzzygeo(city_db, hash_length=3)
    
    address = '1234 n. clark chicago il'
    geocoded_address = geocoder(address, threshold=0.75)


Depends
-----

- [`pandas`](pandas.pydata.org)
- [`pylevenstein`](http://code.google.com/p/pylevenshtein)
- [`fuzzy`](https://pypi.python.org/pypi/Fuzzy)
- [`numpy`](http://www.numpy.org/)
    
        
