#!/bin/bash

    WORK_DIR="/vagrant/"
DAEMON="/usr/bin/python"
ARGS="/vagrant/src/server.py"
PIDFILE="/var/run/sxswserver.pid"
USER="vagrant"

case "$1" in
  start)
    echo "Starting sxsw"
    mkdir -p "$WORK_DIR"
    echo "2"
    /sbin/start-stop-daemon --start --pidfile $PIDFILE \
        -b --make-pidfile \
    --startas /bin/bash -- -c "exec $DAEMON $ARGS > /vagrant/logs/sxsw.log 2>&1"
    ;;
  restart)
  /sbin/start-stop-daemon --stop --retry 5 --quiet --pidfile $PIDFILE
   /sbin/start-stop-daemon --start --pidfile $PIDFILE \
      -b --make-pidfile \
     --startas /bin/bash -- -c "exec $DAEMON $ARGS > /vagrant/logs/sxsw.log 2>&1"
  ;;
  stop)
    echo "Stopping server"
    /sbin/start-stop-daemon --stop --retry 5 --quiet --pidfile $PIDFILE --verbose
    ;;
  *)
    echo "Usage: /etc/init.d/$USER {start|stop}"
    exit 1
    ;;
esac

exit 0

