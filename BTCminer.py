# BTC Miner

# Packages
import pandas as pd
import random
import SolarSimulator

class BTCminer():
	def __init__(self,Th,W):
		self.Th = Th
		self.kW = W/1000
		self.yearly_kWh = 8760 * (W/1000)

	def fit_solar(self, pv_system, nrel_api_key, nrel_api_email, n_iter):
		# Enter Location and specs of pv system
		soalr_sys = SolarSimulator.SolarSimulator(pv_system, nrel_api_key, nrel_api_email)

		# define the bounds for the inputs and the number of iterations
		# x_bounds and y_bounds should be tuples with (min, max) values
		esitmated_capacity_factor = 0.2
		starting_cap = int(self.yearly_kWh/(esitmated_capacity_factor * 8760))

		best_params = None
		best_distance = float('inf')
		
		# Bounds for search
		min_cap = starting_cap - 5
		max_cap = starting_cap + 5
		
		for i in range(n_iter):
			# generate random values for the parameters within the given bounds
			ac = random.randint(min_cap, max_cap)
			dc = random.randint(min_cap, max_cap)
			
			# evaluate the function with the current parameters
			output = sum(soalr_sys.simulate_solar(ac, dc)['shape'].solar)/1000
			
			# compute the distance between the output and the target value
			distance = abs(output - self.yearly_kWh)
			
			# update the best parameters and distance if the current output is closer to the target
			if output >= self.yearly_kWh and distance < best_distance:
				best_params = (ac, dc)
				best_distance = distance

		print(f"Optimal Solar Capacity (kW): ac={best_params[0]}:dc={best_params[1]}")
		print(f"Output with best parameters: {sum(soalr_sys.simulate_solar(*best_params)['shape'].solar)/1000}")
		
		return best_params
