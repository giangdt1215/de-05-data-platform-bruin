# What is Bruin?
Bruin is an end-to-end data platform that combines ingestion, transformations, orchestration, data quality checks, metadata, and lineage into a single tool.

Instead of using five or six different tools configured separately, Bruin lets you have your code logic, configurations, dependencies, and quality checks all in the same place.

# The modern data stack
A typical data stack involves several components:

 - Extract/ingest data from third-party sources or databases into a data warehouse or data lake
 - Run transformations: clean data, create reports, push results to a warehouse, lake, or third-party application
 - Orchestrate: tell different scripts and services when to run, how to run, and how to communicate with each other
 - Data quality and governance: ensure accuracy, completeness, and consistency of data before delivering it to consumers

Bruin brings all of these together so you don't need to be a DevOps person, data infrastructure engineer, and data architect just to build a pipeline.

# Concept: Project
A Project is the root directory where you create your entire Bruin data pipeline. It serves as the foundation for organizing all your data assets, configurations, and connections.

Project Initialization: bruin init zoomcamp my-pipeline

# The .bruin.yml File
Located at the root of your project, this file defines environments, connections, and secrets.

Important: This file is always added to .gitignore to protect secrets. It stays local only and should never be pushed to your repo.

```yaml
default_environment: default

environments:
  default:
    connections:
      duckdb:
        - name: duckdb-default
          path: duckdb.db
      motherduck:
        - name: motherduck
          token: <your-token>

  production:
    connections:
      bigquery:
        - name: bq-prod
          project: my-project
          dataset: production
```
  Environments: 
    Run pipelines locally or on servers without exposing production credentials
    Different teams can have different connection access
    Default to dev environment to prevent accidental production runs
  
  Built-in connections include:
    DuckDB, MotherDuck
    PostgreSQL, MySQL
    BigQuery, Redshift, Snowflake
    Custom connections (for API keys, secrets, etc.)

# Concept: Pipeline
A Pipeline is a grouping mechanism for organizing assets based on their execution schedule and configuration requirements. Within a project, you can have multiple pipelines.

Single Schedule
  Each pipeline has one schedule - this is the primary reason to group assets together:

  Assets with the same schedule belong in the same pipeline
  Common schedules: hourly, daily, monthly, or cron expressions

Pipeline Structure: Each pipeline has its own folder containing a pipeline.yml file
  project/
  ├── .bruin.yml
  ├── pipelines/
  │   ├── nyc-taxi/
  │   │   ├── pipeline.yml
  │   │   └── assets/
  │   └── another-pipeline/
  │       ├── pipeline.yml
  │       └── assets/

The pipeline.yml File
```yaml
name: nyc_taxi
schedule: monthly
start_date: "2019-01-01"
default_connections:
  duckdb: duckdb-default
```
Connection Scoping: Even though connections are defined at the project level (.bruin.yml), each pipeline specifies which connections it uses.

# Concept: Asset
An Asset is a single file that performs a specific task, almost always related to creating or updating a table or view in the destination database.

Each asset file contains two parts:

Definition (Configuration) - Metadata, name, type, connection
Content (Code) - The actual SQL, Python, or R code to execute

Asset Types: 
  Python:	Python scripts - Ingestion, data processing, ML models
  SQL:	SQL queries -	Transformations, aggregations
  YAML/Seed:	File-based tables -	Reference data, static lookups
  R:	R scripts - Statistical analysis, R-specific workflows

Asset Naming:
The asset name can be:

  Explicitly defined in the decorator
  Inferred from file path (default behavior)

Convention: Group assets by schema/dataset:

  assets/raw/trips_raw.py → Creates table raw.trips_raw
  assets/staging/trips_summary.sql → Creates table staging.trips_summary

# Concept: Variables
Variables are dynamically initialized each time a pipeline run is created. They allow you to parameterize your pipelines and pass dynamic values at runtime.

Built-in Variables: start_date, end_date
These dates are determined by the pipeline's schedule: Monthly, Daily, Hourly

Custom Variables is defined in pipeline.yml
```yaml
variables:
  - name: taxi_types
    type: array
    default:
      - "yellow"
```
* Custom variables are prefixed with BRUIN_VAR_
```python
import os
import json

@bruin.asset(name="example.asset", type="python")
def example_asset():
    # Custom variables are prefixed with BRUIN_VAR_
    taxi_types_json = os.environ['BRUIN_VAR_TAXI_TYPES']
    taxi_types = json.loads(taxi_types_json)

    # Use the variable in your code
    for taxi_type in taxi_types:
        # Process each taxi type
        pass
```