#!/bin/bash
# $Id: build_rpm-storage-hp.sh,v 1.11 2009-10-07 12:12:38 marc Exp $


source ./build-lib2.sh

NAME=comoonics-storage-hp-py

build_rpms $NAME $*

##############
# $Log: build_rpm-storage-hp.sh,v $
# Revision 1.11  2009-10-07 12:12:38  marc
# new versions
#
# Revision 1.10  2009/09/28 15:29:30  marc
# updated to new build process
#
# Revision 1.9  2007/12/07 14:29:23  reiner
# Added GPL license to and ATIX AG as author name to RPM header.
#
# Revision 1.8  2007/08/06 13:06:33  marc
# new version
#
# Revision 1.7  2007/07/10 11:38:07  marc
# new version 7
#
# Revision 1.6  2007/06/26 07:52:07  marc
# new version of comoonics-storage-hp-py 0.1-6
#
# Revision 1.5  2007/06/19 13:34:42  marc
# new versions
#
# Revision 1.4  2007/06/15 19:10:28  marc
# new version
#
# Revision 1.3  2007/06/13 09:09:12  marc
# - if management appliance gets locked while working we'll overwrite it
# - added reconnect on timeout
#
# Revision 1.2  2007/04/04 13:20:09  marc
# new revisions for:
# comoonics-cs-py-0.1-30
# comoonics-ec-py-0.1-15
# comoonics-scsi-py-0.1-1
# comoonics-storage-hp-py-0.1-2
# comoonics-storage-py-0.1-2
#
# Revision 1.1  2007/02/09 12:31:24  marc
# initial revision
#
