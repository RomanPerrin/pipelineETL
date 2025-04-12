import google.auth
from google.cloud import bigquery
import apache_beam as beam
from apache_beam.options.pipeline_options import GoogleCloudOptions
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import StandardOptions
from apache_beam.runners import DataflowRunner, DirectRunner
import os
import db

# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"C:\Users\roman\Documents\code\scraper\key.json"
# credentials, project = google.auth.default()
# client = bigquery.Client(credentials=credentials, location='europe-west9')
# instanceConnectionName = 'idyllic-silo-271809:europe-west9:db-1'
# projectId = client.project
# location = 'europe-west9'

class test(beam.DoFn):
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

def run():
    options = PipelineOptions()
    p = beam.Pipeline(options=options)
    
    data = (
        p 
        | 'Create' >> beam.Create(['Start'])
        | 'DBtoBQ' >> beam.ParDo(test())
    )

    result = p.run()
    result.wait_until_finish()
    print(result)

if __name__ == '__main__':
    run()
