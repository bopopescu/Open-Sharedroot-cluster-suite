'''
Created on Feb 4, 2010

@author: marc
'''

# $Id: MigrationTools.py,v 1.4 2010-11-21 21:44:47 marc Exp $
#
# @(#)$File$
#
# Copyright (c) 2001 ATIX GmbH, 2007 ATIX AG.
# Einsteinstrasse 10, 85716 Unterschleissheim, Germany
# All rights reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

__version__ = "$Revision: 1.4 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/comoonics/cdsl/migration/MigrationTools.py,v $

from comoonics.cdsl.migration import ConfigfileFormatException
from comoonics.cdsl.ComCdslRepository import ComoonicsCdslRepository
from comoonics import ComLog

class MigrationTool(object):
    '''
    This is the baseclass for migrating CDSL configfiles from one version to the other
    '''

    def __init__(self, *params, **keys):
        '''
        Constructor
        '''
        self.logger=ComLog.getLogger("comoonics.cdsl.migration.MigrationTool")
    
    def migrate(self, fromversion, toverstion, **kwds):
        pass
    
class DefaultMigrationTool(MigrationTool):
    defaultsmapping={
                     'use_nodeids': "usenodeids",
                     'cdsltree_shared': "cdsltreeshared",
                     'cdsl_link': "cdsllink",
                     'maxnodeidnum': "maxnodeidnum",
                     'cdsltree': "cdsltree",
                     'default_dir': "defaultdir" }
    def migrate(self, fromversion, toversion, **kwds):
        from comoonics.cdsl.ComCdsl import ComoonicsCdsl
        import os.path
        from comoonics import XmlTools
        root=kwds.get("root", "/")
        mountpoint=kwds.get("mountpoint", "")
        toresource=kwds.get("toresource", ComoonicsCdslRepository.default_resources[0])
        fromresource=kwds.get("fromresource", ComoonicsCdslRepository.default_resources[1])
        
        if os.path.exists(fromresource):
            fromdoc=XmlTools.parseXMLFile(fromresource, False)
            fromelement=fromdoc.documentElement
            if fromelement.tagName != ComoonicsCdslRepository.cdsls_element:
                raise ConfigfileFormatException("Config file \"%s\"does not start with an cdsls element. Wrong format." %fromresource)
            
            defaults=fromelement.getElementsByTagName("defaults")
            if defaults:
                defaults=defaults[0]
            
            defaultkeys=self.getDefaultKeys(defaults)
            defaultkeys["root"]=root
            defaultkeys["mountpoint"]=mountpoint
            defaultkeys["resource"]=toresource
            self.logger.debug("defaults: %s" %defaultkeys)
            torepository=ComoonicsCdslRepository(**defaultkeys)
            cdsls=fromelement.getElementsByTagName("cdsl")
            if cdsls and len(cdsls)>0:
                for i in range(len(cdsls)):
                    nodes=[]
                    nodeselement=cdsls[i].getElementsByTagName("nodes")
                    if nodeselement:
                        nodeselement=nodeselement[0]
                        noderefs=nodeselement.getElementsByTagName("noderef")
                        if noderefs and len(noderefs) > 0:
                            for j in range(len(noderefs)):
                                nodes.append(noderefs[j].getAttribute("ref"))
                    cdsl=ComoonicsCdsl(cdsls[i].getAttribute("src"), cdsls[i].getAttribute("type"), torepository, None, nodes, cdsls[i].getAttribute("timestamp"), kwds.get("ignoreerrors", True))
                    torepository.commit(cdsl)
            return torepository
        else:
            raise IOError(2, "Could not find cdsl inventory file %s in %s" %(fromresource, os.getcwd()))
            
    def getDefaultKeys(self, defaults):
        returnkeys=dict()
        for i in range(defaults.attributes.length):
            attr=defaults.attributes.item(i)
            returnkeys[str(self.defaultsmapping.get(attr.name, attr.name))]=str(attr.value)
        return returnkeys
            
                
            
        
        
        
###############
# $Log: MigrationTools.py,v $
# Revision 1.4  2010-11-21 21:44:47  marc
# - fixed bug 391
#   - moved to upstream XmlTools implementation
#
# Revision 1.3  2010/06/29 07:50:53  marc
#   - __init__: added logger
#   - defaultsmapping: adapted to current status
#   - migrate: debug output default values to be migrated
#
# Revision 1.2  2010/04/13 13:24:02  marc
# - support for ignoreerrors
#
# Revision 1.1  2010/02/07 20:01:26  marc
# First candidate for new version.
#