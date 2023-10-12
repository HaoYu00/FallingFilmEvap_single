# calculate dimensionless numbewr
import math

def Re_ff( gamma, VISLIQ ):
    Re_ = 4 * gamma / VISLIQ
    return Re_

def Re_vapor( gamma, VISLIQ ):
    Re_ = gamma / VISLIQ
    return Re_

def Re( Velocity, D, DEN, VISLIQ ):
    Re_ = Velocity * D * DEN / VISLIQ
    return Re_

def alpha( TCXLIQ, DENLIQ, CPLIQ ):
    alpha_ = TCXLIQ / ( DENLIQ * CPLIQ )
    return alpha_

def Gamma_ff( Re_ff, VISLIQ ):
    # mass flow rate per unit length on single side
    gamma_ = VISLIQ * Re_ff / 4
    return gamma_

def Gamma_evaperated_bounded( Gamma, heatFlux, D, H_LV, N_tube ):
    Area = 0.5 * math.pi * D * N_tube
    Gamma_evaperated_ = heatFlux * Area / H_LV
    Gamma_evaperated_ = max( Gamma_evaperated_, Gamma )
    return Gamma_evaperated_

def Gamma_evaperated( heatFlux, D, H_LV, N_tube ):
    Area = 0.5 * math.pi * D * N_tube
    Gamma_evaperated_ = heatFlux * Area / H_LV
    return Gamma_evaperated_

def Bo( Gamma, heatFlux, D, H_LV ):
    Area = 0.5 * math.pi * D
    Bo = heatFlux * Area / ( Gamma * H_LV  + 1E-20 )
    return Bo

def Ga( VISLIQ, DENLIQ, D, gravity ):
    # Galileo number
    Ga_ = gravity * ( D ** 3 ) * ( VISLIQ / DENLIQ ) ** -2

    return Ga_

def Ka( DENLIQ, DENVAP, VISLIQ, STLLIQ, gravity ):
    # Kapitza Number, a ratio of surface tension to viscous force
    Ka_  = VISLIQ ** 4 *gravity\
        / ( ( DENLIQ - DENVAP ) * STLLIQ ** 3 )
    return Ka_

def Ar( DENLIQ, STLLIQ, gravity ):
    # Archimedes number
    Ar_ = ( gravity / DENLIQ ** 2 ) * ( STLLIQ / ( gravity * DENLIQ ) ) ** ( 3 / 2 )
    return Ar_

def Merit( DENLIQ, STLLIQ,  H_LV, VISLIQ ):
    Merit_ = ( DENLIQ * STLLIQ * H_LV ) / VISLIQ
    return Merit_

def Gr( DEN,VIS,Beta,gravity,T_wall,T_surr,D ):
    # Grashof number
    nu = VIS / DEN
    Gr_ = gravity * Beta * ( T_wall - T_surr ) * ( D ** 3 ) / nu
    return Gr_

def Ra(Gr_,Pr_):
    # Raylegih number
    Ra_ = Gr_ * Pr_
    return Ra_

def We(Gamma, D, DENLIQ, STLLIQ):
    # Weber number
    massFlux = Gamma / (math.pi * D )
    We_ = math.pow(massFlux , 2) * D / DENLIQ / STLLIQ
    return We_

def We_j(j, D_min, DEN, STLLIQ):
    # Weber number refered to superficial velocity (j)
    if( j > 0 ):
        We_ = DEN * j ** 2 * D_min / STLLIQ
    else:
        We_ = 0
    return We_

def We_Chein(Gamma, D, DENLIQ, STLLIQ):
    # Weber number
    We_ = 4 * Gamma ** 2\
        / ( math.pi ** 2\
          * D * DENLIQ * STLLIQ )
    return We_

def Ja(DENLIQ, DENVAP, CPLIQ, H_LV, T_wall, T_sat):
    # Jacob number
    Ja_ = DENLIQ * CPLIQ * ( T_wall - T_sat ) / ( DENVAP * H_LV )
    return Ja_

def Pi_Thome_2012(  heatFlux,
                    D,
                    DENLIQ,
                    DENVAP,
                    H_LV,
                    VISLIQ):
    
    Pi_Thome_2012_ = heatFlux ** 2\
                    * D * ( DENLIQ - DENVAP )\
                    / ( H_LV ** ( 5 / 2 ) * VISLIQ )
    return Pi_Thome_2012_

def Fr( U_air, D_tube, DENLIQ, DENVAP, gravity ):
    # Froud number
    if( U_air > 0 ):
        Fr_ = U_air ** 2 / ( D_tube * gravity * ( 1 - DENVAP / DENLIQ ) )
    else:
        Fr_ = 0

    return Fr_


def Nu_cv(Re_ff, PRLIQ):
    Nu_cv = 0.0386\
            * Re_ff ** 0.09\
            * PRLIQ ** 0.986
    return Nu_cv