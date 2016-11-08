#!/usr/bin/python
#version 2.0.5

import sys,re,os,fcntl
from errorcodes import *

def main():

    try:
        return_value    = int(sys.argv[1])
    except:
        return findErrorCode("delete_mb_output: missing node return status")

    try:
        jobname = sys.argv[2]
    except:
        return findErrorCode("delete_mb_output: missing job name")

    if( return_value != 0                                                            and 
        return_value != findErrorCode("run_bucky.py: mrBayes/mbsum results too few") and
        return_value != findErrorCode("run_bucky.py: mrBayes/mbsum results empty")       ):
        myfile = open("QuartetAnalysis.meta", "r+")
        fcntl.flock(myfile,fcntl.LOCK_EX)
        myfile.seek(0,2)
        myfile.write("ERROR in " + jobname + ": " + errorString(return_value) +"\n")
        myfile.close()
        return 0

    try:
        new_info = re.findall(r'\d+', jobname)
        quartet_index = new_info[0]
    except:
        return findErrorCode("delete_mb_output: error finding quartet index")

    try:
        myfile = open("QuartetAnalysis.meta", "r+")
        fcntl.flock(myfile, fcntl.LOCK_EX)
        filelines = myfile.readlines()
    except:
        return findErrorCode("delete_mb_output: Could not open QuartetAnalysis.meta")

    try:
        myfile.seek(0)
        for line in filelines:
            if (re.search(' - BUCKy:', line)):
                info = re.findall(r'\d+', line)
                info[2] = str(int(info[2]) + 1)
                if( return_value == 0 ) :
                   info[3] = str(int(info[3]) + 1)
                else:
                   info[4] = str(int(info[4]) + 1)
                try:
                    line = " - BUCKy:\t\t" + info[0] + "\t" + info[1] + "\t" + info[2] + "\t" + info[3] + "\t\t" + info[4] + "\n"
                except:
                    line = line
            myfile.write(line)

        myfile.close()
    except:
        myfile.close()
        return findErrorCode("delete_mb_output: Could not interpret QuartetAnalysis.meta")

    try:
        os.unlink("run_quartets+QUARTET_"+str(quartet_index)+"+run_bucky.tar.gz")
    except:
        return findErrorCode("delete_mb_output: Could not delete bucky results file")


    return findErrorCode('no error')

sys.exit(main())



