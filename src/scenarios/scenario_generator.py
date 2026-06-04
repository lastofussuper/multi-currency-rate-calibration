import yaml
from src.utils.utils import load_yaml_config
from src.config.setting import DATA_PATH, SCENARIO_CONFIG_PATH
from src.config.schema import VolColumns, CurveColumns

import numpy as np
import pandas as pd
from pathlib import Path
from src.data_generation.curve_generator import generate_all_curves
from src.data_generation.vol_surface_generator import generate_vol_surface

def load_scenario_config()->dict:
    return load_yaml_config(SCENARIO_CONFIG_PATH)

def generate_scenario(scenario:str,config:dict)->dict:
    return config[scenario]

def load_stressed_curve(scenario:dict,base_curve:pd.DataFrame)->pd.DataFrame:
    short =scenario['short']
    long =scenario['long']
    lambda_ =scenario['lambda']
    stress_curve =base_curve.copy()
    short_effect =short*np.exp(-1*lambda_*stress_curve[CurveColumns.MATURITY])
    long_effect =long*(1-np.exp(-1*lambda_*stress_curve[CurveColumns.MATURITY]))
    stress_curve[CurveColumns.ZERO_RATE]=stress_curve[CurveColumns.ZERO_RATE]+ short_effect + long_effect
    
    return stress_curve

def generate_curves()->pd.DataFrame:
    base_curve =generate_all_curves()
    config=load_scenario_config()
    scenarios =config.keys()
    stress_curves=[]
    for s in scenarios:
        scenario =generate_scenario(s,config)
        stress_curve =load_stressed_curve(scenario,base_curve)
        stress_curves.append(stress_curve)
    
    return pd.concat(stress_curves,axis=0,ignore_index =True)

def load_stressed_vol(scenario:dict,base_vol:pd.DataFrame)->pd.DataFrame:
    vol =scenario['vol']
    stress_vol =base_vol.copy()
    stress_vol[VolColumns.SWAPTIONVOL] +=vol
    
    return stress_vol

def generate_vols()->pd.DataFrame:
    base_vol = generate_vol_surface()
    config =load_scenario_config()
    scenarios =config.keys()
    stress_vols =[]
    for s in scenarios:
        scenario = generate_scenario(s,config)
        stress_vol =load_stressed_vol(scenario, base_vol)
        stress_vols.append(stress_vol)
    
    return pd.concat(stress_vols, axis=0, ignore_index=True)


if __name__ == "__main__":
    curves =generate_curves()
    curves.to_csv(DATA_PATH/'stress_curves.csv',index=False)

    vols =generate_vols()
    vols.to_csv(DATA_PATH/'stress_vols.csv', index =False)

    

    
