import math
import numpy as np
import pandas as pd
from scipy import optimize
from copy import deepcopy

import GetProperties
from DataIO import ImportJson, ExportJson, ExportData
import Calc_DN
import HT_correlation
# from limitation import limitation
import limitation

def preProcess(dict_import):
    dict_exprot = {
        'test':""
    }
    return dict_exprot
def check_input(dict_import):
    pass

class SingleTubeUnit:
    def __init__(self, dict_import, epsilon):
        self.dict_import = dict_import
        self.epsilon = epsilon
        
    def Calc_DimensionlessNumber(self):
        
        D_o     = self.dict_import['Tube']['Diameter']['Value']
        L       = self.dict_import['Tube']['Length']['Value']
        D2 = self.dict_import['Tube']['D2']['Value']
        
        # shell-side (cold-side)
        mdot_LIQ     = self.dict_import['Shell_side']['mdot_LIQ']['Value']
        # mdot_VAP     = self.dict_import['Shell_side']['mdot_VAP']['Value']
        j_LIQ     = self.dict_import['Shell_side']['j_LIQ']['Value']
        j_VAP     = self.dict_import['Shell_side']['j_VAP']['Value']
        
        T_sat_ref       = self.dict_import['Shell_side']['T_in']['Value']
        fluType_shell   = self.dict_import['Shell_side']['Fluid']
        fluid_shell     = GetProperties.Fluid_Sat(fluType_shell,T_sat_ref)
        
        gravity = 9.81
        
        Gamma_LIQ = mdot_LIQ / L / 2
        # Gamma_VAP = mdot_VAP / L / 2
        
        Re_ff               = Calc_DN.Re_ff( Gamma_LIQ, fluid_shell.VLIQ() )
        Bo_ff               = 0.1 # this value is an initial guessed value, and it will be iteratively updated later
        Ka_ff               = Calc_DN.Ka( fluid_shell.DENLIQ(), 
                                         fluid_shell.DENVAP(), 
                                         fluid_shell.VLIQ(), 
                                         fluid_shell.STLLIQ(),
                                         gravity )
        We_LIQ              = Calc_DN.We_j( j_LIQ, 
                                            D2,
                                            fluid_shell.DENLIQ(),
                                            fluid_shell.STLLIQ())
        # print("j_LIQ = ", j_LIQ)
        # print("We_LIQ = ", We_LIQ)
        
        We_VAP              = Calc_DN.We_j( j_VAP, 
                                            D2,
                                            fluid_shell.DENVAP(),
                                            fluid_shell.STLLIQ())
        We_VAP_imposed      = 0 # this value is an initial guessed value, and it will be iteratively updated later
        We_VAP_evaperated   = 0 # this value is an initial guessed value, and it will be iteratively updated later
        
        dict_DN = {
            'Gamma_LIQ':Gamma_LIQ,
            # 'Gamma_VAP':Gamma_VAP,
            
            'j_LIQ':j_LIQ,
            'j_VAP':j_VAP,
            
            'Re_ff':Re_ff,
            'Bo_ff':Bo_ff,
            'Ka_ff':Ka_ff,
            'We_LIQ':We_LIQ,
            'We_VAP':We_VAP,
            'We_VAP_imposed':We_VAP_imposed,
            'We_VAP_evaperated':We_VAP_evaperated,
        }
        return dict_DN
    
    def Iter_epsilonNTU(self, epsilon): # output residual
        dict_export = self.Guess_epsilonNTU(epsilon)
        return dict_export['res']
            
    def Guess_epsilonNTU(self, epsilon): # output completed result
        def epsilon2NTU(epsilon):
            NTU = - math.log( 1 - epsilon )
            return NTU
        
        def NTU2epsilon(NTU):
            epsilon = 1 - math.exp( - NTU )
            return epsilon
        
        def LMTD(T_hi, T_ho, T_ci, T_co):
            dT_1 = T_hi - T_co
            dT_2 = T_ho - T_ci
            LMTD_ = ( dT_1 - dT_2 ) / math.log( dT_1 / dT_2 )
            return LMTD_
        
        def R_cylinder(r_i, r_o, TCX, L):
            # print('r_o = ', r_o)
            # print('r_i = ', r_i)
            # print('TCX = ', TCX)
            R_ = math.log( r_o / r_i ) / ( 2 * math.pi * TCX * L )
            return R_

        dict_import = self.dict_import
        
        # print("epsilon = ", epsilon)
        
        D_o = dict_import['Tube']['Diameter']['Value']
        L = dict_import['Tube']['Length']['Value']
        t = dict_import['Tube']['Thickness']['Value']
        TCX_wall = dict_import['Tube']['TCX']['Value']
        Tube_Type = dict_import['Tube']['Tube_Type']
        N_tube_Verti = dict_import['Tube']['N_tube_Verti']['Value']
        
        D_i = D_o - 2 * t
        A_o = math.pi * D_o * L
        A_i = math.pi * D_i * L
        A_cross = 0.25 * math.pi * D_i ** 2
            
        # tube-side (hot-side)
        mdot_in_water = dict_import['Tube_side']['mdot']['Value']
        T_in_water = dict_import['Tube_side']['T_in']['Value']
        P_in_water = dict_import['Tube_side']['P_in']['Value']
        fluType_tube = dict_import['Tube_side']['Fluid']
        fluid_tube = GetProperties.Fluid_NotSat(fluType_tube, T_in_water, P_in_water)
        
        
        massflux_water = mdot_in_water / A_cross
        Re_water = massflux_water * D_i / fluid_tube.V()
        C_h = mdot_in_water * fluid_tube.CP()
        
        # shell-side (cold-side)
        mdot_LIQ = dict_import['Shell_side']['mdot_LIQ']['Value']
        T_sat_ref = dict_import['Shell_side']['T_in']['Value']
        fluType_shell = dict_import['Shell_side']['Fluid']
        fluid_shell = GetProperties.Fluid_Sat(fluType_shell,T_sat_ref)

        # Calculate dimensionless number
        dict_DN = self.Calc_DimensionlessNumber()
        
        
        # print("dict_DN['We_LIQ'] = ", dict_DN['We_LIQ'])
        
        # collect input data for calculation of falling film HT
        dict_Lin_2023_ = { 'heatFlux':30E3,
                            'T_critical':fluid_shell.T_critical(),
                            'T_reducing':fluid_shell.T_reducing(),
                            'P_critical':fluid_shell.P_critical(),
                            'T_sat':T_sat_ref,
                            'P_sat':fluid_shell.P_sat(),
                            'Re_ff':dict_DN['Re_ff'],
                            'gamma_ff':dict_DN['Gamma_LIQ'],
                            'Bo_ff':dict_DN['Bo_ff'],
                            'Ka_ff':dict_DN['Ka_ff'],
                            'We_LIQ':dict_DN['We_LIQ'],
                            'We_VAP':dict_DN['We_VAP'],
                            
                            'DENLIQ':fluid_shell.DENLIQ(),
                            'DENVAP':fluid_shell.DENVAP(),
                            'TCXLIQ':fluid_shell.TCXLIQ(),
                            'VISLIQ':fluid_shell.VLIQ(),
                            'CPLIQ':fluid_shell.CPLIQ(),
                            'H_LV':fluid_shell.H_LV(),
                            'STLLIQ':fluid_shell.STLLIQ(),
                            'PRLIQ':fluid_shell.PRLIQ(),
                            'gravity':9.81,
                            'D':D_o,
                            
                            # 'N_HT_Tube_vertical': 1,
                            'N_HT_Tube_vertical': N_tube_Verti,
                            
                            'We_VAP_imposed':0,
                            'We_VAP_evaperated':dict_DN['We_VAP'],
                            
                            'Tube_Type':Tube_Type,
                            'Fin_Height':0,
                            'Fin_Pitch':0,
                            
                            'F_NB':1
                            }
        
        # calc epsilon-NTU method    
        T_hi = T_in_water
        T_ci = T_sat_ref
        T_co = T_sat_ref
        Q_max = C_h * ( T_hi - T_co )

        res_UA = 1E10 # just a large number
        if( epsilon > 0 or epsilon <= 1 ): # prevent ln error
        # epsilon = 0.9
            NTU = epsilon2NTU(epsilon)
            UA_1 = NTU * C_h
            Q_1 = epsilon * Q_max
            
            mdot_evap = Q_1 / fluid_shell.H_LV()
            if( mdot_evap > mdot_LIQ ):
                Q_1 = mdot_LIQ * fluid_shell.H_LV()
                epsilon = Q_1 / Q_max
                NTU = epsilon2NTU(epsilon)
                UA_1 = NTU * C_h
                
            heatFlux = Q_1 / A_o
            
            # Bo_ff and F_NB is refered to the heat flux, thus, they need to be calcualted iteratively
            dict_Lin_2023_['Bo_ff'] = Calc_DN.Bo( dict_DN['Gamma_LIQ'], 
                                                 heatFlux, 
                                                 D_o, 
                                                 fluid_shell.H_LV() )
            # if( dict_Lin_2023_['Bo_ff'] >= 1.0 ): 
            #     dict_Lin_2023_['Bo_ff'] = 1.0
                
            if( dict_Lin_2023_['heatFlux'] > 0 ):
                # avoid numerical error when heat flux < 0
                dict_F_NB = HT_correlation.Calc_F_NB(dict_Lin_2023_)
                dict_Lin_2023_['F_NB'] = dict_F_NB['F_NB']
            else:
                dict_F_NB = {}
                dict_Lin_2023_['F_NB'] = 1
                
            # dict_F_NB = HT_correlation.Calc_F_NB(dict_Lin_2023_)
            # dict_Lin_2023_['F_NB'] = dict_F_NB['F_NB']
            
            
            T_ho = - Q_1 / C_h + T_hi
            LMTD_ = LMTD(T_hi, T_ho, T_ci, T_co)
            # LMTD_ = ( T_hi + T_ho ) / 2 - T_ci
            
            # calc thermal resistance map


            
            # if( dict_Lin_2023_['Bo_ff'] >= 1.0 ): 
            #     pass
            if( dict_Lin_2023_['Bo_ff'] > 0.0 ): 
                # avoid numerical error when Bo_ff < 0
                dict_o_ff = HT_correlation.h_Lin_2023(dict_Lin_2023_)
                
                # HTC_o = HT_correlation.h_pb_Cooper(heatFlux, fluid_shell.P_reducing() , fluid_shell.MOLEMASS())
                HTC_o = dict_o_ff['HTC_PB_2023_ENHANCED']
                
                HTC_o_ff = dict_o_ff['HTC']
            else:
                dict_o_ff = {}
                
                small = 1e-20
                HTC_o = small
                HTC_o_ff = small  
            
            HTC_i = HT_correlation.h_Ginielinski(Re_water, fluid_tube.PR(), D_i, fluid_tube.TCX())
                    
            R_i = 1 / ( HTC_i * A_i )
            R_o = 1 / ( HTC_o * A_o )
            R_o_ff = 1 / ( HTC_o_ff * A_o )
            R_wall = R_cylinder(D_i / 2, D_o / 2, TCX_wall, L)
            R_total = R_o_ff + R_wall + R_i
            
            # UA_2 =  1 / ( R_i + R_o + R_wall)
            UA_2 =  1 / ( R_i + R_o_ff + R_wall)
            
            Q_2 = UA_2 * LMTD_
            
            res_UA = abs( UA_2 - UA_1 ) / UA_2
            res_Q = abs( Q_2 - Q_1 ) / Q_2
            # res = res_UA + res_Q
            res = res_UA
        
        mdot_o_ref = mdot_LIQ - Q_1 / fluid_shell.H_LV()
        
        dict_DN['Bo_ff'] = dict_Lin_2023_['Bo_ff']
                
        dict_export = {
            'epsilon':epsilon,
            'NTU':NTU,
            'Q_max':Q_max,
            'LMTD':LMTD_,
            'heatFlux':heatFlux,
            
            'T_ho':T_ho,
            'mdot_o_ref':mdot_o_ref,
            
            'HTC_i':HTC_i,
            'HTC_o':HTC_o,
            'HTC_o_ff':HTC_o_ff,
            
            'R_i':R_i,
            'R_wall':R_wall,
            'R_o':R_o,
            'R_o_ff':R_o_ff,
            'R_total':R_total,
            
            'Q_1':Q_1,
            'Q_2':Q_2,
            
            'UA_1':UA_1,
            'UA_2':UA_2,
            
            "massflux_water":massflux_water,
            "Re_water":Re_water,
            "C_h":C_h,
            
            'res_UA':res_UA,
            'res_Q':res_Q,
            'res':res,
            'dict_Lin_2023_':dict_Lin_2023_,
            'dict_o_ff':dict_o_ff,
            'dict_DN':dict_DN,
            'dict_F_NB':dict_F_NB
        }
        return dict_export
    def Guess_epsilonNTU_zeroMdot(self): # output completed result
        def epsilon2NTU(epsilon):
            NTU = - math.log( 1 - epsilon )
            return NTU
        
        def NTU2epsilon(NTU):
            epsilon = 1 - math.exp( - NTU )
            return epsilon
        
        def LMTD(T_hi, T_ho, T_ci, T_co):
            dT_1 = T_hi - T_co
            dT_2 = T_ho - T_ci
            LMTD_ = ( dT_1 - dT_2 ) / math.log( dT_1 / dT_2 )
            return LMTD_
        
        def R_cylinder(r_i, r_o, TCX, L):
            # print('r_o = ', r_o)
            # print('r_i = ', r_i)
            # print('TCX = ', TCX)
            R_ = math.log( r_o / r_i ) / ( 2 * math.pi * TCX * L )
            return R_

        # print("mdot_ref_LIQ = 0")
        dict_import = self.dict_import
        D_o = dict_import['Tube']['Diameter']['Value']
        L = dict_import['Tube']['Length']['Value']
        t = dict_import['Tube']['Thickness']['Value']
        TCX_wall = dict_import['Tube']['TCX']['Value']
        Tube_Type = dict_import['Tube']['Tube_Type']
        N_tube_Verti = dict_import['Tube']['N_tube_Verti']['Value']
        
        D_i = D_o - 2 * t
        A_o = math.pi * D_o * L
        A_i = math.pi * D_i * L
        A_cross = 0.25 * math.pi * D_i ** 2
            
        # tube-side (hot-side)
        mdot_in_water = dict_import['Tube_side']['mdot']['Value']
        T_in_water = dict_import['Tube_side']['T_in']['Value']
        P_in_water = dict_import['Tube_side']['P_in']['Value']
        fluType_tube = dict_import['Tube_side']['Fluid']
        fluid_tube = GetProperties.Fluid_NotSat(fluType_tube, T_in_water, P_in_water)
        
        
        massflux_water = mdot_in_water / A_cross
        Re_water = massflux_water * D_i / fluid_tube.V()
        C_h = mdot_in_water * fluid_tube.CP()
        
        # shell-side (cold-side)
        mdot_LIQ = dict_import['Shell_side']['mdot_LIQ']['Value']
        T_sat_ref = dict_import['Shell_side']['T_in']['Value']
        fluType_shell = dict_import['Shell_side']['Fluid']
        fluid_shell = GetProperties.Fluid_Sat(fluType_shell,T_sat_ref)

        # Calculate dimensionless number
        dict_DN = self.Calc_DimensionlessNumber()
        
        # collect input data for calculation of falling film HT
        dict_Lin_2023_ = { 'heatFlux':30E3,
                            'T_critical':fluid_shell.T_critical(),
                            'T_reducing':fluid_shell.T_reducing(),
                            'P_critical':fluid_shell.P_critical(),
                            'T_sat':T_sat_ref,
                            'P_sat':fluid_shell.P_sat(),
                            'Re_ff':dict_DN['Re_ff'],
                            'gamma_ff':dict_DN['Gamma_LIQ'],
                            'Bo_ff':dict_DN['Bo_ff'],
                            'Ka_ff':dict_DN['Ka_ff'],
                            'We_LIQ':dict_DN['We_LIQ'],
                            'We_VAP':dict_DN['We_VAP'],
                            
                            'DENLIQ':fluid_shell.DENLIQ(),
                            'DENVAP':fluid_shell.DENVAP(),
                            'TCXLIQ':fluid_shell.TCXLIQ(),
                            'VISLIQ':fluid_shell.VLIQ(),
                            'CPLIQ':fluid_shell.CPLIQ(),
                            'H_LV':fluid_shell.H_LV(),
                            'STLLIQ':fluid_shell.STLLIQ(),
                            'PRLIQ':fluid_shell.PRLIQ(),
                            'gravity':9.81,
                            'D':D_o,
                            
                            # 'N_HT_Tube_vertical': 1,
                            'N_HT_Tube_vertical': N_tube_Verti,
                            
                            'We_VAP_imposed':0,
                            'We_VAP_evaperated':dict_DN['We_VAP'],
                            
                            'Tube_Type':Tube_Type,
                            'Fin_Height':0,
                            'Fin_Pitch':0,
                            
                            'F_NB':1
                            }

        
        # calc epsilon-NTU method    
        T_hi = T_in_water
        T_ci = T_sat_ref
        T_co = T_sat_ref
        Q_max = C_h * ( T_hi - T_co )

        small = 1e-20
        res_UA = 1E10 # just a large number

        epsilon = 0
        NTU = 0
        UA_1 = 0
        Q_1 = epsilon * Q_max
        heatFlux = Q_1 / A_o
        
        dict_Lin_2023_['heatFlux'] = heatFlux
        
        # Bo_ff and F_NB is refered to the heat flux, thus, they need to be calcualted iteratively
        dict_Lin_2023_['Bo_ff'] = Calc_DN.Bo( dict_DN['Gamma_LIQ'], 
                                                heatFlux, 
                                                D_o, 
                                                fluid_shell.H_LV() )
        dict_F_NB = {}
        dict_Lin_2023_['F_NB'] = 1
        
        T_ho = - Q_1 / C_h + T_hi
        # LMTD_ = LMTD(T_hi, T_ho, T_ci, T_co)
        LMTD_ = T_hi - T_ci
        # LMTD_ = ( T_hi + T_ho ) / 2 - T_ci
        
        # calc thermal resistance map

        dict_o_ff = {}
        
        HTC_o = small
        HTC_o_ff = small  
        
        HTC_i = HT_correlation.h_Ginielinski(Re_water, fluid_tube.PR(), D_i, fluid_tube.TCX())
                
        R_i = 1 / ( HTC_i * A_i )
        R_o = 1 / ( HTC_o * A_o )
        R_o_ff = 1 / ( HTC_o_ff * A_o )
        R_wall = R_cylinder(D_i / 2, D_o / 2, TCX_wall, L)
        R_total = R_o_ff + R_wall + R_i
        
        # UA_2 =  1 / ( R_i + R_o + R_wall)
        UA_2 =  1 / ( R_i + R_o_ff + R_wall)
        
        Q_2 = UA_2 * LMTD_
        
        res_UA = abs( UA_2 - UA_1 ) / UA_2
        res_Q = abs( Q_2 - Q_1 ) / Q_2
        # res = res_UA + res_Q
        res = res_UA
        
        mdot_o_ref = mdot_LIQ - Q_1 / fluid_shell.H_LV()
        
        dict_DN['Bo_ff'] = dict_Lin_2023_['Bo_ff']
        
        dict_export = {
            'epsilon':epsilon,
            'NTU':NTU,
            'Q_max':Q_max,
            'LMTD':LMTD_,
            'heatFlux':heatFlux,
            
            'T_ho':T_ho,
            'mdot_o_ref':mdot_o_ref,
            
            'HTC_i':HTC_i,
            'HTC_o':HTC_o,
            'HTC_o_ff':HTC_o_ff,
            
            'R_i':R_i,
            'R_wall':R_wall,
            'R_o':R_o,
            'R_o_ff':R_o_ff,
            'R_total':R_total,
            
            'Q_1':Q_1,
            'Q_2':Q_2,
            
            'UA_1':UA_1,
            'UA_2':UA_2,
            
            "massflux_water":massflux_water,
            "Re_water":Re_water,
            "C_h":C_h,
            
            'res_UA':res_UA,
            'res_Q':res_Q,
            'res':res,
            'dict_Lin_2023_':dict_Lin_2023_,
            'dict_o_ff':dict_o_ff,
            'dict_DN':dict_DN,
            'dict_F_NB':dict_F_NB
        }
        # if( mdot_LIQ <= 0 ):
        #     dict_export = {
        #         'epsilon':0,
        #         'NTU':0,
        #         'Q_max':Q_max,
        #         'LMTD':T_in_water - mdot_o_ref,
        #         'heatFlux':0,
                
        #         'T_ho':T_in_water,
        #         'mdot_o_ref':mdot_o_ref,
                
        #         'HTC_i':0,
        #         'HTC_o':0,
        #         'HTC_o_ff':0,
                
        #         'R_i':R_i,
        #         'R_wall':R_wall,
        #         'R_o':1e20,
        #         'R_o_ff':1e20,
        #         'R_total':1e20,
                
        #         'Q_1':0,
        #         'Q_2':0,
                
        #         'UA_1':0,
        #         'UA_2':0,
                
        #         'res_UA':0,
        #         'res_Q':0,
        #         'res':0,
        #         'dict_Lin_2023_':dict_Lin_2023_,
        #         'dict_o_ff':dict_o_ff,
        #         'dict_DN':dict_DN,
        #         'dict_F_NB':dict_F_NB
        #     }
        
        return dict_export

def Guess_SingleTube(dict_import_):
    dict_import = deepcopy(dict_import_)
    mdotLiq_in = dict_import_['Shell_side']['mdot_LIQ']['Value']
    j_LIQ = dict_import_['Shell_side']['j_LIQ']['Value']
    # print("mdotLiq_in = ", mdotLiq_in)
    if( mdotLiq_in > 0 and j_LIQ > 0 ):
        epsilon_initial_guess = 0.9
        epsilon = epsilon_initial_guess
        tubeUnit = SingleTubeUnit(dict_import, epsilon)
        result = optimize.minimize_scalar(tubeUnit.Iter_epsilonNTU, bounds = (1e-10, 1), method = 'bounded')
        epsilon = result.x
        dict_export = tubeUnit.Guess_epsilonNTU(epsilon)
        
        # check if fully dryout
        Bo = dict_export['dict_Lin_2023_']['Bo_ff']
            
        if( Bo > 1 ):
            print("Bo>1")
            Q_max = dict_export['Q_max']
            Q_evap_max = mdotLiq_in * dict_export['dict_Lin_2023_']['H_LV']
            epsilon_new = Q_evap_max / Q_max
            dict_export = tubeUnit.Guess_epsilonNTU(epsilon_new)
    else:
        epsilon_initial_guess = 0.9
        epsilon = epsilon_initial_guess
        tubeUnit = SingleTubeUnit(dict_import, epsilon)
        dict_export = tubeUnit.Guess_epsilonNTU_zeroMdot()
        pass
    return dict_export
         
def unittest_singleTube():
    # dict_import = {
    #     "Geometry":{
    #         "Tube":{
    #             "Length":{'Value': 1, 'Unit':"m"},
    #             "Diameter":{'Value': 19E-3, 'Unit':"m"},
                
    #             "N_tube_Verti":{'Value': 5, 'Unit':""},
    #             "N_tube_Hori":{'Value': 5, 'Unit':""},
                
    #             "Pitch_Verti":{'Value': 50E-3, 'Unit':"m"},
    #             "Pitch_Hori":{'Value': 50E-3, 'Unit':"m"},
                
    #             'Tube_Type':'GEWA-B',
    #             "Tube_Thickness":{'Value': 1E-3, 'Unit':"m"},
    #             "TCX":{'Value': 400, 'Unit':"W/m-K"},
    #             "Top_Distance":{'Value': 10E-3, 'Unit':"m"},
    #             "Bundle_Type":"Staggered"
    #         },
    #         "Chamber":{
    #             "Length":{'Value': 1, 'Unit':"m"},
    #             "Diameter":{'Value': 1, 'Unit':"m"},
    #         },
    #         "Pass":{
    #             "Pass_Type":"Type_1",
    # #             # Type_1: single pass
    # #             # Type_2: side to side
    # #             # Type_3: top to bottom
    # #             # Type_4: bottom to top
    #             "Split_Verti":[1],
    #             "Split_Hori":[1],
    #             # "Priority":[[0,1],[3,2]],
    #             # "Priority":[[0]]
    #         },
    #         "Vapor_exhauster":{
    #             "Type":"Top"
    #         }
    #     },
    #     "BoundaryCondition":{
    #         "Shell_Side_Liquid":{
    #             "Fluid":"R134a",
    #             "Mdot":{'Value': 10, 'Unit':"kg/s"},
    #             "State_1":{'Value': 280, 'Unit':"K"},
    #             "State_2":{'Value': 0, 'Unit':"-"},
    #             "Distribution":"Uniform",
    #             "Liquid_Level":{'Value': 0, 'Unit':"m"},
    #         },
    #         "Shell_side_vapor":{
    #             "Fluid":"R134a",
    #             "Mdot":{'Value': 0, 'Unit':"kg/s"},
    #             "State_1":{'Value': 280, 'Unit':"K"},
    #             "State_2":{'Value': 1, 'Unit':"-"},
    #             "Distribution":"Uniform",
    #             "Direction":"Counter_current"
    #         },
    #         "tube_side_liquid":{
    #             "Fluid":"Water",
    #             "Mdot":{'Value': 1, 'Unit':"kg/s"},
    #             "State_1":{'Value': 300, 'Unit':"K"},
    #             "State_2":{'Value': 101325, 'Unit':"Pa"},
    #             "Distribution":"Uniform"
    #         },
    #     },
    #     "Numerical":{
    #         "N_length":1
    #     },
    #     "Array":{
    #     }
    # }
    # # convert dict_import to dict_import_
    # dict_import_  = {
    #     "Tube":{
    #         "Length":dict_import['Geometry']['Tube']['Length'],
    #         "Diameter":dict_import['Geometry']['Tube']['Diameter'],
    #         "D2":{'Value': 0.1E-3, 'Unit':"m"},
    #         "Thickness":dict_import['Geometry']['Tube']['Tube_Thickness'],
    #         "TCX":dict_import['Geometry']['Tube']['TCX'],
    #         "Tube_Type":dict_import['Geometry']['Tube']['Tube_Type'],
    #         "N_tube_Verti":dict_import['Geometry']['Tube']['N_tube_Verti']  
    #     },
    #     "Tube_side":{
    #         "Fluid": dict_import['BoundaryCondition']['tube_side_liquid']['Fluid'],
    #         "mdot":dict_import['BoundaryCondition']['tube_side_liquid']['Mdot'],
    #         "T_in":dict_import['BoundaryCondition']['tube_side_liquid']['State_1'],
    #         "P_in":dict_import['BoundaryCondition']['tube_side_liquid']['State_2']
    #     },
    #     "Shell_side":{
    #         "Fluid": dict_import['BoundaryCondition']['Shell_Side_Liquid']['Fluid'],
    #         "mdot_LIQ":dict_import['BoundaryCondition']['Shell_Side_Liquid']['Mdot'],
    #         "j_LIQ":{'Value': 1E-4, 'Unit':"kg/s"},
    #         "j_VAP":{'Value': 1E-4, 'Unit':"kg/s"},
    #         "T_in":dict_import['BoundaryCondition']['Shell_Side_Liquid']['State_1'],
    #     }
    # }
    
    dict_import_ = ImportJson("../Temp/CalcSingleTube/SingleTube_setting.json")
    dict_exprot = Guess_SingleTube(dict_import_)
    dict_exprot['citation'] = str(limitation.citation())
    dict_import_['citation'] = str(limitation.citation())
    ExportJson('../Temp/CalcSingleTube/SingleTube_result.json',dict_exprot)
    # ExportJson('../Temp/CalcSingleTube/SingleTube_setting.json',dict_import_)


# unittest_singleTube()

