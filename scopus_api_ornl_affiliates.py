import csv
import requests
import json

#enter your Scopus api key in myKey
myKey = 'ENTER SCOPUS API KEY'
headers = {'accept':'application/json', 'x-els-apikey':myKey}



#creates a generator 
def firstn(n):
	num = 0
	while num < n:
		yield num
		num += 25
	

#get ORNL affiliation EIDs
def get_ornl_affiliates():
	
	auth_ids = []
	
	#Initialize json file
	with open('AUTHOR_ID_FILE', mode='w', encoding='utf-8') as f:
		json.dump({}, f)
		
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
		with open('AUTHOR_ID_FILE', mode='a', encoding = 'utf-8') as fjson:
			json.dump(auth_data['search-results']['entry'], fjson)
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
def get_auth_data(auth_ids):

	auth_affs = []
	
	with open('AUTHOR_AFFIL_FILE', mode='w', encoding='utf-8') as f:
		json.dump({}, f)

	url = 'http://api.elsevier.com/content/author/author_id/'

	i = 0	
	while i < len(auth_ids):
		resp = requests.get(url + auth_ids[i][4].split(':')[1], headers = headers)
		auth_data = resp.json()
		with open('AUTHOR_AFFIL_FILE', mode='a', encoding = 'utf-8') as fjson:
			json.dump(auth_data['author-retrieval-response'], fjson)
		fName = auth_data['author-retrieval-response'][0]['author-profile']['preferred-name']['given-name']
		lName = auth_data['author-retrieval-response'][0]['author-profile']['preferred-name']['surname']
		initials = auth_data['author-retrieval-response'][0]['author-profile']['preferred-name']['initials']
		indName = auth_data['author-retrieval-response'][0]['author-profile']['preferred-name']['indexed-name']
		try: 
			affName = auth_data['author-retrieval-response'][0]['author-profile']['affiliation-history']['affiliation']
			j = 0
			orgData = []
			while j < len(affName):
				address = affName[j]['ip-doc']['address']
				orgName = affName[j]['ip-doc']['preferred-name']
				sortName = affName[j]['ip-doc']['sort-name']
				orgId = affName[j]['ip-doc']['@id']
				orgData.append([address, orgName, sortName, orgId])
				j += 1
		except KeyError: 
			pass
		auth_affs.append([fName, lName, initials, indName, orgData])
		i += 1
		
	return auth_affs


idData = get_ornl_affiliates()
print('Total affiliates retrieved: ' + str(len(idData)))
afData = get_auth_data(idData)
print('Total author affiliations retrieved: ' + str(len(afData)))

#TODO: write function to explode hideous affiliation data, maybe normalize

with open('author_affiliation_data.csv', 'w', newline='', encoding = 'utf-8') as f:
	writer = csv.writer(f)
	i = 0
	while i < len(afData):
		writer.writerow(afData[i])
		i += 1
