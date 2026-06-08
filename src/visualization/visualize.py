import streamlit as st
import pandas as pd
from src.config.setting import OutputFiles, DATA_PATH, CURRENCY_CONFIG_PATH, SCENARIO_CONFIG_PATH, DataGenerationFiles
from src.config.schema import HWParams, FitPrice, StressCurveColumns, RFRColumns
from src.utils.utils import load_yaml_config
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def load_output(path: str|Path)->pd.DataFrame:
    return pd.read_csv(path)

def load_currency_list()->list:
    return load_yaml_config(CURRENCY_CONFIG_PATH)['currency'].keys()

def load_scenario_list()->list:
    return load_yaml_config(SCENARIO_CONFIG_PATH).keys()

def main()->None:
    
    
    
    st.set_page_config(page_title ='MULTI-CURRENCY INTEREST RATE CALIBRATION')
    st.title('MULTI-CURRENCY INTEREST RATE CALIBRATION DASHBOARD')
    
    scenarios =load_scenario_list()
    currencies =load_currency_list()
    selected_scenario =st.sidebar.selectbox('Scenario',scenarios)
    selected_currency = st.sidebar.selectbox('Currency', currencies)
    vasicekparam =load_output(DATA_PATH/OutputFiles.VASICEK_PARAM)

    st.subheader('Vasicek Parameters(Initial Guess)')
    st.dataframe(data =vasicekparam)

    hwparam =load_output(DATA_PATH/OutputFiles.HW_PARAM)
    hwparam_filter =hwparam.loc[hwparam[HWParams.SCENARIO]==selected_scenario,:]
    st.subheader('Hull-White Paramters')
    st.dataframe(data =hwparam_filter)

    
    fitprice =load_output(DATA_PATH/OutputFiles.FIT_PRICE)
    fitprice_selected =fitprice.loc[(
                                    (fitprice[FitPrice.SCENARIO]==selected_scenario)
                                    &(fitprice[FitPrice.CURRENCY]==selected_currency)
                                    ),
                                    [FitPrice.SWAPTENOR,FitPrice.MARKETPRICE,FitPrice.MODELPRICE]
                                    ]
    fitprice_selected[FitPrice.SWAPTENOR]=fitprice_selected[FitPrice.SWAPTENOR].astype('str')
    st.subheader('Generated Fit Prices')
    st.scatter_chart(fitprice_selected, x=FitPrice.SWAPTENOR, y =[FitPrice.MARKETPRICE,FitPrice.MODELPRICE])

    curve=load_output( DATA_PATH/DataGenerationFiles.STRESS_CURVES)
    curve_selected =curve.loc[
        ((curve[StressCurveColumns.SCENARIO]==selected_scenario)
        &(curve[StressCurveColumns.CURRENCY]==selected_currency)
        ),
        [StressCurveColumns.TENOR, StressCurveColumns.ZERO_RATE]]
    st.subheader('Generated Spot Term Structure')
    st.line_chart(curve_selected, x=StressCurveColumns.TENOR, y=StressCurveColumns.ZERO_RATE)

    rfr =load_output(DATA_PATH/DataGenerationFiles.RFRS)
    rfr_selected =rfr.loc[(rfr[RFRColumns.CURRENCY]==selected_currency),[RFRColumns.DATE, RFRColumns.RATE]]
    rfr_selected[RFRColumns.DATE]=pd.to_datetime(rfr_selected[RFRColumns.DATE]).dt.to_period('D').astype('str')
    st.subheader('Generated Historical Risk Free Rate')
    st.line_chart(rfr_selected, x=RFRColumns.DATE, y =RFRColumns.RATE)
    
    




if __name__ =="__main__":
    main()

    


