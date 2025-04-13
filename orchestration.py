import google.auth
from google.cloud import bigquery
import apache_beam as beam
from apache_beam.options.pipeline_options import GoogleCloudOptions
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import StandardOptions
from apache_beam.runners import DataflowRunner, DirectRunner
import os
import db
import gcpSQL
import pandas as pd

# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\roman\Documents\code\scraper\key.json"
# credentials, project = google.auth.default()
# client = bigquery.Client(credentials=credentials, location='europe-west9')
# instanceConnectionName = 'idyllic-silo-271809:europe-west9:db-1'
# projectId = client.project
# location = 'europe-west9'

class DBtoBQ(beam.DoFn):
    def setup(self):
        return super().setup()
    
    def start_bundle(self):
        return super().start_bundle()
    
    def process(self, element, *args, **kwargs):
        db.main()
        # return super().process(element, *args, **kwargs)
    
    def finish_bundle(self):
        return super().finish_bundle()
    
    def teardown(self):
        return super().teardown()

class GetDbData(beam.DoFn):
    def setup(self):
        return super().setup()
    
    def start_bundle(self):
        return super().start_bundle()
    
    def process(self, element, *args, **kwargs):
        data: pd.DataFrame = gcpSQL.getDataFromCloudSql()['bloodwork']
        data = data.values.tolist()
        Dict = []
        for i in range(len(data)):
            row = {'parametername': data[i][-1],
                   'content': data[i][-1],
                   'links': data[i][-1]
                   }
            Dict.append(row)
        print(Dict)
        return Dict
        # return super().process(element, *args, **kwargs)
    
    def finish_bundle(self):
        return super().finish_bundle()
    
    def teardown(self):
        return super().teardown()

projectId = 'idyllic-silo-271809'
datasetId = 'dataset1'
tableName = 'bloodwork'
schema = {
    'fields': [
    {
        'name': 'parametername', 'type': 'STRING', 'mode': 'REQUIRED'
    },
    {
        'name': 'content', 'type': 'STRING', 'mode': 'NULLABLE'
    },
    {
        'name': 'links', 'type': 'STRING', 'mode': 'NULLABLE'
    },
    ]
}
table = f'{projectId}.{datasetId}.{tableName}'


options = PipelineOptions()
with beam.Pipeline(options=options) as p:
    data = (
        p
        | 'Create' >> beam.Create(['Start'])
        | 'fetch db data' >> beam.ParDo(GetDbData())
        # | 'write to text' >> beam.io.WriteToText("C:/Users/roman/Documents/code/scraper/fetchResults", ".txt")
        | 'write into bq' >> beam.io.WriteToBigQuery(table=table,
                                                     schema=schema,
                                                     write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
                                                     create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED,
                                                     method=beam.io.WriteToBigQuery.Method.STORAGE_WRITE_API
                                                     )
    )
    '''data = (
        p
        | 'fetch db data' >> beam.io.ReadFromBigQuery(table=table, method='DIRECT_READ')
        | 'write to text' >> beam.io.WriteToText("./Results", ".txt")
    )'''

