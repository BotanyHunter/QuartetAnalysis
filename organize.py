#!/usr/bin/python
#version 2.0.6

import os,re,optparse,tarfile,shutil,random
from fileReader_condor import *
from quartet_condor import *
from arguments import *

def translate_quartets(ref_dict, quartet_file_name, outputSuffix):
    quartet_file = open(quartet_file_name, 'r')
    new_quartet_file = open('quartets'+outputSuffix+'.txt', 'w');
    kount = 0
    for line in quartet_file:
        replacement_line = ""
        first_word = True
        add_quartet = True
        for word in line.split():
            if( first_word != True): replacement_line += " "
            found_it = False
            for k, v in ref_dict.items():
                if v == word:
                     replacement_line += str(k)
                     found_it = True
            if( found_it == False ): add_quartet = False 
            first_word = False
        if( add_quartet): new_quartet_file.write(replacement_line+'\n');
        kount += 1
    new_quartet_file.close()
    quartet_file.close()
    return kount


def quart_file_is_codes(quartet_file_name):
    '''
    opens up file and checks to see if quartets are numeric
    or alphanumeric meaning need translation from ref_dict.
    '''
    quartet_file = open(quartet_file_name, 'r')
    for line in quartet_file:
        if re.search('[^0-9\s]', line):
            return False

    return True

def write_translate_table(ref_dict, outputSuffix):
    '''
    Writes a translate table for all taxa
    :Input: A reference dictionary containing number/species-name pairs
    '''
    translate_filename = 'translate' + outputSuffix + '.txt'
    translate_file = open(translate_filename, 'w')

    kount = 0
    for k, v in ref_dict.items():
        translate_file.write(str(k) + "\t" + v + "\n")
        kount += 1
    translate_file.close()
    return kount

def write_gene_table(ref_dict, outputSuffix):
    '''
    Writes a translate table for all genes
    :Input: A reference dictionary containing genes
    '''
    gene_filename = "genes" + outputSuffix + ".txt"
    gene_file =  open(gene_filename, 'w')
    kount = 0
    for k, v in ref_dict.items():
        gene_file.write(str(k) + "\t" + v + "\n")
        kount += 1
    gene_file.close()
    return kount

'''
Finds the list of quartets to analyze, and builds the submit.run_taxa file to analyze each individual quartet
'''
def main():
    parser = getParser()
    options, args = parser.parse_args()

    #Prepare output
    out =  "RUNNING organize.py: \n"
    
    # unzip data files if zipped
    if( options.data_is_zipped == 1 ):
        iCount = 0
        for file in os.listdir(options.gene_file):
            isTar = re.search(r".tar.gz$", file )
            if( isTar != None and not re.search(r"^D[0-9]+.tar.gz", file)):
                iCount = iCount + 1
                tarFilename = file
        if( iCount != 1 ):
            print "Error: not exactly one .tar.gz file in directory: %d in %s" % (iCount, options.gene_file)
            return 1
        args += " -z 1"
        myTarfile = tarfile.open(name=options.gene_file+"/"+tarFilename,mode='r')
        
    
    fr = fileReader()
    #find the list of gene files to be analyzed
    files = []
    if (options.list_of_files != None):
        list_of_files = open(options.list_of_files, 'r')
        for line in list_of_files:
            files.append(line.strip())
    else:
        if( options.data_is_zipped == 1 ):
            files = myTarfile.getnames()
        else:
            for (dirpath, dirnames, filenames) in os.walk(options.gene_file):
                files.extend(filenames)
    
    #make reference dictionaries containing all taxa and all genes found in the data set
    taxa_dict = {}
    gene_dict = {}
    gene_count = 0
    for file in files:
        ignore_this_file = False
        if( options.data_is_zipped == 1 ):
            fileInfo = myTarfile.getmember(file)
            if( fileInfo.isfile() ):
                nex_file = myTarfile.extractfile(fileInfo.name)
            else:
                ignore_this_file = True
        else:
            nex_file = open(options.gene_file + file, 'r')
        if( ignore_this_file == False ):
            taxa = fr.get_taxa(nex_file)
            taxa_dict = fr.make_dict(taxa_dict, taxa)
            nex_file.close()
            try:
                use_name = re.findall('[^/]+$', file)[0]
            except:
                print "Error: problem reading file name: %s" % (file)
                return 1
            gene_dict[str(gene_count)] = use_name
            gene_count += 1

    #write a translate table for reference
    numTaxa = write_translate_table(taxa_dict, options.outputSuffix)
    out += "- translate" + options.outputSuffix + ".txt written for " + str(numTaxa) + " taxa.\n"


    #write a gene table
    numGenes = write_gene_table(gene_dict, options.outputSuffix)
    out += "- genes" + options.outputSuffix + ".txt written for " + str(numGenes) + " genes.\n"


    #find the list of quartets to analyze
    q = quartet()
    quartet_filename = "quartets" + options.outputSuffix + ".txt"
    #use a user-specified list if given
    if (options.list_of_quartets != None):
        if (options.list_of_quartets == quartet_filename):
            print "Quartet file cannot be named <"+quartet_filename+">; that filename reserved.  Please rename."
            return 1
        #open up user-specified file, if simply codes, rename if necessary and continue.
        is_codes = quart_file_is_codes(options.list_of_quartets)
        if(  is_codes ):
            shutil.copyfile(options.list_of_quartets, quartet_filename)
            out += "- "+quartet_filename+" copied from " + options.list_of_quartets + ".\n"
            num_quartets = 0
            with open(quartets_filename, 'r') as input:
                for line in input:
                    num_quartets += 1

        else:
            num_quartets = translate_quartets(taxa_dict, options.list_of_quartets, options.outputSuffix)
            if( num_quartets == False):
                print "Error: supplied quartets file could not be translated."
                return 1
        #Now subsample from file.
        if( options.num_quartets != 0 ):
            num_lines = sum(1 for line in open(quartet_filename))
            if( options.num_quartets > num_lines  ):
                print "Error: requested quartets more than quartets in file."
                return 1
            myQuartets = random.sample(xrange(1,num_lines+1), options.num_quartets)
            myQuartets.sort()
            curQ = 0
            curLine = 0
            with open(quartet_filename, 'r') as input:
                with open('xquartets.txt', 'w') as output: 
                    for line in input:
                        curLine=curLine+1;
                        if (curLine in myQuartets):
                            output.write(line)
            os.remove(quartet_filename)
            os.rename("xquartets.txt", quartet_filename)
            out += "- "+quartet_filename+" written for " + str(options.num_quartets) + " quartets given in " + options.list_of_quartets + ".\n"
        else:
            out += "- "+quartet_filename+" written for " + str(num_quartets) + " quartets given in " + options.list_of_quartets + ".\n"
            
    #pick random quartets if no user-specified list
    else:
        quart_file = open(quartet_filename, 'w')
        for i in range(options.num_quartets):
            rand_taxa = q.pick_random_quartet(len(taxa_dict))
            #print rand_taxa
            for num in rand_taxa:
                quart_file.write(str(num) + " ")
            quart_file.write("\n")
        quart_file.close()
        out += "- "+quartet_filename+" written for " + str(options.num_quartets) + " random quartets.\n"

    output_file =  open("organize.meta", 'w')
    output_file.write(out)
    output_file.close()


main()
