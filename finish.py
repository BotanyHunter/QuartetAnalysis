#!/usr/bin/python
#version 2.0.6
import os,re,optparse,tarfile
from quartet_condor import *
from fileWriter_condor import *
from fileReader_condor import *
from arguments import *
from errorcodes import *


splitOrder = ["{1,2|3,4}", "{1,3|2,4}", "{1,4|2,3}"]
translation = { 1234 : [1,2,3], 1243 : [1,3,2], 1324 : [2,1,3], 1342 : [2,3,1], 1423 : [3,1,2], 1432 : [3,2,1],
                2134 : [1,3,2], 2143 : [1,2,3], 2314 : [3,1,2], 2341 : [3,2,1], 2413 : [2,1,3], 2431 : [2,3,1],
                3124 : [2,3,1], 3142 : [2,1,3], 3214 : [3,2,1], 3241 : [3,1,2], 3412 : [1,2,3], 3421 : [1,3,2],
                4123 : [3,2,1], 4132 : [3,1,2], 4213 : [2,3,1], 4231 : [2,1,3], 4312 : [1,3,2], 4321 : [1,2,3] }

def restore_quartet_order(d, taxa_set, orig_quartet):
    '''
    given the four taxa in taxa_set, find them in orig_quartet
    and then change order in d.
    
    '''
    #first find the original quartet
    quartet = None

    for quartet_loop in orig_quartet:
        if( taxa_set[0] in quartet_loop and
            taxa_set[1] in quartet_loop and
            taxa_set[2] in quartet_loop and
            taxa_set[3] in quartet_loop     ):
            quartet = quartet_loop
            break
    
    if( quartet == None ): return None, None
    #now rearrange d
    translate = []
    for taxa in quartet:
        translate.append ( 1+taxa_set.index(taxa) )
    translateKey = translate[0]*1000 + translate[1]*100 + translate[2] * 10 + translate[3]
    
    d_new = {}
    for split in range(0,3):
        tK = splitOrder[translation[translateKey][split]-1]
        d_new[splitOrder[split]] = d[tK]
    return d_new, quartet
'''
Isolates CFs from *.concordance files (output from run_indiv_taxa.py) and builds a comma-separated ouput table
Also isolates gene tree probabilities from *.gene file
'''
def main():

    parser = getParser()
    options, remainder = parser.parse_args()

    output_header = "Taxon1,Taxon2,Taxon3,Taxon4,CF12|34,CF13|24,CF14|23,CI12|34Low,CI12|34High,CI13|24Low,CI13|24High,CI14|23Low,CI14|23High\n"
    output_file =  open("QuartetAnalysis"+options.outputSuffix+".csv", 'w')
    supple_header = "Taxon1,Taxon2,Taxon3,Taxon4,Gene Index,P12|34,P13|24,P14|23\n"
    supple_file =  open("QuartetAnalysis"+options.outputSuffix+".supple", 'w')

    metafile = open("QuartetAnalysis"+options.outputSuffix+".meta", 'r')
    for line in metafile:
        if line.startswith("- instance ID"):
           output_file.write(line)
           supple_file.write(line)

    output_file.write(output_header)
    supple_file.write(supple_header)

    output_file.close()
    supple_file.close()



    finish_output = open("finish.meta",'w')
        
    q = quartet()
    wf = fileWriter(None, None, None, None, None, None)
    fr = fileReader()
    
    #make a reference dictionary with number/species-name pairs

    myQuartets = []
    if( options.maintain_order == 1 ):
        quartets_filename = 'quartets' + options.outputSuffix + '.txt'
        with open(quartets_filename, 'r') as quartets_file:
            for quartet_line in quartets_file:
                myQuartets.append([int(x) for x in quartet_line.split()])

    ref_dict = {}
    translate_filename = 'translate' + options.outputSuffix + '.txt'
    translate_file = open(translate_filename, 'r')
    for line in translate_file:
        words = line.split()
        ref_dict[words[1]] = int(words[0])
    translate_file.close()

    try:
        myTarfile = tarfile.open(name="finish.tar.gz", mode='r')
        files = myTarfile.getnames()
    except:
        print "Error: tarFile finish.tar.gz does not exist."
        return 1

    taxa_set = []
    concfile_count = 0
    genefile_count = 0
    for cfile in files:
        if(cfile.endswith('concordance')):
            concfile_count += 1
            print "working on: "+cfile

            #find number of genes - which was written to the Q#.txt file
            txtFilename = cfile
            txtFilename = txtFilename.replace("concordance","txt")
            txtFile = myTarfile.extractfile(txtFilename)
            num_genes = -1
            for line in txtFile:
                if "genes processed" in line:
                    words = line.split()
                    num_genes = int(words[3])
                    break
            print "gene found = "+str(num_genes)

            concord_file =  myTarfile.extractfile(cfile)

            #find the reference numbers of the taxa
            taxa_names = fr.find_taxa_set(concord_file)
            taxa_count = 0
            for name in taxa_names:
                taxa_set.append(ref_dict[name])
                taxa_count += 1
                
            if( taxa_count == 4 ):
              print "reference #s of taxa set found."
              print taxa_set

              #find the CFs and add them to the growing output.csv file
              d,ciLow,ciHigh = q.isolateCFs(concord_file, num_genes)
              concord_file.close()
              if( options.maintain_order == 1 ):
                  d1, taxa_set1 = restore_quartet_order(d, taxa_set, myQuartets)
                  ciLow1, taxa_set1 = restore_quartet_order(ciLow, taxa_set, myQuartets)
                  ciHigh1, taxa_set1 = restore_quartet_order(ciHigh, taxa_set, myQuartets)
                  if( d1 == None ):
                      finish_output.write('error reordering quartet: ' + str(taxa_set) + '\n')
                      return 1
                  else:
                      d = d1
                      ciLow = ciLow1
                      ciHigh = ciHigh1
                      #taxa_set = taxa_set1
            
              wf.add_to_output_file(d, ciLow, ciHigh, taxa_set1, options.outputSuffix)    #changed from taxa_set on 13 Feb - SJH
              print "CFs added."


              #now grab the gene probabilities from the supplemental file.
              for line in txtFile:
                 myData = [int(x) for x in line.split(',')]
                 geneNumber = myData[0]
                 myDict = {}
                 myDict['{1,2|3,4}'] = myData[1]
                 myDict['{1,3|2,4}'] = myData[2]
                 myDict['{1,4|2,3}'] = myData[3]
                 newData, taxa_set1 = restore_quartet_order(myDict, taxa_set, myQuartets)
                 newDataString = str(newData["{1,2|3,4}"]) + "," + str(newData["{1,3|2,4}"]) + "," + str(newData["{1,4|2,3}"])
                 outputString = str(myData[0]) +"," + newDataString + "\n"
                 wf.add_to_supple_file(outputString, taxa_set1, options.outputSuffix)
              txtFile.close()
              print "Gene probabilities added.\n"


              taxa_set = []

    myTarfile.close()

    finish_output.write('\nRUNNING finish.\n- ' + str(concfile_count) + ' BUCKy outputs (=quartets) found.\n')
    finish_output.close()

            

main()
