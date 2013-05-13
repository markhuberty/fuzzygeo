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
        split_addr = re.split('[0-9]+', addr, maxsplit=1)
        if isinstance(split_addr, str):
            city_chunk = re.sub('[0-9]+', '', split_addr).strip()
        else:
            city_chunk = re.sub('[0-9]+', '', split_addr[-1]).strip()
        # print city_chunk
        addr_candidates = city_chunk.split(' ')
        hashed_addr = [self.hashfun(w)[0] for w in addr_candidates]

        sub_df = self.city_df[self.city_df.city_hash.isin(hashed_addr)]
        
        
        if sub_df.shape[0] > 0:
            city_match = self.search_city(sub_df.city.values,
                                          sub_df.population.values,
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

    def search_city(self, cities, pops, addr_string, threshold):
        """
        Searches the address string for potential city matches
        Takes the best match; if more than one match is returned,
        sorts by (1) position in string, (2) match quality, (3) population
        to disambiguate
        """
        # Here, search for each city in address ngrams
        # of length equal to that of the city name
        potential_matches = []
        for c, p in zip(cities, pops):
            city_ngram = len(c.split(' '))
            addr_split = addr_string.split(' ')
            addr_ngrams = [' '.join(addr_split[i:(i + city_ngram)]) for i in range(len(addr_split))]
            ngrams, sims = zip(*[(ngram,Levenshtein.ratio(ngram, c)) for ngram in addr_ngrams])
            max_idx = np.argmax(sims)
            if sims[max_idx] >= threshold:
                print ngrams[max_idx]
                print addr_string
                match_idx = re.search(ngrams[max_idx], addr_string).end()
                profile = (c, match_idx, sims[max_idx], p)
                potential_matches.append(profile)

                
        if len(potential_matches) > 1:
            print potential_matches
            sorted_by = sorted(potential_matches, key=lambda k: (k[1], k[2], k[3]))
            return sorted_by[-1][0]
        elif len(potential_matches) == 1:
            return potential_matches[0][0]
            return cities[max_idx]
        else:
            return None

    def __call__(self, addr, threshold):
        out = self.geocoder(addr, threshold)
        return out
        
        

