#!/bin/bash
set -o errexit

ROOT_INSTALL_DIR=/opt/loggly/loggly-analytics-web

echo -n "What user do you wish to own $ROOT_INSTALL_DIR? (They must be keyed for github): "
read keyed_user

chown -R $keyed_user:$keyed_user $ROOT_INSTALL_DIR
sudo -u $keyed_user $ROOT_INSTALL_DIR/build-scripts/create-env.sh
