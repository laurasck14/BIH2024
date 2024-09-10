import pandas as pd
from sqlalchemy import create_engine, text
import psycopg2

engine = create_engine('postgresql://laura:pass@127.0.0.1/laura')

def getUnknownGenes(entrez_gene_id):
    query = text(f"SELECT strand FROM geneinfo.genes WHERE gene_no = :entrez_gene_id")
    params = {'entrez_gene_id': entrez_gene_id}
    with engine.connect() as connection:
        result = connection.execute(query, params)
        rows, = result.fetchall()[0]
        return rows

def main():
    input_file = 'not_found.csv'
    df = pd.read_csv(input_file)    
    unknown_genes = []
    other_genes = []
    for index, row in df.iterrows():
        entrez_gene_id = row['entrez_gene_a']
        genesymbol_a = row['genesymbol_a']        
        unknown = getUnknownGenes(entrez_gene_id)
        if unknown:
            unknown_genes.append({
                'entrez_gene_a': entrez_gene_id,
                'genesymbol_a': genesymbol_a,
            })
        else: 
            other_genes.append({
                'entrez_gene_a': entrez_gene_id,
                'genesymbol_a': genesymbol_a,
            })
    unknown_genes_df = pd.DataFrame(unknown_genes)
    other_genes_df = pd.DataFrame(other_genes)
    unknown_genes_df.to_csv('unknown_genes.csv', index=False)
    other_genes_df.to_csv('not_on_GenDaB.csv', index=False)
    print("Unknown genes saved")

if __name__ == "__main__":
    main()