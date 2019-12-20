#!/bin/bash
source ~/.virtualenvs/logger/bin/activate
export $(cat env | grep -v ^# | xargs)
cd server
flask run -p 8888 -h 0.0.0.0
