from stellar_base.keypair import Keypair
from stellar_base.address import Address
from stellar_base.builder import Builder
from stellar_base.asset import Asset

import requests 
import time
import random
import json

from tinydb import TinyDB, Query


def create_account(
	name, systemdb):

	kp = Keypair.random()

	pk = kp.address().decode()
	sk = kp.seed().decode()

	systemdb.insert(
		{'type': 'account',
		 'pk': pk,
		 'sk': sk,
		 'name': name}
		 )

def add_manifest(
	systemdb,
	underlying,
	underlying_source,
	quote,
	quote_source,
	strike_price,
	size,
	expiration_time):

	q = Query()

	printer = systemdb.search(q.name=='Printer')[0]['pk']
	contract = systemdb.search(q.name=='Contract')[0]['pk']
	pipe = systemdb.search(q.name=='Pipe')[0]['pk']
	underlying_source = systemdb.search(q.name == underlying_source)[0]['pk']

	systemdb.insert(
		{'type': 'manifest',
		 'UND': underlying,
		 'UND_source': underlying_source,
		 'QUO': quote, 
		 'QUO_source': quote_source,
		 'strike': strike_price,
		 'size': size,
		 'exp': expiration_time,
		 'printer': printer,
		 'contract': contract,
		 'pipe': pipe 
		})

def fund_account(
	name, systemdb):

	q = Query()
	pk = systemdb.search(q.name == name)[0]['pk']
	url = 'https://friendbot.stellar.org'
	r = requests.get(url, params={'addr': pk})

def see_account_pk(pk, name):

	address = Address(address=pk, network='TESTNET')
	address.get()

	bals = address.balances
	sigs = address.signers
	nots = address.data
	offs = address.offers()
	print name
	print 'sequence number is '+address.sequence
	
	print str(len(bals))+' ASSETS'

	C = 0
	while C < len(bals):
		if bals[C]['asset_type']=='native':
			print '..... XLM: '+bals[C]['balance']
		else:
			print '..... '+bals[C]['asset_code']+': '+bals[C]['balance']
			print '..... (from '+bals[C]['asset_issuer']
		C+=1

	T = address.thresholds
	print 'SECURITY THRESHOLDS'
	print '..... high ops: '+str(T['high_threshold'])
	print '..... low ops: '+str(T['low_threshold'])
	print '..... medium ops: '+str(T['med_threshold'])

	print str(len(sigs))+' SIGNERS'

	C = 0
	while C < len(sigs):
		print '..... '+sigs[C]['key']
		print '..... '+sigs[C]['type']+' weight: '+str(sigs[C]['weight'])
		C+=1
	print 'DATA'
	print nots
	print 'OFFERS'
	records = offs['_embedded']['records']
	C = 0 
	while C < len(records):

		print '..... '+records[C]['amount']+' '+records[C]['selling']['asset_code']+' from '+records[C]['selling']['asset_issuer']
		print '..... for '+records[C]['price']+' '+records[C]['buying']['asset_type']+' per '+records[C]['selling']['asset_code']
		C+=1

	print ''

def see_account(systemdb, name):
	q = Query()
	pk = systemdb.search(q.name == name)[0]['pk']
	see_account_pk(pk, name)

def see(systemdb):
	q = Query()
	for record in systemdb.search(q.type == 'account'):
		see_account(systemdb, record['name'])

def trust_asset(
	systemdb,
	source_name, 
	asset_name, 
	asset_source_name):

	q = Query()
	s_sk = systemdb.search(q.name == source_name)[0]['sk']
	a_pk = systemdb.search(q.name == asset_source_name)[0]['pk']

	b = Builder(secret = s_sk, network='TESTNET')
	b.append_change_trust_op(asset_name, a_pk, '1000000')

	b.sign()
	response = b.submit()

	print response

def send_asset(
	systemdb,
	source_name, 
	asset_name, 
	asset_source_name, 
	amount, 
	recipient_name):

	q = Query()
	a_sk = systemdb.search(q.name == source_name)[0]['sk']
	r_pk = systemdb.search(q.name == recipient_name)[0]['pk']

	b = Builder(secret = a_sk, network='TESTNET')
	if asset_source_name == None:
		b.append_payment_op(r_pk, amount, asset_name, None)
	else:
		as_pk = systemdb.search(q.name == asset_source_name)[0]['pk']
		b.append_payment_op(r_pk, amount, asset_name, as_pk)
	
	b.sign()
	response = b.submit()

	print response

def make_offer(
	systemdb,
	source_name, 
	asset_name, 
	asset_source_name, 
	amount, 
	quote_name, 
	quote_source_name, 
	price, 
	offer__id):
	
	q = Query()
	a_sk = systemdb.search(q.name == source_name)[0]['sk']
	b = Builder(secret = a_sk, network = 'TESTNET')

	if asset_source_name == None:

		q_pk = systemdb.search(q.name == quote_source_name)[0]['pk']
		b.append_manage_offer_op(asset_name, None, quote_name, q_pk,
			amount, price, offer_id = offer__id)

	elif quote_source_name == None:

		as_pk = systemdb.search(q.name == asset_source_name)[0]['pk']
		b.append_manage_offer_op(asset_name, as_pk, quote_name, None,
			amount, price, offer_id = offer__id)
	else:

		as_pk = systemdb.search(q.name == asset_source_name)[0]['pk']
		q_pk = systemdb.search(q.name == quote_source_name)[0]['pk']
		b.append_manage_offer_op(asset_name, as_pk, quote_name, q_pk,
			amount, price, offer_id = offer__id)

	b.sign()
	response = b.submit()

	print response

def make_data_entry(
	systemdb,
	source_name, 
	key, 
	value):

	q = Query()
	a_sk = systemdb.search(q.name == source_name)[0]['sk']
	b = Builder(secret = a_sk, network='TESTNET')

	b.append_manage_data_op(name, message)
	b.sign()
	response = b.submit()

	print response



def genptxs(
	systemdb,
	timestamp):
	"""generates contract ptxs 1-3 given systemdb, including a contract manifest
		in production, will add ptxs will be hosted along with manifest on e.g. IPFS

	"""

	q = Query()
	a_sk = systemdb.search(q.name == 'Contract')[0]['sk']
	a_pk = systemdb.search(q.name == 'Contract')[0]['pk']
	pr_pk = systemdb.search(q.name == 'Printer')[0]['pk']
	pi_pk = systemdb.search(q.name == 'Pipe')[0]['pk']

	UND = systemdb.search(q.type == 'manifest')[0]['UND']
	UND_pk = systemdb.search(q.type == 'manifest')[0]['UND_source']
	QUO = systemdb.search(q.type == 'manifest')[0]['QUO']
	QUO_pk = systemdb.search(q.type == 'manifest')[0]['QUO_source']

	strike = systemdb.search(q.type == 'manifest')[0]['strike']
	size = systemdb.search(q.type == 'manifest')[0]['size']

	address = Address(address=a_pk, network='TESTNET')
	address.get()

	####2 PREAUTH TX ONE #####

	b = Builder(
		secret = str(a_sk), 
		horizon_uri = 'https://horizon.stellar.org',
		network = 'TESTNET', 
		sequence = int(address.sequence)+3)
	"""seq incremented by two bc acct will need to add hash signer, data entry, and lock
	"""

	strikeXsize = str(int(strike)*int(size))

	b.append_payment_op(pr_pk, '0.5', 'OCA', pr_pk)
	if QUO_pk == None:
		b.append_payment_op(pi_pk, strikeXsize, QUO, asset_issuer=None)
	else:
		b.append_payment_op(pi_pk, strikeXsize, QUO, QUO_pk)


	b.append_manage_offer_op('SPA', pr_pk, 'OCA', pr_pk, '0.0000001', '5000000', offer_id=0)
	b.append_manage_offer_op('GTA', pr_pk, 'SPA', pr_pk, '1', '0.0000001', offer_id=0)
	price = str(float(1)/int(size))
	b.append_manage_offer_op(UND, UND_pk, 'GTA', pr_pk, str(size), price, offer_id=0)

	envelope1 = b.gen_te()
	hashish1 = envelope1.hash_meta()
	xdr1 = b.gen_xdr()

	systemdb.insert({
		'type': 'ptx',
		'name': 'ptx1',
		'xdr': xdr1
		})

	####2 PREAUTH TX TWO #####

	b2 = Builder(
		secret = a_sk, 
		horizon_uri ='https://horizon.stellar.org',
		network = 'TESTNET', 
		sequence = int(address.sequence)+3)

	b2.append_payment_op(pi_pk, str(strike), UND, UND_pk)
	b2.append_set_options_op(master_weight=1, low_threshold=0, med_threshold=0, high_threshold=0)

	envelope2 = b2.gen_te()
	hashish2 = envelope2.hash_meta()
	xdr2 = b2.gen_xdr()

	systemdb.insert({
		'type': 'ptx',
		'name': 'ptx2',
		'xdr': xdr2
		})

	####2 PREAUTH TX THREE #####

	b3 = Builder(
		secret = a_sk, 
		horizon_uri ='https://horizon.stellar.org',
		network = 'TESTNET', 
		sequence = int(address.sequence)+4)

	b3.append_set_options_op(master_weight=1, low_threshold=0, med_threshold=0, high_threshold=0)

	envelope3 = b3.gen_te()
	hashish3 = envelope3.hash_meta()
	xdr3 = b3.gen_xdr()

	systemdb.insert({
		'type': 'ptx',
		'name': 'ptx3',
		'xdr': xdr3
		})

 	bX = Builder(secret = a_sk, network='TESTNET')
	bX.append_pre_auth_tx_signer(hashish1, 1, source=None)
	bX.append_pre_auth_tx_signer(hashish2, 1, source=None)
	bX.append_pre_auth_tx_signer(hashish3, 1, source=None)
	bX.sign()
	print bX.submit()
 
def submit(systemdb, Account, ptxnum):
	key = 'ptx'+str(ptxnum)
	q = Query()
	xdr = systemdb.search(q.name==key)[0]['xdr']
	a_sk = systemdb.search(q.name == Account)[0]['sk']

	b = Builder(secret = a_sk, network='TESTNET')
	b.import_from_xdr(xdr)
	print b.submit()

def data(
	systemdb,
	Account, 
	name, 
	message):

	q = Query()
	a_sk = systemdb.search(q.name == Account)[0]['sk']
	b = Builder(secret = a_sk, network='TESTNET')

	b.append_manage_data_op(name, message)
	b.sign()
	print b.submit()

def lock(systemdb, Account):
	q = Query()
	a_sk = systemdb.search(q.name == Account)[0]['sk']
	b = Builder(secret = a_sk, network='TESTNET')

	b.append_set_options_op(master_weight=0, low_threshold=1, med_threshold=1, high_threshold=1)

	b.sign()

	print b.submit()