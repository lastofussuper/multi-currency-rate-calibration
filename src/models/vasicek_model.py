import pandas as pd
import numpy as np
import statsmodels.api as sm
from src.config.schema import RFRColumns, VasicekParamsColumns
from src.utils.utils import load_yaml_config
from src.config.setting import CURRENCY_CONFIG_PATH, DataGenerationFiles,DATA_PATH, OutputFiles
from src.data_generation.historical_rfr_generator import generate_all_rfr

def load_rfr_params():
    return load_yaml_config(CURRENCY_CONFIG_PATH)['rfr_params']

def get_rfr():
    path =DATA_PATH/DataGenerationFiles.RFRS
    if path.exists():
       return pd.read_csv(path)
    else:
        rfr =generate_all_rfr()
        rfr.to_csv(path,index =False)
        return rfr
    
def load_currency_list():
    currency_config =load_yaml_config(CURRENCY_CONFIG_PATH)['currency']
    return list(currency_config.keys())
    

def generate_vasicek_parameters(currency:str,rfr: pd.DataFrame)->dict:
    rfr_params =load_rfr_params()    
    dt =rfr_params['dt']
    
    rfr=rfr.set_index(RFRColumns.DATE) 
    rfr['drates'] =rfr[RFRColumns.RATE].diff()
    rfr['lag_rates']=rfr[RFRColumns.RATE].shift()
    rfr =rfr.dropna()
    X = sm.add_constant(rfr['lag_rates'])
     
    
    model =sm.OLS(rfr['drates'],X).fit()

    alpha =-1*model.params['lag_rates']/dt
    theta =model.params['const']/alpha/dt
    sigma =np.std(model.resid, ddof=1)/np.sqrt(dt)

    return {VasicekParamsColumns.CURRENCY:currency,
            VasicekParamsColumns.ALPHA: alpha,
            VasicekParamsColumns.THETA: theta,
            VasicekParamsColumns.SIGMA: sigma}

def generate_all_vasicek_params():
    
    DATA_PATH.mkdir(parents=True, exist_ok =True)
    currencies =load_currency_list()
    rfrs =get_rfr()
    v_param_list=[]
    for c in currencies:
        rfr =rfrs[rfrs[RFRColumns.CURRENCY]==c]
        v_param =generate_vasicek_parameters(c,rfr)
        v_param_list.append(v_param)

    v_params_df =pd.DataFrame(v_param_list)
    v_params_df.to_csv(DATA_PATH/OutputFiles.VASICEK_PARAM, index=False)
    
    return v_params_df



if __name__=='__main__':
    generate_all_vasicek_params()
    


