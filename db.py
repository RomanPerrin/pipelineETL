import google.auth
from google.cloud import bigquery
import os
import gcpSQL
import scrapper
import pandas as pd
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\roman\Documents\code\scraper\key.json"

credentials, project = google.auth.default()
client = bigquery.Client(credentials=credentials, location='europe-west9')
instanceConnectionName = 'idyllic-silo-271809:europe-west9:db-1'
projectId = client.project
location = 'europe-west9'

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

def getDatasetId():
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

datasetId = getDatasetId()
schema = [
    bigquery.SchemaField('parametername', 'string', mode="REQUIRED"),
    bigquery.SchemaField('content', 'string'),
    bigquery.SchemaField('links', 'string', 'REPEATED')
    ]

tableName = 'bloodwork'
data = gcpSQL.getDataFromCloudSql()

getTables = client.list_tables(f'{projectId}.{datasetId}')
tablesAlreadyCreated = list(map(lambda table: table.table_id, getTables))
table = bigquery.Table(f'{projectId}.{datasetId}.{tableName}', schema=schema)
dataframe: pd.DataFrame = data[tableName]
dfParameterName = list(dataframe['parametername'])
parameterToAdd = dfParameterName if dfParameterName else []
parameterToRemove = []

if not tableName in tablesAlreadyCreated:
    print(f'Creating {tableName}')
    client.create_table(table)
else:
    bqParameterName = list(getDataframe(table)['parametername'])
    parameterToAdd = list(set(dfParameterName)-set(bqParameterName))
    parameterToRemove = list(set(bqParameterName)-set(dfParameterName))

if parameterToAdd:
    wikiData = scrapper.main(pages=parameterToAdd)
    data = []
    for i in range(len(parameterToAdd)):
        wiki = []
        wiki.append(parameterToAdd[i])
        wiki.append(wikiData[parameterToAdd[i]]['text'])
        wiki.append(list(wikiData[parameterToAdd[i]]['links']))
        data.append(wiki)
 
    for i in range(len(parameterToAdd)):
        print(data[i], tuple(data[i]))
        query = f"insert into {table} values {tuple(data[i])} "
        res = client.query(query)
        if res.errors:
            print(res.error_result)
    print(f'loaded {parameterToAdd} into {tableName}')

if parameterToRemove:
    for i in parameterToRemove:
        res = client.query(f"delete from {table} where {schema[0].name} like '{i}'")
        if res.errors:
            print(res.error_result)
    print(f'deleted {parameterToRemove} from {table}')

if not parameterToAdd and not parameterToRemove:
    print(f'{tableName} is synced')

