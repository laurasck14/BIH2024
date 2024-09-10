import numpy as np
from os import path
import pandas as pd
import urllib.request
import json, sys, math, re

def usage():
    """Usage instructions"""
    print("Usage: python3 eutilsGetSummary.py <input_file.csv> <output_file.csv>")
    print("Note: conversion txt -> csv can be done with: sed 's/\\t/,/g' input_file.txt > output_file.csv") 
    print()
    print("Arguments:")
    print("  <gene_ids.csv>: path to the input csv file containing GeneIDs, from NCBI (gene_RefSeqGene.txt)")
    print("  <output_file.csv>: path to the output csv file where the information will be saved.")
    print()
    print("Example:")
    print("  python3 eutilsGetSummary.py gene_RefSeqGene.csv gene_summary.csv")

def summaries(gene_info_file, output_file):
    open(output_file, 'w').close()
    df = pd.read_csv(gene_info_file)
    gene_ids = df['GeneID'].unique()
    symbols = df.set_index('GeneID')['Symbol'].to_dict() #assign the symbols and RSG to the correct GeneIDs
    rsgs = df.set_index('GeneID')['RSG'].to_dict()
    chunk_size = 100
    cn = math.ceil(len(gene_ids)/chunk_size+1)
    for i in range(cn): #separate genes into chunks for faster processing of large inputs
        chunk_genes = gene_ids[chunk_size*i:np.min([chunk_size*(i+1), len(gene_ids)])]
        gids = ','.join([str(s) for s in chunk_genes])
        url =  'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=gene&id=' + gids + '&retmode=json'
        data = json.load(urllib.request.urlopen(url))
        result = []
        for g in chunk_genes: 
            summary = data['result'][str(g)]['summary'] if str(g) in data['result'] else ''
            result.append([g, symbols[g], rsgs[g], summary])
        
        pd.DataFrame(result, columns=['gene_id', 'genesymbol', 'RSG', 'summary' ]).to_csv(
            output_file, index=False, mode='a', header= (i==0))

def main(argv):
    if len(sys.argv) != 3:
        usage()
        sys.exit(1)
    # check for the correct formating of input/output files given
    elif (re.search('.+(csv$)', sys.argv[1])) and (re.search('.+(csv$)', sys.argv[2])):
        gene_info_file = sys.argv[1]
        output_file = sys.argv[2]
        summaries(gene_info_file, output_file)

    else:
        print(f'Error: Some file(s) do not have the right format')
        usage()
        sys.exit(1)
          
if __name__=='__main__':
    main(sys.argv)

# modified from https://www.biostars.org/p/2144/ 
