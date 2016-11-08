#!/usr/bin/python
import sys,os,re,optparse,tarfile,uuid,math
from arguments import *

def TF(inputTF):
    if( inputTF != None and inputTF!=False ): return "True"
    return "False"


'''
Builds several files - the overarching quartets_analysis.dag
                     - and all subsequent dags.
'''
def main():

    current_version = "#version 2.0.8"
    #  Difference in 2.0.3 - is that fileWriter_condor.py
    #      has been corrected to look for species names
    #      only at the beginning of the record.
    #      The prior version looked at the whole record and
    #      incorrect matches where being return.
    #  Difference in 2.0.4 - add supplemental output
    #      the list of all genes by all quartets.
    #  Difference in 2.0.5 - better diagnostics.
    #      Zip up mrBayes output by genegroup.  This avoid 10's of thousands of output in directory.
    #      Correct error in deciding which runs have StDev error
    #      Allow interleaved files
    #  Difference in 2.0.6 - small changes to further improve diagnostics
    #  Difference in 2.0.7 - add disk/memory reqs for finish and organize
	#  Difference in 2.0.8 - add "_$(jobname)" and "requirements = ( Machine =!= "fl-cssc-b217-7.net.wisc.edu" )" on Build RUN_MRBAYES JOB submit and Build RUN_BUCKY JOB submit 


    
    instanceID = uuid.uuid4()
    
    parser = getParser()
    options, remainder = parser.parse_args()

    #fetch the working directory    
    try:
        working_directory = os.path.dirname(os.path.realpath(__file__))
    except:
        sys.exit("Error: problem determining working directory")
        
    #the directory holding the gene files is the only positional argument
    try:
        gene_directory = remainder[-1]
    except:
        sys.exit("Error: please define a data directory.")
    
    #see if data directory exists
    if( not os.path.isdir(gene_directory) ):
        sys.exit("Error: problem gene/data directory, "+gene_directory+", not found.")
    
    file_count = 0
    if (options.list_of_files != None):
        list_of_files = open(options.list_of_files, 'r')
        for line in list_of_files: file_count += 1
        list_of_files.close()
    else:
        if( options.data_is_zipped == 1 ):
            iCount = 0
            for file in os.listdir(gene_directory):
                isTar = re.search(r".tar.gz$", file)
                if( isTar != None and not re.search(r"^D[0-9]+.tar.gz$", file) ):
                    iCount += 1
                    tarFilename = file
            if( iCount != 1 ):
                sys.exit("Error: not exactly one tar file in data directory '"+gene_directory+"/' (="+str(iCount)+").")
            myTarfile = tarfile.open(name=gene_directory+"/"+tarFilename, mode='r')
            files = myTarfile.getnames()
            for file in files :
                fileInfo = myTarfile.getmember(file)
                if( fileInfo.isfile() ): file_count += 1
        else:
            for (dirpath, dirnames, filenames) in os.walk(gene_directory): 
                for filename in filenames:
                    file_count += 1
    options.num_genes = file_count

    #Determine number of quartets
    #   If a file is provided -->  count number of lines.
    #   If no file is provided --> use q option
    num_quartets = 0
    if( options.list_of_quartets == "quartets.txt" ):
        sys.exit("Error: quartet file cannot be named <quartets.txt>")
    if( options.list_of_quartets != None):
       try:
           quartets_file = open(options.list_of_quartets, 'r')
       except:
           sys.exit("Error: problem opening quartet file: " + options.list_of_quartets)
       num_quartets_in_file = sum(1 for line in quartets_file)
       if( num_quartets_in_file == 0 ): sys.exit("Error: no quartets found in: " + options.list_of_quartets)
       if( options.num_quartets == 0 ):
           num_quartets = num_quartets_in_file
       else:
           if( options.num_quartets > num_quartets_in_file ): 
               sys.exit("Error: requested more quartets than available in file.")
           num_quartets = options.num_quartets
       
    else:
       num_quartets = options.num_quartets
    if( num_quartets == 0 ): sys.exit("Error: problem determining number of quartets to analyze.")
            
    #Determine number of genegroups
    #   If option is not set and a file is provided -->  count number of lines.
    #   If no file is provided --> use q option
    num_genegroups = options.num_genegroups

    if( num_genegroups < 1 or num_genegroups > file_count ): 
        sys.exit("Error: Number of genegroups not in range (1,"+str(file_count)+")")
        
    #confirm MrBayes is available
    mb_ok = os.path.isfile(options.mrBayes + "/src/mb")
    if (mb_ok != True): sys.exit("Error: MrBayes not found in directory " + options.mrBayes + "/src")
    mb_size = os.path.getsize(options.mrBayes + "/src/mb")

    #confirm mbsum is available
    mbsum_ok = os.path.isfile(options.bucky + "/src/mbsum")
    if (mbsum_ok != True): sys.exit("Error: mbsum not found in directory " + options.bucky + "/src")
    mbsum_size = os.path.getsize(options.mrBayes + "/src/mbsum")

    #confirm bucky is available
    bucky_ok = os.path.isfile(options.bucky + "/src/bucky")
    if (bucky_ok != True): sys.exit("Error: bucky not found in directory " + options.bucky + "/src")
    bucky_size = os.path.getsize(options.bucky + "/src/bucky")
        
    #open up output file and add information
    out  = "Quartet analysis version: " + current_version + "\n\n"
    out += "Calling command: \n"
    out += "- python " + " ".join(sys.argv) + "\n\n"
    out += "Working environment:\n"
    out += "- directory: " + working_directory + "\n"
    out += "- instance ID: " + str(instanceID) + "\n\n"
    out += "Gene data:\n"
    out += "- directory containing genefiles: " + gene_directory + "\n"
    out += "- is data zipped (-z): " + TF(options.data_is_zipped) +"\n"
    out += "- # gene files: " + str(file_count) + "\n"
    out += "- # gene groups to split data (-x): " + str(num_genegroups) + "\n\n"

    out += "Quartet data:\n"
    out += "- quartet list provided: " + TF(options.list_of_quartets) + "\n"
    if( options.list_of_quartets != None ):
        out += "- quartet list file: " + options.list_of_quartets + "\n"
        if( options.num_quartets > 0 ):
            out += "- " + str(num_quartets)+" will be chosen randomly from list.\n"
        else:
            out += "- all "+str(num_quartets)+" quartets will be run.\n"
    else:
        out += "- # of quartets: " + str(num_quartets) + " quartets will be chosen randomly.\n"
    out += "- will order by maintained (-o): " + TF(options.maintain_order) + "\n\n"

    out += "Other pipeline arguments:\n"
    out += "- allowed failure percent (-c): " + str(options.failure_percent) + "\n"
    out += "- will intermediate files be retained (-t): " + TF(options.testing) + ", t=" + str(options.testing) + "\n\n"

    out += "MrBayes arguments:\n"
    out += " - maximum allowed standard deviation (-d): " + str(options.max_stdev) + "\n"
    out += " - rates (-r): " + options.rates + "\n"
    out += " - amino acid model designated (-g): " + TF(options.aamodel)
    if( options.aamodel != None ): out += ", " + options.aamodel
    out += "\n"
    out += " - nst parameter (-s): " + str(options.nst) + "\n"
    out += " - number of generations (-n): " + str(options.mb_ngen) + "\n"
    out += " - MrBayes source directory (-m): " + options.mrBayes + "\n"
    out += " - size of MrBayes exe: " + str(mb_size) + " "
    if mb_size == 1815501 :
        out += "(vers. 3.2.4)"
    elif mb_size == 1779270 :
        out += "(vers. 3.2.3)"
    else:
        out += "(unknown version)"
    out += "\n\n"
    
    out += "BUCKy arguments:\n"
    out += " - alpha parameter (-a): " + str(options.alpha) + "\n"
    out += " - number of generations (-k): " + str(options.bucky_ngen) + "\n"
    out += " - BUCKy source directory (-b): " + options.bucky + "\n"
    out += " - size of BUCKy exe: " + str(bucky_size) + "\n"
    out += " - size of mbsum exe: " + str(mbsum_size) + "\n\n"
    
    out += "Checking versions of python scripts:\n"
    latest_version = {"organize.py":"#version 2.0.5",
                      "post_organize.py":"#version 2.0.5",
                      "run_mrbayes.py":"#version 2.0.5",
                      "run_bucky.py":"#version 2.0.5",
                      "finish.py":"#version 2.0.5",
                      "fileReader_condor.py":"#version 2.0.5",
                      "fileWriter_condor.py":"#version 2.0.5",
                      "quartet_condor.py":"#version 2.0.2",
                      "append_output.py":"#version 2.0.2",
                      "arguments.py":"#version 2.0.5",
                      "zip_conc_output.py":"#version 2.0.2",
                      "zip_mb_output.py":"#version 2.0.5",
                      "report_results.py":"#version 2.0.6",
                      "delete_mb_output.py":"#version 2.0.5",
                      "delete_files.py":"#version 2.0.4"}

    
    file_error = False
    error_message = ""
    for file_name,version in latest_version.iteritems():
        file_ok = os.path.isfile(file_name)
        if (file_ok != True):
            file_error = True
            error_message += "Error: file -" + file_name + " missing.\n"
        else:
            script_file = open(file_name, 'r')
            first_line = script_file.readline()
            second_line = script_file.readline()
            if( second_line.rstrip() != version ):
                file_error = True
                error_message += "Error: file -" + file_name + " not current version (" + version + ")\n"
                print file_name + "\n"
                print "f:" + second_line.rstrip() + "\n"
                print "c: " + version + "\n"
            else:
                out += "- " + file_name + ": " + second_line
            script_file.close()
    
    if( file_error ): sys.exit(error_message)
    out += "\n"

    #check if directories exist.  If not create them.
    out += "Checking directory structure for output.\n"
    if( os.path.isdir("log") ):
        out += "- log/ directory exists.\n"
    else:
        os.makedirs("log")
        out += "- log/ directory created.\n"

    if( os.path.isdir("err") ):
        out += "- err/ directory exists.\n"
    else:
        os.makedirs("err")
        out += "- err/ directory created.\n"
    if( os.path.isdir("out") ):
        out += "- out/ directory exists.\n\n"
    else:
        os.makedirs("out")
        out += "- out/ directory created.\n\n"

    #create D#.tar.gz files with the data separated into genegroups
    out += "Creating D#.tar.gz files with data subsetted into genegroups\n"
    genes_per_file = math.ceil(1. * file_count / num_genegroups)
    print "num_genegroups = "+str(num_genegroups)+"\n"
    print "file_count = "+str(file_count)+"\n"
    print "genes_per_file = "+str(genes_per_file)+"\n"
    myTarfile = []
    for iGG in range(0, num_genegroups):
        myTarfile.append( tarfile.open("D"+str(iGG)+".tar.gz",mode='w:gz') )
    if( num_genegroups == 1 ):
        out += "- Created D0.tar.gz\n"
    else:
        out += "- Created D0.tar.gz to D" + str(num_genegroups-1) + ".tar.gz\n"

    if (options.list_of_files != None):
        list_of_files = open(options.list_of_files, 'r')
        kount = 0
        for line in list_of_files:
            whichTarget = int(math.floor(1. * kount / genes_per_file))
            myTarfile[whichTarget].add(line)
            kount += 1
        list_of_files.close()
        out += "- Split files from " + options.list_of_files + " across D#.tar.gz files\n\n"
    else:
        if( options.data_is_zipped == 1 ):
            fullTarfile = tarfile.open(name=gene_directory+"/"+tarFilename, mode='r')
            files = fullTarfile.getmembers()
            kount = 0
            for fileInfo in files :
                if fileInfo.isfile():
                    whichTarget = int(math.floor(1. * kount / genes_per_file))
                    fileObj  = fullTarfile.extractfile(fileInfo)
                    myTarfile[whichTarget].addfile(fileInfo, fileObj)
                    kount += 1
            out += "- Split files from " + tarFilename + " across D#.tar.gz files\n\n"
        else:
            kount = 0
            for (dirpath, dirnames, filenames) in os.walk(gene_directory):
                for filename in filenames:
                    whichTarget = int(math.floor(1. * kount / genes_per_file))
                    myTarfile[whichTarget].add(os.path.join(dirpath, filename))
                    kount += 1
            if kount == 0:
                print "\n\nProgram did not find the gene directory\n\n"
                sys.exit()


                
            out += "- Split files from directory " + gene_directory + " across D#.tar.gz files\n\n"

    
            
    out += "Creating DAG and SUBMIT files\n"
    
    #Build QUARTET_ANALYSIS dag
    dg  = "#instanceID="+str(instanceID)+"\n"
    dg += "#Overarching DAG to run quartet_analysis.  To be submitted by user.\n\n"
    dg += "CONFIG QuartetAnalysis.config\n\n"
    dg += "JOB    organize     organize.submit\n"
    dg += "SPLICE run_quartets run_quartets.dag\n"
    dg += "JOB    finish       finish.submit\n\n"
    dg += "SCRIPT POST organize post_organize.py $RETURN\n"
    dg += "SCRIPT PRE  finish   zip_conc_output.py\n"
    dg += "SCRIPT POST finish   delete_files.py $RETURN -t " + str(options.testing) + "\n\n"
    dg += "PARENT organize     CHILD run_quartets\n"
    dg += "PARENT run_quartets CHILD finish\n"
    dag_file = open('QuartetAnalysis.dag', 'w')
    dag_file.write(dg)
    dag_file.close()

    out += "- quartet_analysis.dag\n"

    #Build CONFIG file
    dg  = "#instanceID="+str(instanceID)+"\n"
    dg += "DAGMAN_MAX_JOBS_IDLE=1000\n"
    if( options.testing != 0 ):
      dg += "DAGMAN_VERBOSITY=3\n\n"
    else:
      dg += "DAGMAN_VERBOSITY=1\n\n"
    dag_file = open('QuartetAnalysis.config', 'w')
    dag_file.write(dg)
    dag_file.close()

    out += "- quartet_analysis.dag\n"

    #Build ORGANIZE JOB submit
    st  = "#instanceID="+str(instanceID)+"\n"
    st += "#Submit file for organizing translation table, quartets, gene groups\n"
    st += "# - called by QUARTET_ANALYSIS dag\n\n"
    st += "Executable = $(BDIR)/organize.py\n"
    st += "Universe = Vanilla\n"
    st += "Log    = log/organize.log\n"
    st += "Output = out/organize.out\n"
    st += "Error  = err/organize.err\n\n"

    st += "Request_memory = 1GB\n"
    st += "Request_disk   = 50000\n\n"

    st += "should_transfer_files   = YES\n"
    st += "when_to_transfer_output = ON_EXIT\n\n"
    st += "BDIR  = " + working_directory + "\n"
    st += "GENES = " + gene_directory + "\n\n"
    
    st += "transfer_input_files = "
    st += "$(BDIR)/organize.py,"
    st += "$(BDIR)/fileReader_condor.py,"
    st += "$(BDIR)/quartet_condor.py,"
    st += "$(BDIR)/arguments.py,"
    st += "$(GENES)"
    if (options.list_of_quartets != None): st+= "," + options.list_of_quartets
    if (options.list_of_files != None): st += ",$(BDIR)/" + options.list_of_files
    st+= "\n\n"
    
    st += "Arguments = " + buildArgList("felqzti", options, gene_directory)
    st += "\nQueue\n"
    
    submit_file = open('organize.submit', 'w')
    submit_file.write(st)
    submit_file.close()

    out += "- organize.submit\n"


    #Build RUN_QUARTETS dag
    dg  = "#instanceID="+str(instanceID)+"\n"
    dg += "#This dag set up to run ALL quartets.\n"
    dg += "#  - it is called by quartet_analysis.dag.\n"
    dg += "#  - it calls run_quartet.dag to run each individual quartet.\n\n"
    for iQ in range(1,num_quartets+1):
      dg += "SPLICE QUARTET_"+str(iQ)+" run_quartet.dag\n"
    dag_file = open('run_quartets.dag', 'w')
    dag_file.write(dg)
    dag_file.close()

    out += "- run_quartets.dag\n"

    #Build RUN_QUARTET dag
    dg  = "#instanceID="+str(instanceID)+"\n"
    dg += "#This dag runs an individual quartet.\n"
    dg += "#  - it is called by run_quartets.dag.\n"
    dg += "#  - it calls run_genegroups to distribute the MrBayes calcs on subsets of the genes.\n\n"
    dg += "#  - when these finish, it calls BUCKy.\n\n"
    
    dg += "SPLICE run_genegroups run_genegroups.dag\n"
    dg += "JOB    run_bucky      run_bucky.submit\n"
    dg += 'VARS   run_bucky      jobname = "$(JOB)"\n\n'
    dg += 'SCRIPT PRE  run_bucky zip_mb_output.py $JOB\n'
    dg += 'SCRIPT POST run_bucky delete_mb_output.py $RETURN $JOB\n\n'
    dg += "PARENT run_genegroups CHILD run_bucky\n"
    dag_file = open('run_quartet.dag', 'w')
    dag_file.write(dg)
    dag_file.close()

    out += "- run_quartet.dag\n"
    
    #Build RUN_GENEGROUPS dag
    dg  = "#instanceID="+str(instanceID)+"\n"
    dg += "#This dag runs all genegroups for an individual quartet.\n"
    dg += "#  - it is called by run_quartet.dag.\n"
    dg += "#  - it submits JOBS for each genegroup.\n\n"
    for iG in range(0,num_genegroups):
      dg += "JOB  gene_group_"+str(iG)+" run_mrbayes.submit\n"
      dg += 'VARS gene_group_'+str(iG)+' jobname="$(JOB)" data = "D' + str(iG) + '.tar.gz"\n'
      dg += 'SCRIPT POST gene_group_'+str(iG)+' report_results.py $RETURN $JOB -t '+ str(options.testing) +'\n\n'
    dag_file = open('run_genegroups.dag', 'w')
    dag_file.write(dg)
    dag_file.close()

    out += "- run_genegroups.dag\n"

    #Build RUN_MRBAYES JOB submit
    st  = "#instanceID="+str(instanceID)+"\n"
    st += "#Submit file for running MrBayes and mbsum on a group of genes\n"
    st += "# - called by RUN_GENEGROUPS dag\n\n"
    st += "Executable = $(BDIR)/run_mrbayes.py\n"
    st += "Universe = Vanilla\n"
    if( options.testing != 0 ):
      st += "Log    = log/run_mrbayes.$(CLUSTER).log\n"
      st += "Output = out/run_mrbayes.$(CLUSTER).out\n"
      st += "Error  = err/run_mrbayes.$(CLUSTER).err\n\n"
    else:
      st += "Log    = log/run_mrbayes_$(jobname).log\n"
      st += "Output = out/run_mrbayes_$(jobname).out\n"
      st += "Error  = err/run_mrbayes_$(jobname).err\n\n"
    st += "+WantFlocking  = true\n"
    st += "+WantGlideIn   = true\n"
    st += "Request_memory = 1GB\n"
    st += "Request_disk   = 50000\n\n"
    st += '''requirements = ( Machine =!= "fl-cssc-b217-7.net.wisc.edu" )\n'''
    st += "should_transfer_files = YES\n"
    st += "when_to_transfer_output = ON_EXIT\n\n"
    st += "BDIR    = " + working_directory + "\n"
    st += "MRBAYES = " + options.mrBayes + "/src\n"
    st += "BUCKY   = " + options.bucky + "/src\n"
    
    st += "transfer_input_files = "
    st += "$(BDIR)/run_mrbayes.py,"
    st += "$(BDIR)/fileReader_condor.py,"
    st += "$(BDIR)/fileWriter_condor.py,"
    st += "$(BDIR)/quartet_condor.py,"
    st += "$(BDIR)/arguments.py,"
    st += "$(BDIR)/errorcodes.py,"
    st += "$(MRBAYES)/mb,"
    st += "$(BUCKY)/mbsum,"
    st += "$(BDIR)/translate.txt,"
    st += "$(BDIR)/quartets.txt,"
    st += "$(data)"
    if (options.list_of_quartets != None): st+= "," + options.list_of_quartets
    if (options.list_of_files != None): st += ",$(BDIR)/" + options.list_of_files
    st+= "\n"
    if( options.testing == 0 ):
      st += "transfer_output_files = "
      st += "$(jobname).tar.gz,"
      st += "$(jobname).stats"
      st += "\n\n"
    else:
      st += "\n"
    
    #The genegroups are not launched via queue ##, so replace $PROCESS with $gene group #
    st += "Arguments = -y $(jobname)" + buildArgList("eusnrcdtmbgzf", options, gene_directory) + "\n\n"
    st += "Queue\n"
    
    submit_file = open('run_mrbayes.submit', 'w')
    submit_file.write(st)
    submit_file.close()

    out += "- run_mrbayes.submit\n"

    #Build RUN_BUCKY JOB submit
    st  = "#instanceID="+str(instanceID)+"\n"
    st += "#Submit file for running BUCKy on results of MrBayes for ALL genegroups of a single quartet\n"
    st += "# - called by RUN_QUARTET dag\n\n"
    st += "Executable = $(BDIR)/run_bucky.py\n"
    st += "Universe = Vanilla\n"
    if( options.testing != 0 ):
      st += "Log    = log/run_bucky.$(CLUSTER).log\n"
      st += "Output = out/run_bucky.$(CLUSTER).out\n"
      st += "Error  = err/run_bucky.$(CLUSTER).err\n\n"
    else:
      st += "Log    = log/run_bucky_$(jobname).log\n"
      st += "Output = out/run_bucky_$(jobname).out\n"
      st += "Error  = err/run_bucky_$(jobname).err\n\n"
    st += "+WantFlocking  = true\n"
    st += "+WantGlideIn   = true\n"
    st += "Request_memory = 1GB\n"
    st += "Request_disk   = 5000\n\n"
    st += '''requirements = ( Machine =!= "fl-cssc-b217-7.net.wisc.edu" )\n'''
    st += "should_transfer_files = YES\n"
    st += "when_to_transfer_output = ON_EXIT\n\n"
    st += "BDIR = " + working_directory + "\n"
    st += "BUCKY   = " + options.bucky + "/src\n"
    #if( options.data_is_zipped ): st += "GENES = " + gene_directory + "\n"
    
    st += "transfer_input_files = "
    st += "$(BDIR)/run_bucky.py,"
    st += "$(BDIR)/arguments.py,"
    st += "$(BDIR)/translate.txt,"
    st += "$(BDIR)/genes.txt,"
    st += "$(BDIR)/fileReader_condor.py,"
    st += "$(BDIR)/fileWriter_condor.py,"
    st += "$(BDIR)/quartet_condor.py,"
    st += "$(BDIR)/quartets.txt,"
    st += "$(BDIR)/errorcodes.py,"
    st += "$(BUCKY)/bucky,"
    st += "$(jobname).tar.gz"
    #if (options.list_of_quartets != None): st+= "," + options.list_of_quartets
    #if (options.list_of_files != None): st += ",$(BDIR)/" + options.list_of_files
    #if( options.data_is_zipped ): st += ",$(GENES)"
    st+= "\n\n"
    
    st += "Arguments = -y $(jobname)" + buildArgList("feujakotbzc", options, gene_directory)
    st += "\nQueue\n"
    
    submit_file = open('run_bucky.submit', 'w')
    submit_file.write(st)
    submit_file.close()

    out += "- run_bucky.submit\n"

    #Build FINISH JOB submit
    st  = "#instanceID="+str(instanceID)+"\n"
    st += "#Submit file for summarizing results of all quartets\n"
    st += "# - called by QUARTET_ANALYSIS dag\n\n"
    st += "Executable = $(BDIR)/finish.py\n"
    st += "Universe = Vanilla\n"
    st += "Log    = log/finish.log\n"
    st += "Output = out/finish.out\n"
    st += "Error  = err/finish.err\n"
    st += "Request_memory = 1GB\n"
    st += "Request_disk   = 50000\n\n"
    st += "should_transfer_files = YES\n"
    st += "when_to_transfer_output = ON_EXIT\n\n"
    st += "BDIR = " + working_directory + "\n"
    
    st += "transfer_input_files = "
    st += "$(BDIR)/finish.py,"
    st += "$(BDIR)/fileReader_condor.py,"
    st += "$(BDIR)/fileWriter_condor.py,"
    st += "$(BDIR)/quartet_condor.py,"
    st += "$(BDIR)/translate.txt,"
    st += "$(BDIR)/quartets.txt,"
    st += "$(BDIR)/arguments.py,"
    st += "$(BDIR)/errorcodes.py,"
    st += "$(BDIR)/finish.tar.gz,"
    st += "$(BDIR)/QuartetAnalysis.meta"
    st+= "\n\n"
    
    st += "Arguments = " + buildArgList("ot", options, gene_directory)
    st += "\nQueue\n"
    
    submit_file = open('finish.submit', 'w')
    submit_file.write(st)
    submit_file.close()

    out += "- summarize.submit\n\n"

    output_file = open('QuartetAnalysis.meta', 'w')
    output_file.write(out)
    output_file.close()

    print "\n\nProgram set_up finished successfully.\nA summary can be found in QuartetAnalysis.meta\n\n"

main()
