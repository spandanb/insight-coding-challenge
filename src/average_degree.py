

import json 
import pprint

import pdb
import sys
import itertools 

from dateutil import parser as dateparser
import datetime
from collections import OrderedDict

import time
import cProfile as profile

"""
Some observations:
    ratio of new hashtags pairs to old hashtag pairs= 1:8
    -therefore, makes sense to drop stale hashtags
    -also a linear search on existing hashtags may not be a bad idea
    
    out of order to in-order tweets: 1:10
    -therefore, it makes sense to store tweets ordered by time, since out of order packets are infrequent
    and negligible amount are outside 60second window
    -therefore checking for this and skipping a loop iteration will have negligible gains, albeit no cost either
   
    each iteration, 0.12 entries are invalidated and removed

"""

def printobj(obj):
    print json.dumps(obj, sort_keys=True, indent=4)
    #pprint.pprint(obj)

def get_tweets(filepath):
    """
    Returns a tweets generator 
    Assumes tweets are at filepath
    Can be modified to handle other streams as well
    """
    return open(filepath)

def is_stale(ref, to_compare):
    """
    Returns true if `to_compare` is stale given `ref`, 
    i.e. `to_compare` is older than ref
    by more than or equal to 60 seconds.
    to_compare can be newer than ref
    """
    return (ref-to_compare).total_seconds() >= 60

def get_pairs(hashtags):
    """
    Takes a list of hashtags and
    returns a list of pairs of hashtags
    the pair is s.t. ai < aj -> "ai aj" 
    """
    hashtags = sorted(hashtags)
    return list(itertools.combinations(hashtags, 2))

def pair_to_key(pair):
    return u"{} {}".format(pair[0], pair[1])

def key_to_pair(key):
    return key.split(" ")

def newer(d1, d2):
    """
    returns the newer datetime object
    """
    return max(d1, d2)

def format_num(num):
    """
    returns str repr of num
    Does:
        -truncates to 2 decimal places
        -pads with zeros 
        -append newline
    """
    return "{:.2f}\n".format(int(num * 100)/100.0)

def format_num2(num):
    """
    returns str repr of num
    Does:
        -truncates to 2 decimal places
        -pads with zeros 
    """
    return "{:.2f}".format(int(num * 100)/100.0)


def main(input_file='../tweet_input/tweets4.txt', 
         output_file='../tweet_output/output.txt'):
    
    links = {}

    outfile = open(output_file, 'w')

    #Newest tweet, initialize to epoch
    newest = dateparser.parse("Jan 1 0:0:0 +0000 1970")

    #average number of invalidations per cycle
    invcount = 0
    i=0

    for tweet_str in get_tweets(input_file):

        #Step 1: Update the links
        tweet = json.loads(tweet_str)

        if 'created_at' not in tweet:
            continue
        
        date = dateparser.parse(tweet['created_at'])
        
        #Determine the newest
        newest = newer(newest, date)

        hashtags = [hashtag['text'] for hashtag in tweet['entities']['hashtags']]
        if len(hashtags) > 1: 
            for pair in get_pairs(hashtags):
                pkey = pair_to_key(pair)
                links[pkey] = date 
        else:
            pass
            #print hashtags
       
#        #Step 2: invalidate stale entries
#        #these are valid pairs
#        valid = [ pair for pair, date in links.items() 
#                    if not is_stale(newest, date)]
#        
#        #this can be combined with the above
#        #keep it separate for readability for now
#        #separates pairs into individual tags 
#        #equivalent to, but  supposedly faster, but this splits the string
#        valid = [tag for pair in valid for tag in key_to_pair(pair)]

        oldlen = len(links) 
        #This is an alternate approach to above
        #This one performs better for larger datasets
        links = { pair: date for pair, date in links.items() 
                    if not is_stale(newest, date)}

        newlen = len(links)

        invcount += oldlen - newlen
        i += 1

        valid = [tag for pair in links.keys() for tag in key_to_pair(pair)]

        unique_count = float(len(set(valid)))
        if unique_count == 0:
            avg = 0
        else:
            avg = len(valid) / unique_count 

        #print("{}        {}        {}".format(unique_count, len(valid), format_num2(avg)))
        #print("{}".format(format_num2(avg))) #Actual output
        
        #write output to file
        outfile.write(format_num(avg)) 

    print "Average invalidation count: {}".format(invcount / float(i))

if __name__ == "__main__":
    

    if len(sys.argv) == 3:
        start_time = time.time()
        main(input_file=sys.argv[1], output_file=sys.argv[2])
        print("--- %s seconds ---" % (time.time() - start_time))
        #profile.run('main(input_file=sys.argv[1], output_file=sys.argv[2])')
    else:
       print "Invalid Number of arguments"
       sys.exit(1)

