import google.auth
from google.cloud import bigquery
import os
import gcpSQL
import pandas as pd
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\roman\Documents\code\scraper\key.json"

credentials, project = google.auth.default()
client = bigquery.Client(credentials=credentials, location='europe-west9')
instanceConnectionName = 'idyllic-silo-271809:europe-west9:db-1'

def getDataframe(table: bigquery.Table):
    QUERY = (f'SELECT * FROM `{table}`')
    query_job = client.query(QUERY)  # API request
    result = query_job.to_dataframe()

    return result

def loadDataframe(dataframe: pd.DataFrame, destination:bigquery.Table):
    try:
        client.load_table_from_dataframe(dataframe, destination)
    except:
        print(f'Failed to load dataframe into {destination.friendly_name}')

def getDatasetId(client: bigquery.Client):
    projectId = client.project
    
    datasets = list(client.list_datasets())  # Make an API request.
    if datasets:
        print(f"Datasets in project {projectId}:")
        for dataset in datasets:
            print(f"\t{dataset.dataset_id}")
        datasetId = datasets[0].dataset_id
    else:
        print(f"{projectId} project does not contain any datasets.")
        client.create_dataset(bigquery.Dataset(f'{projectId}.dataset1'))
        print(f"Created datasets dataset1.")
        datasetId = 'dataset1'

    print(f'Using {datasetId}')
    return datasetId

projectId = client.project
location = 'europe-west9'
datasetId = getDatasetId(client)

data = gcpSQL.getDataFromCloudSql()
for tableName in data:
    getTables = client.list_tables(f'{projectId}.{datasetId}')
    tablesAlreadyCreated = list(map(lambda table: table.table_id, getTables))
    table = bigquery.Table(f'{projectId}.{datasetId}.{tableName}')
    dataframe: pd.DataFrame = data[tableName]
    
    if not tableName in tablesAlreadyCreated:
        print(f'Creating {tableName}')
        client.create_table(table)
        loadDataframe(dataframe, table)
    else:
        print(f'Skipping table {tableName}. It exists already')

        preexistingData = getDataframe(table)
        diffData = pd.concat([dataframe,preexistingData]).drop_duplicates(keep=False)
    
        if diffData.empty:
            print(f'{tableName} is already synced')
        else:
            loadDataframe(diffData, table)
            print(f'loaded {diffData} into {tableName}')

    #if data updated!!!
