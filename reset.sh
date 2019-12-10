echo "Dropping"
dropdb logger
echo "Creating"
createdb logger
echo "Populating"
psql -d logger < logger_prod.psql
