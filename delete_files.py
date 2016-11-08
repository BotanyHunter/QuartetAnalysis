#!/usr/bin/python
#version 2.0.4
import sys,os,optparse,tarfile
from arguments import *
from append_output import *

def main():

    try:
        file_finish = open("finish.meta","a")
    except:
        print "Error: Problem in opening finish.out"
        return 1
       
    try:
        return_value = int(sys.argv[1])
    except:
        file_finish.write("Error: Problem in delete_files.py in argument list.\n")
        return 1

    try:
        parser = getParser()
        options, remainder = parser.parse_args()
    except:
        file_finish.write("Error: Problem in delete_files.py in reading options.\n")
        return 1


    if return_value != 0:
        file_finish.write("Error: JOB finish did not terminate successfully.\n")
        return 1

    try:
        #remove all the bucky and mrbayes files
        if( options.testing < 2 ):
            os.system('rm -rf run_mrbayes.*.err run_mrbayes.*.log run_mrbayes.*.out')
            os.system('rm -rf run_bucky.*.err   run_bucky.*.log   run_bucky.*.out')
            os.system('rm -rf run_mrbayes.err run_mrbayes.log run_mrbayes.out')
            os.system('rm -rf run_bucky.err   run_bucky.log   run_bucky.out')
            os.system('rm -rf run_quartets+QUARTET_*+run_bucky.tar.gz')
            os.system('rm -rf D*.tar.gz')
            os.system('rm -rf finish.tar.gz')


        if( options.testing < 1 ):
            os.system('rm -rf *.concordance')
            os.system('rm -rf Q*.txt')

        file_finish.write("- Deleted files. (test options = "+str(options.testing)+")\n")
        file_finish.close()
        return_value = append_output("finish.meta","QuartetAnalysis.meta")
        os.system('rm -rf organize.meta finish.meta')
        return return_value

    except:
        return 1

            

main()
