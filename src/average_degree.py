"""
This contains a solution to calculating the rolling average degree of 
a twiiter hashtag graph

Author: Spandan Bemby
"""

#TODO remove
import json 
import pprint
import pdb

import time
import cProfile as profile

import sys
import itertools 
from dateutil import parser as dateparser
from hashlist import hashlist 


def get_hashtag_pairs(hashtags):
    """
    Returns all possible binary combinations 
    from the list of hashtags provided.
    The hashtags pairs are such that
    the lexiographically lesser string is first.
    
    Arguments:
        hashtags:- list of hashtag strings
    
    Returns:
        iterator over all possible pairs of hashtags
    """
    hashtags = sorted(hashtags)
    return itertools.combinations(hashtags, 2)

def format_num(num):
    """
    Takes a number an returns a
    formatted string of that number. 
    Formatting includes:
        -truncating to 2 decimal places
        -padding with zeros to hundreths 
        -appends newline

    Arguments: 
        num: float to be format
    Returns
        string of formatted number
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

def main(input_file_path, output_file_path):
    
    #The links (egdes) are represented using a hashlist
    links = hashlist()
    #The number of unique links.
    #This can be incrementally computed over each iteration
    link_count = 0
    #For this to work, you need either:
    #1) keep a separate representation of individual tags in a separate dict
    #2) or have a data structure that can do partial matches, i.e. on the first tag or second tag. Perhaps a generalized trie
    unique_count = 0
    entries_added = False 
    entries_removed = True

    #The output file to write to
    output_file = open(output_file_path, 'w')

    #Newest timestamp, initialize to epoch
    newest = dateparser.parse("Jan 1 0:0:0 +0000 1970")

    for tweet_str in open(input_file_path):

        tweet = json.loads(tweet_str)

        #check if this is an actual tweet
        if 'created_at' not in tweet:
            continue
        
        date = dateparser.parse(tweet['created_at'])

        #Determine the newest date
        newest = max(newest, date)

        hashtags = [hashtag['text'] for hashtag in tweet['entities']['hashtags']]
        if len(hashtags) > 1: 
            for pair in get_hashtag_pairs(hashtags):

                #Update new insertions
                if pair not in links: 
                    link_count += 1
                    entries_added = True

                #number of entries that were removed
                removed_count  = links.add_and_update(pair, date)
                link_count -= removed_count
                entries_removed = removed_count != 0
    
        else:
            #explicitly evict entries 
            #since automatic eviction only happens on insert
            removed_count = links.evict_entries(newest)
            link_count -= removed_count 
            entries_removed = removed_count != 0
                
        #Entries were evicted and/or added
        #recalculate the number of unique tags
        if entries_removed or entries_added:
            #list of all tags in all pairings
            all_tags = [tag for pair in links.keys() for tag in pair]
            
            unique_count = float(len(set(all_tags)))
        
        entries_added = False 
        entries_removed = True
        
        #calculate the average, i.e. number of links / number of nodes
        if unique_count == 0:
            avg = 0
        else:
            avg = link_count * 2 / unique_count 

        #print("{}        {}        {}".format(unique_count, len(valid), format_num2(avg)))
        #print("{}".format(format_num2(avg))) #Actual output
        
        #write output to file
        output_file.write(format_num(avg)) 

    output_file.close()

if __name__ == "__main__":
    
    if len(sys.argv) == 3:
        start_time = time.time()
        main(sys.argv[1], sys.argv[2])
        print("--- %s seconds ---" % (time.time() - start_time))
        #profile.run('main(input_file=sys.argv[1], output_file=sys.argv[2])')
    else:
       print "Invalid Number of arguments"
       sys.exit(1)

