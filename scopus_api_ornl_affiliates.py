#!Python 3.5

import json
from decouple import config
import requests
import pandas as pd

from Utility import append_to_json, flatten_json, firstn, append_df_to_excel

#edit .env file to include your Elsevier API key, institutional EID, and path to your data file
inst_EID = config('INSTITUTION_EID')
myKey = config('ELSEVIER_SECRET_KEY')
dataFile = config('DATA_FILE')

headers = {'accept':'application/json', 'x-els-apikey':myKey}



#get ORNL affiliation EIDs
#raw data saved as json file
#returns a list
def get_ornl_affiliates():
	
	auth_ids = []
	
	url = 'https://api.elsevier.com/content/search/author?start='
	
	#the query is for all affiliates of an institution using the institution's Scopus EID
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
			alt_eid = item.get('dc:identifier', 'no identifier')
			docs = item.get('document-count', 'no docs listed')
			auth_ids.append([fName, lName, orcid, eid, alt_eid, docs])
		i += 1
	return auth_ids


#get author data based on retrieved EIDs
#raw data saved as json file 
#processed data written to Excel file for each eid looked up
#returns a list
def get_auth_data(auth_ids):

	auth_affs = []
	
	url = 'http://api.elsevier.com/content/author/author_id/'

	i = 0	
	while i < len(auth_ids):
		eid = auth_ids[i][4].split(':')[1]
		pubs = auth_ids[i][-1]
		orcid = auth_ids[i][2]
		resp = requests.get(url + eid, headers = headers)
		auth_data = resp.json()
		append_to_json(auth_data, 'AUTHOR_AFFIL_FILE.json')
		fName = auth_data['author-retrieval-response'][0]['author-profile']['preferred-name']['given-name']
		lName = auth_data['author-retrieval-response'][0]['author-profile']['preferred-name']['surname']
		initials = auth_data['author-retrieval-response'][0]['author-profile']['preferred-name']['initials']
		indName = auth_data['author-retrieval-response'][0]['author-profile']['preferred-name']['indexed-name']
		affCur = auth_data['author-retrieval-response'][0]['author-profile']['affiliation-current']['affiliation']['ip-doc'].get('afdispname', 'no listed current affiliation')
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
		orgData = [list(map(lambda orgData: orgData + ' | ', org)) for org in orgData] #adding delimiters
		
		#create dataframe, write to excel
		columns = ['EID', 'First Name', 'Last Name', 'Initials', 'Indexed Name', 'Current Affiliation', 'Affiliation History', 'Pubs in Scopus']
		data = pd.DataFrame({'EID': [eid], 'First Name': [fName], 'Last Name':[lName], 'Initials':[initials], 'Indexed Name': [indName], 'Current Affiliation':[affCur], 'Pubs in Scopus':[pubs]})
		data = data.reindex(columns = columns)
		data = data.astype('object')
		data.at[0, 'Affiliation History'] = orgData
		append_df_to_excel(dataFile, data, index = False)
		i += 1
		
	return auth_affs


idData = get_ornl_affiliates()
print('Total affiliates retrieved: ' + str(len(idData)))
afData = get_auth_data(idData)
print('Total authors searched: ' + str(len(afData)))

##write affiliation data to flat file
##todo: write to sqlite or MongoDB
