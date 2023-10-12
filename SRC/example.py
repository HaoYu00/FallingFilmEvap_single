from FallingFilmEvap import unittest_singleTube
# from limitation import limitation
import limitation
import os

def main():
    print("Welcome to calculate falling film evaporation heat transfer, calculation setting will be imported from '../Temp/CalcSingleTube/SingleTube_setting.json'")
    limitation.limitation()
    print("citation:", limitation.citation())
    try:
        unittest_singleTube()
        print("Calculation finished, result has been export to the '../Temp/CalcSingleTube/SingleTube_result.json'")
    except Exception as msg:
        print("Calculation failed, please check following error: ")
        print(msg)
    os.system("pause")

main()