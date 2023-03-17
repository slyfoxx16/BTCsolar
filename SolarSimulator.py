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

# New PySAM Class
class Solar():
	def __init__(self, home):
		# Setup Solar System with PVWATT
		self.pvwatt = pvwatt8.new()
		self.pvwatt.SystemDesign.assign(home['specs'])
		self.pvwatt.AdjustmentFactors.assign({'constant':0})
		# Weather Fetcher
		nsrdbfetcher = tools.FetchResourceFiles(
			tech = 'solar',
			nrel_api_key='bfpWE6iufkhWFk9DfN1G7M4FYeUIlWNp3MCOaQ2Z',
			nrel_api_email='carxtega16@gmail.com')
		# Get Weather Data
		self.location = [(home['location']['lon'], home['location']['lat'])]
		nsrdbfetcher.fetch(self.location)
		nsrdb_path_dict = nsrdbfetcher.resource_file_paths_dict
		nsrdb_fp = nsrdb_path_dict[self.location[0]]
		self.pvwatt.SolarResource.assign({'solar_resource_file':nsrdb_fp})

	def simulate_solar(self,ac_cap = 7,dc_cap = 7):
		sys = 'r'+str(ac_cap)+'|'+str(dc_cap)
		# Update System Specs
		self.pvwatt.SystemDesign.assign({'system_capacity':dc_cap})
		self.pvwatt.SystemDesign.assign({'dc_ac_ratio':dc_cap/ac_cap})
		# Run Simulation
		self.pvwatt.execute()
		# Simulation Data
		hrly_sim = pd.read_csv(self.pvwatt.SolarResource.solar_resource_file, skiprows = 2) \
			[['Year','Month','Day','Hour','Minute','Dew Point','DHI','DNI','GHI','Surface Albedo','Pressure','Temperature','Wind Direction','Wind Speed']]
		hrly_sim['solar'] = self.pvwatt.Outputs.ac
		hrly_sim['solar'] = hrly_sim['solar'].apply(lambda x: x/1000)
		shapes = hrly_sim.groupby(['Month','Day','Hour'])['solar'] \
			.agg('mean').reset_index()
		solar_system = {'spec':sys,'shape':shapes}
		return solar_system

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