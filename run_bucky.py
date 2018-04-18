#!/usr/bin/python
#version 2.0.6
import sys, glob, os, re, optparse, tarfile
from fileReader_condor import *
from fileWriter_condor import *
from quartet_condor import *
from arguments import *
from errorcodes import *

'''
Takes in all mbsum outputs (Q#_...in) and analyzes them with BUCKy.
Input: The mbsum ".in" file for each quartet.
Output: The *.concordance file from BUCKy, containing the concordance factors from a specific quartet. Also outputs a file containing warnings
    if any standard deviations finish greater than 0.1 during mrBayes analysis.
'''

def appendResults(file, geneNumber, probs):
    # A (unnecessarily complex?) algorithm to ensure probs add to 100%
    probs[0] = int(round(probs[0]*100))
    if probs[1] > 0 :
        probs[1] = int(round((100-probs[0]) * probs[1] / (probs[1] + probs[2])))
    probs[2] = 100 - probs[0] - probs[1]
    file.write(str(geneNumber) + "," + str(probs[0]) + "," + str(probs[1]) + "," + str(probs[2]) + "\n" )

def getGeneTranslations(outputSuffix):
    geneDictionaryFilename = "genes"+outputSuffix+".txt"
    geneDictionaryFile = open(geneDictionaryFilename, 'r')
    gene_dict = {}
    for line in geneDictionaryFile:
        geneInfo = line.split()
        gene_dict[geneInfo[1]] = geneInfo[0]
    return gene_dict


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def getQuartetGeneTranslations(quartet_index):
    inputFilename = "Q" + str(quartet_index) + ".input"
    inputFile = open(inputFilename, 'r')
    quartetGene_dict = {}
    for line in inputFile:
        geneInfo = line.split()
        if is_number(geneInfo[0]):
            geneName = geneInfo[1]
            #split off quartet tag at beginning -- Q1_
            # and split off .in at end
            iPos = geneName.find("_")+1
            geneName = geneName[iPos:-3]
            quartetGene_dict[geneInfo[0]] = geneName
    return quartetGene_dict


   


def main():
    parser = getParser()
    options, remainder = parser.parse_args()

    #make a reference dictionary from the translate file (built by get_taxa.py)
    try:
        ref_dict = {}
        translate_filename = 'translate' + options.outputSuffix + '.txt'
        translate_file =  open(translate_filename, 'r')
        for line in translate_file:
            words = line.split()
            ref_dict[int(words[0])] = words[1]
        translate_file.close()
    except:
        return findErrorCode("run_bucky.py: Could not open/interpret translate file")

    #the individual quartet to analyze
    try:
        info = re.findall(r'\d+', options.condor_job_name)
        quartet_index = int(info[0])
    except:
        return findErrorCode("run_bucky.py: Could not interpret job name")
       

    #make a reference dictionary from genes.txt file (build by organize.py)
    try:
        gene_dict = getGeneTranslations(options.outputSuffix)
    except:
        return findErrorCode("run_bucky.py: Could not interpret gene file")
    
    
    #get actual quartet
    try:
        quartets_filename = 'quartets' + options.outputSuffix + '.txt'
        quartets_file = open(quartets_filename)
        for i, quartet in enumerate(quartets_file):
            if i == (quartet_index - 1):
               break
        quartet = quartet.split()
    except:
        return findErrorCode( "run_bucky.py: could not open/interpret quartet file in mrBayes.py")

    #counter for the number of genes failed during mrBayes analysis 
    #         (reasons for failure = standard deviation or missing taxa)
    numFilesToAnalyze = int(options.num_genes)

    #now untar mbsum *.in files
    try:
        myTar = tarfile.open(options.condor_job_name + ".tar.gz")
        files = myTar.getmembers()
        numFilesAnalyzed = len(files)
    except:
        return findErrorCode( "run_bucky.py: could not open tar file with mrBayes/mbsum results")

    if numFilesToAnalyze == 0 :
        return findErrorCode( "run_bucky.py: mrBayes/mbsum results empty")

    print options.condor_job_name
    print float(numFilesAnalyzed)
    print numFilesToAnalyze
    print options.failure_percent
    if float(numFilesAnalyzed) / numFilesToAnalyze < options.failure_percent :
        return findErrorCode( "run_bucky.py: mrBayes/mbsum results too few")

    try:
        myTar.extractall()
        myTar.close()
    except:
        return findErrorCode( "run_bucky.py: could not extract files from .tar.gz")


    #call to BUCKy
    try:
        os.system('./bucky -o Q'+ str(quartet_index) + ' -a ' + str(options.alpha) + ' -n ' + str(options.bucky_ngen) + ' Q'+str(quartet_index)+'_*.in')
    except:
        return findErrorCode( "run_bucky.py: error in BUCKy")


    #make a reference dictionary for the genes used in this quartet.
    try:
        quartetGene_dict = getQuartetGeneTranslations(quartet_index)
    except:
        return findErrorCode( "run_bucky.py: could not make gene dictionary")


    #write the standard deviations of the genes to a file
    try:
        suppl_str  = "genes processed = " + str(numFilesAnalyzed) +  "\n" 
        suppl_file = open("Q" + str(quartet_index) + ".txt", 'w')
        suppl_file.write(suppl_str)
    except:
        return findErrorCode( "run_bucky.py: could not write gene stats")


    #and write genetree probs to same file.
    try:
        geneFile = open('Q'+str(quartet_index)+'.gene', 'r')
        firstGene = True
        whichGene = None
        geneProbs = [0,0,0]
        for line in geneFile:
            if "Gene " in line:
                if not firstGene: 
                    appendResults(suppl_file, whichGene, geneProbs)
                geneProbs = [0,0,0]
                geneIndex = line.split()[1][:-1]
                whichGene = gene_dict[quartetGene_dict[geneIndex]]
                firstGene = False
            if "(1" in line:
                curProbs = re.findall(r' [01]\.[0-9]+', line)
                if "((1,2),3,4)" in line: 
                    geneProbs[0] = float(curProbs[0])
                elif "((1,3),2,4)" in line: 
                    geneProbs[1] = float(curProbs[0])
                elif "(1,(2,3),4)" in line: 
                    geneProbs[2] = float(curProbs[0])
        if whichGene is not None: 
           appendResults(suppl_file, whichGene, geneProbs)
        geneFile.close()             
        suppl_file.close()

    except:
        return findErrorCode( "run_bucky.py: error writing results")


    #remove all bucky files except for the condordance file
    try:
        os.system('rm -rf Q'+str(quartet_index)+'_*.in')

        if( options.testing < 2 ):
            os.system('rm -rf *.cluster *.gene *.input *.out')
    except:
        return findErrorCode( "run_bucky.py: error deleting files.")

    return 0



sys.exit(main())
