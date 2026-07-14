"""@bruin

# TODO: Set the asset name (recommended pattern: schema.asset_name).
# - Convention in this module: use an `ingestion.` schema for raw ingestion tables.
name: ingestion.trips

# TODO: Set the asset type.
# Docs: https://getbruin.com/docs/bruin/assets/python
type: python

# TODO: Pick a Python image version (Bruin runs Python in isolated environments).
# Example: python:3.11
image: python:3.11

# TODO: Set the connection.
connection: duckdb-default

# TODO: Choose materialization (optional, but recommended).
# Bruin feature: Python materialization lets you return a DataFrame (or list[dict]) and Bruin loads it into your destination.
# This is usually the easiest way to build ingestion assets in Bruin.
# Alternative (advanced): you can skip Bruin Python materialization and write a "plain" Python asset that manually writes
# into DuckDB (or another destination) using your own client library and SQL. In that case:
# - you typically omit the `materialization:` block
# - you do NOT need a `materialize()` function; you just run Python code
# Docs: https://getbruin.com/docs/bruin/assets/python#materialization
materialization:
  # TODO: choose `table` or `view` (ingestion generally should be a table)
  type: table
  # suggested strategy: append
  strategy: append

# TODO: Define output columns (names + types) for metadata, lineage, and quality checks.
# Tip: mark stable identifiers as `primary_key: true` if you plan to use `merge` later.
# Docs: https://getbruin.com/docs/bruin/assets/columns
# columns:
#   - name: TODO_col1
#     type: TODO_type
#     description: TODO
columns:
  - name: pickup_datetime
    type: timestamp
    description: "When the meter was engaged"
  - name: dropoff_datetime
    type: timestamp
    description: "When the meter was disengaged"

@bruin"""

# TODO: Add imports needed for your ingestion (e.g., pandas, requests).
# - Put dependencies in the nearest `requirements.txt` (this template has one at the pipeline root).
# Docs: https://getbruin.com/docs/bruin/assets/python


# TODO: Only implement `materialize()` if you are using Bruin Python materialization.
# If you choose the manual-write approach (no `materialization:` block), remove this function and implement ingestion
# as a standard Python script instead.

import os
import json
import requests
import pandas as pd
from io import BytesIO

BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/{taxi_type}_tripdata_{year_month}.parquet"

def materialize():
  start_date = os.environ["BRUIN_START_DATE"]
  end_date = os.environ["BRUIN_END_DATE"]
  taxi_types = json.loads(os.environ["BRUIN_VARS"]).get("taxi_types", ["yellow"])

  # Generate list of months between start and end dates
  months = pd.period_range(start=start_date, end=end_date, freq="M")

  dataframes = []
  for taxi_type in taxi_types:
    for month in months:
      year_month = month.strftime("%Y-%m")
      url = BASE_URL.format(taxi_type=taxi_type, year_month=year_month)

      response = requests.get(url)
      if response.status_code != 200:
        # Some months/taxi types may not have data published yet; skip them.
        continue

      df = pd.read_parquet(BytesIO(response.content))
      df["taxi_type"] = taxi_type
      dataframes.append(df)

  final_dataframe = pd.concat(dataframes, ignore_index=True) if dataframes else pd.DataFrame()

  return final_dataframe
