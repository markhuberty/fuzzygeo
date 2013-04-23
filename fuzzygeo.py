# fuzzy_geocoder.py
# Author: Mark Huberty
# Begun: 18 April 2013
# Purpose: given a list of addresses and dict of possible cities for those addresses,
# geocode at the city level for those addresses
# Does both exact and fuzzy checks for city matches to handle misspellings.
# The fuzzy matches require a hash function to hash the city names first, so that
# the comparison set is smaller. The dmetaphone hash is recommended

import Levenshtein
import fuzzy
import numpy as np
import pandas as pd
import re
import time


class fuzzygeo:
    """
    Implements a fuzzy geographic search from an entity database; returns
    the matched city, latitude, and longitude.

    city_df should be a pandas dataframe of form city:lat:lng.
    hash_length defines the length of a Metaphone phonetic hash. Longer hashes will trade recall
      for precision. 
    
    Usage:
    import fuzzygeo
    geocoder = fuzzygeo.fuzzygeo(city_df=cities, hash_length=3)
    latlng = geocoder(address)
    """
    def __init__(self, city_df, hash_length):
        self.hashfun = fuzzy.DMetaphone(hash_length)
        self.city_df = city_df
        self.city_df['city_hash'] = [self.hashfun(c)[0] for c in self.city_df.city]
        

    def geocoder(self, addr, threshold):
        """
        Checks for a city name in an address. If the city is found (defined as
        found with a levenshtein ratio > j_threshold), returns city and lat/long.
        
        city_df should be a pandas dataframe of form
        city / city_hash / lat / lng. city and address should be case-aligned.
    
        The city hash should be generated from the same hash function that is passed
        as hashfun.
        
        """

        addr = re.sub('^[0-9]+|[0-9]+$', '', addr)
        split_addr = re.split('[0-9]+', addr)
        city_chunk = re.sub('[0-9]+', '', split_addr[-1]).strip()
        addr_candidates = city_chunk.split(' ')
        hashed_addr = [self.hashfun(w)[0] for w in addr_candidates]

        sub_df = self.city_df[self.city_df.city_hash.isin(hashed_addr)]
        
        
        if sub_df.shape[0] > 0:
            city_match = self.search_city(sub_df.city.values,
                                          city_chunk,
                                          threshold
                                          )

            if city_match:
                out = [city_match,
                       self.city_df.lat[self.city_df.city==city_match].values[0],
                       self.city_df.lng[self.city_df.city==city_match].values[0]
                       ]
            else:
                out = [None] * 3
        else:
            out = [None] * 3
        return out

    def search_city(self, cities, addr_string, threshold):
        sims = [Levenshtein.ratio(addr_string, c) for c in cities]
        max_idx = np.argmax(sims)
        if sims[max_idx] >= threshold:
            return cities[max_idx]
        else:
            return None

    def __call__(self, addr, threshold):
        out = self.geocoder(addr, threshold)
        return out
        
        

