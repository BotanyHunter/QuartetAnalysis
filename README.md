# QuartetAnalysis
QA examines four clades for signs of inter-clade hybridization.

If four clades are all reciprocally monophyletic without gene-flow between them, then
a phylogenetic reconstruction using one placeholder from each bin
should recover the same topology independent of which taxa we choose from each bin.

QA, using HTCondor, runs 1000's of different quartets, each quartet with one taxa chosen from each clade.
Also supplied are tools to visualize the resulting topologies.  If either of the above assumptions
do not hold, then the distribution of topologies will show structure and clustering.  This
can be used as evidence that either the groups are not monophyletic or that
there has been gene-flow between them.
