#!/usr/bin/python
import sys,os,re,optparse,tarfile,uuid,math,glob

'''
Builds the quartets file for QuartetAnalysis
'''
# This program takes two arguments
# a file with the taxa to include and their bin assignments.  It should be a simple tab separated file with bin number \t taxa name
# a text string to append to the output files:  e.g.  -o _20161108 results in allQuartets_20161108.txt
#
# example usage:  python createQuartets.py binAssigment_20161108.txt _20161108

def isInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

def main():

    print("")

    #  Get the two required arguments
    if len(sys.argv) != 3:
      print("- Must provide two arguments: 1) bin assigment file and 2) string to append to output name")
      return 1

    #  Read taxa and bin assignments from input file.
    taxa = {}
    count = 0
    errorFound = False
    try:
      with open(sys.argv[1], 'r') as f:
        lines = f.readlines()
    except:
      print("- Error reading from bin assignment file:" + sys.argv[1])
      return 1

    for line in lines:
      count = count + 1
      line = line.rstrip().split()
      if len(line) != 2 :
        print("- Error on line " + str(count) + ": line should be \"binNumber whiteSpace taxaName\".")
        errorFound = True
      elif isInt(line[0]) == False:
        print("- Error on line " + str(count) + ": binNumber (an integer 0 to 4) should be the first item on each line.")
        errorFound = True
      elif (0 <= int(line[0]) <= 4) == False:
        print("- Error on line " + str(count) + ": binNumber must be between 0 and 4.")
        errorFound = True
      elif line[1] in taxa:
        print("- Error on line " + str(count) + ": taxaName \""+ line[1]+"\" already assigned to a bin.")
        errorFound = True
      else:
        try:
          taxa[line[1]] = int(line[0])
        except:
          print("- Error on line " + str(count) + ": taxaName \""+ line[1]+"\" could not be used.")
          errorFound = True
          

    if( errorFound ): return 1
         
    #Make arrays with taxa grouped by group #
    groups = [[], [], [], []]
    
    for taxon,group in taxa.items():
        if group > 0: groups[group-1].append(taxon)

    for iG in range(4):
      if len(groups[iG]) == 0:
          print("- Error: No taxa in bin " + str(iG+1))
          return 1
    	
    count = 0
    newFilename = 'allQuartets'+sys.argv[2]+'.txt'
    quartet_file = open(newFilename, 'w')



    for taxa1 in groups[0]:
    	for taxa2 in groups[1]:
    		for taxa3 in groups[2]:
    			for taxa4 in groups[3]:
    				count += 1
    				quartet_file.write(taxa1 + " " + taxa2 + " " + taxa3 + " " + taxa4 + "\n")
    quartet_file.close()

    print(" - Finished.  New file is named \"" + newFilename + "\"")
    print("")
    				
    return 0
             
             
             
    


main()



