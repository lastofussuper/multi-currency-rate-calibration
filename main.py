from src.data_generation.curve_generator import generate_all_curves
from src.data_generation.historical_rfr_generator import generate_all_rfr
from src.data_generation.vol_surface_generator import generate_vol_surface
from src.scenarios.scenario_generator import generate_curves, generate_vols
from src.models.vasicek_model import generate_all_vasicek_params
from src.models.hull_white_model import generate_output
def main()->None:
    generate_all_curves()
    generate_all_rfr()
    generate_vol_surface()

    generate_curves()
    generate_vols()
    
    generate_all_vasicek_params()
    generate_output()


if __name__=="__main__":
    main()
