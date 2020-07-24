"""
Class for the software_cmdb

Methods for comparing systems and the like
"""
# here is some internal information
# $Id: ComSoftwareCMDB.py,v 1.18 2007-05-10 12:14:01 marc Exp $
#

import os
import re
from comoonics.cmdb.ComBaseDB import BaseDB
from comoonics import ComLog
from comoonics.db.ComDBLogger import DBLogger
from ComSource import Source

class SoftwareCMDB(BaseDB):
    """
    Class for the software_cmdb
    """
    NOT_INSTALLED_STRING="not installed"
    SELECT_FOR_SOFTWARE=("channel",
                         "channelversion",
                         "name",
                         "version",
                         "subversion",
                         "architecture",
                         "sw_type")
    COMPARE_2_SOFTWARE=("name",
                        "version",
                        "subversion",
                        "architecture")
    SELECT_FOR_DIFFS_MASTER=("sourcename", "name", "version_main", "subversion_main", "architecture_main", "version_diffs", "subversion_diffs", "architecture_diffs")

    DIFFS_COLNAME="diffs"

    log=ComLog.getLogger("SoftwareCMDB")

    def getAllColnamesNotInstalled(colnames, colparts, sourcenames):
         ret_colnames=list()
         ilen=len(sourcenames)
         jlen=len(colnames)
         klen=len(colparts)
#         self.log.debug("ilen: %u, jlen: %u, klen: %u" %(ilen, jlen, klen))
         basecolnames=list(colnames)
         for i in range(ilen):
             copy_colnames=""
             for j in range(jlen):
                 if j>=klen*i and j<klen*(i+1):
                     copy_colnames+="\""+SoftwareCMDB.NOT_INSTALLED_STRING+"\" AS "+colnames[j]+", "
                 else:
                     copy_colnames+="rpms"+str(i)+"."+colparts[j%klen]+" AS "+colnames[i]+", "
#             self.log.debug("getAllColnamesNotInstalled: "+copy_colnames[:-2])
             ret_colnames.append(copy_colnames[:-2])
         return ret_colnames

    getAllColnamesNotInstalled=staticmethod(getAllColnamesNotInstalled)

    def __init__(self, **kwds):
        """
        Creates a Software CMDB class giving methods to deal with the sql table "software_cmdb"
        __init__(hostname=.., user=.., password=.., database=.., tablename=..)
        __init__(dbhandle=.., tablename=..)
        """
        if not kwds.has_key("tablename"):
            kwds["tablename"]="software_cmdb"
        super(SoftwareCMDB, self).__init__(**kwds)

    def getClusters(self):
        query="SELECT DISTINCT clustername FROM %s" %(self.tablename)
        rs=self.selectQuery(query)
        row=rs.fetch_row()
        clusters=list()
        while row:
            clusters.append(row[0][0])
            row=rs.fetch_row()
        return clusters

    def getSoftwareDublicates(self, clustername, _select="*", _limitup=0, _limitdown=0, _where=None, _orderby=None):
        if _where==None:
            _where=list()
        # Quickhack to support mysql3
        if type(_where)==list:
            for i in range(len(_where)):
                _where[i]="t1."+_where[i]
        limit=BaseDB.getLimit(_limitup, _limitdown)
        self.log.debug("where: %s" %(_where))
        _where.append("t1.clustername=\"%s\"" %(clustername))
#        _where+=" AND ".join(_where)
        whereclause=BaseDB.resolveWhere(_where)
        orderbyclause=BaseDB.resolveOrderBy(_orderby)
        self.log.debug("whereclause: %s" %(whereclause))
        query="""SELECT DISTINCT %s FROM %s AS t1
    LEFT JOIN %s AS t2
       USING (clustername, name)
       %s
        AND (t1.version != t2.version OR t1.subversion != t2.subversion)
        %s %s;""" \
        %("t1."+", t1.".join(_select), self.tablename, self.tablename, whereclause, orderbyclause, limit)
        self.log.debug("query: %s" %(query))
        return self.selectQuery(query)

    def getSoftware(self, clustername, select="*", limitup=0, limitdown=0, where=None, orderby=None):
        if where==None:
            where=list()
        limit=BaseDB.getLimit(limitup, limitdown)
        where.append("clustername=\"%s\"" %(clustername))
        self.log.debug("where: %s" %(where))
        whereclause=BaseDB.resolveWhere(where)
        orderbyclause=BaseDB.resolveOrderBy(orderby)
        self.log.debug("whereclause: %s" %(whereclause))
        query="SELECT DISTINCT %s FROM %s %s %s %s;" %(", ".join(select), self.tablename, whereclause, orderbyclause, limit)
        self.log.debug("query: %s" %(query))
        return self.selectQuery(query)

    def getColnamesForMain(Installed=False):
        cols=list(SoftwareCMDB.SELECT_FOR_DIFFS_MASTER)
        if Installed:
            cols.append(SoftwareCMDB.DIFFS_COLNAME)
        return cols
    getColnamesForMain=staticmethod(getColnamesForMain)

    def getColnamesForDiff(self, sourcenames, Installed=False, colnames=COMPARE_2_SOFTWARE):
        colnames_ret=list()
        colnames_ret.append(colnames[0])
        for sourcename in sourcenames:
            for colname in colnames[1:]:
                colnames_ret.append(colname+"_"+self.escapeSQL(sourcename))
        if Installed:
            colnames_ret.append(SoftwareCMDB.DIFFS_COLNAME)
        return colnames_ret

    def getColnamesForDiffCategory(self, category, Installed=False, colnames=COMPARE_2_SOFTWARE):
        source=Source(dbhandle=self.db)
        sourcenames=source.getSourcesForCategory(category)
        colnames_ret=list()
        colnames_ret.append(colnames[0])
        for sourcename in sourcenames:
            for colname in colnames[1:]:
                colnames_ret.append(colname+"_"+self.escapeSQL(sourcename))
        if Installed:
            colnames_ret.append(SoftwareCMDB.DIFFS_COLNAME)
        return colnames_ret

    def getDiffsFromSourcesByMain(self, sourcenames, main, colnames=None, limitup=0, limitdown=0, where=None, orderby=None, Diffs=True, NotInstalled=True, Installed=False):
        """
        Returns a resultset of differences of the given sourcenames.
        Parameter are the sourcesnames to compare
        """
        orderbyclause=BaseDB.resolveOrderBy(orderby)
        limit=BaseDB.getLimit(limitup, limitdown)
        self.log.debug("where: %s" %(where))
        self.log.debug("orderbyclause: %s, limit: %s, diffs: %s, notinstalled: %s, Installed: %s" %(orderbyclause, limit, Diffs, NotInstalled, Installed))
        if not colnames:
            self.log.debug("getting colnames")
            colnames=self.SELECT_FOR_DIFFS_MASTER
        j=0
#        ComLog.getLogger().debug("query %s" % query)
        queries=list()
        for sourcename in sourcenames:
            if Installed:
                queries.append(self.selectQueryOnlyEqualInstalledByMain(sourcename, main, colnames, where, Diffs or NotInstalled))
            if Diffs:
                queries.append(self.selectQueryOnlyDiffsByMain(sourcename, main, colnames, where, Installed))
            if NotInstalled:
                queries.append(self.selectQueryNotInstalledByMain(sourcename, main, colnames, where, True, Installed))
                queries.append(self.selectQueryNotInstalledByMain(sourcename, main, colnames, where, False, Installed))
        union="\n UNION \n".join(queries)
        if orderbyclause and orderbyclause!="":
            union+="\n"+orderbyclause
        if limit and limit != "":
            union+="\n"+limit
        self.log.debug("union: "+union)
        return self.selectQuery(union)

    def selectQueryNotInstalledByMain(self, sourcename, main, colnames, where=None, order=True, withInstalled=False, alladdcols=["version", "subversion", "architecture"], diffcols=["version", "subversion"]):
        if not order:
            _main=sourcename
            _sourcename=main
            _colname="rpms"
        else:
            _main=main
            _sourcename=sourcename
            _colname="main"
        _colnames=list(colnames)
        _colnames[0]="\"%s\" AS %s" %(sourcename, _colnames[0])
        _colnames[1]="%s.name AS %s" %(_colname, _colnames[1])
        newlen=len(_colnames[2:])
        for i in range(newlen):
            if int(i/len(alladdcols))==0 and order:
                _colnames[i+2]="main.%s AS %s" %(alladdcols[i%len(alladdcols)], _colnames[i+2])
            elif int(i/len(alladdcols)) != 0 and not order:
                _colnames[i+2]="rpms.%s AS %s" %(alladdcols[i%len(alladdcols)], _colnames[i+2])
            elif int(i/len(alladdcols))==0 and not order:
                _colnames[i+2]="\"not installed\" AS %s" %(_colnames[i+2])
            elif int(i/len(alladdcols))!=0 and order:
                _colnames[i+2]="\"not installed\" AS %s" %(_colnames[i+2])
        if withInstalled and order:
            _colnames.append("2 AS "+SoftwareCMDB.DIFFS_COLNAME)
        elif withInstalled and not order:
            _colnames.append("3 AS "+SoftwareCMDB.DIFFS_COLNAME)
        whererest=""
        if where and type(where)==str and where!="":
            whererest="\n   AND "+_colname+"."+where
        elif where and type(where)==list:
            thestr="\n   AND "+_colname+"."
            whererest=thestr+thestr.join(where)
        query="""SELECT %s
        FROM %s AS %s
        WHERE %s.clustername = "%s" AND
           (name, architecture) NOT IN (SELECT rpms.name, rpms.architecture FROM software_cmdb AS rpms WHERE clustername="%s") %s""" \
         %(", ".join(_colnames), self.tablename, _colname, _colname, _main, _sourcename, whererest)
        return query

    def selectQueryOnlyDiffsByMain(self, sourcename, main, colnames, where=None, withInstalled=False, alladdcols=["version", "subversion", "architecture"]):
        tablealias="odrpms"
        _colnames=list(colnames)
        _colnames[0]=tablealias+"0.clustername AS "+_colnames[0]
        _colnames[1]=tablealias+"0.name AS "+_colnames[1]
        newlen=len(_colnames[2:])
        for i in range(newlen):
            if int(i/len(alladdcols))==0:
                _colnames[i+2]=tablealias+"1.%s AS %s" %(alladdcols[i%len(alladdcols)], _colnames[i+2])
            else:
                _colnames[i+2]=tablealias+"0.%s AS %s" %(alladdcols[i%len(alladdcols)], _colnames[i+2])
        if withInstalled:
            _colnames.append("1 AS "+SoftwareCMDB.DIFFS_COLNAME)
        whererest=""
        if where and type(where)==str and where!="":
            whererest="\n   AND main+."+where
        elif where and type(where)==list:
            thestr="\n   AND main."
            whererest=thestr+thestr.join(where)
        sourcenames=[sourcename, main]
        query=self.selectQueryOnlyDiffs(sourcenames, self.getColnamesForDiff(sourcenames), self.COMPARE_2_SOFTWARE, where, withInstalled)
        regexp=re.compile("SELECT DISTINCT .*$", re.IGNORECASE | re.MULTILINE)
        query=regexp.sub("SELECT DISTINCT "+", ".join(_colnames), query)
        return query

    def selectQueryOnlyEqualInstalledByMain(self, sourcename, main, colnames, where=None, withInstalled=False, alladdcols=["version", "subversion", "architecture"], diffcols=["version", "subversion"]):
        _colnames=list(colnames)
        _colnames[0]="rpms.clustername AS "+_colnames[0]
        _colnames[1]="rpms.name AS "+_colnames[1]
        newlen=len(_colnames[2:])
        for i in range(newlen):
            if int(i/len(alladdcols))==0:
                _colnames[i+2]="main.%s AS %s" %(alladdcols[i%len(alladdcols)], _colnames[i+2])
            else:
                _colnames[i+2]="rpms.%s AS %s" %(alladdcols[i%len(alladdcols)], _colnames[i+2])
        if withInstalled:
            _colnames.append("0 AS "+SoftwareCMDB.DIFFS_COLNAME)
        whererest=""
        if where and type(where)==str and where!="":
            whererest="\n   AND main+."+where
        elif where and type(where)==list:
            thestr="\n   AND main."
            whererest=thestr+thestr.join(where)
        query="""SELECT %s
        FROM %s AS main
        JOIN %s as rpms USING (name, architecture, version, subversion)
        WHERE main.clustername="%s" AND rpms.clustername="%s" %s""" \
        %(", ".join(_colnames), self.tablename, self.tablename, main, sourcename, whererest)
        return query

    def getDiffsFromCategory(self, category, colnames=None, limitup=0, limitdown=0, where=None, orderby=None, Diffs=True, NotInstalled=True, Installed=False):
        """
        Returns a resultset of differences of the given categories.
        Parameter are the sourcesnames to compare
        """
        sources=list()
        source=Source(dbhandle=self.db)
        snames=source.getSourcesForCategory(category)
        if len(snames) == 0:
            return None
        else:
            snames=self.escapeSQL(snames)
            return self.getDiffsFromSources(snames, colnames, limitup, limitdown, where, orderby, Diffs, NotInstalled, Installed)

    def getDiffsFromSources(self, sourcenames, colnames=None, limitup=0, limitdown=0, where=None, orderby=None, Diffs=True, NotInstalled=True, Installed=False):
        """
        Returns a resultset of differences of the given sourcenames.
        Parameter are the sourcesnames to compare
        """
        if not sourcenames or type(sourcenames)!=list or len(sourcenames)<=1:
            return None

        orderbyclause=BaseDB.resolveOrderBy(orderby)
        limit=BaseDB.getLimit(limitup, limitdown)
        self.log.debug("where: %s" %(where))
        self.log.debug("orderbyclause: %s, limit: %s, diffs: %s, notinstalled: %s" %(orderbyclause, limit, Diffs, NotInstalled))
        self.log.debug("getting colnames")
        if not colnames:
            colnames=self.getColnamesForDiff(sourcenames)
        j=0
#        ComLog.getLogger().debug("query %s" % query)
        queries=list()
        installed=None
        if Installed:
            if Diffs or NotInstalled:
                installed=0
            queries.append(self.selectQueryInstalled(sourcenames, colnames, SoftwareCMDB.COMPARE_2_SOFTWARE, where, installed))
        if Diffs:
            if Installed:
                installed=1
            queries.append(self.selectQueryOnlyDiffs(sourcenames, colnames, SoftwareCMDB.COMPARE_2_SOFTWARE, where, installed))
        if NotInstalled:
            queries+=self.selectQueriesNotInstalled(sourcenames, colnames, SoftwareCMDB.COMPARE_2_SOFTWARE, where, Installed)
        union="\n UNION \n".join(queries)
        if orderbyclause and orderbyclause!="":
            union+="\n"+orderbyclause
        if limit and limit != "":
            union+="\n"+limit
        self.log.debug("union: "+union)
        return self.selectQuery(union)

    def selectQueriesNotInstalled(self, sourcenames, allcolnamesr, colnames=COMPARE_2_SOFTWARE, where=None, withInstalled=False):
        queries=list()
#        querycolumns=SoftwareCMDB.getAllColnamesNotInstalled(colnames[1:], SoftwareCMDB.COMPARE_2_SOFTWARE[1:], sourcenames)
#        self.log.debug("querycolumns: %s" %(querycolumns))

        tablealias="nirpms"
        tablealias_2nd="nirpms2nd"
        allcolnames=list()
        allcolnames.append(colnames[0])
        for i in range(len(sourcenames)):
            for colname in colnames[1:]:
                allcolnames.append("%s."+colname)
        #allcolnamesr=colnames
        #allcolnamesr=SoftwareCMDB.getColnamesForDiff(sourcenames, colnames)
        notinstalled=list()
        dbs=list()
        for i in range(len(sourcenames)):
            dbs.append(tablealias+str(i))
        self.log.debug("dbs[%u]: %s" %(len(dbs), dbs))
        self.log.debug("allcolnamesr[%u]: %s" %(len(allcolnamesr), allcolnamesr))
        self.log.debug("allcolnames[%u]: %s" %(len(allcolnames), allcolnames))
        l=len(colnames[1:])
        self.log.debug("colnames/l[%u]:%s" %(l, colnames))
        m=len(sourcenames)
        self.log.debug("sourcenames/m[%u]:%s" %(m, sourcenames))
        p=0
        for i in range(len(sourcenames)*(len(sourcenames)-1)):
            newcolnames=list(allcolnames[1:])
            # all tablealiases that are seen to have installed packages
            newdbs=list(dbs)
            # all tablealiases that are seen to have not installed packages
            newdbs2=list()
            selectcols=list()
            joins=list()
            joins2=list()
            whereequals=list()
            wherenot=list()
            where2=list()
            qname="q%u" %(i)
            j=i%l
            n=i%m
            if n==0:
                for k in range(l):
                    notinstalled.append("\""+SoftwareCMDB.NOT_INSTALLED_STRING+"\"")
            for k in range(len(notinstalled)):
#                self.log.debug("newcolnames[%u], j=%u, k=%u, len(notinstalled)=%u" %((n*len(notinstalled)+k)%len(allcolnames[1:]), j, k, len(notinstalled)))
                newcolnames[(n*len(notinstalled)+k)%len(allcolnames[1:])]=notinstalled[k]
                if k%l==0:
                    self.log.debug("[%u] dbs removing: k mod l: %u, k mod m: %u, n: %u, dbs[%u], %s/%s=removing" %(i, k%l, k%m, n, (n%m)%len(newdbs), newdbs[(n%m)%len(newdbs)], newdbs))
                    newdbs2.append(newdbs[(n%m)%len(newdbs)])
                    del newdbs[(n%m)%len(newdbs)]
            o=0
            for k in range(len(allcolnames[1:])):
                selectcols.append(newcolnames[k]+" AS \""+allcolnamesr[k+1]+"\"")
                if len(joins2)==0 and k%l==0:
                    joins2.append("   FROM "+self.tablename+" AS "+tablealias+str(len(joins2)))
                    where2.append("%s.clustername=\"%s\"" %(tablealias+str(len(joins2)-1), sourcenames[len(joins2)-1]))
                elif k%l==0:
                    joins2.append("   JOIN "+self.tablename+" AS "+tablealias+str(len(joins2))+" USING (name, architecture) ")
                    where2.append("%s.clustername=\"%s\"" %(tablealias+str(len(joins2)-1), sourcenames[len(joins2)-1]))

                if k%l==0 and newcolnames[k].find(SoftwareCMDB.NOT_INSTALLED_STRING)<0:
#                    self.log.debug("add join and whereequals k mod m %u; %u, m:%u" %(k%m, len(notinstalled), m))
                    if len(joins)==0:
                        joins.append("   FROM "+self.tablename+" AS %s")
                    else:
                        joins.append("   JOIN "+self.tablename+" AS %s USING (name, architecture) ")
                    whereequals.append("%s.clustername=\""+sourcenames[o]+"\"")
                    #where2_exist.append("       ")
                    o+=1
                elif k%l==0:
                    wherenot.append(" AND (%s.name,%s.architecture) NOT IN (SELECT %s.name, %s.architecture FROM "+self.tablename+" AS %s WHERE %s.clustername=\""+sourcenames[o]+"\")")
                    #where2_notexist.append("       NOT ")
                    o+=1
            o=0
            for k in range(len(selectcols)):
                if selectcols[k].find(SoftwareCMDB.NOT_INSTALLED_STRING)<0:
#                    self.log.debug("k: %u, o: %u, selectcols[k]: %s, newdbs: %s" %(k, o, selectcols[k], newdbs))
                    selectcols[k]=selectcols[k] %(newdbs[o])
                    if k%l==l-1:
                        o+=1
            self.log.debug("joins: %s, whereequals: %s, newdbs: %s" %(joins, whereequals, newdbs))
            for k in range(len(joins)):
                joins[k]=joins[k] %(newdbs[k])
                whereequals[k]=whereequals[k] %(newdbs[k])

            for k in range(len(wherenot)):
#                diffsquery=self.selectQueryOnlyDiffs(sourcenames, allcolnamesr[:4], selectcols, colnames, where)
#                regexp=re.compile("SELECT (.*) FROM", re.M|re.S)
#                diffsquery=regexp.sub("SELECT %s.name, %s.version, %s.subversion, %s.architecture FROM" %(newdbs[0], newdbs[0], newdbs[0], newdbs[0]), diffsquery)
                wherenot[k]=wherenot[k] %(newdbs[0], newdbs[0], qname+newdbs2[k], qname+newdbs2[k], qname+newdbs2[k], qname+newdbs2[k])#, newdbs[0], newdbs[0], newdbs[0], newdbs[0], diffsquery)

            whererest=""
            if where and type(where)==str and where!="":
                whererest="\n   AND "+newdbs[0]+"."+where
            elif where and type(where)==list:
                thestr="\n   AND "+newdbs[0]+"."
                whererest=thestr+thestr.join(where)

            if withInstalled:
                selectcols.append("2 AS "+SoftwareCMDB.DIFFS_COLNAME)


            # First query matches all software packages not installed on system1 and installed on two without
            # dublicates
            queries.append("SELECT DISTINCT "+newdbs[0]+"."+allcolnames[0]+" AS \""+allcolnamesr[0]+"\", \n      "+", ".join(selectcols)+\
                           "\n"+"\n".join(joins)+\
                           "\n   WHERE "+\
                           " AND ".join(whereequals)+\
                           "\n   "+\
                           "\n   ".join(wherenot)+
                           whererest)
            # Second query matches all software packages not installed on system1 and installed on two with
            # taking dublicates into account. So that if n packages are installed on system1 and m on system2
            # the differing m-n packages are displayed
            _clusternames=list()
            _equals=list()
            _equals2=list()
            for k in range(len(newdbs)):
                _clusternames.append("%s.clustername=%s.clustername" %(tablealias_2nd, newdbs[k]))
                _equals.append("%s.name=%s.name" %(tablealias_2nd, newdbs[k]))
                _equals.append("%s.architecture=%s.architecture" %(tablealias_2nd, newdbs[k]))
            for k in range(len(newdbs2)):
                __equals3=list()
                __equals3.append("%s.version=%s.version" %(tablealias_2nd, newdbs2[k]))
                __equals3.append("%s.subversion=%s.subversion" %(tablealias_2nd, newdbs2[k]))
                _equals2.append("("+(" AND ").join(__equals3)+")");

            _where2_templ="EXISTS\n"+\
                          "        (SELECT DISTINCT * FROM "+self.tablename+" AS "+tablealias_2nd+"\n"+\
                          "           WHERE (%s) \n"+\
                          "             AND %s \n"+\
                          "             AND (%s)) \n"
            where2_exist="     "+_where2_templ %(" OR ".join(_clusternames), " AND ".join(_equals), " OR ".join(_equals2))

            _clusternames=list()
            _equals=list()
            _equals2=list()
            for k in range(len(newdbs2)):
                _clusternames.append("%s.clustername=%s.clustername" %(tablealias_2nd, newdbs2[k]))
                _equals.append("%s.name=%s.name" %(tablealias_2nd, newdbs2[k]))
                _equals.append("%s.architecture=%s.architecture" %(tablealias_2nd, newdbs2[k]))
            for k in range(len(newdbs)):
                __equals3=list()
                __equals3.append("%s.version=%s.version" %(tablealias_2nd, newdbs[k]))
                __equals3.append("%s.subversion=%s.subversion" %(tablealias_2nd, newdbs[k]))
                _equals2.append("("+(" AND ").join(__equals3)+")");

            where2_notexist="     NOT "+_where2_templ %(" OR ".join(_clusternames), " AND ".join(_equals), " OR ".join(_equals2))

            _clusternames1=list()
            _clusternames2=list()
            for k in range(len(newdbs)):
                _clusternames1.append("clustername=%s.clustername" %(newdbs[k]))
            for k in range(len(newdbs2)):
                _clusternames2.append("clustername=%s.clustername" %(newdbs2[k]))
            where2_count="       (SELECT COUNT(name) FROM "+self.tablename+" WHERE (%s) AND name=%s0.name AND architecture=%s0.architecture GROUP BY name, architecture) >\n"+\
                         "       (SELECT COUNT(name) FROM "+self.tablename+" WHERE (%s) AND name=%s0.name AND architecture=%s0.architecture GROUP BY name, architecture)"
            where2_count=where2_count %(" OR ".join(_clusternames1), tablealias, tablealias, " OR ".join(_clusternames2), tablealias, tablealias)
            queries.append("SELECT DISTINCT "+newdbs[0]+"."+allcolnames[0]+" AS \""+allcolnamesr[0]+"\", \n      "+", ".join(selectcols)+\
                           "\n"+"\n".join(joins2)+\
                           "\n   WHERE "+\
                           "\n     AND ".join(where2)+"\n     AND \n"+\
                           where2_exist+"\n     AND \n"+\
                           where2_notexist+"\n     AND \n"+\
                           where2_count+whererest)
        return queries

    def selectQueryInstalled(self, sourcenames, allcolnamesr, colnames=COMPARE_2_SOFTWARE, where=None, withInstalled=None, equals=["name", "architecture", "version", "subversion"], unequals=None):
        """
        Returns all installed software on all sourcenames
        """
        tablealias="irpms"
        dbs=list()
        columns=list()
        where=list()
        for i in range(len(sourcenames)):
            _db=tablealias+str(i)
            if i==0:
                columns.append(_db+"."+colnames[0]+" AS \""+allcolnamesr[0]+"\"")
            for j in range(len(colnames[1:])):
                columns.append(_db+"."+colnames[j+1]+" AS \""+allcolnamesr[i*len(colnames[1:])+1+j]+"\"")
            where.append(_db+".clustername= \""+sourcenames[i]+"\"")
            if len(dbs)==0:
                dbs.append(self.tablename+" AS "+_db)
            else:
                dbs.append(" LEFT JOIN "+self.tablename+" AS "+_db+" USING(name, architecture, version, subversion)")
        columns.append("%u AS %s" %(withInstalled, SoftwareCMDB.DIFFS_COLNAME))
        query="SELECT DISTINCT "+", ".join(columns)+" FROM "+"\n   ".join(dbs)+\
               "\n   WHERE "+" AND ".join(where)
        self.log.debug("selectQueryInstalled: %s" %query)
        return query

    def selectQueryOnlyDiffs(self, sourcenames, allcolnamesr, colnames=COMPARE_2_SOFTWARE, where=None, withInstalled=None, equals=["name", "architecture"], unequals=["version", "subversion"]):
        """
        Returns the select query that only filters differences between installed Software.
        See selectNotInstalledQuery.
        """
        if not unequals:
            unequals=list()
        j=0
        tablealias="odrpms"
        version_unequalcols=list()
        subversion_unequalcols=list()
        joins=list()
        columns=list()
        dbs=list()
        wherelst=list()
        dbs2=list()
        wherelst2=list()
        notexists=list()
        joins2=list()
        equals2=list(equals)
        equals2+=unequals
        unequalsmap=dict()
        count_clusternames=list()
        for unequal in unequals:
            unequalsmap[unequal]=list()
        for i in range(len(sourcenames)):
            formatedname=self.formatToSQLCompat(sourcenames[i])
            if j==0:
                columns.append(tablealias+str(i)+"."+colnames[1]+" AS \""+allcolnamesr[j+1]+\
                               "\", MAX("+tablealias+str(i)+"."+colnames[2]+") AS \""+allcolnamesr[j+2]+\
                               "\", MAX("+tablealias+str(i)+"."+colnames[3]+") AS \""+allcolnamesr[j+3]+"\"")
            elif j+3 < len(allcolnamesr):
                columns.append(tablealias+str(i)+"."+colnames[1]+" AS \""+allcolnamesr[j+1]+"\", "+tablealias+str(i)+"."+colnames[2]+" AS \""+\
                               allcolnamesr[j+2]+"\", "+tablealias+str(i)+"."+colnames[3]+" AS \""+allcolnamesr[j+3]+"\"")
            _db=tablealias+str(i)
            dbs.append(self.tablename+" AS "+_db)
            if i > 0:
                joins.append(" INNER JOIN "+dbs[i]+" USING (%s) " %(", ".join(equals)))
            wherelst.append(tablealias+str(i)+".clustername=\""+sourcenames[i]+"\"")
            for unequal in unequals:
                unequalsmap[unequal].append(tablealias+str(i)+"."+unequal)

            _db1=tablealias+str(len(sourcenames)+i)
            dbs2.append(self.tablename+" AS "+_db1)
            if i > 0:
                joins2.append("      LEFT JOIN "+dbs2[i]+" USING (%s) " %(", ".join(equals2)))
            wherelst2.append("\n         "+_db1+".clustername=\""+sourcenames[i]+"\"")
            for col in unequals:
                wherelst2.append("\n         "+_db1+"."+col+"="+_db+"."+col)

            _db2=tablealias+str(len(sourcenames)*2+i)
            _notexists="\n    SELECT * FROM "+self.tablename+" AS "+_db2+\
                       " \n     WHERE \n        "+_db2+".clustername="+_db+".clustername"
            # name and architecutre need to be equal
            for col in equals:
                _notexists+=" AND \n        "+_db2+"."+col+"="+_db+"."+col;
            _ors=list()
            for k in range(len(sourcenames)):
                if k==i:
                    continue
                _ands=list()
                for col in unequals:
                    _ands.append("%s.%s=%s.%s" %(_db2, col, tablealias+str(k), col))
                _ors.append("("+" AND ".join(_ands)+")")
            if len(_ors)==1:
                _notexists+=" AND \n        %s " %(_ors[0])
            else:
                _notexists+=" AND \n        (%s) " %(" OR \n         ".join(_ors))
            notexists.append("NOT EXISTS (%s)" %(_notexists))
            count_clusternames.append("%s.clustername="+_db+".clustername")

            j+=3

        # If special names are filter that where clause is generated here
        whererest=""
        if where and type(where)==str and where!="":
            whererest="\n   AND "+tablealias+"0."+where
        elif where and type(where)==list:
            _tmpname="\n   AND "+tablealias+"0."
            whererest=_tmpname+_tmpname.join(where)

        unequalstr=""
        for unequal in unequals:
            unequalstr+=" OR %s" %(" OR ".join(BaseDB.BinOperatorFromList(unequalsmap[unequal], "!=")))
        if unequalstr != "":
            unequalstr="  AND (%s)\n" %(unequalstr[4:])

        self.log.debug("selectQueryOnlyDiffs %s" %withInstalled)
        if withInstalled!=None:
            columns.append("%u AS %s" %(withInstalled, SoftwareCMDB.DIFFS_COLNAME))

        notexistsquery="NOT EXISTS ("+"\n    SELECT * FROM "+dbs2[0]+"\n"+\
            "\n ".join(joins2)+\
            "\n      WHERE "+" AND ".join(wherelst2)+")"
        _countname=tablealias+str(len(joins)+len(notexists)+2)
        for k in range(len(count_clusternames)):
            count_clusternames[k]=count_clusternames[k] %(_countname)

        countquery="SELECT COUNT("+_countname+".name) FROM "+self.tablename+" AS "+_countname+\
              "\n    WHERE"+\
              "\n      ("+" OR ".join(count_clusternames)+")"+\
              "\n      AND "+_countname+".name="+tablealias+"0.name AND "+_countname+".architecture="+tablealias+"0.architecture GROUP BY "+_countname+".name"
        if len(notexists)<=2:
            _notexist_op="\n  AND "
        else:
            _notexist_op="\n  OR "
        query="SELECT DISTINCT "+tablealias+"0."+colnames[0]+" AS \""+allcolnamesr[0]+"\", "+','.join(columns)+"\n FROM "+dbs[0]+"\n"+\
              "\n ".join(joins)+\
              "\n WHERE "+" AND ".join(wherelst)+"\n"+\
              unequalstr+"  AND "+notexistsquery+"\n  AND ("+\
              _notexist_op.join(notexists)+")"\
              "\n  AND ("+countquery+") % "+str(len(sourcenames))+ "=0"\
              " "+whererest+"\n GROUP BY "+tablealias+"0.version, "+tablealias+"0.subversion" # +" ORDER BY "+tablealias+"0.name"
        return query

    def updateRPM(self, _rpm, name, channelname, channelversion, count=1):
        """
        Updates the given rpmheader in the software_cmdb of this cluster
        rpm: the rpm-header defined by python-rpm with extensions like in ComDSL (channelname and -version)
        name: the name of the cluster/system
        count: the amount of rpms found with this name
        """
        insertquery="INSERT INTO %s VALUES(\"rpm\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\");" \
                    %(self.tablename, name, channelname, channelversion, _rpm["name"], _rpm["version"], _rpm["release"], _rpm["arch"])
        selectquery="SELECT name, version, subversion AS \"release\", architecture AS \"arch\", channel AS channelname, channelversion FROM %s WHERE clustername=\"%s\" AND name=\"%s\" AND architecture=\"%s\"" \
                    %(self.tablename, name, _rpm["name"], _rpm["arch"])
        updatequery="UPDATE %s SET clustername=\"%s\", channel=\"%s\", channelversion=\"%s\", name=\"%s\", version=\"%s\", subversion=\"%s\", architecture=\"%s\" WHERE clustername=\"%s\" AND name=\"%s\";" \
                    %(self.tablename, name, channelname, channelversion, _rpm["name"], _rpm["version"], _rpm["release"], _rpm["arch"], name, _rpm["name"])
        unequal_list=["version", "release", "channelname", "channelversion"]
        if count > 1:
            selectquery += " AND version=\"%s\" AND subversion=\"%s\"" %(_rpm["version"], _rpm["release"])
            updatequery="UPDATE %s SET clustername=\"%s\", channel=\"%s\", channelversion=\"%s\", name=\"%s\", version=\"%s\", subversion=\"%s\", architecture=\"%s\" WHERE clustername=\"%s\" AND name=\"%s\" AND version=\"%s\";" \
                        %(self.tablename, name, channelname, channelversion, _rpm["name"], _rpm["version"], _rpm["release"], _rpm["arch"], name, _rpm["name"], _rpm["version"])
            unequal_list=["channelname", "channelversion"]
        # ComLog.getLogger().debug("select %s" % selectquery)
        ret=super(SoftwareCMDB, self).updateRPM(insertquery, updatequery, selectquery, _rpm,
                                               unequal_list,
                                               { "channelname": channelname, "channelversion": channelversion})
        self.updateRPMinTMP(_rpm, name, channelname, channelversion)
        if ret==1:
            self.dblog.log(DBLogger.DB_LOG_LEVEL, "Added new software package %s-%s.%s.%s (table: %s)" %(_rpm["name"], _rpm["version"], _rpm["release"], _rpm["arch"], self.tablename))
        elif ret>1:
            self.dblog.log(DBLogger.DB_LOG_LEVEL, "Updated existing software package %s-%s.%s.%s (table: %s)" %(_rpm["name"], _rpm["version"], _rpm["release"], _rpm["arch"], self.tablename))

    def cleanTMP(self, name):
        query="DELETE FROM %s_tmp WHERE clustername=\"%s\";" %(self.tablename, name)
        self.dblog.log(DBLogger.DB_LOG_LEVEL, "Cleaning %s_tmp for %s" %(self.tablename, name))
        self.db.query(query)

    def updateRPMinTMP(self, _rpm, name, channelname, channelversion):
        query="INSERT INTO %s_tmp VALUES(\"rpm\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\");" \
                    %(self.tablename, name, channelname, channelversion, _rpm["name"], _rpm["version"], _rpm["release"], _rpm["arch"])
        self.db.query(query)

    def deleteNotInTmp(self, name, names=""):
        _names=""
        if type(names)==list:
            for _name in names:
                _names+=" OR software_cmdb.name=\"%s\"" %(_name)
            if len(names)>0:
                _names=" AND ("+_names[3:]+")"
        else:
            _names="%s" %(names)

        query="""DELETE FROM software_cmdb  WHERE clustername="%s" AND
  (name, version, subversion, architecture)
  NOT IN (SELECT name, version, subversion, architecture FROM software_cmdb_tmp WHERE clustername="%s")
     %s;""" %(name, name, _names)

        self.log.debug("deleteNotInTmp: query: "+query)
        self.db.query(query)

        if self.db.affected_rows() > 0:
            self.dblog.log(DBLogger.DB_LOG_LEVEL, "Deleting old software %u." %(self.db.affected_rows()))


def test():
    colnames=["name", "c1", "c2", "c3"]
    sources=["s1", "s2", "s3"]
    softwarecmdb=SoftwareCMDB(hostname="localhost", user="atix", password="atix", database="atix_cmdb")
    print "Testing getColnamesForDiff"
    allcolnames=SoftwareCMDB.getColnamesForDiff(sources, colnames)
    print allcolnames

    print "Testing selectQueriesNotInstalled:"
    queries=softwarecmdb.selectQueriesNotInstalled(sources, allcolnames, colnames)
    for i in range(len(queries)):
        print "[%u]:%s" %(i, queries[i])
    print "%u queries" %(len(queries))

if __name__ == '__main__':
    test()

# $Log: ComSoftwareCMDB.py,v $
# Revision 1.18  2007-05-10 12:14:01  marc
# Hilti RPM Control
# - Bugfix for Where-Clause
#
# Revision 1.17  2007/05/10 08:22:47  marc
# Hilti RPM Control
# - fixed ambigous query in getSoftwareDublicates for mysql v3.
#
# Revision 1.16  2007/05/10 07:59:36  marc
# Hilti RPM Control:
# - BZ #46 Fixed
#
# Revision 1.15  2007/04/18 10:17:07  marc
# Hilti RPM Control
# - fixed ambigousness with mysql3 in getDublicateSoftware..
# - removed architecture in in getDublicateSoftware..
#
# Revision 1.14  2007/04/18 07:59:12  marc
# Hilti RPM Control
# - added getSoftwareDublicates
# - added Installed for Categories and Diffs
#
# Revision 1.13  2007/04/12 13:07:15  marc
# Hilti RPM Control
# - added also installed for diffs
#
# Revision 1.12  2007/04/12 12:20:48  marc
# Hilti RPM Control
# - new feature also installed for n:m compares
#
# Revision 1.11  2007/04/12 07:53:05  marc
# Hilti RPM Control
# - Bugfix in changing or adding multiple rpms with same name
#
# Revision 1.10  2007/04/11 11:48:40  marc
# Hilti RPM Control
# - support for multiple RPMs with same name
#
# Revision 1.9  2007/04/02 11:13:34  marc
# For Hilti RPM Control :
# - added MainCompare
# - some bugfixes
#
# Revision 1.8  2007/03/14 16:51:42  marc
# fixed AND instead of OR in OnlyDiffs Join
#
# Revision 1.7  2007/03/14 15:26:34  marc
# compatible with mysql3 dialect and ambigousness. (RHEL4 has mysql3) (4th)
#
# Revision 1.6  2007/03/14 15:11:37  marc
# compatible with mysql3 dialect and ambigousness. (RHEL4 has mysql3) (3rd)
#
# Revision 1.5  2007/03/14 14:57:21  marc
# compatible with mysql3 dialect and ambigousness. (RHEL4 has mysql3)
#
# Revision 1.4  2007/03/14 14:37:24  marc
# compatible with mysql3 dialect and ambigousness. (RHEL4 has mysql3)
#
# Revision 1.3  2007/03/14 13:16:48  marc
# added support for comparing multiple n>2 sources
#
# Revision 1.2  2007/03/05 16:10:30  marc
# first rpm version
#
# Revision 1.1  2007/02/23 12:42:23  marc
# initial revision
#
