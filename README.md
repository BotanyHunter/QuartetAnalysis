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
  <li>Place in the QuartetAnalysis a subdirectory for the data files.  The data should be in a zipped tar bar (i.e. tar.gz)</li>
</ul>
