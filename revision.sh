#!/bin/bash
source ~/.virtualenvs/logger/bin/activate
export $(cat env | grep -v ^# | xargs)
cd server
flask db revision
echo "Don't forget to commit the migration, if any..."
