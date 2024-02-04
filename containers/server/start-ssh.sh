#!/bin/bash

cd /usr/bin
ln -s python3 python

cd /root/.ssh
chmod go-rxw *

/etc/init.d/ssh start
sleep infinity
exit 0

