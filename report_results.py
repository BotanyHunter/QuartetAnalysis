#!/usr/bin/python
#version 2.0.7

import sys,os, fcntl
from append_output import *
from errorcodes import *
from fileReader_condor import *

def main():

    try:
        return_value    = int(sys.argv[1])
    except:
        return findErrorCode("report_results: missing node return status")

    try:
        job_name    = sys.argv[2]
    except:
        return findErrorCode("report_results: missing job name")

    try:
        outputSuffix    = sys.argv[3]
    except:
        return findErrorCode("report_results: missing output suffix")


    if( return_value != 0 ):
        myfile = open("QuartetAnalysis"+outputSuffix+".meta", "r+")
        fcntl.flock(myfile,fcntl.LOCK_EX)
        myfile.seek(0,2)    #end of file
        if( sys.argv[1] == "-1002" ):
           myfile.write("ERROR in " + job_name + ": error code = " + sys.argv[1] + "; will signal job as failed; to be rescued.\n")
           myfile.close()
           return return_value
        else:
           myfile.write("ERROR in " + job_name + ": error code = " + sys.argv[1] + " = " + errorString(return_value) +"\n")
           myfile.close()
           return 0

    try:
        test_option    = int(sys.argv[5])
    except:
        return findErrorCode("report_results: missing test code")

    errors = []
    try:
        new_results = open(job_name+".stats", "r")
        lines = new_results.readlines()
        new_results.close()
        new_stats = re.findall(r'\d+', lines[0])
        if len(lines) > 1 :
            errors = lines[1:]
    except:
        return findErrorCode("report_results: Could not read new stats from file")


    try:
        myfile = open("QuartetAnalysis"+outputSuffix+".meta", "r+")
        fcntl.flock(myfile, fcntl.LOCK_EX)
        filelines = myfile.readlines()
    except:
        myfile.close()
        return findErrorCode("report_results: Could not open QuartetAnalysis metafile")

    try:
        myfile.seek(0)
        for line in filelines:
            if (re.search(' - MrBayes:', line)):
                info = re.findall(r'\d+', line)
                info[3] = str(int(info[3]) + int(new_stats[0]))
                info[4] = str(int(info[4]) + int(new_stats[1]))
                info[5] = str(int(info[5]) + int(new_stats[2]))
                info[6] = str(int(info[6]) + int(new_stats[3]))
                info[7] = str(int(info[7]) + int(new_stats[4]))
                try:
                    line = " - MrBayes:\t" + info[0] + "\t" + info[1] + "\t" + info[2] + "\t"+ info[3] + "\t"+info[4]+"\t"+info[5]+"\t"+info[6]+"\t"+info[7]+"\n"
                except:
                    line = line
            myfile.write(line)
        if len(errors) > 0 :
            for error in errors:
                myfile.write(error)

        myfile.close()
    except:
        myfile.close()
        return findErrorCode("report_results: Could not interpret QuartetAnalysis metafile")

    if test_option == 0:
        try:
           os.system('rm ' + job_name +".stats")
        except:
            return findErrorCode("report_results: Could not delete stats file")


    return findErrorCode('no error')

sys.exit (main())
