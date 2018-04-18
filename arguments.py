#Arguments.py
#version 2.0.6

import os, optparse

def buildArgList(whichArgs, options, gene_file):
    #build arguments for later submit files
    args = ""
    if( "a" in whichArgs ): args += " -a " + str(options.alpha)
    if( "b" in whichArgs ):
      if (options.bucky != '/usr/local/bin'):
        args += " -b " + options.bucky + "/src"
      else:
        args += " -b " + options.bucky
    if( "c" in whichArgs ): args += " -c " + str(options.failure_percent)
    if( "d" in whichArgs ): args += " -d " + str(options.max_stdev)
    if( "e" in whichArgs ): args += " -e " + os.path.dirname(os.path.realpath(__file__))
    if( "f" in whichArgs ): args += " -f " + gene_file + "/"
    if ("g" in whichArgs and options.aamodel != None): args += " -g " + options.aamodel
    if ("i" in whichArgs and options.list_of_files != None): args += " -i " + options.list_of_files
    if ("j" in whichArgs ): args += " -j " + str(options.num_genes)
    if( "k" in whichArgs ): args += " -k " + str(options.bucky_ngen)
    if ("l" in whichArgs and options.list_of_quartets != None): args += " -l " + options.list_of_quartets
    if( "m" in whichArgs ):
      if (options.mrBayes != '/usr/local/bin'):
        args += " -m " + options.mrBayes + "/src"
      else:
        args += " -m " + options.mrBayes
    if( "n" in whichArgs ): args += " -n " + str(options.mb_ngen)
    if( "o" in whichArgs ): args += " -o " + str(options.maintain_order)
    if( "p" in whichArgs ): args += " -p $(PROCESS)"
    if( "q" in whichArgs ): args += " -q " + str(options.num_quartets)
    if( "r" in whichArgs ): args += " -r " + options.rates
    if( "s" in whichArgs ): args += " -s " + str(options.nst)
    if( "t" in whichArgs ): args += " -t " + str(options.testing)
    if( "u" in whichArgs ): args += " -u " + str(options.burnin)
    if( "v" in whichArgs ): args += " -v " + str(options.outputSuffix)
    if( "x" in whichArgs ): args += " -x " + str(options.num_genegroups)
    if( "y" in whichArgs ): args += " -y $(jobname)"
    if( "z" in whichArgs ): args += " -z " + str(options.data_is_zipped)

    #if user-specified lists of quartets and/or files are included, add them to the argument list. Otherwise leave them out.
        
    return args
    


def getParser():
    parser = optparse.OptionParser()
    #general options
    parser.add_option('-b', '--bucky', dest = 'bucky', default = '/usr/local/bin', help = 'Absolute path to $(BUCKY_HOME)')
    parser.add_option('-c', '--failure_percent', dest = 'failure_percent', type = 'float', default = '0.50', help = 'Percentage of the number of genes that can fail without affecting BUCKy analysis')
    parser.add_option('-e', '--execDir', dest = 'execDir', default = '.', help = 'Current directory where the executable is located')
    parser.add_option('-f', '--gene_file', dest = 'gene_file', default = '.', help = 'Absolute path to folder containing nexus files')
    parser.add_option('-i', '--list_of_files', dest = 'list_of_files', default = None, help = 'Text file containing user-specified nexus-formatted files (one per line) to analyze')
    parser.add_option('-j', '--num_genes', dest='num_genes', default = 0, help = 'for internal use')
    parser.add_option('-l', '--list_of_quartets', dest = 'list_of_quartets', default = None, help = 'Text file containing user-specified quartets to analyze')
    parser.add_option('-m', '--mrBayes', dest = 'mrBayes', default = '/usr/local/bin', help = 'Absolute path to $(MRBAYES_HOME)')
    parser.add_option('-o', '--order', dest='maintain_order',type='int',default=0,help='set to 1 to maintain quartet order')
    parser.add_option('-p', '--process', dest = 'process', help = "Process number")
    parser.add_option('-q', '--num_quartets', dest = 'num_quartets', type = 'int', default = 0, help = 'Number of 4-taxon sets to be analyzed')
    parser.add_option('-t', '--test', dest = 'testing', type='int', default = 0, help = 'Set to 1 to not delete .err, .out, .log files')
    parser.add_option('-u', '--burnin', dest = 'burnin', type = 'float', default = '0.25', help = 'Burnin frequency for mrBayes and BUCKy')
    parser.add_option('-v', '--output_suffix', dest='outputSuffix', default='', help = 'suffix to add to output filenames')
    parser.add_option('-w', '--quartet', dest='quartet',help='4-taxon set')
    parser.add_option('-x', '--num_genegroups', dest='num_genegroups',type='int', default=1, help='File containing genes to consider')
    parser.add_option('-y', '--condor_job_name', dest='condor_job_name', default = '', help = 'used internally to pass information')
    parser.add_option('-z', '--data_is_zipped', dest = 'data_is_zipped', type='int', default = 0, help = 'Set to 1 if data is provided in a tar.gz file.')
    
    #mrBayes options
    mb_group = optparse.OptionGroup(parser, "mrBayes options", "Optional arguments for mrBayes analyses")
    mb_group.add_option('-s', '--nst', dest = 'nst', type = 'int', default = 2, help = 'Determines the nst parameter of mrBayes')
    mb_group.add_option('-n', '--mb_ngen', dest = 'mb_ngen', type = 'int', default = 1000000, help = 'The number of generations of mrBayes')
    mb_group.add_option('-r', '--rates', dest = 'rates', default = 'gamma', help = 'Determines the rate parameter of mrBayes')
    mb_group.add_option('-d', '--max_stdev', dest = 'max_stdev', type = 'float', default = 0.1, help = 'Maximum standard deviation allowed in mrBayes analyses')
    mb_group.add_option('-g', '--aamodel', dest = 'aamodel', default=None, help='amino acide model, such as Poisson, Jones')
    parser.add_option_group(mb_group)
    
    #BUCKy options
    bucky_group = optparse.OptionGroup(parser, "BUCKy options", "Optional arguments for BUCKy analyses")
    bucky_group.add_option('-a', '--alpha', dest = 'alpha', type = 'float', default = 1.0, help = 'Determines the alpha parameter of BUCKy')
    bucky_group.add_option('-k', '--bucky_ngen', dest = 'bucky_ngen', type = 'int', default = 1000000, help = 'Number of generations of BUCKy')
    parser.add_option_group(bucky_group)
    
    return parser

