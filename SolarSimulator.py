# Solar Simulator

# Creates python module based on NREL pysam package.
# Input lat/lon and system specs
# Pulls historical weather data then runs NREL PySAM
# Creates expected solar generation based historical weather

# Packages
import pandas as pd
import PySAM.Pvwattsv8 as pvwatt8
import PySAM.ResourceTools as tools
from functools import reduce
import itertools

class SolarSimulator():
	def __init__(self, system_info):
		# create new instance of pvwatt8
		self.pvwatt = pvwatt8.new()
		# assign system information passed to constructor
		self.system_info = system_info
		# set system specs and fetch weather data
		self.set_system_specs()
		self.fetch_weather_data()

	def set_system_specs(self):
		# assign system information specs to system_design attribute of pvwatt
		self.pvwatt.SystemDesign.assign(self.system_info['specs'])
		# assign adjustment factor dict to adjustment_factors attribute  of pvwatt
		self.pvwatt.AdjustmentFactors.assign({'constant':0})

	def fetch_weather_data(self):
		# get latitude and longitude from system info to fetch weather data
		location = [(self.system_info['location']['lon'], self.system_info['location']['lat'])]
		# create instance of FetchResourceFiles using nrel api
		nrel = tools.FetchResourceFiles(
			tech='solar',
			nrel_api_key='bfpWE6iufkhWFk9DfN1G7M4FYeUIlWNp3MCOaQ2Z',
			nrel_api_email='carxtega16@gmail.com'
		)
		# fetch resource files based on location
		nsrdb_path_dict = nrel.fetch(location).resource_file_paths_dict
		# assign fetched solar resource data path to solar_resource_file attribute of pvwatt
		self.pvwatt.SolarResource.assign({'solar_resource_file':nsrdb_path_dict[location[0]]})
		
	def simulate_solar(self,ac_cap=7,dc_cap=7):
		# create system id from input ac capacity and dc capacity
		sys_id = 'r'+str(ac_cap)+'|'+str(dc_cap)
		# update system specs in pvwatt
		self.pvwatt.SystemDesign.assign({
			'system_capacity':dc_cap,
			'dc_ac_ratio':dc_cap/ac_cap
		})
		# execute solar simulation 
		self.pvwatt.execute()
		# read hourly simulation data using pandas
		hrly_sim = pd.read_csv(
			self.pvwatt.SolarResource.solar_resource_file,
			skiprows=2,
			usecols=['Month','Day','Hour','DHI','DNI','GHI','Temperature']
		)
		# get solar output data from pvwatt and assign to 'solar' column of hourly sim data frame
		hrly_sim['solar'] = self.pvwatt.Outputs.ac
		# group hourly simulation data by month, day and hour, get mean solar value for each group
		shapes = hrly_sim.groupby(['Month','Day','Hour'])['solar'].agg('mean').reset_index()
		# return simulation configuration info along with the calculated shapes
		return {'spec':sys_id, 'shape':shapes}

	def compare_systems(self):
		# Capacity Options
		ac_cap = [5,7,10,12]
		dc_cap = [5,7,10,12,15]
		# Create Solar Simulations
		generaion = []
		for i in ac_cap:
			for j in dc_cap:
				if i/j < 1 and i/j > 2:
					continue
				solar_gen = self.simulate_solar(i,j)
				spec = solar_gen['spec']
				shape = solar_gen['shape']
				shape.rename(columns={"solar": "spec"})
				generaion.append()
		generaion = reduce(lambda x, y: pd.merge(x, y, on = ['Month','Day','Hour']), generaion)
		return generaion