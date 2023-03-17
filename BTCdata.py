"""
BTCdata

Created By Slyfox

Custom class BTCblock that contains high level info of a BTC block
BTCblock class has function to pull furhter detail about block

Function getBTCdata creates list of BTCblocks based on start and end time

URL Reference:
https://www.blockchain.com/api/blockchain_api
"""

import requests, json
import datetime as dt

# Helper Functions


class BTCblock():
	ticker = 'BTC'
	def __init__(self,hash,time=None,full_info=False):
		self.hash = hash
		if time != None:
			self.time = dt.datetime.fromtimestamp(time)

	def get_info(self):
		url = f"https://blockchain.info/rawblock/{self.hash}"
		response = requests.get(url)
		self.info = json.loads(response.text)
		self.time = dt.datetime.fromtimestamp(self.info['time'])

	def estimate_difficulty(self):
		if hasattr(self, 'info') == False:
			self.get_info()
		current_target = self.info['bits']
		difficulty_target = int("00000000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF", 16)#maximum target that is used to calculate mining difficulty
		self.difficulty = difficulty_target/current_target
		print('Block Difficulty: '+str(self.difficulty))

	def block_time(self):
		if hasattr(self, 'info') == False:
			self.get_info()
		prv_hash = self.current_blk.info['prev_block']
		prv_blk = BTCblock(prv_hash)
		prv_blk.get_info()
		self.blk_time = self.time - prv_blk.get_info().time

class BTCchain:
	def __init__(self,init_hash):
		self.chain = []
		self.current_blk = BTCblock(init_hash,True)
		self.current_blk.get_info(self)

		prv_hash = self.current_blk.info['prev_block']
		nxt_hash = self.current_blk.info['next_block'][0]
		self.next_blk = BTCblock(nxt_hash)
		self.prv_blk = BTCblock(prv_hash)

	def next_block(self):
		self.prv_blk = self.current_blk
		self.current_blk = self.next_blk
		self.current_blk.get_info()
		prv_hash = self.current_blk.info['prev_block']
		self.next_blk = BTCblock(prv_hash)
			
	def previous_block(self):
		self.next_blk = self.current_blk
		self.current_blk = self.prv_blk
		self.current_blk.get_info()
		nxt_hash = self.current_blk.info['next_block'][0]
		self.next_blk = BTCblock(nxt_hash)

		self.current_blk = self.prv_blk
		self.next_blk = BTCblock(self.current_blk.next_blk)
		self.prv_blk = BTCblock(self.current_blk.prv_blk)
