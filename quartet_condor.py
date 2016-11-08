#quartet_condor.py
#version 2.0.2

import random, sys


def addToDict(d):
    '''
    Ensures each quartet has three concordance factors (CFs)
    a dictionary d has less than three CFs, add CFs with the value 0 until there are three
    Input: a dictionary containing CFs, a counter of how many CFs are in the dictionary
    '''
    if ("{1,2|3,4}" not in  d):
        d["{1,2|3,4}"] = 0.0
    if ("{1,3|2,4}" not in d):
        d["{1,3|2,4}"] = 0.0
    if ("{1,4|2,3}" not in d):
        d["{1,4|2,3}"] = 0.0

class quartet:
    '''
    Picks individual quartets and isolates concordance factors
    '''
    def __init__(self):
        #length of a split in *.concordance file
        self.length_of_splits = 10
        self.quartet_length = 4
        #list to hold the 4 taxa
        self.taxa = []
        #dictionaries to hold cfs with splits
        self.d = {}
        self.d2 = {}


    def pick_random_quartet(self, ntax):
        '''
        Randomly select the 4 taxa to be included in the quartet analysis
        :Input: The total number of taxa in an analysis
        :Return: A sorted list of 4 unique taxa
        '''
        self.taxa = []
        while len(self.taxa) < self.quartet_length:
            num = random.randint(0, ntax-1)
            if num not in self.taxa:
                self.taxa.append(num)
        self.taxa = sorted(self.taxa)
        #return a sorted list of 4 random taxa
        return self.taxa
    
    def isolateCFs(self, file, num_genes):
        '''
        Isolates the CFs within a *.concordance file, and sorts the three from largest to smallest
        :Input: A *.concordance file
        :Return: A sorted dictionary of three CFs 
        '''
        self.d = {}
        self.ciLow = {}
        self.ciHigh = {}
        split = ""
        cf = 0
        #counter to ensure 3 entries
        counter = 0
        
        for line in file:
            #finds all splits, which have CFs associated with them
            if (line[0] == '{' and len(line) == self.length_of_splits):
                split = line
            #find CF associated with the split found above
            if (line.startswith('mean')):
                words = line.split()
                #CF guarenteed by BUCKy to be the 4th "word"
                cf = float(words[3])
                #add split/CF pair to dictionary
                self.d[split.strip()] = cf
                counter += 1
            if( line.startswith('95% CI for CF')):
                useline = line.translate(None,"()")
                useline = useline.replace(","," ")
                words = useline.split()
                self.ciLow[split.strip()] = float(words[5]) / num_genes
                self.ciHigh[split.strip()] = float(words[6]) / num_genes
        
        #fill out dictionary if there were less than 3 splits
        if (counter < 3):
            addToDict(self.d)
            addToDict(self.ciLow)
            addToDict(self.ciHigh)
            
        return self.d, self.ciLow, self.ciHigh
