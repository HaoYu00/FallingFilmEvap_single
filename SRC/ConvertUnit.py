import math

def Uint_mm2m(input):
    output = input / 1000
    return output
def Uint_m2mm(input):
    output = input * 1000
    return output
def Uint_kW2W(input):
    output = input * 1000
    return output
def Uint_W2kW(input):
    output = input / 1000
    return output
def Uint_C2K(input):
    output = input + 273.15
    return output
def Uint_K2C(input):
    output = input - 273.15
    return output

def Uint_LPM2m3pSec(input):
    output = input * ( 1 / 60 / 1000 )
    return output
def Uint_m3pSec2LPM(input):
    output = input / ( 1 / 60 / 1000 )
    return output

def Uint_Pa2Bar(input):
    output = input * 1E5
    return output
def Uint_Bar2Pa(input):
    output = input / 1E5
    return output

def Uint_Gage_Pa2Abs_Pa(input):
    output = input + 101325
    return output

def convertStr2Num(inputList,TypeFlag):
    
    for i in range(0,len(inputList)):

        if inputList[i] != '' :
            if TypeFlag=='np.float64':
                inputList[i] = float(inputList[i]) 
            elif TypeFlag=='np.int64':
                inputList[i] = int(inputList[i]) 

    return inputList

def convertNum2Str(inputList):
    TypeFlag = '.3E'
    ListFlag = isinstance(inputList,list)
    if ListFlag == True:
        for i in range(0,len(inputList)):

            if inputList[i] != '' :
                inputList[i] = str(format(inputList[i],'.3E'))
    else:
        if inputList != '' :
            inputList = str(format(inputList,'.3E'))
    return inputList