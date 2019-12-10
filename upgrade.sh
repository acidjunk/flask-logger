#!/bin/bash
source ~/.virtualenvs/logger/bin/activate
export $(cat env | grep -v ^# | xargs)
cd server
flask db upgrade
