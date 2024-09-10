# Ensembl API
The API prvided by Ensembl was used to obtain the protein IDs from the proteins not present in STRING that are in the BioGRID database. Some of these proteins in the BioGRID database are named using old gene symbols so the goal was to update them. The symbol is updated and then the Ensembl protein ID is searched from the new symbol. The proteins that remain still not found are stored in not_found.csv\
This codes connects to pgAdmin where the data from BioGRID was stored.

**ensembl_api.py**\
Usage: python3 ensembl_api.py <input_file.csv> <output_file.csv>

**unknown_genes.py**\
To further investigate the "not found genes" these were searched in the internal database from GenDaB
Usage: python3 unknown_genes.py not_found.csv
