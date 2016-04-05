Overview
========
My solution to the Insight Data Science Coding Challenge.


Requirements
============
Requires python2.7 to run.


Architecture
============
This solution uses a hash table that additionally stores
the order of the entries. Specifically, the hash table maps
pairs of hashtags to the time that their mutual 'edge' was created
and orders this by these times. This allows for efficient eviction of
stale entries.


