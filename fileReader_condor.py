#fileReader_condor.py
#version 2.0.5

import re,string

class fileReader:
    """
    Reads files (in .nexus format) for relevant information
    """
    
    def __init__(self):
        self.ntax_line = ""
        self.ntax = "0"
        self.nchar_line = ""
        self.nchar = ""
        self.mb_block = ""
        self.format_line = ""
        self.taxa = []
        self.ref_dict = {}
        #used in calculation of number of trees to store
        self.NGEN = 100000
        
    
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

    
    def read_file(self, file, mb_nst, mb_ngen, mb_rates, mb_burnin, mb_aamodel):
        '''
        Reads the .nex file and stores all relevant information
        :Input: The file to be analyzed, as well as various information to build a mrBayes block - the number of states, the number
            of generations, the rates, and the burnin value
        '''
        ntax_found = False
        nchar_found = False
        matrix_found = False
        end_matrix = False
        found_mb = False
        found_end_of_mb = False
        self.mb_block = ""
        self.taxa = []
        
        for line in file:
            #remove the comments
            line = self.remove_comment(line)
            
            #find the number of taxa
            if (re.search('(?<=ntax=)', line.lower())):
                self.ntax_line = re.search('(?<=ntax=)', line.lower())
                words = self.ntax_line.string.split()
                for word in words:
                    if "ntax" in word.lower():
                        self.ntax = word.split("=")
                        self.ntax = self.ntax[1]
                        self.ntax = re.sub('[^0-9]','',self.ntax)
                        self.ntax =  int(self.ntax)
                        ntax_found = True
                        
            #find the number of characters
            if (re.search('(?<=nchar=)', line.lower())):
                self.nchar_line = re.search('(?<=nchar=)', line.lower())
                words = self.nchar_line.string.split()
                for word in words:
                    if "nchar" in word.lower():
                        self.nchar = word.split("=")
                        self.nchar = self.nchar[1]
                        self.nchar = re.sub('[^0-9]','',self.nchar)
                        self.nchar = int(self.nchar)
                        nchar_found = True
            
            #find the formatting description 
            if re.search('format', line.lower()):
                self.format_line = line
                
            #find the mb block
            if (re.search('begin mrbayes', line.lower())):
                found_mb = True
            if (found_mb and found_end_of_mb != True):
                self.mb_block += line + "\n"
            if (found_mb and re.search('end', line.lower())):
                found_end_of_mb = True

        #if there was no mrBayes file, add one
        if (found_mb != True):
            #calculate sample frequency/print freq based on the number of generations
            #have a max of 100000 trees stored
            if (mb_ngen <= self.NGEN):
                samplefreq = mb_ngen
            else:
                samplefreq = mb_ngen/self.NGEN + 1
            self.mb_block += "begin mrbayes;\n"
            self.mb_block += "\tset autoclose=yes nowarn=yes;\n"
            self.mb_block += "\tlset nst=" + str(mb_nst) + " rates=" + str(mb_rates) + ";\n"
            if( mb_aamodel != None):
                self.mb_block += "\tprset aamodelpr=fixed("+mb_aamodel+");\n"
            self.mb_block += "\tmcmcp ngen = " + str(mb_ngen) + " relburnin=yes burninfrac=" + str(mb_burnin) + " printfreq=" + str(mb_ngen/2) + " samplefreq=" + str(samplefreq) + " nchains=1 savebrlens=yes;\n"
            self.mb_block += "\tmcmc;\n\tsumt;\nend;"
                
    def get_ntax(self):
        '''
        :Return: The number of taxa
        '''
        return self.ntax
    
    def get_nchar(self):
        '''
        :Return: The number of characters
        '''
        return self.nchar
    
    def get_format_line(self):
        '''
        :Return: The FORMAT line of the nexus file
        '''
        return self.format_line
    
    def get_mb_block(self):
        '''
        :Return: The mrBayes block of the file
        '''
        return self.mb_block
    
    def get_taxa(self, file):
        '''
        Finds the taxa in a file
        :Input: The specified file to search
        :Return: The list of all taxa
        '''
        matrix_found = False
        end_matrix = False
        
        for line in file:
            line = self.remove_comment(line)
            #find end of matrix
            if (matrix_found and re.search(';', line)):
                end_matrix = True
            #find the taxa within the matrix
            if matrix_found and not end_matrix:
                words = line.split()
                #store the first word (the taxa name) in the taxa list
                if (words != []):
                    self.taxa.append(words[0])
            #find beginning of the matrix
            if (re.search('matrix', line.lower())):
                matrix_found = True
        return self.taxa
    
    def make_dict(self, d, taxa):
        '''
        Makes a dictionary with the taxa as values and their corresponding numbers as keys
        :Input: A dictionary containing previously found taxa, a list of taxa
        :Return: a dictionary containing numbers and taxa as key-value pairs
        '''
        for i in range(len(taxa)):
            if taxa[i] not in d.values():
                d[len(d)] = taxa[i]
        return d
    
    def find_taxa_set(self, concord_file):
        '''
        Find the taxa set in a *.concordance file
        :Input: The *.concordance file
        :Return: A list of taxa
        '''
        taxa_list = []
        translate_found = False
        translate_end = False
        for line in concord_file:
            if (translate_found and not translate_end):
                indiv_taxa = line.split()
                taxa = indiv_taxa[1]
                taxa_list.append(taxa[:-1])
            if (re.search('translate', line)):
                translate_found = True
            if (translate_found and re.search(';', line)):
                translate_end = True
                break
        return taxa_list
    
    def find_stdev(self, mcmc_file):
        '''
        Find the standard deviation of a mrBayes run
        :Input: The *.mcmc file created by a mrBayes analysis
        :Output: The standard deviation
        '''
        for line in mcmc_file:
            pass
        last = line
        #last number on the last line is the desired final stdev
        words = last.split()
        return words[-1]

