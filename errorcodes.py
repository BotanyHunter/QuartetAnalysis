#errorcodes.py
#version 2.0.5

errorList = ["no error",
             "error code 1",
             "mrBayes.py: Could not open quartet.txt",
             "mrBayes.py: Could not interpret quartet.txt",
             "mrBayes.py: Could not open translate.txt",
             "mrBayes.py: Could not interpret translate.txt",
             "mrBayes.py: Could not interpret condor job name",
             "mrBayes.py: Could not find tarfile",
             "mrBayes.py: Could not create data subdirectory",
             "mrBayes.py: Could not open tarfile",
             "mrBayes.py: Could not open list of gene files",
             "mrBayes.py: Could not get gene files from tarfile",
             "mrBayes.py: Could not get gene files from data directory",
             "mrBayes.py: Could not interpret read tar.gz",
             "mrBayes.py: Could not extract file from tar.gz",
             "mrBayes.py: Could not open gene file",
             "mrBayes.py: Could not interpret gene file",
             "mrBayes.py: Could not initialize quartet subset of gene file",
             "mrBayes.py: Could not write quartet subset of gene file",
             "mrBayes.py: Could not run mrBayes",
             "mrBayes.py: Filename mismatch",
             "mrBayes.py: Could not find expected mcmc output",
             "mrBayes.py: Could not run mbsum",
             "mrBayes.py: Could not delete temporary files",
             "mrBayes.py: Could not create or write results file",
             "mrBayes.py: Could not create gene group zip file",
             "mrBayes.py: Could not delete file after zipping",
             "mrBayes.py: Statistics do not add",
             "mrBayes.py: Could not write gene group zip file"
             "zip_mb_output.py: Could not interpret condor job name",
             "zip_mb_output.py: Could not open target tar file",
             "zip_mb_output.py: Could not open input tar.gz",
             "zip_mb_output.py: Could not extract .in file",
             "zip_mb_output.py: Could not add .in file",
             "zip_mb_output.py: Could not delete .in file",
             "zip_mb_output.py: Could not delete input tar.gz",
             "zip_mb_output.py: Could not get directory.",
             "zip_mb_output.py: No input tar.gz found",
             "post_organize: missing node return status",
             "post_organize: organize.submit returned an error value",
             "post_organize: Could not update QuartetAnalysis.meta",
             "post_organize: Could not interpret QuartetAnalysis.meta",
             "report_results: missing node return status"
             "report_results: missing job name",
             "report_results: run_mrbayes.submit returned a non-zero value",
             "report_results: Could not read new stats from file",
             "report_results: Could not open QuartetAnalysis.meta",
             "report_results: Could not create new statistics line",
             "report_results: Could not interpret QuartetAnalysis.meta",
             "report_results: Could not delete stats file",
             "delete_mb_output: missing node return status",
             "delete_mb_output: missing job name",
             "delete_mb_output: error finding quartet index",
             "delete_mb_output: Could not open QuartetAnalysis.meta",
             "delete_mb_output: Could not interpret QuartetAnalysis.meta",
             "delete_mb_output: Could not delete bucky results file",
             "fileWriter_condor: Could not initialize",
             "fileWriter_condor: Less than four taxa found",
             "fileWriter_condor: Could not open new nexus file",
             "fileWriter_condor: Could not create or write header",
             "fileWriter_condor: Could not write data",
             "fileWriter_condor: Could not write END to data block",
             "fileWriter_condor: Could not write MrBayes Block",
             "fileWriter_condor: Could not close new nexus file",
             "run_bucky.py: Could not open/interpret translate.txt",
             "run_bucky.py: Could not interpret job name",
             "run_bucky.py: Could not interpret gene file",
             "run_bucky.py: could not open/interpret quartet file in mrBayes.py",
             "run_bucky.py: number of gene files is zero",
             "run_bucky.py: could not open/interpret QuartetAnalysis.meta",
             "run_bucky.py: could not open tar file with mrBayes/mbsum results",
             "run_bucky.py: mrBayes/mbsum results empty", 
             "run_bucky.py: mrBayes/mbsum results too few",
             "run_bucky.py: could not extract files from .tar.gz",
             "run_bucky.py: error in BUCKy",
             "run_bucky.py: could not write gene stats",
             "run_bucky.py: could not make gene dictionary",
             "run_bucky.py: error writing results",
             "run_bucky.py: error deleting files.",
             "mrBayes.py: Execution failed",
             "mrBayes.py: Unknown mrBayes execution error"
          ]

def findErrorCode(errorString):
    try:
        errorCode = errorList.index(errorString)
    except:
        errorCode = -1
    return errorCode

def errorString(errorCode):
    if( errorCode == -1 ):
       return "unknown error code"
    try:
       errorString = errorList[errorCode]
    except:
       errorString = "unknown error code"
    return errorString    

