import pandas as pd
import sqlalchemy

dbIp = '34.155.234.2'
tcpPort = '5432'

# Database connection parameters
databaseType = 'postgresql'
username = 'postgres'
password = 'appocffn'
host = dbIp
port = tcpPort
databaseName = 'postgres'
schema = 'public'

connection_string = f'{databaseType}://{username}:{password}@{host}:{port}/{databaseName}'
engine = sqlalchemy.create_engine(connection_string)#, 
                                #   connect_args={'options': '-csearch_path={}'.format("schema_name")}, 
                                #   echo=True)

sqlTypes = {}
sqlTypes['postgre'] = {
    'smallint' : 'int2',
    'integer' : 'int4',
    'bigint' : 'int8',
    'decimal' : 'variable',
    'numeric' : 'variable',
    'real' : 'float4',
    'double precision' : 'float8',
    'smallserial' : 'int2',
    'serial' : 'int4',
    'bigserial' : 'int8',
    'character varying' : 'string',
    'character' : 'string',
    'bpchar' : 'string',
    'text' : 'string'
}
sqlTypes['pandas'] = {
    'smallint' : 'int8',
    'integer' : 'int8',
    'bigint' : 'int8',
    'decimal' : 'float32',
    'numeric' : 'float32',
    'real' : 'float32',
    'double precision' : 'float32',
    'smallserial' : 'int8',
    'serial' : 'int8',
    'bigserial' : 'int8',
    'character varying' : 'string',
    'character' : 'string',
    'bpchar' : 'string',
    'text' : 'string'
}


def getTypesDict(table: str):
    types = pd.read_sql(f"""select column_name, data_type 
                        from INFORMATION_SCHEMA.COLUMNS 
                        where table_name = '{table}'""", engine)
    types = types.T.to_dict()

    newDict = {}
    for col in types:
        col = types[col]
        newDict[col['column_name']] = sqlTypes['pandas'][col['data_type']]

    return newDict

def getDataFromCloudSql():
    queryAllTables = f"SELECT table_name FROM information_schema.tables WHERE table_schema='{schema}'"
    tableNames = list(pd.read_sql(queryAllTables, engine)['table_name'])

    data = {}
    for table in tableNames:
        print(f"Processing {table} ...")

        queryAllFromTable = f"SELECT * FROM {table}"
        queryTypes = getTypesDict(table)

        df = pd.read_sql(queryAllFromTable, engine)
        df = df.astype(queryTypes)
        data[table] = df
    print('Done')

    return data

if __name__ == "__main__":
    data = getDataFromCloudSql()
    print(data)
