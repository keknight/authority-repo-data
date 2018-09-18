

####TO DO: COMBINE THIS FILE WITH OTHER SCOPUS API FILES INTO LOCAL LIBRARY#########

import pandas as pd
from pandas_datareader import wb
import requests
import itertools
import json

myKey = #type in your api key
headers = {'accept':'application/json', 'x-els-apikey':myKey}

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


#get country data from pandas_datareader (World Bank data)
country_data = wb.get_countries().fillna('none')
writer = pd.ExcelWriter('country_data.xlsx')
country_data.to_excel(writer, 'Country Data')
writer.save()

#get affiliation data from Scopus, assumes you have a list of eids in a csv file
df = pd.read_csv('scopus_author_data.csv', encoding = 'ISO-8859-1')
eids = df[['eid']].as_matrix()
eids = eids.tolist()
eids = list(itertools.chain.from_iterable(eids))
url = 'http://api.elsevier.com/content/author/author_id'


authData = []
i = 0
while i < len(eids):
	resp = requests.get(url + str(eid[i]), headers = headers)
	auDat = resp.json()	
	fName = auDat['author-retrieval-response'][0]['author-profile']['preferred-name']['given-name']
	lName = auDat['author-retrieval-response'][0]['author-profile']['preferred-name']['surname']
	initials = auDat['author-retrieval-response'][0]['author-profile']['preferred-name']['initials']
	indName = auDat['author-retrieval-response'][0]['author-profile']['preferred-name']['indexed-name']
	try: 
		affName = flatten_json(auDat['author-retrieval-response'][0]['author-profile']['affiliation-history']['affiliation'])
		j = 0
		orgData = []
		while j < len(affName):
			orgAddress = affName['ip-doc_address_address-part']
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
	authData.append([fName, lname, initials, indName, orgData])
	i += 1
	
with open('author_aff_data.csv', 'w', newline='', encoding = 'utf-8') as f:
	writer = csv.writer(f)
	i = 0
	while i < len(authData):
		writer.writerow(authData[i])
		i += 1
