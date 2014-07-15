#!/bin/bash

BUILD_DIR="$( cd "$( dirname "$0" )" && pwd )" 
PACKAGE_DIR="$( dirname $BUILD_DIR )"
ROOT_INSTALL_DIR=/opt/loggly/loggly-analytics-web
BRANCH=$1

cd $BUILD_DIR

# Get the version -- combination of timestamp and git hash.
if [ -z "$BRANCH" ]; then
  branch=`git rev-parse --abbrev-ref HEAD`
else
  branch="$BRANCH"
fi

timestamp_branch=`git rev-parse --abbrev-ref HEAD`
timestamp=`git log --date=raw -n 1 --pretty=fuller $timestamp_branch | awk '/CommitDate:/ { print $2 + (60 * substr($1, 1, 3)) }'`

commit=`git log --pretty=format:'%h' --abbrev-commit -1`
pkgversion=$timestamp.$commit.$branch

# Clean previous build output
echo -n 'Removing old build files...'
rm -rf $PACKAGE_DIR/dist $PACKAGE_DIR/*.egg $PACKAGE_DIR/*.egg-info *.deb
echo 'DONE'

# Find packages isn't working unless we are in the top level package dir.
cd $PACKAGE_DIR && python setup.py sdist
cd $BUILD_DIR

# Create deb package that installs in root path.
fpm -s dir \
    -t deb \
    -n loggly-analytics-web \
    --prefix $ROOT_INSTALL_DIR \
    -v $pkgversion \
    --depends 'python-virtualenv > 1.7' \
    --depends 'libmysqlclient-dev' \
    --depends 'python-dev' \
    --after-install post-install.sh \
    --before-remove destroy-env.sh \
    -C $BUILD_DIR/..\
    requirements.txt dist build-scripts/create-env.sh conf/law.wsgi

if [ $? -ne 0 ]; then
  echo "Failed to create package."
fi
