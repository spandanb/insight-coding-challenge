"""
This contains a solution to calculating the rolling average degree of 
a twiiter hashtag graph

Author: Spandan Bemby
"""

import json
import sys
import itertools 
from dateutil import parser as dateparser
from hashlist import hashlist 

import time
import cProfile as profile


def get_hashtag_pairs(hashtags):
    """
    Returns all possible binary combinations 
    from the list of hashtags provided.
    The hashtags pairs are such that
    the lexiographically lesser hashtag is first.
    
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

def is_stale(ref, to_compare):
    """
    Determines whether to_compare is outside the 
    60 second window with respect to ref

    Arguments:
        ref:- datetime reference object
        to_compare:- the datetime object to compare
    
    Returns:-Boolean on whether to_compare is stale or not
    """

    return (ref - to_compare).total_seconds() >= 60

def average_degree(input_file_path, output_file_path):
    """
    Calculates the rolling average degree of the hashtag
    graph constructed by the tweets in input_file_path. 
    Then writes the results to output_file_path

    Arguments:
        input_file_path:- the file containing the tweets
        output_file_path:- output file to write the rolling average to
    """
    
    #The links (egdes) are represented using a hashlist
    links = hashlist()
    #The number of links.
    #This can be incrementally computed over each iteration
    link_count = 0
    #Number of unique tags
    tag_count = 0
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
        
        created_at = dateparser.parse(tweet['created_at'])

        #if this entry is outside the 60-second window, skip it
        if is_stale(newest, created_at): 
            continue

        #Determine the newest date since we can have out of order tweets
        #and the newest tweet determines which entries to evict
        newest = max(newest, created_at)

        hashtags = [hashtag['text'] for hashtag in tweet['entities']['hashtags']]
        if len(hashtags) > 1: 
            for pair in get_hashtag_pairs(hashtags):

                #Update new insertions
                if pair not in links: 
                    link_count += 1
                    entries_added = True

                #number of entries that were removed
                removed_count  = links.add_and_update(pair, created_at)
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
            
            tag_count = float(len(set(all_tags)))
        
        entries_added = False 
        entries_removed = True
        
        #calculate the average, i.e. number of incident edges/ number of nodes
        #note that the numer of incident edges = 2 * links
        if tag_count == 0:
            avg = 0
        else:
            avg = link_count * 2 / tag_count 

        #write output to file
        output_file.write(format_num(avg)) 
        
    output_file.close()

if __name__ == "__main__":
    #First argument is the input file, and the second
    #argument is the output file
    average_degree(sys.argv[1], sys.argv[2])
