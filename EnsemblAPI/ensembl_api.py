import requests, sys, re
import pandas as pd
from sqlalchemy import create_engine, text
import psycopg2

def usage():
    """ Usage instructions!
    script to obtain the Ensembl protein IDs from the proteins not present in STRING 
    that are in the BioGRID database. Some have old gene symbols, so for those the updated gene symbol 
    is looked up first, and then the Ensembl protein ID is searched for the new symbol """
    print("Usage: python3 ensembl_api.py <input_file.csv> <output_file.csv>")
    print()
    print("Arguments:")
    print("  <input_file.csv>: path to the input csv file containing the gene symbols)")
    print("  <output_file.csv>: path to the output csv file where the information will be saved.")
    print()
    print("Example:")
    print("  python3 ensembl_api.py gene_symbols.csv ensembl_ids.csv")


# Ensembl REST API endpoint and headers
server = "https://rest.ensembl.org"
headers = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}
# connection to local pgAdmin
engine = create_engine('postgresql://laura:pass@127.0.0.1/laura')

# get Ensembl IDs from the Ensembl API
def getEnsemblIDs(symbol):
    ext_symbol = f"/lookup/symbol/homo_sapiens/{symbol}?expand=1"
    try:
        response = requests.get(f"{server}{ext_symbol}", headers=headers)
        response.raise_for_status()
        data = response.json()
        transcripts = data.get("Transcript", [])
        ensembl_protid = [transcript["Translation"]["id"] 
            for transcript in transcripts 
            if "Translation" in transcript and "id" in transcript["Translation"]]
        return ensembl_protid[0] if ensembl_protid else None

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred for symbol '{symbol}': {http_err}")
        return None

# get Synonyms from the local gene repository of GenDaB
def getGeneSynonyms(entrez_id):
    query = text(f"SELECT genesymbol FROM geneinfo.genes WHERE gene_no = :entrez_gene_id")   
    params = {'entrez_gene_id': entrez_id}
    with engine.connect() as connection:
        result = connection.execute(query, params)
        rows, = result.fetchall()[0]
        return rows

def main(argv):
    if len(sys.argv) != 3:
        usage()
        sys.exit(1)

    elif (re.search('.+(csv$)', sys.argv[1])) and (re.search('.+(csv$)', sys.argv[2])):
        df = pd.read_csv(sys.argv[1])        
        output_file = sys.argv[2]  
        results = []
        not_found = []
        for index, row in df.iterrows():
            symbol = row['genesymbol_a']
            entrez_id = row['entrez_gene_a']
            ensembl_protid = getEnsemblIDs(symbol)
            if ensembl_protid: results.append({
                    'entrez_gene_a': entrez_id,
                    'genesymbol_a': symbol,
                    'ensembl_protid': ensembl_protid,
                    'synonym': '-'
                })
            elif not ensembl_protid:
                print(f"Looking for {symbol} synonym")
                synonym = getGeneSynonyms(entrez_id)
                ensembl_protid2 = getEnsemblIDs(synonym)
                if synonym and not ensembl_protid2 and not ensembl_protid:
                    print(f"{symbol} has no Ensembl protein ID")
                    not_found.append({
                        'entrez_gene_a': entrez_id,
                        'genesymbol_a': symbol,
                    })
                elif synonym and ensembl_protid2:
                    results.append({
                    'entrez_gene_a': entrez_id,
                    'genesymbol_a': symbol,
                    'ensembl_protid': ensembl_protid2,
                    'synonym': synonym
                })
               

        results_df = pd.DataFrame(results)
        not_found_df = pd.DataFrame(not_found)
        results_df.to_csv(output_file, index=False)
        print(f"Data saved to {output_file}")
        not_found_df.to_csv('not_found.csv', index=False)
    else:
        usage()
        sys.exit(1)

if __name__ == "__main__":
    main(sys.argv)
