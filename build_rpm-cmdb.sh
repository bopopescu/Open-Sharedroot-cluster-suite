#!/bin/bash

# $Id: build_rpm-cmdb.sh,v 1.16 2009-10-07 12:12:38 marc Exp $


source ./build-lib2.sh

NAME=comoonics-cmdb-py

build_rpms $NAME $*


##############
# $Log: build_rpm-cmdb.sh,v $
# Revision 1.16  2009-10-07 12:12:38  marc
# new versions
#
# Revision 1.15  2009/09/28 15:29:06  marc
# updated to new build process
#
# Revision 1.14  2007/12/07 14:29:23  reiner
# Added GPL license to and ATIX AG as author name to RPM header.
#
# Revision 1.13  2007/05/10 12:44:01  marc
# Hilti RPM Control
# - Bugfix for Where-Clause
#
# Revision 1.12  2007/05/10 08:24:22  marc
# Hilti RPM Control
#
# Revision 1.11  2007/04/18 10:25:35  marc
# Hilti RPM Control
# - version cmdb-21 and db-6
#
# Revision 1.10  2007/04/12 13:23:50  marc
# Hilti RPM Control
# - new versions
#
# Revision 1.9  2007/04/02 11:55:31  marc
# Hilti RPM Control
#
# Revision 1.8  2007/03/14 16:56:29  marc
# fixed AND instead of OR in OnlyDiffs Join
#
# Revision 1.7  2007/03/14 15:26:34  marc
# compatible with mysql3 dialect and ambigousness. (RHEL4 has mysql3) (4th)
#
# Revision 1.6  2007/03/14 15:12:58  marc
# compatible with mysql3 dialect and ambigousness. (RHEL4 has mysql3) (3rd)
#
# Revision 1.5  2007/03/14 14:58:01  marc
# compatible with mysql3 dialect and ambigousness. (RHEL4 has mysql3)
#
# Revision 1.4  2007/03/14 14:39:00  marc
# compatible with mysql3 dialect and ambigousness. (RHEL4 has mysql3)
#
# Revision 1.3  2007/03/14 13:17:13  marc
# added support for comparing multiple n>2 sources
#
# Revision 1.2  2007/03/06 07:11:25  marc
# not needed
#
# Revision 1.1  2007/03/05 21:12:18  marc
# first rpm version
#
#
