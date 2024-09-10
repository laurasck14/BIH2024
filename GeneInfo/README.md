# Gene information
NCBI and Open Targets were selected as sources to provide gene information summaries.

**eutilsGetSummary.py**\
API from NCBI was used to obtain the gene ID, symbol, Ref Seq Gene ID and summary from the list of genes available at the NCBI website.\
Usage: python3 eutilsGetSummary.py gene_RefSeqGene.csv gene_summary.csv

**OPT_API.py**\
API from Open Targets was used to obtain also the gene summaries. It requires to have Java installed in your local computer and the corresponding data. It will just extract the solicited information into a table\
Usage: python3 OPT_API.py 
