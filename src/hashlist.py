import pdb

class odict(dict):
    def __init__(self, *args, **kw):
        super(odict,self).__init__(*args, **kw)
        self.itemlist = super(odict,self).keys()

    def __setitem__(self, key, value):
        """
        A few things need to happen here
        -check for existing key
        -insert in increasing order
        -removing stale keys
        """

        maxdist = 59

        #Handle updates to existing key
        if super(odict,self).has_key(key): 
            #NOTE: This is super inefficient
            #since this does a linear search
            #consider using linkedlist
            self.itemlist.remove(key)

        #insert so is ordered (increasing) by value
        if len(self.itemlist) > 0:
            if value >= self[self.itemlist[-1]]:
                self.itemlist.append(key)
            else:
                #Attach at head
                if self[self.itemlist[0]] >= value:
                    self.itemlist.insert(0, key)

                else:
                    #must attach somewhere in the middle
                    #start by moving the tail element, one over
                    self.itemlist.append(self.itemlist[-1])
                    
                    for i in range(len(self.itemlist) - 3, 0, -1):
                        #matching location found
                        #insert and break
                        if value >= self[self.itemlist[i]]:
                            self.itemlist[i+1] = key
                            break
                        else:
                            #Move the element one over
                            self.itemlist[i+1] = self.itemlist[i]

        else:
            self.itemlist.append(key)
        super(odict,self).__setitem__(key, value)

        #delete stale entries
        #NOTE: in-actual case, we would never have the case
        #where a stale entry is being inserted 
        #since that would have been checked before
        tail = self[self.itemlist[-1]]
        #index and key
        for i, k in enumerate(self.itemlist):
            #if tail - self[k] < 59:
            if (tail - self[k]).total_seconds() < 60:
                break

        #remove all elements until but excluding i
        to_remove = self.itemlist[0:i]
        self.itemlist = self.itemlist[i:]
        
        for k in to_remove:
            super(odict, self).__delitem__(k)

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
    d = odict()
    d['a'] = 1
    print d
    d['b'] = 0
    print d
    d['d'] = 2
    print d
    d['x'] = 4
    print d

