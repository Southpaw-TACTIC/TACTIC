#!/bin/sh

rm tactic.zip

# copy everything in the application directory
cp -r ../../pyasm/application pyasm
cp  ../../pyasm/application/__init__.py pyasm/__init__.py

# create a zip file
find . -name "*.py" -print | grep -v ".svn" | zip tactic.zip -@
zip tactic.zip "./pyasm/application/common/interpreter/tactic_client_lib/VERSION" "./pyasm/application/common/interpreter/tactic_client_lib/VERSION_API"
chmod 666 tactic.zip 

cp tactic.zip ../../client/tactic_client_lib/
