import math
from copy import deepcopy

import GetProperties
from DataIO import ImportJson, ExportJson

def h_Dittos(Re, Prandtl, D, TCX):
    
    Nu_ = 0
    if(Re <= 2300):
        Nu_=3.66
    else:
        Nu_ = 0.23\
            * Re ** 0.8\
            * Prandtl ** 0.4
    HTC_ = Nu_ * TCX / D
    
    return HTC_

def h_Ginielinski(Re, Prandtl, D, TCX):
    
    Nu_ = 0
    if(Re <= 2300):
        Nu_ = 3.66
    else:
        f = ( 1.58 * math.log( Re ) - 3.28 ) ** -2
        Nu_ = ( f / 2 ) * ( Re - 1000 ) * Prandtl\
            / ( 1.07 + 12.7 * ( f / 2 ) ** 0.5 * ( Prandtl ** ( 2 / 3 ) - 1 ) )
    HTC_ = Nu_ * TCX / D
    
    return HTC_

def h_pb_Cooper(heatFlux, P_reducing, MOLEMASS):
    
    Roughness = 100e-6

    # Cooper correlation
    # Cooper, M. G., "Heat Flow Rates in Saturated Nucleate Pool Boiling-
    # A Wide-Ranging Examination Using Reduced Properties", 1984, Advances in Heat Transfer
    # c = 537
    c = 55

    h_pb = c * heatFlux ** 0.67\
            * P_reducing ** (0.12 - 0.2*math.log10( Roughness ) )\
            * ( -math.log10( P_reducing ) ) ** -0.55\
            * MOLEMASS ** -0.5

    return h_pb



def h_Lin_2023_noDryout(dict_data):
    def D_bubble_Departure_pb(DENLIQ, DENVAP, STLLIQ, gravity):
        D_b = 0.511 * ( 2 * STLLIQ\
                      / ( gravity * ( DENLIQ - DENVAP ) ) ) **0.5
        return D_b
    def Re_dryout(heatflux, D, VISLIQ, H_LV):
        
        Re_dryout_ = 938 * ( 1 - math.exp( -0.055 * heatflux * D / (VISLIQ * H_LV) ) )
        
        return Re_dryout_

    def h_nb(heatflux, T_sat, T_critical, P_sat, P_critical, TCXLIQ, PRLIQ, DENLIQ, DENVAP, STLLIQ, gravity):
        
        factor_c = 0.855\
                 * ( DENVAP / DENLIQ ) ** 0.309\
                 * ( P_sat / P_critical) ** ( -0.437 )
        D_b = D_bubble_Departure_pb(DENLIQ, DENVAP, STLLIQ, gravity)
        
        h_nb_ =  10 * ( TCXLIQ / D_b )\
                * ( ( heatflux * D_b ) / ( TCXLIQ * T_sat ) ) ** factor_c\
                * ( P_sat / P_critical ) ** 0.1\
                * ( 1 - T_sat / T_critical ) ** ( - 1.4 )\
                * PRLIQ ** ( -0.25 )

        return h_nb_

    def h_cv_laminar(Re, Ka, TCXLIQ, DENLIQ, VISLIQ, STLLIQ, gravity):
        nu = VISLIQ / DENLIQ

        h_cv_ = 2.65\
                * Re ** ( -0.16 )\
                * Ka ** ( 0.057 )\
                * TCXLIQ * ( nu ** 2 / gravity ) ** ( - 1/3 )
        return h_cv_

    def h_cv_turbulent(Re, TCXLIQ, PRLIQ, DENLIQ, VISLIQ, STLLIQ, gravity):
        nu = VISLIQ / DENLIQ

        h_cv_ = 0.03\
                * Re ** ( 0.2 )\
                * PRLIQ ** ( 0.7 )\
                * TCXLIQ * ( nu ** 2 / gravity ) ** ( - 1/3 )
        return h_cv_
    
    HTC_nb = h_nb(  dict_data['heatFlux'], 
                    dict_data['T_sat'], 
                    dict_data['T_critical'], 
                    dict_data['P_sat'], 
                    dict_data['P_critical'], 
                    dict_data['TCXLIQ'], 
                    dict_data['PRLIQ'], 
                    dict_data['DENLIQ'], 
                    dict_data['DENVAP'], 
                    dict_data['STLLIQ'], 
                    dict_data['gravity'])
    
    HTC_cv_lam = h_cv_laminar(  dict_data['Re_ff'], 
                                dict_data['Ka_ff'], 
                                dict_data['TCXLIQ'], 
                                dict_data['DENLIQ'], 
                                dict_data['VISLIQ'], 
                                dict_data['STLLIQ'], 
                                dict_data['gravity'])

    HTC_cv_tur = h_cv_turbulent(dict_data['Re_ff'], 
                                dict_data['TCXLIQ'], 
                                dict_data['PRLIQ'], 
                                dict_data['DENLIQ'], 
                                dict_data['VISLIQ'], 
                                dict_data['STLLIQ'], 
                                dict_data['gravity'])
    
    Re_dryout_ = Re_dryout( dict_data['heatFlux'],
                            dict_data['D'],
                            dict_data['VISLIQ'],
                            dict_data['H_LV'])

    F_NB = dict_data['F_NB']
    HTC_nb *= F_NB

    Nu_nb = HTC_nb / ( dict_data['D'] / dict_data['TCXLIQ'] )

    HTC_cv = ( HTC_cv_lam ** 5 + HTC_cv_tur ** 5 ) ** ( 1 / 5 )
    
    if( dict_data['Tube_Type'] == 'Low-Fin' ):
        
        HTC_o = HTC_cv
        
        # Prof. Wang's textbook, p.78 - circular fin
        Fin_Height = dict_data['Fin_Height']
        Fin_Pitch = dict_data['Fin_Pitch']
        D_tube = dict_data['D'] 
        D_fin = dict_data['D'] + 2 * Fin_Height
        thickness_fin = 0.5 * Fin_Pitch
        TCX_fin = 400.0
        
        A_fin_side = 2 * 0.25 * math.pi * ( D_fin ** 2 - D_tube ** 2 )
        A_total = A_fin_side + Fin_Pitch * ( math.pi * ( D_tube + D_fin ) / 2 )
        A_tube = Fin_Pitch * ( math.pi * D_tube )
        
        fin_m = ( 2 * HTC_o / ( TCX_fin * thickness_fin ) ) ** 0.5
        fin_le = Fin_Height + 0.5 * thickness_fin
        fin_r_ = D_fin / D_tube
        fin_b = 1
        if( fin_r_ > 2 ):
            fin_b = 0.9706 + 0.17125 * math.log( fin_r_ )
        else:
            fin_b = 0.9107 + 0.0893 * fin_r_
        fin_n = math.exp( 0.13 * fin_m * fin_le - 1.3863 )
        fin_a = fin_r_ ** ( -0.246 )
        fin_phi = fin_m * fin_le * fin_r_ ** fin_n
        
        eta_f = 1
        if( fin_phi > 0.6 + 2.257 * fin_r_ ** -0.445 ):
            eta_f = fin_a * ( fin_m * fin_le ) ** fin_b
        else:
            eta_f = math.tanh(fin_phi) / fin_phi
        
        F_cv = eta_f * A_total / A_tube
        HTC_cv *= F_cv
        
    
    Nu_cv = HTC_cv / ( dict_data['D'] / dict_data['TCXLIQ'] )

    aa = [-3.97351771, #0
        -0.22364944,   #1
        -3.97690136,   #2
        -2.80453982,    #3
        0.02447119,     #4
        -3.17001108]    #5
    
    bb = [1.19346312,  #0
        -0.36959395,   #1
        -1.06048942,   #2
        -0.35933778,    #3
        -0.2082303,     #4
        0.14801294]     #5
        
    F_downwardVapor_nb = 0
    F_downwardVapor_cv = 0
    
    F_downwardVapor_nb2 = 0
    F_downwardVapor_cv2 = 0
    
    if( dict_data['We_VAP_imposed'] > 0 ):

        F_downwardVapor_nb = aa[0] + ( aa[1] * math.log(dict_data['We_VAP_imposed']) - aa[2] ) / ( 1 + math.exp( - ( aa[1] * math.log(dict_data['We_VAP_imposed']) - aa[2] ) ) )
        F_downwardVapor_cv =  bb[0] + ( bb[1] * math.log(dict_data['We_VAP_imposed']) - bb[2] ) / ( 1 + math.exp( - ( bb[1] * math.log(dict_data['We_VAP_imposed']) - bb[2] ) ) )
        
        F_downwardVapor_nb2 = aa[3] + ( aa[4] * math.log(dict_data['We_VAP_imposed']) - aa[5] ) / ( 1 + math.exp( - ( aa[4] * math.log(dict_data['We_VAP_imposed']) - aa[5] ) ) )
        F_downwardVapor_cv2 =  bb[3] + ( bb[4] * math.log(dict_data['We_VAP_imposed']) - bb[5] ) / ( 1 + math.exp( - ( bb[4] * math.log(dict_data['We_VAP_imposed']) - bb[5] ) ) )
    

    a = [-0.03435267,  #0
        5.05548408,    #1
        4.95952787,    #2
        1.62473816,    #3
        0.8795923,     #4
        -0.17506631,   #5
        -0.76713439,   #6
        0.23314937,    #7
        -0.50524289,   #8
        -1.91632406,   #9
        -0.09453801,   #10
        0.63414529,
        0.76406263,
        0.62643503,
        0.58090242,
        0.52191563,
        0.56215667]
    b = [0.09785411, #0
        -2.86910674, #1
        0.42673679,  #2
        0.26252733,  #3
        2.15732293,  #4
        3.64350929,  #5
        -0.00908086, #6
        8.51322012,  #7
        -0.4959429,  #8
        -1.85618559, #9
        0.92998663,  #10
        -0.43733525,
        -0.21875559,
        -0.19123504,
        -0.16443344,
        -0.15247846,
        -0.09770357]

    E_mist_nb = math.exp( a[0] * dict_data['N_HT_Tube_vertical'] * math.tanh( a[1] * (math.log(dict_data['We_LIQ'])-a[2]) )\
                                + a[3] * math.tanh( a[4] * math.log(dict_data['Bo_ff'])-F_downwardVapor_nb + a[5])\
                                * math.tanh( a[7] * math.log(dict_data['We_VAP_evaperated'])-F_downwardVapor_nb2 + a[8])\
                                + ( a[9] * dict_data['T_reducing'] + a[10]))
                      
    E_mist_cv = math.exp( b[0] * dict_data['N_HT_Tube_vertical'] * math.tanh( b[1] * (math.log(dict_data['We_LIQ']) - b[2]) )\
                                + b[3] * math.tanh( b[4] * math.log(dict_data['Bo_ff'])-F_downwardVapor_cv + b[5])\
                                * math.tanh( b[7] * math.log(dict_data['We_VAP_evaperated'])-F_downwardVapor_cv2 + b[8])\
                                + ( b[9] * dict_data['T_reducing'] + b[10]))

    Nu_nb_bundle = Nu_nb *E_mist_nb
    Nu_cv_bundle = Nu_cv * E_mist_cv
    
    Nu_ = 0
    E_mist = 0
    if( Nu_nb >= Nu_cv ):
        Nu_ = Nu_nb_bundle
        E_mist = E_mist_nb
    else:
        Nu_ = Nu_cv_bundle
        E_mist = E_mist_cv
        
    HTC_ = ( Nu_ ) * ( dict_data['D'] / dict_data['TCXLIQ'] )
    HTC_nb_bundle = ( Nu_nb_bundle ) * ( dict_data['D'] / dict_data['TCXLIQ'] )
    HTC_cv_bundle = ( Nu_cv_bundle ) * ( dict_data['D'] / dict_data['TCXLIQ'] )

    HTC_ratio = HTC_ / HTC_nb

    # HTC_cv = Nu_cv * ( dict_data['D'] / dict_data['TCXLIQ'] )
    # HTC_wetting = max( HTC_nb, HTC_cv )
    
    dict_out = {
                'HTC':HTC_,
                'HTC_nb_bundle':HTC_nb_bundle,
                'HTC_cv_bundle':HTC_cv_bundle,
                
                'HTC_ratio':HTC_ratio,
                
                'Nu_nb':Nu_nb,
                'Nu_cv':Nu_cv,
                'HTC_cv':HTC_cv,
                
                'HTC_PB_2023_ENHANCED':HTC_nb,
                
                'E_mist':E_mist,
                'E_mist_nb':E_mist_nb,
                'E_mist_cv':E_mist_cv,
                
                'Nu_':Nu_,
                'Nu_nb_bundle':Nu_nb_bundle,
                'Nu_cv_bundle':Nu_cv_bundle,
                
                'F_NB':F_NB
                }
    
    return dict_out

def h_Lin_2023(dict_data_):
    dict_data = deepcopy(dict_data_)
    dict_out = h_Lin_2023_noDryout(dict_data)
    # if( dict_data['We_LIQ'] > 0 ):
    #     dict_out = h_Lin_2023_noDryout(dict_data)
    # else:
    #     dict_out = {
    #                 'HTC':0,
    #                 'HTC_nb_bundle':0,
    #                 'HTC_cv_bundle':0,
                    
    #                 'HTC_ratio':0,
                    
    #                 'Nu_nb':0,
    #                 'Nu_cv':0,
    #                 'HTC_cv':0,
                    
    #                 'HTC_PB_2023_ENHANCED':0,
                    
    #                 'E_mist':0,
    #                 'E_mist_nb':0,
    #                 'E_mist_cv':0,
                    
    #                 'Nu_':0,
    #                 'Nu_nb_bundle':0,
    #                 'Nu_cv_bundle':0,
                    
    #                 'F_NB':0
    #                 }  
    return dict_out

def Calc_F_NB(dict_data):
    def D_bubble_Departure_pb(DENLIQ, DENVAP, STLLIQ, gravity):
        D_b = 0.511 * ( 2 * STLLIQ\
                      / ( gravity * ( DENLIQ - DENVAP ) ) ) **0.5
        return D_b

    def h_nb(heatflux, T_sat, T_critical, P_sat, P_critical, TCXLIQ, PRLIQ, DENLIQ, DENVAP, STLLIQ, gravity):
        
        # [1] Jung, D., Kim, Y., Ko, Y., and Song, K., 2003, 
        # "Nucleate boiling heat transfer coefficients of pure halogenated refrigerants," 
        # International Journal of Refrigeration, 26(2), pp. 240-248.
        
        factor_c = 0.855\
                 * ( DENVAP / DENLIQ ) ** 0.309\
                 * ( P_sat / P_critical) ** ( -0.437 )
        D_b = D_bubble_Departure_pb(DENLIQ, DENVAP, STLLIQ, gravity)
        
        h_nb_ =  10 * ( TCXLIQ / D_b )\
                * ( ( heatflux * D_b ) / ( TCXLIQ * T_sat ) ) ** factor_c\
                * ( P_sat / P_critical ) ** 0.1\
                * ( 1 - T_sat / T_critical ) ** ( - 1.4 )\
                * PRLIQ ** ( -0.25 )

        return h_nb_
    
    D_bubble = D_bubble_Departure_pb(dict_data['DENLIQ'], 
                                dict_data['DENVAP'], 
                                dict_data['STLLIQ'], 
                                dict_data['gravity'])
    
    HTC_nb_plain = h_nb(  dict_data['heatFlux'], 
                    dict_data['T_sat'], 
                    dict_data['T_critical'], 
                    dict_data['P_sat'], 
                    dict_data['P_critical'], 
                    dict_data['TCXLIQ'], 
                    dict_data['PRLIQ'], 
                    dict_data['DENLIQ'], 
                    dict_data['DENVAP'], 
                    dict_data['STLLIQ'], 
                    dict_data['gravity'])


    # [3] Roques, J. F., and Thome, J. R., 2007, 
    # "Falling Films on Arrays of Horizontal Tubes with R-134a, 
    # Part I: Boiling Heat Transfer Results for Four Types of Tubes," 
    # Heat Transfer Engineering, 28(5), pp. 398-414.
    HTC_nb_enhanced = HTC_nb_plain
    HTC_nb_plain_Thome_2007 = HTC_nb_plain
    F_NB = 1
    eta = 1
    
    HTC_nb_plain_Thome_2007 = 171 * dict_data['heatFlux'] ** 0.376
    F_NB_plain_Thome = HTC_nb_plain_Thome_2007 / HTC_nb_plain
    if( dict_data['Tube_Type'] == 'Low-Fin' ):
        
        HTC_o = HTC_nb_plain
        
        # Prof. Wang's textbook, p.78 - circular fin
        Fin_Height = dict_data['Fin_Height']
        Fin_Pitch = dict_data['Fin_Pitch']
        D_tube = dict_data['D'] 
        D_fin = dict_data['D'] + 2 * Fin_Height
        thickness_fin = 0.5 * Fin_Pitch
        TCX_fin = 400.0
        
        A_fin_side = 2 * 0.25 * math.pi * ( D_fin ** 2 - D_tube ** 2 )
        A_total = A_fin_side + Fin_Pitch * ( math.pi * ( D_tube + D_fin ) / 2 )
        A_tube = Fin_Pitch * ( math.pi * D_tube )
        
        fin_m = ( 2 * HTC_o / ( TCX_fin * thickness_fin ) ) ** 0.5
        fin_le = Fin_Height + 0.5 * thickness_fin
        fin_r_ = D_fin / D_tube
        fin_b = 1
        if( fin_r_ > 2 ):
            fin_b = 0.9706 + 0.17125 * math.log( fin_r_ )
        else:
            fin_b = 0.9107 + 0.0893 * fin_r_
        fin_n = math.exp( 0.13 * fin_m * fin_le - 1.3863 )
        fin_a = fin_r_ ** ( -0.246 )
        fin_phi = fin_m * fin_le * fin_r_ ** fin_n
        
        eta_f = 1
        if( fin_phi > 0.6 + 2.257 * fin_r_ ** -0.445 ):
            eta_f = fin_a * ( fin_m * fin_le ) ** fin_b
        else:
            eta_f = math.tanh(fin_phi) / fin_phi
        
        F_NB = eta_f * A_total / A_tube
        # F_NB = 1
        HTC_nb_enhanced *= F_NB
        
    elif( dict_data['Tube_Type'] == 'Turbo-BII-HP' ):
        
        # HTC_nb_plain_Thome_2007 = 171 * dict_data['heatFlux'] ** 0.376
        HTC_GEWA_BII_HP = ( 2.17E6 ) * dict_data['heatFlux'] ** -0.432
        # F_NB = HTC_GEWA_BII_HP / HTC_nb_plain_Thome_2007
        F_NB = HTC_GEWA_BII_HP / HTC_nb_plain
        HTC_nb_enhanced = HTC_GEWA_BII_HP
        
    elif( dict_data['Tube_Type'] == 'GEWA-B' ):
        
        # HTC_nb_plain_Thome_2007 = 171 * dict_data['heatFlux'] ** 0.376
        HTC_GEWA_B = ( 3.06E4 ) * dict_data['heatFlux'] ** -0.042
        # F_NB = HTC_GEWA_B / HTC_nb_plain_Thome_2007
        F_NB = HTC_GEWA_B / HTC_nb_plain
        HTC_nb_enhanced = HTC_GEWA_B

    elif( dict_data['Tube_Type'] == 'High-Flux' ):
        
        # HTC_nb_plain_Thome_2007 = 171 * dict_data['heatFlux'] ** 0.376
        HTC_High_Flux = ( 3.92E7 ) * dict_data['heatFlux'] ** -0.623
        # F_NB = HTC_High_Flux / HTC_nb_plain_Thome_2007
        F_NB = HTC_High_Flux / HTC_nb_plain
        HTC_nb_enhanced = HTC_High_Flux
    else:
        pass

    Nu_nb_plain_Thome_2007 = HTC_nb_plain_Thome_2007 / ( dict_data['D'] / dict_data['TCXLIQ'] )
    Nu_nb_plain = HTC_nb_plain / ( dict_data['D'] / dict_data['TCXLIQ'] )
    Nu_nb_enhanced = HTC_nb_enhanced / ( dict_data['D'] / dict_data['TCXLIQ'] )
    
    # if((dict_data['Reference_ID'] == 'D6' or
    #    dict_data['Reference_ID'] == 'D7' or
    #    dict_data['Reference_ID'] == 'D8')and
    #    (dict_data['Tube_Type'] == 'Smooth')):
    #     Nu_nb_enhanced = Nu_nb_plain_Thome_2007
    #     HTC_nb_enhanced = HTC_nb_plain_Thome_2007
    #     F_NB = F_NB_plain_Thome
    
    dict_out = {
                # 'Nu_nb_plain_Thome_2007':Nu_nb_plain_Thome_2007,
                'Nu_nb_plain':Nu_nb_plain,
                'Nu_nb_enhanced':Nu_nb_enhanced,
                
                # 'HTC_nb_plain_Thome_2007':HTC_nb_plain_Thome_2007,
                'HTC_nb_plain':HTC_nb_plain,
                'HTC_nb_enhanced':HTC_nb_enhanced,
                
                'F_NB':F_NB,
                # 'F_NB_plain_Thome':F_NB_plain_Thome,
                
                # 'D_bubble':D_bubble
                }
    
    return dict_out


def unittest():
    fluType_shell = 'R134a'
    T_sat_ref = 280
    D_o = 19.05E-3
    
    fluid_shell = GetProperties.Fluid_Sat(fluType_shell,T_sat_ref)

    dict_Lin_2023_ = { 'heatFlux':30E3,
                        'T_critical':fluid_shell.T_critical(),
                        'T_reducing':fluid_shell.T_reducing(),
                        'P_critical':fluid_shell.P_critical(),
                        'T_sat':T_sat_ref,
                        'P_sat':fluid_shell.P_sat(),
                        
                        "Re_ff": 1637.0483423306646,
                        "gamma_ff": 0.09999999999999999,
                        "Bo_ff": 0.01,
                        "Ka_ff": 2.4274746156629958e-11,
                        "We_LIQ": 1,
                        "We_VAP": 1E-2,
                        
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
                        
                        'N_HT_Tube_vertical': 10,
                        
                        'We_VAP_imposed':0,
                        'We_VAP_evaperated':1E-2,
                        
                        'Tube_Type':'GEWA-B',
                        'Fin_Height':0,
                        'Fin_Pitch':0,
                        
                        'F_NB':1
                        }
    
    # dict_out_Lin_2023 = h_Lin_2023(dict_Lin_2023_)
    # ExportJson('../Temp/FF_Lin_2023.json',dict_out_Lin_2023)
    DICT_F_NB = Calc_F_NB(dict_Lin_2023_)
    print('DICT_F_NB = ', DICT_F_NB)



# unittest()