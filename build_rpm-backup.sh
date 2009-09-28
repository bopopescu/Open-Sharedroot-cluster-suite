#!/bin/bash
# $Id: build_rpm-backup.sh,v 1.4 2009-09-28 15:29:06 marc Exp $

source ./build-lib.sh

RELEASE=2
REQUIRES="--requires=comoonics-ec-py"
NOAUTO_REQ="--no-autoreq"
NAME="comoonics-backup-py"
VERSION="0.1"
DESCRIPTION="Comoonics Backup utilities and libraries written in Python"
LONG_DESCRIPTION="
Comoonics Backup utilities and libraries written in Python
"
AUTHOR="ATIX AG - Marc Grimme"
AUTHOR_EMAIL="grimme@atix.de"
URL="http://www.atix.de/comoonics/"
PACKAGE_DIR='"comoonics.backup" : "lib/comoonics/backup"'
PACKAGES='"comoonics.backup"'
setup

##############
# $Log: build_rpm-backup.sh,v $
# Revision 1.4  2009-09-28 15:29:06  marc
# updated to new build process
#
# Revision 1.3  2007/12/07 14:29:23  reiner
# Added GPL license to and ATIX AG as author name to RPM header.
#
# Revision 1.2  2007/06/13 09:00:55  marc
# - now backuping full path to support incremental backups (0.1-2)
#
# Revision 1.1  2007/04/04 13:42:42  marc
# initial revision
#
