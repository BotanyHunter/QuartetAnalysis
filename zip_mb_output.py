#!/usr/bin/python
#version 2.0.5

import sys,re,os,tarfile
from errorcodes import *

def main():

    try:
        jobname = sys.argv[1]
        info = re.findall(r'\d+', jobname)
        quartet_index = info[0]
    except:
        return findErrorCode("zip_mb_output.py: Could not interpret condor job name")

    try:
        myTar = tarfile.open("run_quartets+QUARTET_"+str(quartet_index)+"+run_bucky.tar.gz","w")
    except:
        return findErrorCode("zip_mb_output.py: Could not open target tar file")

    try:
        files = os.listdir(".")
    except:
        return findErrorCode("zip_mb_output.py: Could not get directory.")

    num_input_tars = 0
    reString = "^run_quartets\+QUARTET_" + str(quartet_index) + "\+run_genegroups\+gene_group_[0-9]+\.tar\.gz$"
    for file in files:
        if( re.search(reString, file)):
            try:
                infileTar = tarfile.open(file)
            except:
                return findErrorCode("zip_mb_output.py: Could not open input tar.gz")
            inputFiles = infileTar.getmembers()
            for inputFile in inputFiles:
                print "extracting...\n"
                try:
                    infileTar.extract(inputFile)
                except:
                    return findErrorCode("zip_mb_output.py: Could not extract .in file")
                try:
                    myTar.add(inputFile.name)
                except:
                    return findErrorCode("zip_mb_output.py: Could not add .in file")
                try: 
                    os.system('rm -rf ' + inputFile.name)
                except:
                    return findErrorCode("zip_mb_output.py: Could not delete .in file")

            try:
               os.system('rm -rf ' + file)
            except:
               return findErrorCode("zip_mb_output.py: Could not delete input tar.gz")
            num_input_tars += 1

    if num_input_tars == 0:
        return findErrorCode("zip_mb_output.py: No input tar.gz found")

    return findErrorCode("no error")

print main()
