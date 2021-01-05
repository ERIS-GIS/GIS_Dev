import arcpy,os
import ConfigParser

def server_loc_config(configpath,environment):
    configParser = ConfigParser.RawConfigParser()
    configParser.read(configpath)
    if environment == 'test':
        reportcheck_test = configParser.get('server-config','reportcheck_test')
        reportviewer_test = configParser.get('server-config','reportviewer_test')
        reportinstant_test = configParser.get('server-config','instant_test')
        reportnoninstant_test = configParser.get('server-config','noninstant_test')
        upload_viewer = configParser.get('url-config','uploadviewer')
        server_config = {'reportcheck':reportcheck_test,'viewer':reportviewer_test,'instant':reportinstant_test,'noninstant':reportnoninstant_test,'viewer_upload':upload_viewer}
        return server_config
    elif environment == 'prod':
        reportcheck_prod = configParser.get('server-config','reportcheck_prod')
        reportviewer_prod = configParser.get('server-config','reportviewer_prod')
        reportinstant_prod = configParser.get('server-config','instant_prod')
        reportnoninstant_prod = configParser.get('server-config','noninstant_prod')
        upload_viewer = configParser.get('url-config','uploadviewer_prod')
        server_config = {'reportcheck':reportcheck_prod,'viewer':reportviewer_prod,'instant':reportinstant_prod,'noninstant':reportnoninstant_prod,'viewer_upload':upload_viewer}
        return server_config
    else:
        return 'invalid server configuration'
class Report_Type:
    wetland = 'wetland'
    ny_wetland = 'ny_wetland'
    flood = 'flood'
    topo = 'topo'
    relief = 'relief'
    wells = 'wells'
    
server_environment = 'test'
server_config_file = r'\\cabcvan1gis006\GISData\ERISServerConfig.ini'
server_config = server_loc_config(server_config_file,server_environment)
connectionString = 'eris_gis/gis295@cabcvan1ora006.glaciermedia.inc:1521/GMTESTC'
report_path = server_config['noninstant']
viewer_path = server_config['viewer']
upload_link = server_config['viewer_upload']+r"/ErisInt/BIPublisherPortal_prod/Viewer.svc/"
#production: upload_link = r"http://CABCVAN1OBI002/ErisInt/BIPublisherPortal_prod/Viewer.svc/"
reportcheck_path = server_config['reportcheck']
connectionPath = r"\\cabcvan1gis005\GISData\PSR\python"

scratch_folder=  arcpy.env.scratchFolder

order_geom_lyr_point = r"\\cabcvan1gis005\GISData\PSR\python\mxd\SiteMaker.lyr"
order_geom_lyr_polyline = r"\\cabcvan1gis005\GISData\PSR\python\mxd\orderLine.lyr"
order_geom_lyr_polygon = r"\\cabcvan1gis005\GISData\PSR\python\mxd\orderPoly.lyr"
buffer_lyr_file = r"\\cabcvan1gis005\GISData\PSR\python\mxd\buffer.lyr"
grid_lyr_file = r"\\cabcvan1gis005\GISData\PSR\python\mxd\Grid_hollow.lyr"
relieflyrfile = r"\\cabcvan1gis005\GISData\PSR\python\mxd\relief.lyr"



data_shadedrelief = r"\\cabcvan1fpr009\US_DEM\CellGrid_1X1Degree_NW.shp"
data_geol = r'\\cabcvan1gis005\GISData\Data\PSR\PSR.gdb\GEOL_DD_MERGE'
# data_flood = r'\\cabcvan1gis005\GISData\Data\PSR\PSR.gdb\S_Fld_Haz_Ar_merged2018'
data_flood = r'\\cabcvan1gis005\GISData\Data\PSR\PSR.gdb\flood_map_wgs84'

data_flood_panel = r'\\cabcvan1gis005\GISData\Data\PSR\PSR.gdb\flood_panel_map_wgs84'
data_wetland = r'\\cabcvan1gis005\GISData\Data\PSR\PSR.gdb\Merged_wetland_Final'
eris_wells = r"\\cabcvan1gis005\GISData\PSR\python\mxd\ErisWellSites.lyr"   #which contains water, oil/gas wells etc.
path_shadedrelief = r"\\cabcvan1fpr009\US_DEM\hillshade13"
datalyr_wetland = r"\\cabcvan1gis005\GISData\PSR\python\mxd\wetland_kml.lyr"
##datalyr_wetlandNY = r"E:\GISData\PSR\python\mxd\wetlandNY.lyr"
datalyr_wetlandNYkml = r"\\cabcvan1gis005\GISData\PSR\python\mxd\wetlandNY_kml.lyr"
datalyr_wetlandNYAPAkml = r"\\cabcvan1gis005\GISData\PSR\python\mxd\wetlandNYAPA_kml.lyr"
datalyr_flood = r"\\cabcvan1gis005\GISData\PSR\python\mxd\flood.lyr"
datalyr_geology = r"\\cabcvan1gis005\GISData\PSR\python\mxd\geology.lyr"
datalyr_contour = r"\\cabcvan1gis005\GISData\PSR\python\mxd\contours_largescale.lyr"
datalyr_plumetacoma = r"\\cabcvan1gis005\GISData\PSR\python\mxd\Plume.lyr"

imgdir_demCA = r"\\Cabcvan1fpr009\US_DEM\DEM1"
masterlyr_demCA = r"\\Cabcvan1fpr009\US_DEM\Canada_DEM_edited.shp"
imgdir_dem = r"\\Cabcvan1fpr009\US_DEM\DEM13"
masterlyr_dem = r"\\Cabcvan1fpr009\US_DEM\CellGrid_1X1Degree_NW_imagename_update.shp"
masterlyr_states = r"\\cabcvan1gis005\GISData\PSR\python\mxd\USStates.lyr"
masterlyr_counties = r"\\cabcvan1gis005\GISData\PSR\python\mxd\USCounties.lyr"
masterlyr_cities = r"\\cabcvan1gis005\GISData\PSR\python\mxd\USCities.lyr"
masterlyr_NHTowns = r"\\cabcvan1gis005\GISData\PSR\python\mxd\NHTowns.lyr"
masterlyr_zipcodes = r"\\cabcvan1gis005\GISData\PSR\python\mxd\USZipcodes.lyr"


mxdfile_relief =  r"\\cabcvan1gis005\GISData\PSR\python\mxd\shadedrelief.mxd"
mxdMMfile_relief =  r"\\cabcvan1gis005\GISData\PSR\python\mxd\shadedreliefMM.mxd"
mxdfile_wetland = r"\\cabcvan1gis005\GISData\PSR\python\mxd\wetland.mxd"
mxdfile_wetlandNY = r"\\cabcvan1gis005\GISData\PSR\python\mxd\wetlandNY_CC.mxd"
mxdMMfile_wetland = r"\\cabcvan1gis005\GISData\PSR\python\mxd\wetlandMM.mxd"
mxdMMfile_wetlandNY = r"\\cabcvan1gis005\GISData\PSR\python\mxd\wetlandMMNY.mxd"
mxd_file_flood = r"\\cabcvan1gis005\GISData\PSR\python\mxd\flood.mxd"
mxd_mm_file_flood = r"\\cabcvan1gis005\GISData\PSR\python\mxd\floodMM.mxd"
mxdfile_geol = r"\\cabcvan1gis005\GISData\PSR\python\mxd\geology.mxd"
mxdMMfile_geol = r"\\cabcvan1gis005\GISData\PSR\python\mxd\geologyMM.mxd"
mxdfile_soil = r"\\cabcvan1gis005\GISData\PSR\python\mxd\soil.mxd"
mxdMMfile_soil = r"\\cabcvan1gis005\GISData\PSR\python\mxd\soilMM.mxd"
mxdfile_wells = r"\\cabcvan1gis005\GISData\PSR\python\mxd\wells.mxd"
mxdMMfile_wells = r"\\cabcvan1gis005\GISData\PSR\python\mxd\wellsMM.mxd"

srGCS83 = arcpy.SpatialReference(os.path.join(connectionPath, r"projections\GCSNorthAmerican1983.prj"))

datapath_soil_HI =r'\\cabcvan1fpr009\SSURGO\CONUS_2015\gSSURGO_HI.gdb'
datapath_soil_AK =r'\\cabcvan1fpr009\SSURGO\CONUS_2015\gSSURGO_AK.gdb'
datapath_soil_CONUS =r'\\cabcvan1fpr009\SSURGO\CONUS_2015\gSSURGO_CONUS_10m.gdb'

hydrologic_dict = {
        "A":'Soils in this group have low runoff potential when thoroughly wet. Water is transmitted freely through the soil.',
        "B":'Soils in this group have moderately low runoff potential when thoroughly wet. Water transmission through the soil is unimpeded.',
        "C":'Soils in this group have moderately high runoff potential when thoroughly wet. Water transmission through the soil is somewhat restricted.',
        "D":'Soils in this group have high runoff potential when thoroughly wet. Water movement through the soil is restricted or very restricted.',
        "A/D":'These soils have low runoff potential when drained and high runoff potential when undrained.',
        "B/D":'These soils have moderately low runoff potential when drained and high runoff potential when undrained.',
        "C/D":'These soils have moderately high runoff potential when drained and high runoff potential when undrained.',
        }

hydric_dict = {
        '1':'All hydric',
        '2':'Not hydric',
        '3':'Partially hydric',
        '4':'Unknown',
        }

fc_soils_fieldlist  = [['muaggatt.mukey','mukey'], ['muaggatt.musym','musym'], ['muaggatt.muname','muname'],['muaggatt.drclassdcd','drclassdcd'],['muaggatt.hydgrpdcd','hydgrpdcd'],['muaggatt.hydclprs','hydclprs'], ['muaggatt.brockdepmin','brockdepmin'], ['muaggatt.wtdepannmin','wtdepannmin'], ['component.cokey','cokey'],['component.compname','compname'], ['component.comppct_r','comppct_r'], ['component.majcompflag','majcompflag'],['chorizon.chkey','chkey'],['chorizon.hzname','hzname'],['chorizon.hzdept_r','hzdept_r'],['chorizon.hzdepb_r','hzdepb_r'], ['chtexturegrp.chtgkey','chtgkey'], ['chtexturegrp.texdesc1','texdesc'], ['chtexturegrp.rvindicator','rv']]
fc_soils_keylist = ['muaggatt.mukey', 'component.cokey','chorizon.chkey','chtexturegrp.chtgkey']
fc_soils_whereClause_queryTable = "muaggatt.mukey = component.mukey and component.cokey = chorizon.cokey and chorizon.chkey = chtexturegrp.chkey"

tbx = r"\\cabcvan1gis005\GISData\PSR\python\ERIS.tbx"
# grid size
grid_size = "2 MILES"
# Explorer
datalyr_wetland = r"\\cabcvan1gis005\GISData\PSR\python\mxd\wetland_kml.lyr"
datalyr_flood = r"\\cabcvan1gis005\GISData\PSR\python\mxd\flood.lyr"
datalyr_geology = r"\\cabcvan1gis005\GISData\PSR\python\mxd\geology.lyr"


def output_jpg(order_obj, report_type):
    if report_type == Report_Type.wetland :
        return os.path.join(scratch_folder, str(order_obj.number) +'_US_WETL.jpg')
    elif report_type == Report_Type.ny_wetland :
         return os.path.join(scratch_folder, str(order_obj.number) +'_NY_WETL.jpg')
    elif report_type == Report_Type.flood:
        return os.path.join(scratch_folder, order_obj.number + '_US_FLOOD.jpg')
    elif report_type == Report_Type.topo:
        return os.path.join(scratch_folder, order_obj.number+'_US_TOPO.jpg')
### order geometry paths config
order_geometry_pcs_shp =  os.path.join(scratch_folder,'order_geometry_pcs.shp')
order_geometry_gcs_shp =  os.path.join(scratch_folder,'order_geometry_gcs.shp')
order_buffer_shp =  os.path.join(scratch_folder,'order_buffer.shp')
order_geom_lyr_file = None
spatial_ref_pcs = None
### topo report paths config
mxd_file_topo = r"\\cabcvan1gis005\GISData\PSR\python\mxd\topo.mxd"
mxd_file_topo_Tacoma = r"\\cabcvan1gis005\GISData\PSR\python\mxd\topo_tacoma.mxd"
mxd_mm_file_topo = r"\\cabcvan1gis005\GISData\PSR\python\mxd\topoMM.mxd"
mxd_mm_file_topo_Tacoma = r"\\cabcvan1gis005\GISData\PSR\python\mxd\topoMM_tacoma.mxd"
topo_master_lyr = r"\\cabcvan1gis005\GISData\Topo_USA\masterfile\CellGrid_7_5_Minute_wgs84.shp"
data_topo = r"\\cabcvan1gis005\GISData\Topo_USA\masterfile\Cell_PolygonAll.shp"
topo_white_lyr_file = r"\\cabcvan1gis005\GISData\PSR\python\mxd\topo_white.lyr"
topo_csv_file = r"\\cabcvan1gis005\GISData\Topo_USA\masterfile\All_USTopo_T_7.5_gda_results.csv"
topo_tif_dir = r"\\cabcvan1fpr009\USGS_Topo\USGS_currentTopo_Geotiff"
topo_frame = os.path.join(scratch_folder, "topo_frame.shp")

### flood report paths config
order_buffer_flood_shp = os.path.join(scratch_folder,'order_buffer_flood.shp')
flood_selectedby_order_shp = os.path.join(scratch_folder,"flood_selectedby_order.shp")
flood_panel_selectedby_order_shp = os.path.join(scratch_folder,"flood_panel_selectedby_order.shp")

