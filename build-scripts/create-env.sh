#!/bin/bash
set -o errexit

ROOT_INSTALL_DIR=/opt/loggly/loggly-analytics-web
export LAW=INSTALL

cd $ROOT_INSTALL_DIR
filename=$(ls -1tr dist | tail -1)
# Generate an environment to be placed in this package
virtualenv --no-site-packages environment
environment/bin/pip install distribute -U
environment/bin/pip install -r requirements.txt
environment/bin/pip install dist/$filename

echo -e '\nDone sourcing LAW environment.  All good in the hood.\n'
