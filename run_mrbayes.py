#!/usr/bin/python
#version 2.0.5
import sys, os, subprocess, re, optparse, shutil, tarfile
from fileReader_condor import *
from fileWriter_condor import *
from quartet_condor import *
from arguments import *
from errorcodes import *

'''
Takes in an individual quartet and genegroup and analyzes it using mrBayes and then summarizes with mbsum.
Input: A quartet to analyze and a group of genes.
Output: The mbsum ".in" file for each gene. 
        Also outputs a file containing warnings if any standard deviations finish greater than 0.1 during mrBayes analysis.
'''
def main():

    parser = getParser()
    options, remainder = parser.parse_args()

    #the individual quartet to analyze
    info = re.findall(r'\d+', options.condor_job_name)
    try:
        quartet_index = int(info[0])
        gene_group    = int(info[1])
    except:
        return findErrorCode("mrBayes.py: Could not interpret condor job name")

    try:
        results_file = open(options.condor_job_name + ".stats", 'w')
    except:
        return findErrorCode("mrBayes.py: Could not create or write results file")

    try:
        myTar = tarfile.open(options.condor_job_name + ".tar.gz","w")
    except:
        return findErrorCode("mrBayes.py: Could not create gene group zip file")

    #make a list of .mb errors to print out to the .stats file
    mb_error = []

    #make a reference dictionary from the translate.txt file (built by organize.py)
    ref_dict = {}
    try:
        translate_file = open('translate.txt', 'r')
    except:
        return findErrorCode("mrBayes.py: Could not open translate.txt")
    try:
        for line in translate_file:
            words = line.split()
            ref_dict[int(words[0])] = words[1]
        translate_file.close()
    except:
        return findErrorCode("mrBayes.py: Could not interpret translate.txt")

    #get actual quartet
    try:
        quartets_file = open("quartets.txt")
    except:
        return findErrorCode("mrBayes.py: Could not open quartet.txt")

    try:
        for i, quartet in enumerate(quartets_file):
            if i == (quartet_index - 1):
               break
        quartet = quartet.split()
    except:
        return findErrorCode("mrBayes.py: Could not interpret quartet.txt")

    #if data file if zipped, reposition
    #if( options.data_is_zipped == 1 ):
    filename = "D" + str(gene_group) + ".tar.gz"
    if not os.path.isfile(filename):
        return findErrorCode("mrBayes.py: Could not find tarfile")

    #move file to data directory - to be consistent with non-zipped
    try:
        os.mkdir(options.gene_file)
    except:
        return findErrorCode("mrBayes.py: Could not create data subdirectory")

    shutil.move(filename, options.gene_file+filename)
    filename = options.gene_file+filename
    try:
        myTarfile = tarfile.open(filename,mode='r')
    except:
        return findErrorCode("mrBayes.py: Could not open tarfile")

    #find the files to analyze
    files = []
    if (options.list_of_files != None):
        try:
            list_of_files = open(options.list_of_files, 'r')
        except:
            return findErrorCode("mrBayes.py: Could not open list of gene files")
            
        for line in list_of_files:
            files.append(line.strip())
    else:
        if( options.data_is_zipped == 1 ):
            try:
                files = myTarfile.getnames()
            except:
                return findErrorCode("mrBayes.py: Could not get gene files from tarfile")
        else:
            try:
                for (dirpath, dirnames, filenames) in os.walk(options.gene_file):
                    files.extend(filenames)
            except:
                return findErrorCode("mrBayes.py: Could not get gene files from data directory")

    #counters
    #________
    num_genes        = 0
    files_ignored    = 0    #items in tar.gz that are not files (i.e. directories)
    taxa_not_present = 0
    mb_errors        = 0    #mrBayes does not return 0
    stdev_too_high   = 0
    num_completed    = 0

    fr = fileReader()
    for file in files:

        #read an individual .nexus gene file
        ignore_this_file = False
    
        if( options.data_is_zipped == 1 ):
            try:
                fileInfo = myTarfile.getmember(file)
            except:
                return findErrorCode("mrBayes.py: Could not interpret read tar.gz")

            if( fileInfo.isfile() ):
                try:
                    nex_file = myTarfile.extractfile(file)
                except:
                    return findErrorCode("mrBayes.py: Could not extract file from tar.gz")
            else:
                ignore_this_file = True
                files_ignored += 1
        else:
            try:
                nex_file = open(options.gene_file + file, 'r')
            except:
                return findErrorCode("mrBayes.py: Could not open gene file")


        if( ignore_this_file == False ):
            num_genes += 1
            try:
                fr.read_file(nex_file, options.nst, options.mb_ngen, options.rates, options.burnin, options.aamodel)
                nex_file.close()
            except:
                return findErrorCode("mrBayes.py: Could not interpret gene file")


            #initialize a new .nexus file, containing just the individual quartet
            try:
                wf = fileWriter(fr.get_ntax(), fr.get_nchar(), fr.get_format_line(), fr.get_mb_block(), ref_dict, quartet)
            except:
                return findErrorCode("mrBayes.py: Could not initialize quartet subset of gene file")

            #write file and note if there are any missing taxa
            try:
                if( options.data_is_zipped == 1 ):
                    taxa_present = wf.write_quartetFile(options.gene_file, file, myTarfile)
                else:
                    taxa_present = wf.write_quartetFile(options.gene_file, file)
            except:
                return findErrorCode("mrBayes.py: Could not write quartet subset of gene file")

            #only run mrBayes and mbsum if all of the taxa are present
            if (taxa_present == findErrorCode("fileWriter_condor: Less than four taxa found")):
                taxa_not_present += 1

            elif (taxa_present != 0 ):
                mb_error.append("Error creating nexus for gene " + file + " in gene group " + str(gene_group) + " for quartet " + str(quartet_index) + ". Error: " + errorString(taxa_present) + "\n")

            else:
                #call to mrBayes
                if( options.data_is_zipped == 0 ):
                    filename = options.gene_file + file + '_quartet.nex'
                else:
                    filename = options.gene_file + os.path.basename(file) + '_quartet.nex'
                if not os.path.isfile(filename):
                    return findErrorCode("mrBayes.py: Filename mismatch")

                else:
                    print "found file " + filename + "\n"

                try:
                    retValue = subprocess.call(["./mb",filename], shell=False)
                except OSError as e:
                    return findErrorCode("mrBayes.py: Execution failed")
                except:
                    return findErrorCode("mrBayes.py: Unknown mrBayes execution error")
                    #error 78 is when arguments are uninterpretable.
 
                if retValue != 0:
                    mb_error.append("Error running MrBayes for gene " + file + " in gene group " + str(gene_group) + " for quartet " + str(quartet_index) + ". Error code " + str(retValue) + "\n")
                    mb_errors += 1
                else:
                    #find the final standard deviation in .mcmc file
                    mcmcname = filename + ".mcmc"
                    if not os.path.isfile(mcmcname):
                        return findErrorCode("mrBayes.py: Could not find expected mcmc output")

                    mcmc_file = open(mcmcname, 'r')
                    stdev = fr.find_stdev(mcmc_file)
                    mcmc_file.close()

            
                    #if the stdev exceeds the maximum allowed, give a warning and add one to the genes_failed counter
                    if (float(stdev) > options.max_stdev):
                        stdev_too_high += 1

                    #otherwise, run mbsum and continue with analysis
                    else:
                        if( options.data_is_zipped == 1 ):
                            usename = 'Q' + str(quartet_index) + "_"+ os.path.basename(file) + '.in'
                        else:
                            usename = 'Q' + str(quartet_index) + "_"+ file + '.in'
                        try:
                            os.system('./mbsum -o ' + usename + ' ' + options.gene_file + '*.t')
                        except:
                            return findErrorCode("mrBayes.py: Could not run mbsum")

                remove_extensions = [".ckp*",
                                     ".nex",
                                     ".mcmc",
                                     ".tre",
                                     ".parts",
                                     ".p",
                                     ".t",
                                     ".trprobs",
                                     ".tstat",
                                     ".vstat"]
                for ext in remove_extensions:
                    try:
                        os.system('rm -rf '+options.gene_file+'*'+ext)
                    except:
                        return findErrorCode("mrBayes.py: Could not delete temporary files")

    #zip up .in files
    try:
        files = os.listdir(".")
        reString = "^Q[0-9]+.+?\.nex\.in$"
        for file in files:
            if( re.search(reString, file)):
                myTar.add(file)
                num_completed += 1
                try:
                    os.system('rm -rf '+file)
                except:
                    return findErrorCode("mrBayes.py: Could not delete file after zipping")

         
    except:
        return findErrorCode("mrBayes.py: Could not write gene group zip file")
    


    summary_stats = "num genes: " + str(num_genes) + " completed: " + str(num_completed) + " SD > limit: " + str(stdev_too_high) + " missing taxa: " + str(taxa_not_present) + " mb error: " + str(mb_errors) + "\n"
    if (num_genes != num_completed + taxa_not_present + mb_errors + stdev_too_high):    
        return findErrorCode("mrBayes.py: Statistics do not add")

    try:
        results_file.write(summary_stats)
        if mb_errors != 0 :
            for iError in range(mb_errors):
                results_file.write(mb_error[iError])
    except:
        return findErrorCode("mrBayes.py: Could not create or write results file")

    results_file.close()

    return findErrorCode("no error")


sys.exit( main() )
