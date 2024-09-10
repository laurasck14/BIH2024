from pyspark.sql import SparkSession
import pyspark.sql.functions as F
import glob, os
import pandas as pd

"""
Open Targets Platform API to retrieve information related to gene summaries
Data was downloaded on July 2024 from: 
    wget --recursive --no-parent --no-host-directories --cut-dirs 8 ftp://ftp.ebi.ac.uk/pub/databases/opentargets/platform/24.06/output/etl/json/targets
This code was generated from the help page of Open Targets: 
    https://platform-docs.opentargets.org/data-access/datasets
Usage: python3 OPT_API.py (need Java installed)
"""
evidencePath = "targets/"
spark = (SparkSession.builder.master('local[*]').getOrCreate())

# read evidence dataset
evd = spark.read.json(evidencePath)
#filter only entries with Descriptions
evd_filtered = evd.filter(F.size(F.col("functionDescriptions")) > 0)

# select fields of interest based on the schema
evdSelect = (evd_filtered.select("id",
        "approvedSymbol",
        F.concat_ws(", ", "functionDescriptions").alias("functionDescriptions"))
)
#evdSelect.show() # to show queried data
evdSelect.write.csv("opt_summaries.csv", header=True)
spark.stop()

# merge generated files
part_files = glob.glob(os.path.join("opt_summaries.csv", 'part-*'))
df_list = [pd.read_csv(file) for file in part_files]
merged_df = pd.concat(df_list)
merged_csv_path = os.path.join("opt_summaries.csv", 'opt_merged.csv')
merged_df.to_csv(merged_csv_path, index=False)
