# Solar Simulator

# Creates python module based on NREL pysam package.
# Input lat/lon and system specs
# Pulls historical weather data then runs NREL PySAM
# Creates expected solar generation based historical weather

# Packages
import pandas as pd
import PySAM.Pvwattsv8 as pvwatt8
import PySAM.ResourceTools as tools

# Define a class named SolarSimulator
class SolarSimulator():
    """Class to simulate a solar pv system. 
    Requires NREL API key and registered email"""

    def __init__(self, system_info, nrel_api_key, nrel_api_email):
        # create an instance of pvwatt8
        self.pvwatt = pvwatt8.new()
        # assign system information passed to constructor
        self.system_info = system_info
        # set system specs and fetch weather data
        self.set_system_specs()
        self.fetch_weather_data(nrel_api_key, nrel_api_email)

    def set_system_specs(self):
        """Set system specs"""
        # assign system information specs to system_design attribute of pvwatt
        self.pvwatt.SystemDesign.assign(self.system_info['specs'])
        # assign adjustment factor dict to adjustment_factors attribute  of pvwatt
        self.pvwatt.AdjustmentFactors.assign({'constant': 0})

    def fetch_weather_data(self, nrel_api_key, nrel_api_email):
        """Get Weather Data"""
        # get latitude and longitude from system info to fetch weather data
        location = [(self.system_info['location']['lon'],
                     self.system_info['location']['lat'])]
        # create instance of FetchResourceFiles using nrel api
        nrel = tools.FetchResourceFiles(
            tech='solar',
            nrel_api_key=nrel_api_key,
            nrel_api_email=nrel_api_email
        )
        # fetch weather data for the given location using nrel api
        nrel.fetch(location)
        # get dictionary mapping location to downloaded file path
        nsrdb_path_dict = nrel.resource_file_paths_dict
        # assign solar resource file to SolarResource attribute of pvwatt instance
        self.pvwatt.SolarResource.assign(
            {'solar_resource_file': nsrdb_path_dict[location[0]]})
        # fetch resource files based on location
        nsrdb_path_dict = nrel.fetch(location).resource_file_paths_dict
        # assign fetched solar resource data path to solar_resource_file attribute of pvwatt
        self.pvwatt.SolarResource.assign(
            {'solar_resource_file': nsrdb_path_dict[location[0]]})

    def simulate_solar(self, ac_cap=7, dc_cap=7):
        """Simulate PV Generation"""
        # create system id from input ac capacity and dc capacity
        sys_id = 'r'+str(ac_cap)+'|'+str(dc_cap)
        # update system specs in pvwatt
        self.pvwatt.SystemDesign.assign({
            'system_capacity': dc_cap,
            'dc_ac_ratio': dc_cap/ac_cap})
        # execute solar simulation
        self.pvwatt.execute()
        # read hourly simulation data using pandas
        hrly_sim = pd.read_csv(
            self.pvwatt.SolarResource.solar_resource_file,
            skiprows=2,
            usecols=['Month', 'Day', 'Hour', 'DHI', 'DNI', 'GHI', 'Temperature'])
        # get solar output data from pvwatt and assign to 'solar' column of hourly sim data frame
        hrly_sim['solar'] = self.pvwatt.Outputs.ac
        # group hourly simulation data by month, day and hour, get mean solar value for each group
        shapes = hrly_sim.groupby(['Month', 'Day', 'Hour'])[
            'solar'].agg('mean').reset_index()
        # return simulation configuration info along with the calculated shapes
        return {'spec': sys_id, 'shape': shapes}