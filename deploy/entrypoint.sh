#!/bin/bash

/wait-for-it.sh mysql:3306 -- flask --app model.schema:app create &
/wait-for-it.sh mysql:3306 -- flask --app model.schema:app migrate &

exec "$@"
