#!Python 3.5

import json
from decouple import config
import requests
import pandas as pd

from Utility import append_to_json, flatten_json, firstn, append_df_to_excel

#edit .env file to include your Elsevier API key and institutional EID
inst_EID = config('INSTITUTION_EID')
myKey = config('ELSEVIER_SECRET_KEY')
headers = {'accept':'application/json', 'x-els-apikey':myKey}


#get ORNL affiliation EIDs
#raw data saved as json file in case api cuts out
def get_ornl_affiliates():
	
	auth_ids = []
	
	url = 'https://api.elsevier.com/content/search/author?start='
	
	#the query is for all affiliates of an institution using the inst. Scopus EID
	query = '&query=AF-ID%28' + inst_EID + '%29'
	
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
			orgData = []
			for item in auth_data['author-retrieval-response'][0]['author-profile']['affiliation-history']['affiliation']:
				affName = flatten_json(item)
				orgAddress = affName.get('ip-doc_address_address-part', 'n/a')
				orgCity = affName.get('ip-doc_address_city', 'n/a')
				orgAbb = affName.get('ip-doc_afdispname', 'n/a')
				orgName = affName.get('ip-doc_preferred-name_$', 'n/a')
				sortName = affName.get('ip-doc_sort-name', 'n/a')
				orgState = affName.get('ip-doc_address_state', 'n/a')
				orgCount = affName.get('ip-doc_address_country', 'n/a')
				orgZip = affName.get('ip-doc_address_postal-code', 'n/a')
				orgId = affName.get('ip-doc_@id', 'n/a')
				orgData.append([orgAbb, orgName, sortName, orgAddress, orgCity, orgCount, orgState, orgId][:])
		except (KeyError, AttributeError, TypeError): 
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


##todo: change this to pandas dataframe, explode orgData list
with open('author_affiliation_data.csv', 'w', newline='', encoding = 'utf-8') as f:
	writer = csv.writer(f)
	i = 0
	while i < len(afData):
		writer.writerow(afData[i])
		i += 1
