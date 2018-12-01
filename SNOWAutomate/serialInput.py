import json
import requests
from collections import defaultdict

'--------------------Global Variables-------------------'
company_groupings = defaultdict(list)
invalid_serial = list()
valid_companies = list()
serial1 = list()


#Main Program Script
def main():
	#Main Variables
	task_response = True
	serial = list()
	
	#Testing Instances
	#serial = ['VC05100004532','VC05100002916','VC05100002358','VC05100002164']
	with open("testJson.json") as infile:
		data=json.load(infile)
	valid_companies.append(data['Company'])
	
	for x in data['Serial_Number']:
		serial.append(x['SN'])	
	
	#Remove empty serial numbers
	for x in serial:
		if x.strip() != "" and x not in serial1:
			serial1.append(x)
		elif x in serial1:
			newTuple = ([x,"Duplicate Value"])
			invalid_serial.append(newTuple)
	#Pull Provisioning Tasks from Service Now	
	openP = obtainProvisioningTasks()
	
	#Verify Serial Number existence in Service Now and if companies match to said serial number
	companyCheck(listPull(serial1), valid_companies)
	print("\n----------Serial Number Errors----------\n")
	for key,values in invalid_serial:
		print(key,values)
	print("\n----------Provisioning Task Assignment----------\n")

	while task_response:
		assignTask = input("Start Task Assignment?(y/n): ")
		if assignTask.lower().strip() == 'y':
			assignProvisioningTask(company_groupings, openP)
			task_response = False
		elif assignTask.lower().strip() == 'n':
			print("\nProgram Terminated")
			task_response = False

def listPull(listScan: list):
	'''The purpose of this function is to verify the serial number in multiple ways: (1) Verify that the serial number assigned correctly to the right company, (2) Identify that the status is to 1 - Provisioning with the state being Open'''
	
	print('----------Checking Serial-Number in Service Now----------\n')
	validSerialNumber = []
	
	for y in listScan:
		sysparmOffset = 0
		bool1 = True
		while bool1:
			offsetCheck = 0
			
			#Rest Api call = Obtain serial Numbers that match inputted serial numbers
			response = requests.get('https://qosconsultingdev.service-now.com/api/now/table/u_velocloud?sysparm_display_value=True&sysparm_exclude_reference_link=False&sysparm_offset='+str(sysparmOffset), auth=('btung', 'Mychick3n'), headers={"Content-Type":"application.json","Accept":"application/json"},params={'serial_number': y})			
			
			#Identify whether serial number is found in Service Now
			if len(response.json()['result']) == 0:
				print('Serial Number not found in SNOW/Entered Incorrectly:',y,'\n')
				invalid_serial.append(y)
			else:
				print('Velocloud Serial Number Found: ',y,'\n')
				validSerialNumber.append(response.json()) 
			
			#Sysparm_offset to iterate through tables  more than 10000
			sysparmOffset += 10000
			for counter in response.json()['result']:
				if 'short_description' in counter:
					offsetCheck += 1

			#Stops the iteration of lists
			if offsetCheck != 10000:
				bool1 = False

	return validSerialNumber
	
def companyCheck(existingSN: list, validName: list):
	'''The purpose of this function is check the company to the serial number. This will determine the relation between SN and company'''
	
	print("----------Checking if serial-number is valid for companies or is in stock----------\n")
	
	for x in existingSN:
		for y in x['result']:
			#Pull Necessary data for Company & Configuration Item verification/integration
			companyLink = y['company']['link']
			configurationItemGrab = y['asset']['link']

			#API calls for the following: (1)Configuration Item by asset tag and (2)Company by Task
			config = requests.get(configurationItemGrab,auth=('btung','Mychick3n'),headers={"Content-Type":"application/json","Accept":"application/json"})
			response = requests.get(companyLink,auth=('btung','Mychick3n'),headers={"Content-Type":"application/json","Accept":"application/json"}) 
			
			#Obtain Configuration Item from created serial Number
			configurationItem = config.json()['result']['ci']['value']
			configurationItemLink = config.json()['result']['ci']['link']
			
			getStatus = requests.get(configurationItemLink,auth=('btung','Mychick3n'),headers={"Content-Type":"application/json","Accept":"application/json"})
			
			print("Serial Number:",y['serial_number'],'is currently assigned to',str(response.json()['result']['name']))
			
			#Create tuple of system id and serial_number for individual Veloclouds
			newTuple = tuple([y['serial_number'],y['sys_id'],configurationItem])
			
			#Index check for for company name and grouping information to the company(from the tuple)
			if response.json()['result']['name'] in validName and getStatus.json()['result']['install_status'] == '6':
				company_groupings[response.json()['result']['name']].append(newTuple)
				
				patchStatusToInstall = requests.patch(configurationItemLink,auth=("btung","Mychick3n"),headers={"Content-Type":"application/json","Accept":"application/json"},data='{"install_status":"4"}')
				print("Company and Serial Number Valid, added to database\n")
			
			elif response.json()['result']['name'] == "QOS Networks" and getStatus.json()['result']['install_status'] =='6':
				company_groupings[response.json()['result']['name']].append(newTuple)
				patchStatusToInstall = requests.patch(configurationItemLink,auth=("btung","Mychick3n"),headers={"Content-Type":"application/json","Accept":"application/json"},data='{"install_status":"4"}')

				print("Serial number is in stock at QOS Networks, added to database\n")
			else:
				if response.json()['result']['name'] not in ['QOS Networks',valid_companies[0]] and getStatus.json()['result']['install_status'] =='6':
					newTuple = ([y['serial_number'],"Company Serial Number does not match: Check Serial Number Company in Service Now"])
				
				elif response.json()['result']['name'] in ['QOS Networks',valid_companies[0]] and getStatus.json()['result']['install_status'] !='6':
					newTuple = ([y['serial_number'],"Invalid install_status: Please check status of Serial Number"])
				else:
					newTuple = ([y['serial_number'],"Serial Number issue(s) detected: Please check Serial Number company and status through configuration item"])
				invalid_serial.append(newTuple)
				
				print("Invalid company provisioning match, serial number",y['serial_number'],"not added.\n")
			

def obtainProvisioningTasks():
	'''The purpose of this function is to collect open provisioning tasks under the parameters: "state = Open" and "short_description = 1 - Provisioning"'''
	
	#Local Variables
	bool1 = True
	sysparmOffset = 0
	dd1 = defaultdict(list)
	
	#Obtain open provisioning tasks
	while bool1:
		offsetCheck = 0
		response = requests.get('https://qosconsultingdev.service-now.com/api/now/table/pm_project_task?sysparm_display_value=True&sysparm_fields=state%2Ctask%2Ccompany%2Csys_id&sysparm_offset'+str(sysparmOffset), auth=('btung','Mychick3n'),headers = {'Content-Type':'application/json','Accept':'application/json'},params={'short_description': '1 - Provisioning','state':'Open'})

		for x in response.json()['result']:
			if "short_description" in x:
				offsetCheck += 1
			
			#Grouping companies with task name and system_identification
			newTuple = tuple([x['task'],x['sys_id']])
			dd1[dict(x['company'])['display_value']].append(newTuple)
		
		sysparmOffset += 10000
		if offsetCheck != 10000:
			bool1 = False
	return dd1

def assignProvisioningTask(dd: 'defaultdict(list)', provisioningDictionary: 'defaultdict(list)'):
	'''Assign serial number to valid, open provisioning task in ServiceNow'''
	
	#Local Variables
	choiceOfStock = True
	companySerialOnHand = dd
	stock = list()
	snow = list()
	inputList = list()
	finalList = list()
	assignedIndex = list()
	unassignedSN = list()
	assignedSN = list()
	requestCount = 0
	
	#Verify whether user wants to assign ones in stock and/or Veloclouds that are already assigned to the company
	while choiceOfStock:
		newAnswer=input('Include the Velocloud(s) not assigned to the company and currently in stock at QOS Networks?(y/n): ')
		if newAnswer.lower().strip() == "y":
			choiceOfStock = False
		elif newAnswer.lower().strip() == "n":
			try:
				del companySerialOnHand["QOS Networks"]
			except KeyError:
				pass
			choiceOfStock = False
	
	#Format Dictionaries for local serial numbers
	for key,values in companySerialOnHand.items():
		for x in values:
			newTuple = tuple([key,x])
			stock.append(newTuple)
			unassignedSN.append(x[0]) 
	
	#Format Service Now information
	for key,values in provisioningDictionary.items():
		for x in values:
			newTuple = [key,x,0]
			snow.append(newTuple)
	
	
	#Assign Provisioning Tasks
	for stock1 in stock:
		for snow1 in snow:
			if stock1[0] == valid_companies[0] and stock1[0]==snow1[0] and snow1[-1] != 1:
				list1 = [snow1[0],snow1[1]+stock1[1]]	
				snow1[-1] = 1
				finalList.append(list1)
				break

			elif stock1[0] == "QOS Networks" and snow1[-1] != 1 and snow1[0] not in stock:
				list1 = [snow1[0],snow1[1]+stock1[1]]
				snow1[-1] = 1
				finalList.append(list1)
				break
	for x in finalList:
		if x[1][2] in unassignedSN:
			unassignedSN.remove(x[1][2])

	print()
	#Patch Open Changes
	for x in finalList:
		
		#Local Variables
		requestCount += 1
		headers = {"Content-Type":"application/xml","Accept":"application/xml"}
		
		#Obtain parent URL
		url = 'https://qosconsultingdev.service-now.com/api/now/table/pm_project_task/'+str(x[1][1])
		parentTaskUrl = requests.get(url,auth=("btung","Mychick3n"),headers={"Content-Type":"application/json","Accept":"application/json"})
		newURL = parentTaskUrl.json()['result']['parent']['link']
		
		print("Assigned "+x[1][2]+" to task number: "+x[1][0])
			
		#Patching configuration item to a provisioning task & change state from Open to Pending
		addCIToProvTask = requests.patch(url,auth=("btung","Mychick3n"),headers=headers,data="<request><entry><cmdb_ci>"+str(x[-1][-1])+"</cmdb_ci><state>Pending</state></entry></request>")
		
		#Patching configuration item to corresponding parent task
		addCIToParent = requests.patch(newURL,auth=("btung","Mychick3n"),headers=headers,data="<request><entry><cmdb_ci>"+str(x[-1][-1])+"</cmdb_ci></entry></request>")
		
		#Close Provisioning Task (Consult with August)
		closeProvisioningTask = requests.patch(url,auth=("btung","Mychick3n"),headers=headers,data="<request><entry><state>Closed Complete</state></entry></request>")
	
		print("\n"+str(requestCount)+"-Request Patch Complete\n")
	print()

	if len(unassignedSN)>0:
		print("\nThe following serial numbers have not been added to task (More Serial Numbers than Task): "+str(unassignedSN))
	else:
		pass
def easyView(list1: list):
	'''Open JSON in a readable format'''
	for x in list1:
		for y in x['result']:
			for z in y.items():	
				print(str(z)+'\n')

if __name__ == '__main__':
	main()
