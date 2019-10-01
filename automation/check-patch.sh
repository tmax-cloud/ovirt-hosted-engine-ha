#!/bin/bash -e
if [ -x /usr/bin/python3 ] ; then
export PYTHON=/usr/bin/python3
fi

./autogen.sh --system

# make distcheck skipped due to bug afflicting automake.
# fc29: https://bugzilla.redhat.com/1716384
# fc30: https://bugzilla.redhat.com/1757854
# el8:  https://bugzilla.redhat.com/1759942
# make distcheck
# rm -f *.tar.gz

./automation/build-artifacts.sh
