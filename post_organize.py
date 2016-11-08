#!/usr/bin/python
#version 2.0.5

import sys,os
from append_output import *
from errorcodes import *
from fileReader_condor import *

def main():

    try:
        return_value    = sys.argv[1]
    except:
        return findErrorCode("post_organize: missing node return status")


    if( return_value != "0" ):
        return findErrorCode("post_organize: organize.submit returned a non-zero value")

    try:
        myfile = open("QuartetAnalysis.meta", "r")
        filelines = myfile.readlines()
        myfile.close()
        results = [0,0]
        for line in filelines:
            if (re.search('# gene files:', line)):
                info = re.findall(r'\d+', line)
                results[0] = info[0]
            if (re.search('# of quartets:', line)):
                info = re.findall(r'\d+', line)
                results[1] = info[0]
            if (re.search('all [0-9]+ quartets', line)):
                info = re.findall(r'\d+', line)
                results[1] = info[0]
            if (re.search('[0-9]+ will be chosen randomly', line)):
                info = re.findall(r'\d+', line)
                results[1] = info[0]
            numRuns = str(int(results[0]) * int(results[1]))
    except:
        return findErrorCode("post_organize: Could not interpret QuartetAnalysis.meta")

    try:
        append_output("organize.meta", "QuartetAnalysis.meta")
        with open("QuartetAnalysis.meta", "a") as myfile:
            myfile.write("\n")
            myfile.write("Run MrBayes and BUCKy:\n")
            myfile.write("   \t\t# Genes\t# Quart\t# ExpRs\t# Compl\t# NoErr\t# StD>>\t# Tax<4\t# MBErr\n")
            myfile.write(" - MrBayes:\t" + results[0] + "\t" + results[1] + "\t" + numRuns + "\t0\t0\t0\t0\t0\n")
            myfile.write(" - BUCKy:\t\t" + results[1] + "\t"+ results[1]+"\t0\t0\t\t0\n")
        myfile.close()
    except:
        return findErrorCode("post_organize: Could not update QuartetAnalysis.meta")

    return findErrorCode('no error')

main()
