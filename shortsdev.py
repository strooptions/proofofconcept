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
simdb = TinyDB('c:\projects\opop\simdb.json')
q = Query()
record = simdb.search(q.name == 'XRPdis')[0]
systemdb.insert(record)


create_account('Test', systemdb)
fund_account('Test', systemdb)

create_account('Guy', systemdb)
fund_account('Guy', systemdb)

trust_asset(systemdb, 'Test', 'XRP', 'XRPdis')
create_account('Printer', systemdb)
fund_account('Printer', systemdb)
trust_asset(systemdb, 'Test', 'USD', 'Printer')
send_asset(systemdb, 'Printer', 'USD', 'Printer', '1000', 'Test')

"""
		4
	2		6
1	3		5	7





"""

def ptxtree(systemdb):
	a_sk = systemdb.search(q.name == 'Test')[0]['sk']
	a_pk = systemdb.search(q.name == 'Test')[0]['pk']
	as_pk = systemdb.search(q.name == 'XRPdis')[0]['pk']
	as2_pk = systemdb.search(q.name == 'Printer')[0]['pk']

	address = Address(address=a_pk, network='TESTNET')
	address.get()

	b1 = Builder(
	secret = str(a_sk), 
	horizon_uri = 'https://horizon.stellar.org',
	network = 'TESTNET', 
	sequence = int(address.sequence)+1)
	b1.append_manage_offer_op('USD', as2_pk, 'XRP', as_pk, '1', '1', offer_id=0)

	envelope1 = b1.gen_te()
	hashish1 = envelope1.hash_meta()
	xdr1 = b1.gen_xdr()

	systemdb.insert({
		'type': 'ptx',
		'name': 'ptx1',
		'xdr': xdr1
		})

	b2 = Builder(
	secret = str(a_sk), 
	horizon_uri = 'https://horizon.stellar.org',
	network = 'TESTNET', 
	sequence = int(address.sequence)+2)
	b2.append_manage_offer_op('USD', as2_pk, 'XRP', as_pk, '2', '1', offer_id=0)

	envelope2 = b2.gen_te()
	hashish2 = envelope2.hash_meta()
	xdr2 = b2.gen_xdr()

	systemdb.insert({
		'type': 'ptx',
		'name': 'ptx2',
		'xdr': xdr2
		})


	b3 = Builder(
	secret = str(a_sk), 
	horizon_uri = 'https://horizon.stellar.org',
	network = 'TESTNET', 
	sequence = int(address.sequence)+2)
	b3.append_manage_offer_op('USD', as2_pk, 'XRP', as_pk, '3', '1', offer_id=0)

	envelope3 = b3.gen_te()
	hashish3 = envelope3.hash_meta()
	xdr3 = b3.gen_xdr()

	systemdb.insert({
		'type': 'ptx',
		'name': 'ptx3',
		'xdr': xdr3
		})

	b23 = Builder(
	secret = str(a_sk), 
	horizon_uri = 'https://horizon.stellar.org',
	network = 'TESTNET', 
	sequence = int(address.sequence)+1)
	b23.append_pre_auth_tx_signer(hashish2, 1, source=None)
	b23.append_pre_auth_tx_signer(hashish3, 1, source=None)

	envelope23 = b23.gen_te()
	hashish23 = envelope23.hash_meta()
	xdr23 = b23.gen_xdr()

	systemdb.insert({
		'type': 'ptx',
		'name': 'ptx23',
		'xdr': xdr23
		})




	bX = Builder(secret = a_sk, network='TESTNET')
	bX.append_pre_auth_tx_signer(hashish1, 1, source=None)
	bX.append_pre_auth_tx_signer(hashish23, 1, source=None)
	bX.sign()
	print bX.submit()

#see(systemdb)

#ptxtree(systemdb)

#see(systemdb)

#submit(systemdb, 'Test', 1)




# M = maximum price, equal to the current spot price plus the margin the trader will put in the account
# G = granularity: how many price points will be included?
# example: with the asset as Tesla, max price = spot of 300+50 = 350, G = 350
# meaning we need preauthorized transactions for offers at $1, $2, $3, ..., $350
def tree(maxprice, granularity):
	unit = float(maxprice)/float(granularity)
	prices = []
	C = unit
	while C<=maxprice:
		prices.append(C)
		C=C+unit
	return prices