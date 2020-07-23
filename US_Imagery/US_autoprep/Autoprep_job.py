## Create job folder, pull images from nas, copy images to job folder/clip doqq images for process
## may need to pass back json to FE or DB

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
class EmptyImage(Exception):
    pass
def get_ordergeometry(coordinates,geometry_type):
    ordergeometry = os.path.join(scratch,'OrderGeometry.shp')
    if geometry_type == 'POINT':
        arcpy.CreateFeatureclass_management(scratch,'OrderGeometry.shp','POINT','','','',4326)
        cursor = arcpy.da.InsertCursor(ordergeometry,["SHAPE@XY"])
        print coordinates[0]
        xy = (coordinates[0])

if __name__ == '__main__':
    start = timeit.default_timer()
    orderID = '828239'#arcpy.GetParameterAsText(0)
    scratch = r'C:\Users\JLoucks\Documents\JL\usaerial'
    job_directory = r'C:\Users\JLoucks\Documents\JL'
    conversion_input = r'\\192.168.136.164\v2_usaerial\input'
    conversion_output = r'\\192.168.136.164\v2_usaerial\output'
    Conversion_URL = r'http://erisservice3.ecologeris.com/ErisInt/USAerialAppService_test/USAerial.svc/USAerialImagePromote_temp?inputfile='

    ##get info for order from oracle

    orderInfo = Oracle('test').call_function('getorderinfo',orderID)
    OrderNumText = str(orderInfo['ORDER_NUM'])
    get_ordergeometry(orderInfo['ORDER_GEOMETRY']['GEOMETRY'],orderInfo['ORDER_GEOMETRY']['GEOMETRY_TYPE'])
    

    #call Oracle to get list of images
    #image_candidates = {'singleframe':[imagename,path,year,source,auid], 'doqq':[imagename,path,year,source,auid]} ## inhouse only
    image_candidates = {'AR1VBIO00030260': {'IMAGE_NAME' :r'66_USGS_AR1VBIO00030260.tif', 'IMAGE_PATH' : r'C:\Users\JLoucks\Desktop\Mike_samples\processed\arc_info_added\66_USGS_AR1VBIO00030260.tif',
    'YEAR':'1966', 'SOURCE':'USGS','TYPE':'singleframe'}, 'AR1VBIO00030260': {'IMAGE_NAME' :r'66_USGS_AR1VBIO00030260.tif', 'IMAGE_PATH' : r'C:\Users\JLoucks\Desktop\Mike_samples\processed\arc_info_added\66_USGS_AR1VBIO00030260.tif',
    'YEAR':'1966', 'SOURCE':'USGS','TYPE':'doqq'}}
    try:
        job_folder = os.path.join(os.path.join(job_directory,OrderNumText))
        org_image_folder = os.path.join(job_folder,'org')
        if os.path.exists(job_folder):
            shutil.rmtree(job_folder)
        os.mkdir(job_folder)
        os.mkdir(org_image_folder)
        if len(list(image_candidates.keys())) == 0:
            raise EmptyImage
        for inhouse_image in list(image_candidates.keys()):
            ### CONVERSION OR COPY???###
            image_auid = inhouse_image
            image_name = image_candidates[image_auid]['IMAGE_NAME']
            image_path = image_candidates[image_auid]['IMAGE_PATH']
            image_year = image_candidates[image_auid]['YEAR']
            image_source = image_candidates[image_auid]['SOURCE']
            image_type = image_candidates[image_auid]['TYPE']
            #arcpy.Copy_management(image_path,os.path.join(conversion_input,image_auid+'.'+image_name.split('.')[-1]))
            arcpy.CopyRaster_management (image_path, os.path.join(conversion_input,image_auid+'.'+image_name.split('.')[-1]), '', '', '', '', 'ColormapToRGB', '8_BIT_UNSIGNED')
            #try:
            call_url = Conversion_URL + image_auid + '.' + image_name.split('.')[-1]
            contextlib.closing(urllib.urlopen(call_url))
            #except:
                #arcpy.AddError('Unable to convert image')
    except EmptyImage:
        arcpy.AddWarning('No image candidates')

