#fileWriter_condor.py
#version 2.0.5

import re,os,sys
from errorcodes import *

class fileWriter:
    '''
    Writes files needed for analyses
    '''
    def __init__(self, ntax, nchar, format_line, mb_block, tax_dict, which_taxa):
        if (ntax != None):
            self.ntax = ntax
        if (nchar != None):
            self.nchar = nchar
        if (format_line != None):
            self.format_line = format_line
        if (mb_block != None):
            self.mb_block = mb_block
        if (tax_dict != None):
            self.tax_dict = tax_dict
        if (which_taxa != None):
            self.which_taxa = which_taxa
        
        #file header
        self.header = ""
        self.data = []
        self.tax_list = []

    def init_header(self):
        '''
        Builds the header of an individual quartet's .nex file
        '''
        self.header = ""
        self.header += "#NEXUS\n\nBEGIN DATA;\n\tDIMENSIONS NTAX=" + str(len(self.which_taxa))
        self.header += " NCHAR=" + str(self.nchar) + ";\n" + self.format_line
        self.header += "\tMATRIX\n"
        
    def init_taxa(self, file_path, file, zip_file=0):
        '''
        Finds genetic data associated with each taxon, and build a string containing both the taxa and its associated data
        :Input: The file path to an individual .nexus file
        :Return: True if all 4 taxa were found in the file, False otherwise
        '''
        #boolean to make sure the matrix header has been seen
        matrix_found = False
        
        self.tax_list = []      #initialize the genetic data to be written to the data
        self.data = []          #the sequences
        taxa_line_count = []         #the number of lines (>1 for interleaved) of data per taxon
        taxa_counter = 0
        for num in self.which_taxa:
            self.tax_list.append(self.tax_dict[int(num)])
            self.data.append("")
            taxa_line_count.append(0)
        
        #find the genetic data associated with each taxon
        if( zip_file == 0 ):
            orig_file = open(file_path + '/' + file, 'r')
        else:
            orig_file = zip_file.extractfile(file)

        for line in orig_file:
            line = self.remove_comment(line)       #added 24 Aug 2016 by SJH
            #find the matrix header
            if (re.search('matrix', line.lower())):
                matrix_found = True
            
            if matrix_found:
		propTaxaName = re.match("^\s*([^\s]*)\s",line)			#added 24 Aug 2016 by SJH  
		                                                                #changed from "^\s*([^\s-]*)\s" on 19 Mar 2018 by SJH
                if propTaxaName:					       	#added 24 Aug 2016 by SJH
			propTaxaName = propTaxaName.group(1)			#added 24 Aug 2016 by SJH
		else:								#added 24 Aug 2016 by SJH
			propTaxaName = line					#added 24 Aug 2016 by SJH
                for i in range(len(self.tax_list)):
                    if propTaxaName == self.tax_list[i] :			#changed 24 Aug 2016 by SJH
                        if taxa_line_count[i] == 0 :
                            self.data[i] += line.rstrip()
                            taxa_counter += 1
                        else:
                            sequence_data = re.search(r"(?<=\s)[A-Za-z-]+$", line)    #changed " " to \s   24 Aug 2016 SJH
                            self.data[i] += sequence_data.group(0)
                        taxa_line_count[i] += 1
        orig_file.close()
        
        #if the number of taxa found isn't 4, return false
        if (taxa_counter != len(self.which_taxa)):
            return False
        else:
            return True 

    def remove_comment(self, line):
        '''
        Remove the comments from a line
        :Input: The line from a .nexus file
        '''
        comment_found = False
        begin = False
        end = False
        line_str = ""
        
        #account for white space
        if (line == None):
            return line
        
        #see if there is a comment (marked by '[]')
        elif (re.search('\[', line) and re.search('\]', line)):
            comment_found = True
            for word in line.split():
                #check to see where the comment begins and ends
                if (re.search('\[', word)):
                    begin = True
                    end = False
                if (re.search('\]', word)):
                    word = ""
                    end = True
                    begin = False
                #if the comment has started, but the end hasn't happened yet, set the
                #word to nothing
                if (begin and not end):
                    word = ""
                #add the uncommented word to a growing new line
                if (word != ""):
                    line_str += word + " "
                    
            #return the new line if there were comments
            return line_str
        else:
            #if no comments, return the line as is
            return line

        
    def write_quartetFile(self, file_path, file, zip_file = 0):
        '''
        Writes the 4-taxon file to a file, called "<filename>_quartet.nex", which will be analyzed with mrBayes
        :Input: The file path to an individual .nexus file, and the name of the file
        :Return: True if all 4 taxon had data and were written to the *_quartet.nex file, False otherwise
        '''
        try:
            taxa_found = self.init_taxa(file_path, file, zip_file)
        except:
            return findErrorCode("fileWriter_condor: Could not initialize")

        #if 4 taxa have been found, build the quartet file. Don't build it otherwise.
        if (taxa_found):
            if(  zip_file != 0 ):
                #remove subdirectory names from zipped files.
                tail = os.path.basename(file)
                name = file_path + tail + "_quartet.nex"
            else:
                name = file_path + file + "_quartet.nex"

            try:
                new_file = open(name, 'w')
            except:
                return findErrorCode("fileWriter_condor: Could not open new nexus file")

            try:
                self.init_header()
                new_file.write(self.header)
            except:
                return findErrorCode("fileWriter_condor: Could not create or write header")

            try:
                for i in range(len(self.tax_list)):
                    new_file.write(self.data[i] + "\n")
            except:
                return findErrorCode("fileWriter_condor: Could not write data")

            try:
                new_file.write(";\n\nEND;")
            except:
                return findErrorCode("fileWriter_condor: Could not write END to data block")

            #include a mrBayes block
            try:
                new_file.write("\n\n" + self.mb_block + "\n")
            except:
                return findErrorCode("fileWriter_condor: Could not write MrBayes Block")

            try:
                new_file.close()
            except:
                return findErrorCode("fileWriter_condor: Could not close new nexus file")

            return 0
        else:
            return findErrorCode("fileWriter_condor: Less than four taxa found")
            
    def add_to_output_file(self, cf_dict, ciLow_dict, ciHigh_dict, which_taxa):
        '''
        Adds a line of data to the output.csv file
        :Input: The concordance_factor dictionary containing the concordance factors associated with specific splits,
            and the numbers of the individual taxa in the quartet
        '''
        line = ""
        #go through the random taxa list and add those taxon numbers, along with split-associated CFs, to the line
        for num in which_taxa:
            line += str(num) + ","
        line += str(cf_dict["{1,2|3,4}"]) + ","
        line += str(cf_dict["{1,3|2,4}"]) + ","
        line += str(cf_dict["{1,4|2,3}"]) + ","
        line += str(ciLow_dict["{1,2|3,4}"]) + ","
        line += str(ciHigh_dict["{1,2|3,4}"]) + ","
        line += str(ciLow_dict["{1,3|2,4}"]) + ","
        line += str(ciHigh_dict["{1,3|2,4}"]) + ","
        line += str(ciLow_dict["{1,4|2,3}"]) + ","
        line += str(ciHigh_dict["{1,4|2,3}"]) + "\n"
        output_file = open("QuartetAnalysis.csv", 'a')
        output_file.write(line)
        output_file.close()

    def add_to_supple_file(self, genestring, quartet_taxa):
        '''
        Adds a line of data to the QuartetAnalysis.supple file
        :Input: the quartet taxa and the gene data previously written (gene #, prob (1,2), prob (1,3), prob (1,4)
        '''
        line = ""
        #go through the random taxa list and add those taxon numbers, along with split-associated CFs, to the line
        for num in quartet_taxa:
            line += str(num) + ","
        line += genestring
        output_file = open("QuartetAnalysis.supple", 'a')
        output_file.write(line)
        output_file.close()
