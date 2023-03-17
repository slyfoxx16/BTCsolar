"""
BTCminer

Created By Slyfox

Custom class BTCblock that contains high level info of a BTC block
BTCblock class has function to pull furhter detail about block

Function getBTCdata creates list of BTCblocks based on start and end time

URL Reference:
https://www.blockchain.com/api/blockchain_api
"""

import BTCdata

class BTCminer():
	def __init__(self,Herts,Watts,var):
		self.Herts = Herts
		self.kW = Watts
		self.var = var
