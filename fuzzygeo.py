# fuzzy_geocoder.py
# Author: Mark Huberty
# Begun: 18 April 2013
# Purpose: given a list of addresses and dict of possible cities for those addresses,
# geocode at the city level for those addresses

import Levenshtein
import itertools as it
import numpy as np
import pandas as pd
import re
import time

re_numbers = re.compile('[0-9]+')
re_multispace = re.compile('\s+')

class fuzzygeo:
    """
    Implements a fuzzy geographic search from an entity database; returns
    the matched city, latitude, and longitude.
            
    city_df should be a pandas dataframe with the following columns:
    country, region, city, population, lat, lng

    hash_length defines the length of a Metaphone phonetic hash.
    Longer hashes will trade recall for precision. 
    
    Usage:
    import fuzzygeo
    geocoder = fuzzygeo.fuzzygeo(city_df=cities, hash_length=3)
    latlng = geocoder(address)
    """
    def __init__(self, city_df):

        self.city_df = city_df#.set_index('country')
        self.city_df['city_hash'] = [c[0] for c in self.city_df.city]
        self.city_df['city_ngram'] = [len(c.split(' ')) for c in self.city_df.city]

        self.country = self.city_df.country.drop_duplicates()
        if self.country == 'us':
            self.states = self.city_df.region.drop_duplicates()
            self.states = [s.lower() for s in self.states]
            state_strlist = '|'.join(self.states)
            state_regexp = '\s(%s)\s{0,}$' % state_strlist
            self.re_states = re.compile(state_regexp)
        
    def geocoder(self, addr, country, threshold):
        """
        Checks for a city name in an address. If the city is found (defined as
        found with a levenshtein ratio > threshold), returns city and lat/long.
        

        """
        addr = re_numbers.sub('', addr).strip()
        split_addr = re_multispace.split(addr)
        #addr = re.sub('^[0-9]+|[0-9]+$', '', addr).strip()
        #split_addr = re.split('[0-9]+', addr, maxsplit=1)
        # if isinstance(split_addr, str):
        #     city_chunk = re.sub('[0-9]+', '', split_addr).strip()
        # else:
        #     city_chunk = re.sub('[0-9]+', '', split_addr[-1]).strip()
        # city_chunk = re.sub('\s{2,}', ' ', city_chunk)
        # print city_chunk
        addr_candidates = split_addr #city_chunk.split(' ')
        hashed_addr = [w[0] for w in addr_candidates]
        bool_addr = self.city_df.city_hash.isin(hashed_addr)

        sub_df = self.city_df[bool_addr]

        #sub_df = region_df
        
        # If the country is United States, subset by state
        city_chunk = addr
        if country=='us':
            this_state = self.id_state(addr)

            if this_state:
                sub_df = sub_df[sub_df.region == this_state]
                city_chunk = re.sub('\s' + this_state + '\s{0,}$', '', addr)

        if sub_df.shape[0] > 0:
            city_match = self.search_city(sub_df.city.values,
                                          sub_df.city_ngram,
                                          sub_df.population.values,
                                          city_chunk,
                                          threshold
                                          )

            if city_match:
                out = [city_match,
                       sub_df.lat[sub_df.city==city_match].values[0],
                       sub_df.lng[sub_df.city==city_match].values[0]
                       ]
                return out
            
        return [None] * 3

    def find_potential_match(self, addr_ngrams, addr, c, cn, p, t):

        sims = np.fromiter([Levenshtein.ratio(ngram, c) for ngram in addr_ngrams],
                           float,
                           len(addr_ngrams)
                           )
        max_idx = np.argmax(sims)
        if sims[max_idx] >= t:
            match_idx = re.search(addr_ngrams[max_idx], addr).end()
            profile = (c, match_idx, sims[max_idx], p)
            return profile
        else:
            return None

    def find_exact_match(self, addr, cities, pops):

        matches = []
        for c, p in it.izip(cities, pops):
            if c == addr:
                return c
            else:
                _c = ' ' + c
                if _c in addr:
                    matches.append((c, p, re.search(_c, addr).end()))

        if len(matches) > 1:
            sorted_matches = sorted(matches, key=lambda k: (k[1], k[2]))
            return sorted_matches[-1][0]
        elif len(matches) == 1:
            return matches[0][0]
        else:
            return None

    def compute_address_ngrams(self, addr_split, n):
        ngrams = [' '.join(addr_split[i:i+n]) for i in range(len(addr_split))]
        return ngrams

    def search_city(self, cities, ngrams, pops, addr_string, threshold):
        """
        Searches the address string for potential city matches
        Takes the best match; if more than one match is returned,
        sorts by (1) position in string, (2) match quality, (3) population
        to disambiguate
        """
        # Here, search for each city in address ngrams
        # of length equal to that of the city name

        # exact_match = self.find_exact_match(addr_string, cities, pops)

        # if exact_match:
        #     return exact_match
        
        addr_split = addr_string.split(' ')
        unique_ngrams = ngrams.drop_duplicates()
        addr_ngrams = [self.compute_address_ngrams(addr_split, n) for n in unique_ngrams]
        addr_ngrams = dict(zip(unique_ngrams, addr_ngrams))
        potential_matches = [self.find_potential_match(addr_ngrams[cn], addr_string, c, cn, p, threshold)
                             for c,cn,p in it.izip(cities, ngrams, pops)
                             ]
        potential_matches = filter(None, potential_matches)

        # potential_matches = []
        # for c, p in zip(cities, pops):
        #     city_ngram = len(c.split(' '))
        #     addr_split = addr_string.split(' ')
        #     addr_ngrams = [' '.join(addr_split[i:(i + city_ngram)]) for i in range(len(addr_split))]
        #     sims = [Levenshtein.ratio(ngram, c) for ngram in addr_ngrams]
        #     max_idx = np.argmax(sims)
        #     if sims[max_idx] >= threshold:
        #         match_idx = re.search(addr_ngrams[max_idx], addr_string).end()
        #         profile = (c, match_idx, sims[max_idx], p)
        #         potential_matches.append(profile)

                
        if len(potential_matches) > 1:
            sorted_by = sorted(potential_matches, key=lambda k: (k[1], k[2], k[3]))
            return sorted_by[-1][0]
        elif len(potential_matches) == 1:
            return potential_matches[0][0]
        else:
            return None

    def is_us(self, addr_string):
        """
        Looks for the US state in the latter half of the string.
        Returns TRUE if found
        """
        addr_split = addr_string.split(' ')
        has_state = [True if chunk in self.states else False for chunk in addr_split]
        is_state = any(has_state)
        return is_state

    def id_state(self, addr_string):
        potential_states = self.re_states.search(addr_string)
        if potential_states:
            this_state = potential_states.group()
            return this_state.strip()
        return None

    def __call__(self, addr, country, threshold):
        out = self.geocoder(addr, country, threshold)
        return out
        
        

