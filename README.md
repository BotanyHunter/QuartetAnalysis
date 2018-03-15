# QuartetAnalysis
QA examines four clades/bins for signs of inter-clade hybridization.

If four clades are 1) all reciprocally monophyletic and 2) without gene-flow between them, then
a phylogenetic reconstruction using one placeholder from each bin
should recover the same topology independent of which taxa we choose from each bin. 
If either of the above assumptions do not hold, then the distribution of topologies will show structure and clustering.  
This is evidence that one or both of the assumptions is incorrect, i.e. either the groups are not monophyletic or
there has been gene-flow between them.

QA, using HTCondor, will simulataneously run the 1000's of different quartets necessary for this analysis.
Also supplied are tools to visualize the resulting topologies.

Steps to use QuartetAnalysis:
<ul>
  <li>From a HTCondor node, clone the QuartetAnalysis repository:</br>
      git clone ...</li>
  <li>Place in the QuartetAnalysis a subdirectory for the data files.  
      The data should be in a zipped tar ball (i.e. tar.gz) 
      and in the nexus format.</li>
  <li>A file should be created that signals which taxa belongs to each of the four bins.
      This file should have one line for each taxa and the format of each line is: # (tab) taxaname
      where # is 1, 2, 3, or 4.  If # is 0, then this taxa is not included in the analysis.</li>
  <li>To create the quartets to run, run the following program from the command line:</br>
      python createQuartets.py <i>binFileName</i> <i>suffix</i></br>
      where <i>binFileName</i> is the name of the file created above with the bin allocations and
      <i>suffix</i> is a suffix that will be appended to the file with the list of quartets,
      allQuartets_<i>suffix</i>.txt.</i>
</ul>
