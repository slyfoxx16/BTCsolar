"""
BTCassistant

Created By Slyfox

Custom functions to assist with interacting with BTCblock class

URL Reference:
https://www.blockchain.com/api/blockchain_api
"""

# Packages
import requests, json
import datetime as dt
import pickle as pkl

# Custom Packages
import BTCdata

## Helper Functions
# Get BTC Block Data (Choose: Headers or Full Data)
def getBTCdata(start,end,full_data=False):

	start = dt.datetime.strptime(start, "%Y-%m-%d").timestamp()
	end = dt.datetime.strptime(end, "%Y-%m-%d").timestamp()
	t = start

	block_list = []

	while True:
		if t > end:
			break
		url = f"https://blockchain.info/blocks/{int(t*1000)}?format=json"
		response = requests.get(url)
		blk_header = json.loads(response.text)
		for header in blk_header:
			blk = BTCdata.BTCblock(header['hash'],header['time'])
			if full_data == True:
				blk.get_info()
			block_list.append(blk)
		t += 60*60*24
	
	return block_list


# Store BTC Block Data in Pickle file (Full Data)
def archiveBTCdata(start,end):

	# Get Block Data (10 mins for 1 month of data)
	block_list = getBTCdata(start,end,True)

	# write Block Data to a pkl file
	with open('HistData/HistBTCdata.pkl', 'wb') as f:
		pkl.dump(block_list, f)