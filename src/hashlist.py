
class hashlist(dict):
    """
    This class provides an ordered dictionary with
    an age based eviction policy.
    The keys are sorted (in increasing order) by the corresponding value.
    
    When an insert happens the entry is inserted 
    in order to maintain ordering among the values. 
    In addition, stale entries are evicted.  
    
    Typical usage would be where keys are hashtag
    pairs and values are the dates.
    """
    def __init__(self, *args, **kw):
        super(hashlist,self).__init__(*args, **kw)
        #itemlist is an ordered list of keys
        self.itemlist = super(hashlist,self).keys()
        #the maximum age of an entry compared to the youngest entry   
        self.maxstep = 60

    def evict_entries(self, ref):
        """
        deletes stale entries with
        respect to ref, i.e. those entries whose
        value is less than ref by more than or equal
        to maxstep 

        Arguments:
            ref:- reference value to compare the other values with

        Returns: 
            number of elements deleted
        """
        
        #index and key
        for i, k in enumerate(self.itemlist):
            #if ref - self[k] < self.maxstep:
            if (ref - self[k]).total_seconds() < self.maxstep:
                break
        else:
            #if a break didn't happen must delete the whole list
            i = len(self.itemlist)
        
        #remove all elements until but excluding i
        to_remove = self.itemlist[0:i]
        self.itemlist = self.itemlist[i:]
        
        for k in to_remove:
            super(hashlist, self).__delitem__(k)

        return len(to_remove)

    def add_and_update(self, key, value):
        """
        Convenience method that calls __setitem__ and evict_entries

        Arguments:-
            key: key of new entry to dict
            value: value of new entry to dict

        Returns: number of elements evicted
        """
        self.__setitem__(key, value)

        #NOTE: eviction must happen after the set operation
        tail = self[self.itemlist[-1]]
        return self.evict_entries(tail)

    def __setitem__(self, key, value):
        """
        Sets the key, value pair. The insertions
        maintain order with regards to values, i.e.
        the tail has the highest value and the head 
        has the lowest value.

        Arguments:-
            key: key of new entry to dict
            value: value of new entry to dict
        """

        #Handle updates to existing key
        #remove key from its old location so it can 
        #be added to new location
        if super(hashlist, self).has_key(key): 
            #NOTE: This does a linear search 
            #consider using linkedlist
            self.itemlist.remove(key)

        #insert so ordering of values is preserved
        #insert at the tail of the list if list is empty 
        #or if this entry has the highest value
        if not self.itemlist or value >= self[self.itemlist[-1]]:
            self.itemlist.append(key)

        #insert at head of the list
        elif self[self.itemlist[0]] >= value:
            self.itemlist.insert(0, key)

        #must attach somewhere in the middle
        else:
            #start by moving the tail element, one over
            self.itemlist.append(self.itemlist[-1])
            
            #start from the tail end of the list and find the correct
            #location to insert the key
            #the idx of last element is __len__ -1
            #the list was extended by 1, so to access last element would be __len__ -2
            #to access the second last element is therefore __len__ -3
            for i in range(len(self.itemlist) - 3, 0, -1):
                #matching location found
                #insert and break
                if value >= self[self.itemlist[i]]:
                    self.itemlist[i+1] = key
                    break
                else:
                    #Move the element one over
                    self.itemlist[i+1] = self.itemlist[i]

        super(hashlist,self).__setitem__(key, value)


    def __iter__(self):
        return iter(self.itemlist)
    def keys(self):
        return self.itemlist
    def values(self):
        return [self[key] for key in self]  
    def itervalues(self):
        return (self[key] for key in self)

    def __repr__(self):
        return "{}".format([ "{}: {}".format(key, self[key]) for key in self])

if __name__ == "__main__":
    d = hashlist()
    d['a'] = 1
    print d
    d['b'] = 0
    print d
    d['d'] = 2
    print d
    d.evict_entries(70)
    print d

