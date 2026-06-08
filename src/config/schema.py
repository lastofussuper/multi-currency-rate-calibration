class CurveColumns:
    CURRENCY = 'currency'
    TENOR = "tenor"
    MATURITY = 'maturity'
    ZERO_RATE = "zero_rate"

class VolColumns:
    CURRENCY = "currency"
    OPTIONTENOR = "option_tenor"
    SWAPTENOR = "swap_tenor"
    SWAPTIONVOL = "swaption_vol"

class RFRColumns:
    CURRENCY = "currency"
    DATE = "date"
    RATE = "rate"

class VasicekParamsColumns:
    CURRENCY = 'currency'
    ALPHA ='alpha'
    THETA ='theta'
    SIGMA ='sigma'

class HWParamsColumns:
    CURRENCY = 'currency'
    ALPHA ='alpha'
    SIGMA ='sigma'

class StressCurveColumns:
    CURRENCY = 'currency'
    TENOR = "tenor"
    MATURITY = 'maturity'
    ZERO_RATE = "zero_rate"
    SCENARIO =  "scenario"

class StressVolColumns:
    CURRENCY = "currency"
    OPTIONTENOR = "option_tenor"
    SWAPTENOR = "swap_tenor"
    SWAPTIONVOL = "swaption_vol"
    SCENARIO = "scenario"


class HWParams:
    CURRENCY ='currency'
    SCENARIO ='scenario'
    ALPHA ='alpha'
    SIGMA ='sigma'
    ITERATIONS = 'iterations'
    ERROR = 'error'

class FitPrice:
    CURRENCY = 'currency'
    SCENARIO = 'scenario'
    OPTIONTENOR = 'option_tenor'
    SWAPTENOR = 'swap_tenor'
    MARKETPRICE = 'market_price'
    MODELPRICE = 'model_price'
