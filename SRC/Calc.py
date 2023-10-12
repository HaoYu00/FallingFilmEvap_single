import math
import os
import pandas as pd
import numpy as np

import ConvertUnit
import GetProperties

def Calc_ConvertUnit_1(df):
    
    # Convert items:
    # 1. flowrate: LPM -> kg/m-s
    # 2. temperature: C -> K
    # 3. pressure: Bar(gage) -> Pa (abs)
    # 4. power: kW -> W
    
    len_df = df.shape[0]

    # 1. flowrate: LPM -> kg/m-s
    df['Flowrate_HotWater(m3/s)'] = 0
    df['Flowrate_ColdWater(m3/s)'] = 0

    for i in range(0,len_df):
        df.loc[i,'Flowrate_HotWater(m3/s)'] = ConvertUnit.Uint_LPM2m3pSec(df.loc[i,'CoolingWaterFlowrate(LPM)'])
        df.loc[i,'Flowrate_ColdWater(m3/s)'] = ConvertUnit.Uint_LPM2m3pSec(df.loc[i,'ChilledWaterFlowrate(LPM)'])
    
    # 2. temperature: C -> K
    df['InletTemp_ChilledWater(K)'] = 0
    df['OutletTemp_ChilledWater(K)'] = 0
    df['InletTemp_CoolingWater(K)'] = 0
    df['OutletTemp_CoolingWater(K)'] = 0
    df['EvaporationTemp(K)'] = 0
    df['CondensingTemp(K)'] = 0
    df['DischargeTemp(K)'] = 0

    for i in range(0,len_df):
        df.loc[i,'InletTemp_ChilledWater(K)'] = ConvertUnit.Uint_C2K(df.loc[i,'InletTemp_ChilledWater(C)'])
        df.loc[i,'OutletTemp_ChilledWater(K)'] = ConvertUnit.Uint_C2K(df.loc[i,'OutletTemp_ChilledWater(C)'])
        df.loc[i,'InletTemp_CoolingWater(K)'] = ConvertUnit.Uint_C2K(df.loc[i,'InletTemp_CoolingWater(C)'])
        df.loc[i,'OutletTemp_CoolingWater(K)'] = ConvertUnit.Uint_C2K(df.loc[i,'OutletTemp_CoolingWater(C)'])
        df.loc[i,'EvaporationTemp(K)'] = ConvertUnit.Uint_C2K(df.loc[i,'EvaporationTemp(C)'])
        df.loc[i,'CondensingTemp(K)'] = ConvertUnit.Uint_C2K(df.loc[i,'CondensingTemp(C)'])
        df.loc[i,'DischargeTemp(K)'] = ConvertUnit.Uint_C2K(df.loc[i,'DischargeTemp(C)'])
    
    # 3. pressure: Bar(gage) -> Pa (abs)   
    df['SuctionPressure(Pa,abs)'] = 0
    df['DischargePressure(Pa,abs)'] = 0
    df['EvaporationPressure(Pa,abs)'] = 0
    df['CondensingPressure(Pa,abs)'] = 0    

    for i in range(0,len_df):
        df.loc[i,'SuctionPressure(Pa,abs)'] = ConvertUnit.Uint_Gage_Pa2Abs_Pa(ConvertUnit.Uint_Bar2Pa(df.loc[i,'SuctionPressure(bar,gage)']))
        df.loc[i,'DischargePressure(Pa,abs)'] = ConvertUnit.Uint_Gage_Pa2Abs_Pa(ConvertUnit.Uint_Bar2Pa(df.loc[i,'DischargePressure(bar,gage)']))
        df.loc[i,'EvaporationPressure(Pa,abs)'] = ConvertUnit.Uint_Gage_Pa2Abs_Pa(ConvertUnit.Uint_Bar2Pa(df.loc[i,'EvaporationPressure(bar,gage)']))
        df.loc[i,'CondensingPressure(Pa,abs)'] = ConvertUnit.Uint_Gage_Pa2Abs_Pa(ConvertUnit.Uint_Bar2Pa(df.loc[i,'CondensingPressure(bar,gage)']))

    # 4. power: kW -> W
    df['Capacity(W)'] = 0
    df['Power(W)'] = 0

    for i in range(0,len_df):
        df.loc[i,'Capacity(W)'] = ConvertUnit.Uint_kW2W(df.loc[i,'Capacity(kW)'])
        df.loc[i,'Power(W)'] = ConvertUnit.Uint_kW2W(df.loc[i,'Power(kW)'])

    print('Finish : Calc_DimensionlessNumber')
    return df

def Calc_ThermalCycle(df):
    
    # thermal cycle:
    # Isenthalpic expansion:    T1 -> T2
    # Isobaric evaporation:     T2 -> T3
    # Isentropic compression:   T3 -> T4
    # Isobaric condensation:    T4 -> T1
        
    df['T1_ref(K)'] = 0
    df['T2_ref(K)'] = 0
    df['T3_ref(K)'] = 0
    df['T4_ref(K)'] = 0
    
    df['Th_in_water(K)'] = 0
    df['Th_out_water(K)'] = 0
    df['Tc_in_water(K)'] = 0
    df['Tc_out_water(K)'] = 0
    
    df['T1_ref(K)'] = df['CondensingTemp(K)'].copy(deep = True)
    df['T4_ref(K)'] = df['T1_ref(K)'].copy(deep = True)
    
    df['T2_ref(K)'] = df['EvaporationTemp(K)'].copy(deep = True)
    df['T3_ref(K)'] = df['T2_ref(K)'].copy(deep = True)
    
    df['Th_in_water(K)'] = df['InletTemp_CoolingWater(K)'].copy(deep = True)
    df['Th_out_water(K)'] = df['OutletTemp_CoolingWater(K)'].copy(deep = True)
    
    df['Tc_in_water(K)'] = df['InletTemp_ChilledWater(K)'].copy(deep = True)
    df['Tc_out_water(K)'] = df['OutletTemp_ChilledWater(K)'].copy(deep = True)
    
    # df['Th_in_water(K)'] = df['InletTemp_ChilledWater(K)'].copy(deep = True)
    # df['Th_out_water(K)'] = df['OutletTemp_ChilledWater(K)'].copy(deep = True)
    
    # df['Tc_in_water(K)'] = df['InletTemp_CoolingWater(K)'].copy(deep = True)
    # df['Tc_out_water(K)'] = df['OutletTemp_CoolingWater(K)'].copy(deep = True)
    
    df['mdot_h_water(kg/s)'] = 0
    df['mdot_c_water(kg/s)'] = 0
    df['mdot_h_ref(kg/s)'] = 0
    df['mdot_c_ref(kg/s)'] = 0

    df['Q_h_water(W)'] = 0
    df['Q_c_water(W)'] = 0
    df['Q_h_ref(W)'] = 0
    df['Q_c_ref(W)'] = 0

    df['H_LV_h_ref(J/kg)'] = 0
    df['H_LV_c_ref(J/kg)'] = 0
    
    df['X_in_c_ref(J/kg)'] = 0
    df['X_in_c_ref_Isenthalpic(J/kg)'] = 0
    

    # --------------------------------------------
    # declare fluid type
    
    len_df = df.shape[0]
    df_id = 0
    for df_id in range(0, len_df):
        reftype = df.loc[ df_id, 'Fluid_shellSide' ]
        # T_sat = df.loc[ df_id, 'T1_ref(K)' ]
        T_sat = df.loc[ df_id, 'CondensingTemp(K)' ]
        ff_ref_h = GetProperties.Fluid_Sat(reftype,T_sat)
        
        reftype = df.loc[ df_id, 'Fluid_shellSide' ]
        # T_sat = df.loc[ df_id, 'T2_ref(K)' ]
        T_sat = df.loc[ df_id, 'EvaporationTemp(K)' ]
        ff_ref_c = GetProperties.Fluid_Sat(reftype,T_sat)
        
        reftype = df.loc[ df_id, 'Fluid_tubeSide' ]
        P = 101325.0
        T = ( df.loc[ df_id, 'Th_in_water(K)' ] + df.loc[ df_id, 'Th_out_water(K)' ] ) / 2
        ff_water_h = GetProperties.Fluid_NotSat(reftype, P, T)
        
        reftype = df.loc[ df_id, 'Fluid_tubeSide' ]
        P = 101325.0
        T = ( df.loc[ df_id, 'Tc_in_water(K)' ] + df.loc[ df_id, 'Tc_out_water(K)' ] ) / 2
        ff_water_c = GetProperties.Fluid_NotSat(reftype, P, T)
        
        # calcaulate water-side mass flow rate
        df.loc[ df_id, 'mdot_h_water(kg/s)'] = df.loc[ df_id, 'Flowrate_HotWater(m3/s)'] * ff_water_h.DEN()
        df.loc[ df_id, 'mdot_c_water(kg/s)'] = df.loc[ df_id, 'Flowrate_ColdWater(m3/s)'] * ff_water_c.DEN()
        # df.loc[ df_id, 'mdot_h_ref(kg/s)'] = 0
        # df.loc[ df_id, 'mdot_c_ref(kg/s)'] = 0
        
        # calcaulate water-side mass flow rate
        # df.loc[ df_id, 'Q_h_water(W)'] = df.loc[ df_id, 'mdot_h_water(kg/s)']* ff_water_h.CP()\
        #                                 * abs( df.loc[ df_id, 'Th_out_water(K)'] - df.loc[ df_id, 'Th_in_water(K)'] )
        # df.loc[ df_id, 'Q_c_water(W)'] = df.loc[ df_id, 'mdot_c_water(kg/s)']* ff_water_h.CP()\
        #                                 * abs( df.loc[ df_id, 'Tc_out_water(K)'] - df.loc[ df_id, 'Tc_in_water(K)'] )

        df.loc[ df_id, 'Q_h_water(W)'] = df.loc[ df_id, 'mdot_h_water(kg/s)']* ff_water_h.CP()\
                                        * abs( df.loc[ df_id, 'Th_out_water(K)'] - df.loc[ df_id, 'Th_in_water(K)'] )
        df.loc[ df_id, 'Q_c_water(W)'] = df.loc[ df_id, 'mdot_c_water(kg/s)']* ff_water_h.CP()\
                                        * abs( df.loc[ df_id, 'Tc_in_water(K)'] - df.loc[ df_id, 'Tc_out_water(K)'] )
        
        df.loc[ df_id,'H_LV_h_ref(J/kg)'] = ff_ref_h.H_LV()
        df.loc[ df_id,'H_LV_c_ref(J/kg)'] = ff_ref_c.H_LV()
        df.loc[ df_id, 'mdot_h_ref(kg/s)'] = df.loc[ df_id, 'Q_h_water(W)'] / df.loc[ df_id,'H_LV_h_ref(J/kg)']
        # df.loc[ df_id, 'mdot_c_ref(kg/s)'] = 0
        
        df.loc[ df_id, 'X_in_c_ref(J/kg)'] = 1 - df.loc[ df_id, 'Q_c_water(W)'] / ( df.loc[ df_id,'H_LV_c_ref(J/kg)'] * df.loc[ df_id, 'mdot_h_ref(kg/s)'] )
        df.loc[ df_id, 'X_in_c_ref_Isenthalpic(J/kg)'] = ( ff_ref_h.HLIQ() - ff_ref_c.HLIQ() ) / ff_ref_c.H_LV()
        
        refered_Xin = 'X_in_c_ref(J/kg)'
        df.loc[ df_id, 'mdot_c_ref(kg/s)'] = df.loc[ df_id, 'mdot_h_ref(kg/s)'] * (1 - df.loc[ df_id, refered_Xin] )
        
        df.loc[ df_id, 'Q_h_ref(W)'] = df.loc[ df_id, 'mdot_h_ref(kg/s)'] * df.loc[ df_id,'H_LV_h_ref(J/kg)']
        df.loc[ df_id, 'Q_c_ref(W)'] = df.loc[ df_id, 'mdot_c_ref(kg/s)'] * df.loc[ df_id,'H_LV_c_ref(J/kg)']
        
    print('Finish : Calc_ThermalCycle')
    return df
def Calc_convertSetting(df):
    df_setting = pd.DataFrame()
    
    
    print('Finish : Calc_convertSetting') 
    return df_setting


def Calc_Properties_1(df):
    len_df = df.shape[0]
    
    DENLIQ = [0.0] * len_df
    VISLIQ = [0.0] * len_df
    TCXLIQ = [0.0] * len_df
    PRLIQ = [0.0] * len_df
    CPLIQ = [0.0] * len_df

    DENVAP = [0.0] * len_df
    VISVAP = [0.0] * len_df
    TCXVAP = [0.0] * len_df
    PRVAP = [0.0] * len_df
    CPVAP = [0.0] * len_df
    
    H_LV = [0.0] * len_df
    MOLEMASS = [0.0] * len_df
    STLLIQ = [0.0] * len_df
    
    P_sat = [0.0] * len_df
    P_critical = [0.0] * len_df
    P_reducing = [0.0] * len_df
    
    T_critical = [0.0] * len_df
    T_reducing = [0.0] * len_df
    
    properties_dic = {
        'DENLIQ':DENLIQ,
        'VISLIQ':VISLIQ,
        'TCXLIQ':TCXLIQ,
        'PRLIQ':PRLIQ,
        'CPLIQ':CPLIQ,
        
        'DENVAP':DENVAP,
        'VISVAP':VISVAP,
        'TCXVAP':TCXVAP,
        'PRVAP':PRVAP,
        'CPVAP':CPVAP,
        
        'H_LV':H_LV,
        'MOLEMASS':MOLEMASS,
        'STLLIQ':STLLIQ,
        
        'P_sat':P_sat,
        'P_critical':P_critical,
        'P_reducing':P_reducing,
        
        'T_critical':T_critical,
        'T_reducing':T_reducing
    }
    
    T_sat = df['T_sat(K)']
    RefType  = df['Fluid']
    
    for i in range(0,len_df):
        if( T_sat[i] != '' and 
            RefType[i] != ''):
            Fluid = GetProperties.Fluid_Sat( RefType[i], T_sat[i] )

            DENLIQ[i] = Fluid.DENLIQ()
            VISLIQ[i] = Fluid.VLIQ()
            TCXLIQ[i] = Fluid.TCXLIQ()
            PRLIQ[i] = Fluid.PRLIQ()
            CPLIQ[i] = Fluid.CPLIQ()

            DENVAP[i] = Fluid.DENVAP()
            VISVAP[i] = Fluid.VVAP()
            TCXVAP[i] = Fluid.TCXVAP()
            PRVAP[i] = Fluid.PRVAP()
            CPVAP[i] = Fluid.CPVAP()
            
            H_LV[i] = Fluid.H_LV()
            MOLEMASS[i] = Fluid.MOLEMASS()
            STLLIQ[i] = Fluid.STLLIQ()
            
            P_sat[i] = Fluid.P_sat()
            P_critical[i] = Fluid.P_critical()
            P_reducing[i] = Fluid.P_reducing()
            
            T_critical[i] = Fluid.T_critical()
            T_reducing[i] = Fluid.T_reducing()

    for key, value in properties_dic.items():
        df[key] = value
              
    print('Finish : Calc_Properties') 
    return df


def Calc_Properties_2(df):
    len_df = df.shape[0]
    
    DENLIQ = [0.0] * len_df
    VISLIQ = [0.0] * len_df
    TCXLIQ = [0.0] * len_df
    PRLIQ = [0.0] * len_df
    CPLIQ = [0.0] * len_df

    DENVAP = [0.0] * len_df
    VISVAP = [0.0] * len_df
    TCXVAP = [0.0] * len_df
    PRVAP = [0.0] * len_df
    CPVAP = [0.0] * len_df
    
    H_LV = [0.0] * len_df
    MOLEMASS = [0.0] * len_df
    STLLIQ = [0.0] * len_df
    
    P_sat = [0.0] * len_df
    P_critical = [0.0] * len_df
    P_reducing = [0.0] * len_df
    
    T_critical = [0.0] * len_df
    T_reducing = [0.0] * len_df
    
    properties_dic = {
        'DENLIQ':DENLIQ,
        'VISLIQ':VISLIQ,
        'TCXLIQ':TCXLIQ,
        'PRLIQ':PRLIQ,
        'CPLIQ':CPLIQ,
        
        'DENVAP':DENVAP,
        'VISVAP':VISVAP,
        'TCXVAP':TCXVAP,
        'PRVAP':PRVAP,
        'CPVAP':CPVAP,
        
        'H_LV':H_LV,
        'MOLEMASS':MOLEMASS,
        'STLLIQ':STLLIQ,
        
        'P_sat':P_sat,
        'P_critical':P_critical,
        'P_reducing':P_reducing,
        
        'T_critical':T_critical,
        'T_reducing':T_reducing
    }
    
    T_sat = df['T_sat(K)']
    RefType  = df['Fluid']
    
    for i in range(0,len_df):
        if( T_sat[i] != '' and 
            RefType[i] != ''):
            Fluid = GetProperties.Fluid_Sat( RefType[i], T_sat[i] )

            DENLIQ[i] = Fluid.DENLIQ()
            VISLIQ[i] = Fluid.VLIQ()
            TCXLIQ[i] = Fluid.TCXLIQ()
            PRLIQ[i] = Fluid.PRLIQ()
            CPLIQ[i] = Fluid.CPLIQ()

            DENVAP[i] = Fluid.DENVAP()
            VISVAP[i] = Fluid.VVAP()
            TCXVAP[i] = Fluid.TCXVAP()
            PRVAP[i] = Fluid.PRVAP()
            CPVAP[i] = Fluid.CPVAP()
            
            H_LV[i] = Fluid.H_LV()
            MOLEMASS[i] = Fluid.MOLEMASS()
            STLLIQ[i] = Fluid.STLLIQ()
            
            P_sat[i] = Fluid.P_sat()
            P_critical[i] = Fluid.P_critical()
            P_reducing[i] = Fluid.P_reducing()
            
            T_critical[i] = Fluid.T_critical()
            T_reducing[i] = Fluid.T_reducing()

    for key, value in properties_dic.items():
        df[key] = value
              
    print('Finish : Calc_Properties') 
    return df