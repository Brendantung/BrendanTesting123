#-------------SYSLOG GENERATOR ---------------

# Made for generating a log file in Proficio's wanted format
#
# REQUIREMENTS
# - None
#
# COMMAND USAGE
# - python2 sysLogGen.py
#
# Created By: August Gross/Brendan Tung

# =============== SYSLOG GENERATOR ===============


# --------------- IMPORT STATEMENTS --------------

# For making calls to velocloud
import requests

# For parsing requests events
import json

# For Python syslog socket
import socket
# =============== IMPORT STATEMENTS ==============

# -------------------- GLOBALS -------------------

# Public Storage VCO
VCO = 'vco104-usca1'

# Syslog Server IP (ENTER IN SYSLOG IP AND PORT HERE)
SYSLOG_IP = '10.0.0.128'
PORT = 5000

# Public Storage Enterprise
ENTERPRISE_ID = 1

# Bytes List
BYTELIST = list()

# Calender Key for Syslog Time Format
CALENDER = {'01':'Jan','02':'Feb','03':'Mar','04':'Apr','05':'May','06':'Jun','07':'Jul','08':'Aug','09':'Sep','10':'Oct','11':'Nov','12':'Dec'}

# Velocloud Event List (Example)
'''
VELOCLOUD EVENT LIST (Example):
{'eventTime': '2018-12-12T16:41:43.000Z',
'event': 'LINK_ALIVE',
'id': 10251200,
'enterpriseUsername': None,
'edgeName': 'PSA022303 / PS-1327 / Citrus Heights, CA',
'severity': 'INFO',
'detail': '{"logicalId":"2a:30:44:27:2f:40:0000", "internalId":"00000002-cedd-4558-bb76-ead7ddf1c65b"}',
'category': 'NETWORK',
'message': 'Link GE2 is no longer DEAD'}
''' 

# --------------------- MAIN ---------------------

# Pulls all events from a given Enterprise, then submit to Syslog Server

# ARGUMENTS:
# - None

# OUTPUT:
# - None

def main():

	# Username and Password for Public Storage VCO
	USERNAME = "api@qos-consulting.com"
	PASSWORD = "q1E$Xms47iTiMCec*j"

	# Create a requests session that we will send all of our requests through
	vcoSession = requests.Session()

	# Generate a login cookie for the Public Storage VCO
	login = vcoSession.post('https://vco104-usca1.velocloud.net/portal/login/enterpriseLogin',data = { "username": USERNAME,"password": PASSWORD,"backward_compatibility_mode": True },headers = { "Content-Type": "application/json" })

	# The data used to pull events the way we want
	eventData = {"enterpriseId": ENTERPRISE_ID,"filter": {"limit":None},"detail": True}

	# The payload sent for completing our event pull
	payload = {"jsonrpc": "2.0","id": 1,"method": "event/getEnterpriseEvents","params": eventData }

	# Pull events from the VCO
	events = vcoSession.post('https://vco104-usca1.velocloud.net/portal/', data = json.dumps(payload),headers = {"Content-Type": "application/json" },verify = True)
	
	# Format the events
	events = events.json()["result"]
		
	# Takes each event and pulls the relevant information
	for event in events["data"]:
		
		base = event['eventTime'].split('-')
		time = CALENDER[base[1]] + " " + base[-1][:2] + " " +  base[-1][3:11]
		
		# Generate the Message
		syslog_msg = (time + " host CEF:0|VeloCloud|VeloCloud|v1.0|" + str(event["id"]) + "|" + str(event["event"]) + "|" + str(event["severity"]) + "|msg=" + str(event["message"]) + " " + "deviceExternalId=Edge:" + str(event["edgeName"]) + "\n")

		# Convert syslog string message into bytes
		arr = bytearray(syslog_msg,'utf-8')
		BYTELIST.append(arr)
		
	# Send Event Message to Syslog
	for x in BYTELIST:
		try:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((SYSLOG_IP,PORT))
			s.sendall(x)
		except:
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect((SYSLOG_IP,PORT))
			s.sendall(x)
	s.close()
# ===================== MAIN =====================

# Causes "main" function to run automatically upon start
if __name__ == "__main__":
	main()

