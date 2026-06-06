
from src.config.setting import CURRENCY_CONFIG_PATH, DATA_PATH, DataGenerationFiles
from src.config.schema import RFRColumns
from src.data_generation.curve_generator import load_currency_config
import pandas as pd
import numpy as np




def generate_rfr(currency:str,config: dict)->pd.DataFrame:
    currency_config =config['currency'][currency]
    start_rate =currency_config['start_rate']
    mean_ = currency_config['mean']
    alpha =currency_config['alpha']
    sigma =currency_config['sigma']

    rfr_params =config['rfr_params']
    n_days = rfr_params['data_length']*252
    dt =rfr_params['dt']
    
    
    dates = pd.date_range(end=pd.Timestamp.today(),
                                      periods =n_days,
                                      freq='B')
    

    rng =np.random.default_rng(rfr_params['seed'] + list(config['currency'].keys()).index(currency))
    rates =np.zeros(n_days)
    rates[0]=start_rate
    
    for i in range(1,n_days):
        shock =rng.normal(0,1)
        rates[i]=rates[i-1]+alpha*(mean_-rates[i-1])*dt +sigma*np.sqrt(dt)*shock
    
    return pd.DataFrame({RFRColumns.CURRENCY: currency,
                         RFRColumns.DATE: dates,
                         RFRColumns.RATE: rates
                         })

def generate_all_rfr()->pd.DataFrame:
    config =load_currency_config()
    currencies =config['currency'].keys()
    rfrs =[]
    for c in currencies:
        rfr =generate_rfr(c,config)
        rfrs.append(rfr)
    return pd.concat(rfrs,axis=0,ignore_index=True)

if __name__ =='__main__':
    DATA_PATH.mkdir(parents=True,exist_ok=True)
    rfrs =generate_all_rfr()
    rfrs.to_csv(DATA_PATH/'historical_rfrs.csv',index=False)
    