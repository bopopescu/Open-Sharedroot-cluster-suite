""" Comoonics filesystem copy object module


here should be some more information about the module, that finds its way inot the onlinedoc

"""


# here is some internal information
# $Id: ComFilesystemCopyObject.py,v 1.1 2006-06-29 07:24:02 mark Exp $
#


__version__ = "$Revision: 1.1 $"
# $Source: /atix/ATIX/CVSROOT/nashead2004/management/comoonics-clustersuite/python/lib/Attic/ComFilesystemCopyObject.py,v $

from xml import xpath

from ComDevice import Device
import ComFileSystem
from ComFileSystem import FileSystem, MountPoint
from ComCopyObject import CopyObject
from ComExceptions import *         


class FilesystemCopyObject(CopyObject):
    """ Base Class for all source and destination objects"""
    def __init__(self, element, doc):
        CopyObject.__init__(self, element, doc)
        try:
            __device=xpath.Evaluate('device', element)[0]
            self.device=Device(__device, doc)
        except Exception:
            raise ComException("device for copyset not defined")
        try:    
            __fs=xpath.Evaluate('device/filesystem', element)[0]
            self.filesystem=ComFileSystem.getFileSystem(__fs, doc)
        except Exception:
            raise ComException("filesystem for copyset not defined")
        try:
            __mp=xpath.Evaluate('device/mountpoint', element)[0]
            self.mountpoint=MountPoint(__mp, doc)
        except Exception:
            raise ComException("device for copyset not defined")
        self.umountfs=False

    def getFileSystem(self):
        return self.filesystem
    
    def getDevice(self):
        return self.device
    
    def getMountpoint(self):
        return self.mountpoint
    
    def setFileSystem(self, filesystem):
        __parent=self.filesystem.getElement().parentNode
        __newnode=filesystem.getElement().cloneNode(True)
        __oldnode=self.filesystem.getElement()
        self.filesystem.setElement(__newnode)
        __parent.replaceChild(__newnode, __oldnode)
        
    def prepareAsSource(self):   
        # Check for mounted
        if not self.device.isMounted():
            self.filesystem.mount(self.device, self.mountpoint)
            self.umountfs=True
        # scan filesystem options
        self.filesystem.scanOptions(self.device, self.mountpoint)
    
    def cleanupSource(self):
        if self.umountfs:
            self.filesystem.umountDir(self.mountpoint)
    
    def cleanupDest(self):
        self.filesystem.umountDir(self.mountpoint)
        
    def prepareAsDest(self):
        # - mkfs
        # TODO add some intelligent checks
        self.filesystem.formatDevice(self.device)
        self.filesystem.mount(self.device, self.mountpoint)
        

# $Log: ComFilesystemCopyObject.py,v $
# Revision 1.1  2006-06-29 07:24:02  mark
# initial checkin
#