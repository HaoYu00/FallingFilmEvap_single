import math
# import unittest
from CoolProp.CoolProp import PropsSI as ps
from CoolProp.CoolProp import FluidsList

class Fluid_Sat:
    # Constructor
    def __init__(self, refType, T_sat):
        self.refType = refType
        self.T_sat = T_sat        

    #filting input value
    # @property
    # def refType(self):
    #     return self.__refType
    # @refType.setter
    # def refType(self, value):
    #     refType_list = FluidsList()
    #     if value in FluidsList():
    #         self.__refType = value
    #     else:
    #         raise ValueError("[Invalid input] available refType: " , FluidsList())

    # @property
    # def T_sat(self):
    #     return self.__T_sat
    # @T_sat.setter
    # def T_sat(self, value):
    #     if value >= self.T_min() and value <= self.T_max():
    #         self.__T_sat = value
    #     else:
    #         raise ValueError("[Invalid input] available T_sat: (T_min,T_max) = ", self.T_min(), self.T_max())

    # Method
    def DENLIQ(self):
        value = ps('D','T',self.T_sat,'Q',0,self.refType)
        name = 'Density'
        SIUnit = 'kg/m3'
        return value

    def VLIQ(self):
        value = ps('V','T',self.T_sat,'Q',0,self.refType)
        name = 'Viscosity'
        SIUnit = 'Pa-s'
        return value
        
    def HLIQ(self):
        value = ps('H','T',self.T_sat,'Q',0,self.refType)
        name = 'Enthalpy'
        SIUnit = 'J/kg'
        return value
        
    def TCXLIQ(self):
        value = ps('CONDUCTIVITY','T',self.T_sat,'Q',0,self.refType)
        name = 'Thermal Conductivity'
        SIUnit = 'W/m-K'
        return value
        
    def CPLIQ(self):
        value = ps('CPMASS','T',self.T_sat,'Q',0,self.refType)
        name = 'Mass specific Isobaric heat capacity'
        SIUnit = 'J/kg-K'
        return value

    def CVLIQ(self):
        value = ps('CVMASS','T',self.T_sat,'Q',0,self.refType)
        name = 'Mass specific Isochoric heat capacity'
        SIUnit = 'J/kg-K'
        return value
        
    def GAMMALIQ(self):
        value = self.CPLIQ() / self.CVLIQ()
        name = 'Cp/Cv'
        SIUnit = ''
        return value
        
    def ZLIQ(self):
        value = ps('Z','T',self.T_sat,'Q',0,self.refType)
        name = 'Compressibility factor'
        SIUnit = ''
        return value
        
    def STLLIQ(self):
        value = ps('SURFACE_TENSION','T',self.T_sat,'Q',0,self.refType)
        name = 'SURFACE_TENSION'
        SIUnit = 'N/m'
        return value
        
    def PRLIQ(self):
        value = ps('PRANDTL','T',self.T_sat,'Q',0,self.refType)
        name = 'Prandtl number'
        SIUnit = ''
        return value
        
    def SVLIQ(self):
        value = 1/self.DENLIQ()
        name = 'Specific Volume'
        SIUnit = 'm3/kg'
        return value

    def BETALIQ(self):
        value = ps('isobaric_expansion_coefficient','T',self.T_sat,'Q',0,self.refType)
        name = 'isobaric_expansion_coefficient'
        SIUnit = '1/K'
        return value

    def DENVAP(self):
        value = ps('D','T',self.T_sat,'Q',1,self.refType)
        name = 'Density'
        SIUnit = 'kg/m3'
        return value

    def VVAP(self):
        value = ps('V','T',self.T_sat,'Q',1,self.refType)
        name = 'Viscosity'
        SIUnit = 'Pa-s'
        return value
        
    def HVAP(self):
        value = ps('H','T',self.T_sat,'Q',1,self.refType)
        name = 'Enthalpy'
        SIUnit = 'J/kg'
        return value
        
    def TCXVAP(self):
        value = ps('CONDUCTIVITY','T',self.T_sat,'Q',1,self.refType)
        name = 'Thermal Conductivity'
        SIUnit = 'W/m-K'
        return value
               
    def CPVAP(self):
        value = ps('CPMASS','T',self.T_sat,'Q',1,self.refType)
        name = 'Mass specific Isobaric heat capacity'
        SIUnit = 'J/kg-K'
        return value

    def CVVAP(self):
        value = ps('CVMASS','T',self.T_sat,'Q',1,self.refType)
        name = 'Mass specific Isochoric heat capacity'
        SIUnit = 'J/kg-K'
        return value
        
    def GAMMAVAP(self):
        value = self.CPVAP() / self.CVVAP()
        name = 'Cp/Cv'
        SIUnit = ''
        return value
        
    def ZVAP(self):
        value = ps('Z','T',self.T_sat,'Q',1,self.refType)
        name = 'Compressibility factor'
        SIUnit = ''
        return value

    def PRVAP(self):
        value = ps('PRANDTL','T',self.T_sat,'Q',1,self.refType)
        name = 'Prandtl number'
        SIUnit = ''
        return value
        
    def SVVAP(self):
        value = 1/self.DENVAP()
        name = 'Specific Volume'
        SIUnit = 'm3/kg'
        return value

    def BETAVAP(self):
        value = ps('isobaric_expansion_coefficient','T',self.T_sat,'Q',0,self.refType)
        name = 'isobaric_expansion_coefficient'
        SIUnit = '1/K'
        return value

    def H_LV(self):
        value = self.HVAP() - self.HLIQ()
        name = 'Latent Heat'
        SIUnit = 'J/kg'
        return value

    def P_sat(self):
        value = ps('P','T',self.T_sat,'Q',0,self.refType)
        name = 'Saturated Pressure'
        SIUnit = 'Pa'
        return value

    def P_critical(self):
        value = ps('Pcrit',self.refType)
        name = 'Critical Pressure'
        SIUnit = 'Pa'
        return value

    def P_reducing(self):
        # value = ps('P_reducing','P',self.P_sat(),self.refType)
        value = self.P_sat() / self.P_critical()
        name = 'Reduced Pressure'
        SIUnit = ''
        return value

    def T_critical(self):
        value = ps('Tcrit',self.refType)
        name = 'Critical Temperature'
        SIUnit = 'K'
        return value

    def T_reducing(self):
        # value = ps('T_reducing','T',T_sat, self.refType)
        value = self.T_sat / self.T_critical()
        name = 'Reduced Temperature'
        SIUnit = ''
        return value

    def MOLEMASS(self):
        value = ps('MOLEMASS',self.refType)*1000
        name = 'MOLEMASS'
        SIUnit = 'kg/kmol'
        return value

    def R(self):
        value = 8314/self.MOLEMASS()
        name = 'Individual Gas Constant'
        SIUnit = 'J/kg-K'
        return value

    def T_max(self):
        value = ps('T_max',self.refType)
        name = 'Max Temp. of Coolprop database'
        SIUnit = 'K'
        return value

    def T_min(self):
        value = ps('T_min',self.refType)
        name = 'Min Temp. of Coolprop database'
        SIUnit = 'K'
        return value

    def T_triple(self):
        value = ps('T_triple',self.refType)
        name = 'Triple Point Temperature'
        SIUnit = 'K'
        return value

    def P_max(self):
        value = ps('P_max',self.refType)
        name = 'Max Press. of Coolprop database'
        SIUnit = 'K'
        return value

    def P_min(self):
        value = ps('P_min',self.refType)
        name = 'Min Press. of Coolprop database'
        SIUnit = 'K'
        return value

class Fluid_NotSat:
    # Constructor
    def __init__(self, refType, P, T):

        self.refType = refType
        self.P = P  # Atmospheric pressure (Pa)
        self.T = T # Air Temperature (K)
        
    #filting input value

    # @property
    # def refType(self):
    #     return self.__refType
    # @refType.setter
    # def refType(self, value):
    #     if value in FluidsList():
    #         self.__refType = value
    #     else:
    #         raise ValueError("[Invalid input] available refType: " , FluidsList())

    # @property
    # def T(self):
    #     return self.__T
    # @T.setter
    # def T(self, value):
    #     if value >= self.T_min() and value <= self.T_max():
    #         self.__T = value
    #     elif value < self.T_min():
    #         raise ValueError("[Invalid input] available T: (T_min,T_max) = ", self.T_min(), self.T_max())

    # @property
    # def P(self):
    #     return self.__P
    # @P.setter
    # def P(self, value):
    #     if value >= self.P_min() and value <= self.P_max():
    #         self.__P = value
    #     elif value < self.P_min():
    #         raise ValueError("[Invalid input] available P: (P_min,P_max) = ", self.P_min(), self.P_max())

    # Method
    def DEN(self):
        value = ps('D','T',self.T,'P', self.P, self.refType)
        name = 'Density'
        SIUnit = 'kg/m3'
        return value

    def V(self):
        value = ps('V','T',self.T,'P', self.P, self.refType)
        name = 'Viscosity'
        SIUnit = 'Pa-s'
        return value
        
    def H(self):
        value = ps('H','T',self.T,'P', self.P,self.refType)
        name = 'Enthalpy'
        SIUnit = 'J/kg'
        return value
        
    def TCX(self):
        value = ps('CONDUCTIVITY','T',self.T,'P', self.P,self.refType)
        name = 'Thermal Conductivity'
        SIUnit = 'W/m-K'
        return value      
               
    def CP(self):
        value = ps('CPMASS','T',self.T,'P', self.P,self.refType)
        name = 'Mass specific Isobaric heat capacity'
        SIUnit = 'J/kg-K'
        return value

    def CV(self):
        value = ps('CVMASS','T',self.T,'P', self.P,self.refType)
        name = 'Mass specific Isochoric heat capacity'
        SIUnit = 'J/kg-K'
        return value
        
    def GAMMA(self):
        value = self.CPAIR() / self.CVAIR()
        name = 'Cp/Cv'
        SIUnit = ''
        return value
        
    def Z(self):
        value = ps('Z','T',self.T,'P', self.P,self.refType)
        name = 'Compressibility factor'
        SIUnit = ''
        return value
        
    def PR(self):
        value = ps('PRANDTL','T',self.T,'P', self.P,self.refType)
        name = 'Prandtl number'
        SIUnit = ''
        return value
        
    def SV(self):
        value = 1/self.DENAIR()
        name = 'Specific Volume'
        SIUnit = 'm3/kg'
        return value

    def BETA(self):
        value = ps('isobaric_expansion_coefficient','T',self.T,'P', self.P, self.refType)
        name = 'isobaric_expansion_coefficient'
        SIUnit = '1/K'
        return value

    def Z(self):
        value = ps('P','T',self.T,'P',self.P,self.refType)
        name = 'Compressibility factor'
        SIUnit = ''
        return value

    def MOLEMASS(self):
        value = ps('MOLEMASS',self.refType)*1000
        name = 'MOLEMASS'
        SIUnit = 'kg/kmol'
        return value

    def R(self):
        value = 8314/self.MOLEMASS()
        name = 'Individual Gas Constant'
        SIUnit = 'J/kg-K'
        return value

    def P_critical(self):
        value = ps('Pcrit',self.refType)
        name = 'Critical Pressure'
        SIUnit = 'Pa'
        return value

    def P_reducing(self):
        # value = ps('P_reducing','P',self.P_sat(),self.refType)
        value = self.P / self.P_critical()
        name = 'Reduced Pressure'
        SIUnit = ''
        return value

    def T_critical(self):
        value = ps('Tcrit',self.refType)
        name = 'Critical Temperature'
        SIUnit = 'K'
        return value

    def T_reducing(self):
        # value = ps('T_reducing','T',T_sat, self.refType)
        value = self.T / self.T_critical()
        name = 'Reduced Temperature'
        SIUnit = ''
        return value


    def T_max(self):
        value = ps('T_max',self.refType)
        name = 'Max Temp. of Coolprop database'
        SIUnit = 'K'
        return value

    def T_min(self):
        value = ps('T_min',self.refType)
        name = 'Min Temp. of Coolprop database'
        SIUnit = 'K'
        return value

    def T_triple(self):
        value = ps('T_triple',self.refType)
        name = 'Triple Point Temperature'
        SIUnit = 'K'
        return value

    def P_max(self):
        value = ps('P_max',self.refType)
        name = 'Max Press. of Coolprop database'
        SIUnit = 'K'
        return value

    def P_min(self):
        value = ps('P_min',self.refType)
        name = 'Min Press. of Coolprop database'
        SIUnit = 'K'
        return value

# Test
def unittest_Fluid_NotSat():
    fluidType = 'Air'
    P = 101325.0
    T = 300.0
    if(fluidType in FluidsList()):
        ff = Fluid_NotSat(fluidType,P,T)
        print("ff = ", ff.DEN())
    else:
        print("unavailable fluid = ", fluidType)
        print("available fluid = ", FluidsList())
        
def unittest_Fluid_Sat():
    fluidType = 'R1234ze(E)'
    T = 273.15 + 10
    if(fluidType in FluidsList()):
        ff = Fluid_Sat(fluidType,T)
        print("ff = ", ff.DENLIQ())
    else:
        print("unavailable fluid = ", fluidType)
        print("available fluid = ", FluidsList())

# unittest_Fluid_NotSat()
# unittest_Fluid_Sat()

# ff = Fluid_NotSat('Air',101325.0,300.0)
# print("ff = ", ff.DEN())
# print("ff = ", ff.Z())

# T_sat = 273.15 + 10
# ff = Fluid_Sat('R1234ze(E)',T_sat)

# print("P_sat = ", ff.P_sat())

# print("P_critical = ", ff.P_critical())
# print("T_critical = ", ff.T_critical())

# print("P_reducing = ", ff.P_reducing())
# print("T_reducing = ", ff.T_reducing())

# print("ff = ", ff.CVVAP())
# print("ff = ", ff.CPVAP())
# print("ff = ", ff.R())
# print("ff = ", ff.CPVAP() - ff.CVVAP())
# print("ff = ", ff.CPVAP() / ff.CVVAP())
# print("ff = ", ff.GAMMAVAP())
# print("ff = ", ff.ZVAP())
# print("ff = ", ff.ZLIQ())

# print("ff = ", ff.HVAP())
# print("ff = ", ff.HLIQ())

# print("ff = ", ff.HVAP() - ff.HLIQ())
# print("ff = ", ff.T_max())
# print("ff = ", ff.T_min())
# print("ff = ", ff.T_triple())
# print("ff = ", ff.T_critical())
# print("ff = ", ff.MOLEMASS())
# print("ff = ", ff.R())
# from CoolProp.CoolProp import FluidsList
# print(FluidsList())