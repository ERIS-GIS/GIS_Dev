#-------------------------------------------------------------------------------
# Name:        GIS US Aerial Report Image
# Purpose:
#
# Author:      jloucks
#
# Created:     07/20/2020
# Copyright:   (c) jloucks 2020
#-------------------------------------------------------------------------------

import sys
import arcpy
import cx_Oracle
import contextlib
import json
import os
import shutil
import timeit
import urllib
start1 = timeit.default_timer()
arcpy.env.overwriteOutput = True

class Machine:
    machine_test = r"\\cabcvan1gis006"
    machine_prod = r"\\cabcvan1gis007"
class Credential:
    oracle_test = r"ERIS_GIS/gis295@GMTESTC.glaciermedia.inc"
    oracle_production = r"ERIS_GIS/gis295@GMPRODC.glaciermedia.inc"
class ReportPath:
    caaerial_prod= r"\\CABCVAN1OBI007\ErisData\prod\aerial_ca"
    caaerial_test= r"\\CABCVAN1OBI007\ErisData\test\aerial_ca"
class TestConfig:
    machine_path=Machine.machine_test
    caaerial_path = ReportPath.caaerial_test

    def __init__(self):
        machine_path=self.machine_path
        self.LAYER=LAYER(machine_path)
        self.MXD=MXD(machine_path)
class ProdConfig:
    machine_path=Machine.machine_prod
    caaerial_path = ReportPath.caaerial_prod

    def __init__(self):
        machine_path=self.machine_path
        self.LAYER=LAYER(machine_path)
        self.MXD=MXD(machine_path)
class Oracle:
    # static variable: oracle_functions
    oracle_functions = {'getorderinfo':"eris_gis.getOrderInfo"
    }
    erisapi_procedures = {'getaeriallist':'flow_autoprep.getAerialImageJson','passclipextent': 'flow_autoprep.setClipImageDetail','getselectedimages':"FLOW_report_gis.getSelectedImages",
    'passreportextent':"FLOW_report_gis.insertAerialImageInfo"}
    def __init__(self,machine_name):
        # initiate connection credential
        if machine_name.lower() =='test':
            self.oracle_credential = Credential.oracle_test
        elif machine_name.lower()=='prod':
            self.oracle_credential = Credential.oracle_production
        else:
            raise ValueError("Bad machine name")
    def connect_to_oracle(self):
        try:
            self.oracle_connection = cx_Oracle.connect(self.oracle_credential)
            self.cursor = self.oracle_connection.cursor()
        except cx_Oracle.Error as e:
            print(e,'Oracle connection failed, review credentials.')
    def close_connection(self):
        self.cursor.close()
        self.oracle_connection.close()
    def call_function(self,function_name,orderID):
        self.connect_to_oracle()
        cursor = self.cursor
        try:
            outType = cx_Oracle.CLOB
            func = [self.oracle_functions[_] for _ in self.oracle_functions.keys() if function_name.lower() ==_.lower()]
            if func !=[] and len(func)==1:
                try:
                    if type(orderID) !=list:
                        orderID = [orderID]
                    output=json.loads(cursor.callfunc(func[0],outType,orderID).read())
                except ValueError:
                    output = cursor.callfunc(func[0],outType,orderID).read()
                except AttributeError:
                    output = cursor.callfunc(func[0],outType,orderID)
            return output
        except cx_Oracle.Error as e:
            raise Exception(("Oracle Failure",e.message.message))
        except Exception as e:
            raise Exception(("JSON Failure",e.message.message))
        except NameError as e:
            raise Exception("Bad Function")
        finally:
            self.close_connection()
    def call_erisapi(self,erisapi_input):
        self.connect_to_oracle()
        cursor = self.cursor
        arg1 = erisapi_input
        arg2 = cursor.var(cx_Oracle.CLOB)
        arg3 = cursor.var(cx_Oracle.CLOB)
        arg4 = cursor.var(str)
        try:
            func = ['eris_api.callOracle']
            if func !=[] and len(func)==1:
                try:
                    output = cursor.callproc(func[0],[arg1,arg2,arg3,arg4])
                except ValueError:
                    output = cursor.callproc(func[0],[arg1,arg2,arg3,arg4])
                except AttributeError:
                    output = cursor.callproc(func[0],[arg1,arg2,arg3,arg4])
            return [output[0],cx_Oracle.LOB.read(output[1]),cx_Oracle.LOB.read(output[2]),output[3]]
        except cx_Oracle.Error as e:
            raise Exception(("Oracle Failure",e.message))
        except Exception as e:
            raise Exception(("JSON Failure",e.message))
        except NameError as e:
            raise Exception("Bad Function")
        finally:
            self.close_connection()
    def pass_values(self,function_name,value):#(self,function_name,data_type,value):
        self.connect_to_oracle()
        cursor = self.cursor
        try:
            func = [self.oracle_functions[_] for _ in self.oracle_functions.keys() if function_name.lower() ==_.lower()]
            if func !=[] and len(func)==1:
                try:
                    #output= cursor.callfunc(func[0],oralce_object,value)
                    output= cursor.callproc(func[0],value)
                    return 'pass'
                except ValueError:
                    raise
            return 'failed'
        except cx_Oracle.Error as e:
            raise Exception(("Oracle Failure",e.message.message))
        except Exception as e:
            raise Exception(e.message)
        except NameError as e:
            raise Exception("Bad Function")
        finally:
            self.close_connection()
## Custom Exceptions ##
class SingleEmptyImage(Exception):
    pass
class DoqqEmptyImage(Exception):
    pass
class OracleBadReturn(Exception):
    pass
class NoAvailableImage(Exception):
    pass
def createGeometry(pntCoords,geometry_type,output_folder,output_name, spatialRef = arcpy.SpatialReference(4326)):
    outputSHP = os.path.join(output_folder,output_name)
    if geometry_type.lower()== 'point':
        arcpy.CreateFeatureclass_management(output_folder, output_name, "MULTIPOINT", "", "DISABLED", "DISABLED", spatialRef)
        cursor = arcpy.da.InsertCursor(outputSHP, ['SHAPE@'])
        cursor.insertRow([arcpy.Multipoint(arcpy.Array([arcpy.Point(*coords) for coords in pntCoords]),spatialRef)])
    elif geometry_type.lower() =='polyline':
        arcpy.CreateFeatureclass_management(output_folder, output_name, "POLYLINE", "", "DISABLED", "DISABLED", spatialRef)
        cursor = arcpy.da.InsertCursor(outputSHP, ['SHAPE@'])
        cursor.insertRow([arcpy.Polyline(arcpy.Array([arcpy.Point(*coords) for coords in pntCoords]),spatialRef)])
    elif geometry_type.lower() =='polygon':
        arcpy.CreateFeatureclass_management(output_folder,output_name, "POLYGON", "", "DISABLED", "DISABLED", spatialRef)
        cursor = arcpy.da.InsertCursor(outputSHP, ['SHAPE@'])
        cursor.insertRow([arcpy.Polygon(arcpy.Array([arcpy.Point(*coords) for coords in pntCoords]),spatialRef)])
    del cursor
    return outputSHP
def export_reportimage(imagedict,ordergeometry):
    ## In memory
    mxd = arcpy.mapping.MapDocument(mxdexport_template)
    df = arcpy.mapping.ListDataFrames(mxd,'*')[0]
    sr = arcpy.SpatialReference(4326)
    df.SpatialReference = sr
    geo_lyr = arcpy.mapping.Layer(ordergeometry)
    arcpy.mapping.AddLayer(df,geo_lyr,'TOP')
    ordered_all_values = imagedict.keys()
    if len(ordered_all_values) == 1:
        sorted_order = ordered_all_values
    else:
        sorted_order = ordered_all_values.sort()
    for order_value in sorted_order:
        auid = imagedict[order_value][0]
        image_source = imagedict[order_value][1]
        imagepath = imagedict[order_value][2]
        lyrpath = os.path.join(scratch,str(auid) + '.lyr')
        arcpy.MakeRasterLayer_management(imagepath,lyrpath)
        image_lyr = arcpy.mapping.Layer(lyrpath)
        arcpy.mapping.AddLayer(df,image_lyr,'TOP')
    geometry_layer = arcpy.mapping.ListLayers(mxd,'OrderGeometry',df)[0]
    geometry_layer.visible = False
    geo_extent = geometry_layer.getExtent(True)
    df.extent = geo_extent
    if df.scale <= MapScale:
        df.scale = MapScale
        export_width = 5100
        export_height = 6600
    elif df.scale > MapScale:
        df.scale = ((int(df.scale)/100)+1)*100
        export_width = int(5100*1.4)
        export_height = int(6600*1.4)
    arcpy.RefreshActiveView()
    ###############################
    ## NEED TO EXPORT DF EXTENT TO ORACLE HERE


    ##############################
    #arcpy.mapping.ExportToJPEG(mxd,os.path.join(job_folder,'year'+'_source'+auid + '.jpg'),df,df_export_width=5100,df_export_height=6600,world_file=True,color_mode = '24-BIT_TRUE_COLOR', jpeg_quality = 50)
    #arcpy.DefineProjection_management(os.path.join(job_folder,'year'+'_source'+auid + '.jpg'), 3857)
    #shutil.copy(os.path.join(job_folder,'year'+'_source'+auid + '.jpg'),os.path.join(jpg_image_folder,auid + '.jpg'))
    arcpy.mapping.ExportToJPEG(mxd,os.path.join(job_fin,image_year + '_' + image_source  + '.jpg'),df,df_export_width=export_width,df_export_height=export_height,world_file=True,color_mode = '24-BIT_TRUE_COLOR', jpeg_quality = 50)
    extent =arcpy.Describe(os.path.join(job_fin,image_year + '_' + image_source  + '.jpg')).extent
    NW_corner= str(extent.XMin) + ',' +str(extent.YMax)
    NE_corner= str(extent.XMax) + ',' +str(extent.YMax)
    SW_corner= str(extent.XMin) + ',' +str(extent.YMin)
    SE_corner= str(extent.XMax) + ',' +str(extent.YMin)
    print NW_corner, NE_corner, SW_corner, SE_corner
    try:
        image_extents = str({"PROCEDURE":Oracle.erisapi_procedures['passreportextent'], "ORDER_NUM" : OrderNumText,"TYPE":"ae_pdf",
        "SWLAT":str(extent.YMin),"SWLONG":str(extent.XMin),"NELAT":(extent.YMax),"NELONG":str(extent.XMax),"FILENAME":str(image_year + '_' + image_source  + '.jpg'),
        "CENTERLAT" : "", "CENTERLONG":"", "IMAGE_WIDTH":"","IMAGE_HEIGHT":""})
        message_return = Oracle('test').call_erisapi(image_extents)
        if message_return[3] != 'Y':
            raise OracleBadReturn
    except OracleBadReturn:
        arcpy.AddError('status: '+message_return[3]+' - '+message_return[2])
    mxd.saveACopy(os.path.join(scratch,image_year+'_export.mxd'))
    del mxd


if __name__ == '__main__':
    start = timeit.default_timer()
    orderID = '908897'#arcpy.GetParameterAsText(0)
    scratch = r'C:\Users\JLoucks\Documents\JL\psr2'#arcpy.env.scratchFolder
    job_directory = r'\\192.168.136.164\v2_usaerial\JobData\test'
    mxdexport_template = r'\\cabcvan1gis006\GISData\Aerial_US\mxd\Aerial_US_Export.mxd'
    MapScale = 6000

    ##get info for order from oracle
    orderInfo = Oracle('test').call_function('getorderinfo',orderID)
    OrderNumText = str(orderInfo['ORDER_NUM'])
    job_folder = os.path.join(job_directory,OrderNumText)
    ## Return aerial list from oracle
    #oracle_autoprep = str({"PROCEDURE":Oracle.erisapi_procedures['getaeriallist'],"ORDER_NUM":OrderNumText})
    #aerial_list_return = Oracle('test').call_erisapi(oracle_autoprep)
    #aerial_list_json = json.loads(aerial_list_return[1])

    OrderGeometry = createGeometry(eval(orderInfo[u'ORDER_GEOMETRY'][u'GEOMETRY'])[0],orderInfo['ORDER_GEOMETRY']['GEOMETRY_TYPE'],scratch,'OrderGeometry.shp')
    shutil.copy(mxdexport_template,os.path.join(scratch,'template.mxd'))
    mxdexport_template = os.path.join(scratch,'template.mxd')
    ## Get order geometry 

    oracle_input = str({"PROCEDURE":Oracle.erisapi_procedures['getselectedimages'],"ORDER_NUM":OrderNumText})
    selected_list_return = Oracle('test').call_erisapi(oracle_input)
    selected_list_json = json.loads(selected_list_return[1])

    ##create fin directory
    job_fin = os.path.join(job_folder,'fin')
    if os.path.exists(job_fin):
        shutil.rmtree(job_fin)
    os.mkdir(os.path.join(job_fin))
    ##get image matrix and export
    for image_year in selected_list_json['RESULTS'].keys():
        getimage_dict = {}
        for image in selected_list_json['RESULTS'][image_year]:
            order_key = image['REPORT_DISPLAY_ORDER']
            image_auid = image['AUI_ID']
            image_source = image['IMAGE_SOURCE']
            image_path = image['ORIGINAL_IMAGE_PATH']

            getimage_dict[order_key] = [image_auid,image_source,image_path]
            
        export_reportimage(getimage_dict,OrderGeometry)



