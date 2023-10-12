import math
import os
import json
import pandas as pd
# from openpyxl import load_workbook

def ImportData(filename,sheet_name):
       
    df = pd.read_excel(filename, sheet_name)
    print( 'finish import total data : ', filename )
    return df

def ExportData(filename,sheet_name,df):

    if os.path.exists(filename): os.remove(filename)
    df.to_excel(filename, sheet_name )
    print( 'finish Export total data : ', filename )

def ImportJson(filename):
    # filename = 'importData.json'
    fr = open(filename,'r+')
    # read_dict = eval(fr.read())
    importData = eval(fr.read())   #读取的str转换为字典
    fr.close()

    print( 'finish import total data : ', filename )
    return importData

def ExportJson(filename_, exportData):
    js = json.dumps(exportData)
    # filename = filename_ + ".json"
    filename = filename_ 
    file = open(filename, 'w')
    file.write(js)
    file.close()
    print( 'finish Export total data : ', filename )