DB_FARM=./data
SQL_PATH=./monetdb/sql
monetdbd create $DB_FARM
# rm -rf data
# unzip data-local.zip
monetdbd stop $DB_FARM
monetdbd start $DB_FARM
monetdb destroy -f dataflow_analyzer
monetdb create dataflow_analyzer
monetdb release dataflow_analyzer
monetdb status
# running SQL scripts
mclient -p 50000 -d dataflow_analyzer $SQL_PATH/create-schema.sql
mclient -p 50000 -d dataflow_analyzer $SQL_PATH/database-script.sql
