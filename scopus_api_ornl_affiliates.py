
#from decouple import config
import csv
import requests
import json


#TODO: add .env file to use decouple/config to manage env variables
#enter your Scopus api key in myKey
myKey = 'ENTER SCOPUS API KEY'
headers = {'accept':'application/json', 'x-els-apikey':myKey}


#helper function to append json to file as valid json
def append_to_json(_dict,path): 
    with open(path, 'ab+') as f:
		f.seek(0,2)                            	       	#Go to the end of file    
		if f.tell() == 0 :                             	#Check if file is empty
			f.write(json.dumps([_dict]).encode())  		#If empty, write an array
		else :
			f.seek(-1,2)           
			f.truncate()                           		#Remove the last character, open the array
			f.write(' , '.encode())                		#Write the separator
			f.write(json.dumps(_dict).encode())    		#Dump the dictionary
			f.write(']'.encode())                  		#Close the array


#function to flatten json output from Scopus
def flatten_json(y):
	out = {}
	def flatten(x, name = ''):
		if type(x) is dict:
			for a in x:
				flatten(x[a], name + a + '_')
		elif type(x) is list:
			i = 0
			for a in x:
				flatten(a, name)
				i += 1
		else:
			out[name[:-1]] = x
	flatten(y)
	return out
	
			
#creates a generator 
def firstn(n):
	num = 0
	while num < n:
		yield num
		num += 25
	

#get ORNL affiliation EIDs
#raw data saved as json file in case api cuts out
#TODO: change function to take any institution Scopus ID
def get_ornl_affiliates():
	
	auth_ids = []
	
	url = 'https://api.elsevier.com/content/search/author?start='
	
	#the query is for ORNL's ID in Scopus
	query = '&query=AF-ID%2860024266%29'
	
	resp = requests.get(url + '0' + query, headers = headers)
	amt = resp.json()['search-results']['opensearch:totalResults']
	print('Total affiliates: ' + amt)
	start = list(firstn(int(amt)))
	
	i = 0
	while i < len(start):
		resp = requests.get(url + str(start[i]) + query, headers = headers)
		auth_data = resp.json()
		append_to_json(auth_data, 'AUTHOR_EID_FILE.json')
		for item in auth_data['search-results']['entry']:
			fName = item['preferred-name']['given-name']
			lName = item['preferred-name']['surname']
			orcid = item.get('orcid', 'no orcid listed')
			eid = item.get('eid', 'no eid')
			id = item.get('dc:identifier', 'no identifier')
			docs = item.get('document-count', 'no docs listed')
			auth_ids.append([fName, lName, orcid, eid, id, docs])
		i += 1
	return auth_ids


#get author data based on retrieved EIDs
#raw data saved as json file in case api cuts out
def get_auth_data(auth_ids):

	auth_affs = []
	
	url = 'http://api.elsevier.com/content/author/author_id/'

	i = 0	
	while i < len(auth_ids):
		resp = requests.get(url + auth_ids[i][4].split(':')[1], headers = headers)
		auth_data = resp.json()
		append_to_json(auth_data, 'AUTHOR_AFFIL_FILE.json')
		fName = auth_data['author-retrieval-response'][0]['author-profile']['preferred-name']['given-name']
		lName = auth_data['author-retrieval-response'][0]['author-profile']['preferred-name']['surname']
		initials = auth_data['author-retrieval-response'][0]['author-profile']['preferred-name']['initials']
		indName = auth_data['author-retrieval-response'][0]['author-profile']['preferred-name']['indexed-name']
		try: 
			affName = flatten_json(auth_data['author-retrieval-response'][0]['author-profile']['affiliation-history']['affiliation'])
			j = 0
			orgData = []
			while j < len(affName):
				address = affName['ip-doc_address_address-part']
				orgCity = affName['ip-doc_address_city']
				orgAbb = affName['ip-doc_afdispname']
				orgName = affName['ip-doc_preferred-name_$']
				sortName = affName['ip-doc_sort-name']
				orgState = affName['ip-doc_address_state']
				orgCount = affName['ip-doc_address_country']
				orgZip = affName['ip-doc_address_postal-code']
				orgId = affName['ip-doc_@id']
				orgData.append([orgAbb, orgName, sortName, orgAddress, orgCity, orgCount, orgState, orgId])
				j += 1
		except KeyError: 
			pass
		auth_affs.append([fName, lName, initials, indName, orgData])
		i += 1
		
	return auth_affs


idData = get_ornl_affiliates()
print('Total affiliates retrieved: ' + str(len(idData)))
afData = get_auth_data(idData)
print('Total authors searched: ' + str(len(afData)))

##write affiliation data to flat file
##todo: write to sqlite or MongoDB

with open('author_affiliation_data.csv', 'w', newline='', encoding = 'utf-8') as f:
	writer = csv.writer(f)
	i = 0
	while i < len(afData):
		writer.writerow(afData[i])
		i += 1
