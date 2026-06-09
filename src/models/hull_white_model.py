import pandas as pd
import numpy as np
from src.config.setting import DATA_PATH, DataGenerationFiles, CURRENCY_CONFIG_PATH, SCENARIO_CONFIG_PATH, OutputFiles, MODEL_CONFIG_PATH
from src.config.schema import StressCurveColumns, StressVolColumns,VasicekParamsColumns, HWParams, FitPrice
from src.utils.utils import load_yaml_config
from src.scenarios.scenario_generator import generate_curves, generate_vols
from src.models.vasicek_model import generate_all_vasicek_params
from pathlib import Path
from dataclasses import dataclass
from scipy.stats import norm
from scipy.optimize import brentq, minimize
from typing import Callable


global freq

@dataclass(frozen =True)
class ZeroCurve:
    rates: np.ndarray
    tenors: np.ndarray

    def interpolate(self,t:float)->float:
        return np.interp(t,self.tenors,self.rates)
    
    
    def discount(self,t:float)->float:
        return np.exp(-1*self.interpolate(t)*t)

@dataclass(frozen =True)
class Swaption:
    
    option_tenor: int
    swap_tenor: int
    black_vol: float

@dataclass(frozen=True)
class Params:
    alpha: float
    sigma: float

@dataclass(frozen=True)
class InputData:
    swaption_df: pd.DataFrame
    curve_df: pd.DataFrame
    params_df: pd.DataFrame

@dataclass(frozen=True)
class OutputData:
    hwparam_df :pd.DataFrame
    fitprice_df :pd.DataFrame
    



def get_data(path: Path,generator: Callable[[],pd.DataFrame])->pd.DataFrame:
    data_path =DATA_PATH/path
    if data_path.exists():
        return pd.read_csv(data_path)
    df =generator()
    data_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(data_path, index=False)
    return df

def load_input_data()->InputData:
    swaption_df =get_data(DataGenerationFiles.STRESS_VOLS, generate_vols)
    curve_df =get_data(DataGenerationFiles.STRESS_CURVES,generate_curves)
    params_df =get_data(OutputFiles.VASICEK_PARAM,generate_all_vasicek_params)
    return InputData(swaption_df, curve_df, params_df)
    
   

def load_params(path: Path):
    return load_yaml_config(path)

freq = load_params(CURRENCY_CONFIG_PATH)['hw_params']['dt']

def generate_payment_schedule(swpt: Swaption)->np.ndarray:
    
    return([swpt.option_tenor+i*freq for i in range(1,int(swpt.swap_tenor/freq)+1)])

def swap_annuity(curve:ZeroCurve,schedule: np.ndarray)->float:
    
    return freq*sum([curve.discount(t) for t in schedule])

def forward_swap_rate(curve: ZeroCurve, schedule: np.ndarray)->float:
    
    annuity=swap_annuity(curve, schedule)
    return (curve.discount(schedule[0])-curve.discount(schedule[-1]))/annuity

def black_swaption(curve: ZeroCurve, swpt: Swaption)->float:
    
    schedule =generate_payment_schedule(swpt)
    forward =forward_swap_rate(curve,schedule)
    annuity=swap_annuity(curve,schedule)
    strike =forward
    vol_sqrt_t =swpt.black_vol*np.sqrt(swpt.option_tenor)
    d1 =0.5*vol_sqrt_t
    d2 =-1*d1
    return annuity*(forward*norm.cdf(d1)-strike*norm.cdf(d2))

def hw_B(alpha:float, t:int, T:int)->float:
    if alpha<1e-8:
        return T-t
    return (1.0 -np.exp(-alpha*(T-t)))/alpha

def hw_bond_price(params: Params, t:int, T:int,r_t,curve:ZeroCurve)->float:
    alpha =params.alpha
    sigma =params.sigma
       
    B =hw_B(alpha,t,T)
    convexity =(sigma**2*(1-np.exp(-2*alpha*t))*B**2)/(2*alpha)
    A =curve.discount(T)/curve.discount(t)*np.exp(B*curve.interpolate(t)-0.5*convexity)
    if abs(B*r_t)>50:
        print(f"alpha={alpha},sigma={sigma},B={B},r_t={r_t}")
    return A*np.exp(-1*B*r_t)

def hw_bond_option_vol(params: Params, t:int, T: int):
    alpha = params.alpha
    sigma = params.sigma
    B =hw_B(alpha,t,T)

    convexity =(sigma**2*(1-np.exp(-2*alpha*t))*B**2)/(2*alpha)
    return np.sqrt(convexity)

def bond_put_price(curve:ZeroCurve, t:int, T:int,strike:float,params: Params)->float:

    p0t =curve.discount(t)
    p0T=curve.discount(T)
    vol =hw_bond_option_vol(params,t,T)
    d1 =np.log(p0T/(strike*p0t))/(vol)+0.5*vol
    d2=d1-vol
    return strike*p0t*norm.cdf(-d2)-p0T*norm.cdf(-d1)

def jamshidian_root(curve:ZeroCurve,params:Params,schedule:np.ndarray,fixed_rate:float,model_param:dict)->float:
    
    rstar_bound =model_param['RstarBoundaries']

    cashflows = np.full(len(schedule),fixed_rate*freq)
    cashflows[-1]+=1
    def fixed_legs(r:float)->float:
        return sum(
            c*hw_bond_price(params,schedule[0],s, r, curve)
              for s,c in zip(schedule,cashflows)
              )-1
    return brentq(fixed_legs,rstar_bound['lower'],rstar_bound['upper'])


def hw_atm_swaption(curve:ZeroCurve, swpt: Swaption, params: Params,model_param:dict)->float:
    
    schedule =generate_payment_schedule(swpt)
    fixed_rate =forward_swap_rate(curve, schedule)

    r_star =jamshidian_root(curve, params, schedule, fixed_rate,model_param)
    
    cashflows = np.full(len(schedule),freq*fixed_rate)
    cashflows[-1]+=1
    price =0.0
    for c, s in zip(cashflows,schedule):
        strike =hw_bond_price(params, swpt.option_tenor, s, r_star, curve)
        price +=c*bond_put_price(curve,swpt.option_tenor,s,strike,params)
    
    return price

def object_func(x: np.ndarray, curve: ZeroCurve, swaption: list[Swaption],model_param:dict)->float:
    alpha,sigma =x
    param_boundaries = model_param['ParamsBoundaries']
    if (alpha >= param_boundaries['alpha']['upper']
        or alpha <=param_boundaries['alpha']['lower']
        or sigma >=param_boundaries['sigma']['upper']
        or sigma <= param_boundaries['sigma']['lower']
    ):
        return 1e10
   
    params =Params(alpha, sigma)
    model_prices =np.array([hw_atm_swaption(curve, swpt, params,model_param) for swpt in swaption ])
    market_prices =np.array([black_swaption(curve, swpt) for swpt in swaption])

    return sum(np.abs(market_prices-model_prices))

def calibrate_hw(swaption:list[Swaption],curves:ZeroCurve, param:Params,model_param:dict)->Params:
    
    x0 =np.array([param.alpha,param.sigma])
    optimizerparams =model_param['OptimizationMethod']
    result =minimize(object_func, x0=x0, args=(curves, swaption,model_param),method =optimizerparams['method'],
                           options={'maxiter':optimizerparams['maxiter'],
                                    'xatol': optimizerparams['xatol'],
                                    'fatol':optimizerparams['fatol']})
    
    
    return result

def load_swapt_vol(swaption_df: pd.DataFrame,currency:str, scenario:str)->Swaption:
    swaption_row =swaption_df.loc[
                (swaption_df[StressVolColumns.CURRENCY]==currency)
                  & (swaption_df[StressVolColumns.SCENARIO]==scenario),
                                      [StressVolColumns.OPTIONTENOR, StressVolColumns.SWAPTENOR, StressVolColumns.SWAPTIONVOL]]
    swaption=[]
    for _, row in swaption_row.iterrows():
        swpt =Swaption(option_tenor =row[StressVolColumns.OPTIONTENOR],
                        swap_tenor =row[StressVolColumns.SWAPTENOR],
                        black_vol =row[StressVolColumns.SWAPTIONVOL])
        swaption.append(swpt)
    return swaption

def load_curve(curve_df:pd.DataFrame,currency:str, scenario:str)->ZeroCurve:
    curves_row =curve_df.loc[
                (curve_df[StressCurveColumns.CURRENCY]==currency) 
                & (curve_df[StressCurveColumns.SCENARIO]==scenario),
                                 [StressCurveColumns.ZERO_RATE,StressCurveColumns.MATURITY]]
    return ZeroCurve(rates =curves_row[StressCurveColumns.ZERO_RATE].to_numpy(float),
                             tenors=curves_row[StressCurveColumns.MATURITY].to_numpy(float)
                             )
def load_vasicek_param(df:pd.DataFrame, currency:str)->Params:
    
    x0_row =df.loc[df[VasicekParamsColumns.CURRENCY]==currency,[VasicekParamsColumns.ALPHA, VasicekParamsColumns.SIGMA]].iloc[0]
    alpha =x0_row[VasicekParamsColumns.ALPHA]
    sigma =x0_row[VasicekParamsColumns.SIGMA]
    return Params(alpha =alpha, sigma =sigma)

def load_price_fit(curve:ZeroCurve, swaption: list[Swaption],model_param:dict,param:np.ndarray,currency:str,scenario:str)->pd.DataFrame:
    
    rows =[]
    for swpt in swaption:
        market_price =black_swaption(curve, swpt)
        model_price =hw_atm_swaption(curve,swpt, param,model_param)
        rows.append({FitPrice.CURRENCY: currency,
                     FitPrice.SCENARIO: scenario,
                     FitPrice.OPTIONTENOR: swpt.option_tenor,
                     FitPrice.SWAPTENOR: swpt.swap_tenor,
                     FitPrice.MARKETPRICE: market_price,
                     FitPrice.MODELPRICE: model_price})
    return rows

def generate_output()->OutputData:

    
    input_dfs = load_input_data()
    swaption_df =input_dfs.swaption_df
    curve_df =input_dfs.curve_df
    params_df =input_dfs.params_df
    model_param =load_params(MODEL_CONFIG_PATH)
    
    
    currencies =load_yaml_config(CURRENCY_CONFIG_PATH)['currency'].keys()
    scenarios =load_yaml_config(SCENARIO_CONFIG_PATH).keys()
    hw_params =[]
    fit_price =[]

    for c in currencies:
        for s in scenarios:
            print(c,s)
            swaption =load_swapt_vol(swaption_df,c,s)
            
            curves = load_curve(curve_df,c,s)

            x0 =load_vasicek_param(params_df,c)

            result =calibrate_hw(swaption, curves, x0,model_param)
            alpha,sigma = result.x
            param =Params(alpha, sigma)
            hp_param = {HWParams.CURRENCY: c,
                              HWParams.SCENARIO: s,
                              HWParams.ALPHA: alpha,
                              HWParams.SIGMA: sigma,
                              HWParams.ITERATIONS: result.nfev,
                              HWParams.ERROR: result.fun}
            hw_params.append(hp_param)
            fit_price.extend(load_price_fit(curves, swaption,model_param,param,c,s))
            
    hw_params =pd.DataFrame(hw_params)
    fit_price =pd.DataFrame(fit_price)
    
    hw_params.to_csv(DATA_PATH/OutputFiles.HW_PARAM, index=False)
    fit_price.to_csv(DATA_PATH/OutputFiles.FIT_PRICE, index=False)

    return OutputData(hw_params,fit_price)


if __name__=='__main__':
    generate_output()
    


