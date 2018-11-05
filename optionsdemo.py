from stellar_base.keypair import Keypair
from stellar_base.address import Address
from stellar_base.builder import Builder
from stellar_base.asset import Asset

import requests 
import time
import random
from functionsX import (create_account, fund_account, trust_asset, send_asset, add_manifest, 
	see_account, genptxs, submit, data, make_offer, see, lock)

from tinydb import TinyDB, Query


systemdb = TinyDB('c:\projects\opop\systemdb.json')
"""	contains references to writer-side accounts and the contract manifest.
	manifest includes XDRs of preauthorized transactions
	simulates an e.g. IPFS db referenced in a data entry on the contract account
	"systemdb.purge()" to reset 
	"see(systemdb)" to see the state of the contract system
"""
simdb = TinyDB('c:\projects\opop\simdb.json')
#	contains XRPdis account with ~10,000 XRP for testing
#	loading record(s) from simdb into systemdb at program start:
q = Query()
record = simdb.search(q.name == 'XRPdis')[0]
systemdb.insert(record)

exptime = '1539490534'
#	expiration time for the option contract


# creating and funding writer account:

create_account('Writer', systemdb)
fund_account('Writer', systemdb)
trust_asset(systemdb, 'Writer', 'XRP', 'XRPdis')
send_asset(systemdb, 'XRPdis', 'XRP', 'XRPdis', '100', 'Writer')
see(systemdb)

def write():

	# Create utility accounts:

	create_account('Printer', systemdb)
	create_account('Contract', systemdb)
	create_account('Pipe', systemdb)

	fund_account('Printer', systemdb)
	fund_account('Contract', systemdb)
	fund_account('Pipe', systemdb)

	# Create and allocate utility assets, Option Contract Asset:

	trust_asset(systemdb, 'Writer', 'OCA', 'Printer')
	trust_asset(systemdb, 'Contract', 'GTA', 'Printer')
	trust_asset(systemdb, 'Contract', 'SPA', 'Printer')
	trust_asset(systemdb, 'Contract', 'XRP', 'XRPdis')
	trust_asset(systemdb, 'Contract', 'OCA', 'Printer')

	send_asset(systemdb, 'Printer', 'OCA', 'Printer', '1', 'Writer')
	send_asset(systemdb, 'Printer', 'GTA', 'Printer', '1', 'Contract')
	send_asset(systemdb, 'Printer', 'SPA', 'Printer', '0.0000001', 'Contract')

	# Simulate writer acquiring underlying and funding Contract account
	send_asset(systemdb, 'Writer', 'XRP', 'XRPdis', '100', 'Contract')

	# Writer creates a manifest describing contract, publicly accessible

	add_manifest(
		systemdb, 
		'XRP', 
		'XRPdis', 
		'XLM', 
		None, 
		'2', 
		'100', 
		exptime)

	# Writer generates preauthorized transactions 1, 2, and 3
	# *immediately* adds data entry to:
	# - announce option in announcement format
	# - - underlying + size + month of expiration + unit strike price
	# - locks Contract and Printer accounts
	# - if any more/less than these txs are submitted, ptxs will fail! 

	genptxs(systemdb, exptime)
	data(systemdb, 'Contract', 'opop!', 'XRP100NOV2')
	lock(systemdb, 'Printer')
	lock(systemdb, 'Contract')

"""basic exercise script, here executed by the writer on his own option...
"""
def exercise():
	send_asset(systemdb, 'Writer', 'OCA', 'Printer', '0.5', 'Contract')
	send_asset(systemdb, 'Writer', 'XLM', None, '200', 'Contract')
	print 'Exercise price and 1/2 OCA sent to Contract:'
	see_account(systemdb, 'Contract')
	print 'Submitting preauthorized transaction 1:'
	submit(systemdb, 'Writer', 1)
	print 'There are now offers on the Contract account to convert 0.5 OCA into 100 XRP:'
	see_account(systemdb, 'Contract')
	print 'Exercising party makes corresponding offers...'
	trust_asset(systemdb, 'Writer', 'SPA', 'Printer')
	make_offer(systemdb, 'Writer', 'OCA', 'Printer', '0.5', 'SPA', 'Printer', '0.0000002', 0)

	trust_asset(systemdb, 'Writer', 'GTA', 'Printer')
	make_offer(systemdb, 'Writer', 'SPA', 'Printer', '0.0000001', 'GTA', 'Printer', '10000000', 0)

	trust_asset(systemdb, 'Writer', 'XRP', 'XRPdis')
	make_offer(systemdb, 'Writer', 'GTA', 'Printer', '1', 'XRP', 'XRPdis', '100', 0)
	print 'Finished.'
	see(systemdb)







