import yaml
import numpy as np
import pandas as pd
from pathlib import Path
from src.config.setting import CURRENCY_CONFIG_PATH, DATA_PATH



def load_currency_config(path=CURRENCY_CONFIG_PATH)->dict:
    with open(path,'r') as f:
        return yaml.safe_load(f)
    

def generate_curve(currency:str,config:dict,seed:int|None=None)->pd.DataFrame:
    rng =np.random.default_rng(seed)
    tenors =config['tenors']
    currency_config =config['currency'][currency]
    
    level =currency_config['level']

    slope_lambda =currency_config['slope_lambda']
    curvature_lambda =currency_config['slope_lambda']
    noise =rng.normal(0,currency_config['noise_std'])

    rows =[]
    for k,v in tenors.items():
        slope =currency_config['slope']*np.exp(-1*v*slope_lambda)

        curvature =currency_config['curvature']*np.exp(-1*v*curvature_lambda)

        rate =level +slope+curvature+noise

        rows.append(
            {
                'currency':currency,
                'tenor':k,
                'maturity':v,
                'zero_rate':rate,
            }
        )
    return pd.DataFrame(rows)

def generate_all_curves(seed:int=38)->pd.DataFrame:
    
    config =load_currency_config()
    currencies =config['currency'].keys()
    curves =[]
    for i, c in enumerate(currencies):
        curve =generate_curve(c,config,seed+i)
        curves.append(curve)
    
    return pd.concat(curves,ignore_index=True,axis=0)


if __name__ =='__main__':
    
    DATA_PATH.mkdir(parents=True,exist_ok=True)
    curves=generate_all_curves()
    curves.to_csv(DATA_PATH/'curves.csv',index =False)

