import yaml
import pandas as pd
import numpy as np

from src.data_generation.curve_generator import load_currency_config
from src.config.setting import DATA_PATH, DataGenerationFiles
from src.config.schema import VolColumns
def generate_vol(currency:str,config:dict)->pd.DataFrame:
    vol_config =config['volatility_params']
    seed =vol_config['seed']+ hash(currency)%1000
    rng =np.random.default_rng(seed)
    base_vol =config['currency'][currency]['vol']
    
    

    noise_std = vol_config['noise_std']

    min_vol =vol_config['min_vol']
    
    expiry_lambda = vol_config['expiry_lambda']
    tenor_lambda = vol_config['tenor_lambda']
    
    expiry_premium = vol_config['expiry_premium']
    tenor_premium =vol_config['tenor_premium']

    swaption_tenor =list(range(1,vol_config['tenor']+1))
    
    rows =[]
    for t in swaption_tenor:
        expiry =vol_config['tenor']+1-t
        expiry_effect =expiry_premium*np.exp(-1*expiry*expiry_lambda)
        tenor_effect =tenor_premium*np.exp(-1*t*tenor_lambda)
        smile_noise = rng.normal(0,noise_std)
        vol =base_vol +expiry_effect + tenor_effect +smile_noise
        vol =max(vol, min_vol)

        rows.append({VolColumns.CURRENCY: currency,
                     VolColumns.OPTIONTENOR: expiry,
                     VolColumns.SWAPTENOR: t,
                     VolColumns.SWAPTIONVOL: vol})
    
    return pd.DataFrame(rows)

def generate_vol_surface(seed:int=38)->pd.DataFrame:

    config=load_currency_config()
    currencies =config['currency'].keys()
    surfaces =[]
    for i, c in enumerate(currencies):
        surface =generate_vol(c,config)
        surfaces.append(surface)
    
    return pd.concat(surfaces, axis=0, ignore_index =True)


if __name__=='__main__':
    vols =generate_vol_surface()
    vols.to_csv(DATA_PATH/DataGenerationFiles.VOLS,index=False)


