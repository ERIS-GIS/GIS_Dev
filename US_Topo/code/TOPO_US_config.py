import os
import sys
import arcpy
import ConfigParser

addpath = os.path.abspath(__file__).replace(os.path.relpath(__file__),"GIS_Dev")
sys.path.insert(1,os.path.join(addpath,'DB_Framework'))
import db_connections as con
import models

def server_loc_config(configpath,environment):
    if not os.path.exists(scratch):
        os.mkdir(scratch)
    if not os.path.exists(scratch):
        arcpy.management.CreateFileGDB(scratch, scratchgdb)

    configParser = ConfigParser.RawConfigParser()
    configParser.read(configpath)
    if environment == 'test':
        dbconnection = configParser.get('server-config','dbconnection_test')
        reportcheck = configParser.get('server-config','reportcheck_test')
        reportviewer = configParser.get('server-config','reportviewer_test')
        reportinstant = configParser.get('server-config','instant_test')
        reportnoninstant = configParser.get('server-config','noninstant_test')
        upload_viewer = configParser.get('url-config','uploadviewer_test')
        server_config = {'dbconnection':dbconnection,'reportcheck':reportcheck,'viewer':reportviewer,'instant':reportinstant,'noninstant':reportnoninstant,'viewer_upload':upload_viewer}
        return server_config
    # elif environment == 'prod':
    #     dbconnection = configParser.get('server-config','dbconnection_prod')
    #     reportcheck = configParser.get('server-config','reportcheck_prod')
    #     reportviewer = configParser.get('server-config','reportviewer_prod')
    #     reportinstant = configParser.get('server-config','instant_prod')
    #     reportnoninstant = configParser.get('server-config','noninstant_prod')
    #     upload_viewer = configParser.get('url-config','uploadviewer_prod')
    #     server_config = {'dbconnection':dbconnection,'reportcheck':reportcheck,'viewer':reportviewer,'instant':reportinstant,'noninstant':reportnoninstant,'viewer_upload':upload_viewer}
    #     return server_config
    else:
        return 'invalid server configuration'

# order info
# OrderIDText = arcpy.GetParameterAsText(0)#'734618'#
order_obj = models.Order().get_order(20200422040)

# flags
# yesBoundary = arcpy.GetParameterAsText(2)#'no'##
yesBoundary = "yes"        # fixed/yes/no
delyearFlag = "N"           # Y/N, for internal use only, blank maps, etc.
multipage = "N"             # Y/N, for multipages, set yesBoundary to 'fixed' (not 'yes') if want boundary to display

# scratch file/folder outputs
# scratch = arcpy.env.scratchWorkspace
# scratchgdb = "scratch.gdb"
def createScratch():
    scratch = os.path.join(r"\\cabcvan1gis005\MISC_DataManagement\_AW\TOPO_US_SCRATCHY", "test_test10")
    scratchgdb = "scratch.gdb"
    if not os.path.exists(scratch):
        os.mkdir(scratch)
    if not os.path.exists(os.path.join(scratch, scratchgdb)):
        arcpy.CreateFileGDB_management(scratch, "scratch.gdb")
    return scratch, scratchgdb
scratch, scratchgdb = createScratch()

summaryPdf = os.path.join(scratch,'summary.pdf')
coverPdf = os.path.join(scratch,"cover.pdf")
shapePdf = os.path.join(scratch, 'shape.pdf')
annotPdf = os.path.join(scratch, "annot.pdf")
orderGeometry = os.path.join(scratch, scratchgdb, "orderGeometry")
orderGeometryPR = os.path.join(scratch, scratchgdb, "orderGeometryPR")
orderBuffer = os.path.join(scratch, scratchgdb, "buffer")
extent = os.path.join(scratch, scratchgdb, "extent")

# connections/report outputs
server_environment = 'test'
server_config_file = con.server_config_file #r"\\cabcvan1gis006\GISData\ERISServerConfig.ini"
server_config = server_loc_config(server_config_file,server_environment)

reportcheckFolder = server_config["reportcheck"]
viewerFolder = server_config["viewer"]
topouploadurl =  server_config["viewer_upload"] + r"/TopoUpload?ordernumber="
connectionString = server_config["dbconnection"] #con.connection_string #'eris_gis/gis295@cabcvan1ora006.glaciermedia.inc:1521/GMTESTC'

# folders
testpath = r"\\cabcvan1gis005\GISData\Topo_USA"
mxdpath = os.path.join(testpath, r"mxd")

# master data files\folders
mastergdb = os.path.join(testpath, r"masterfile\MapIndices_National_GDB.gdb")
csvfile_h = os.path.join(testpath, r"masterfile\All_HTMC_all_all_gda_results.csv")
csvfile_c = os.path.join(testpath, r"masterfile\All_USTopo_T_7.5_gda_results.csv")
tifdir_h = r'\\cabcvan1fpr009\USGS_Topo\USGS_HTMC_Geotiff'
tifdir_c = r'\\cabcvan1fpr009\USGS_Topo\USGS_currentTopo_Geotiff'

# mxds
mxdfile = os.path.join(mxdpath,"template.mxd")
mxdfile_nova = os.path.join(mxdpath,'template_nova.mxd')

# layers
topolyrfile_none = os.path.join(mxdpath,"topo.lyr")
topolyrfile_b = os.path.join(mxdpath,"topo_black.lyr")
topolyrfile_w = os.path.join(mxdpath,"topo_white.lyr")
bufferlyrfile = os.path.join(mxdpath,"buffer.lyr")
orderGeomlyrfile_point = os.path.join(mxdpath,"orderPoint.lyr")
orderGeomlyrfile_polyline = os.path.join(mxdpath,"orderLine.lyr")
orderGeomlyrfile_polygon = os.path.join(mxdpath,"orderPoly.lyr")
gridlyr = os.path.join(mxdpath,"grid.lyr")

# pdfs
annot_poly = os.path.join(mxdpath,"annot_poly.pdf")
annot_line = os.path.join(mxdpath,"annot_line.pdf")
annot_poly_c = os.path.join(mxdpath,"annot_poly_red.pdf")
annot_line_c = os.path.join(mxdpath,"annot_line_red.pdf")
pdfsymbolfile = os.path.join(mxdpath, "US Topo Map Symbols v7.4.pdf")

# logos
logopath = os.path.join(mxdpath,"logos")

# covers
coverPic = os.path.join(mxdpath, "coverPic", "ERIS_2018_ReportCover_Topographic Maps_F.jpg")
summarypage = os.path.join(mxdpath, "coverPic", "ERIS_2018_ReportCover_Second Page_F.jpg")

# other
logfile = os.path.join(testpath, r"log\USTopoSearch_Log.txt")
logname = "TOPO_US_dev"
readmefile = os.path.join(mxdpath,"readme.txt")