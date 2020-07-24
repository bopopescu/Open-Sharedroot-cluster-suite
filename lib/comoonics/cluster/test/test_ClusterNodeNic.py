from BaseClusterTestClass import baseClusterTestClass

import unittest

class test_ClusterNodeNic(baseClusterTestClass):
    """
    Methods from ComoonicsClusterNodeNic
    """
    def init(self):
        import os.path
        from comoonics.cluster.ComClusterRepository import ClusterRepository
        from comoonics.cluster.ComClusterInfo import ClusterInfo
        from comoonics import ComSystem
        ComSystem.setExecMode(ComSystem.SIMULATE)
        super(test_ClusterNodeNic, self).init()
        #create comclusterRepository Object
        self.clusterRepository = ClusterRepository(os.path.join(self._testpath, "cluster2.conf"))

        #create comclusterinfo object
        self.clusterInfo = ClusterInfo(self.clusterRepository)  

        # setup the cashes for clustat for redhat cluster
        import logging
        self.clusterInfo.helper.setSimOutput()
        self.nics=list()
        for node in self.clusterInfo.getNodes():
            node.helper.output=self.clusterInfo.helper.output
            for nic in node.getNics():
                self.nics.append(nic)
      
    def testGetname(self):
        i = 0
        for nic in self.nics:
            self.assertEqual(nic.getName(), self.nicValues[i]["name"])
            i = i + 1
            
    def testGetmac(self):
        i = 0
        for nic in self.nics:
            self.assertEqual(nic.getMac(), self.nicValues[i]["mac"])
            i = i + 1
            
    def testGetip(self):
        i = 0
        for nic in self.nics:
            self.assertEqual(nic.getIP(), self.nicValues[i]["ip"])
            i = i + 1
            
    def testGetgateway(self):
        i = 0
        for nic in self.nics:
            self.assertEqual(nic.getGateway(), self.nicValues[i]["gateway"])
            i = i + 1
            
    def testGetnetmask(self):
        i = 0
        for nic in self.nics:
            self.assertEqual(nic.getNetmask(), self.nicValues[i]["netmask"])
            i = i + 1
            
    def testGetmain(self):
        i = 0
        for nic in self.nics:
            self.assertEqual(nic.getMain(), self.nicValues[i]["main"])
            i = i + 1
            
    def testGetsubordinate(self):
        i = 0
        for nic in self.nics:
            self.assertEqual(nic.getSubordinate(), self.nicValues[i]["subordinate"])
            i = i + 1

def test_main():
    try:
        from test import test_support
        test_support.run_unittest(test_ClusterNodeNic)
    except ImportError:
        unittest.main()

if __name__ == '__main__':
    test_main()
