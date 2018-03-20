import csv
import requests
import json
import pandas as pd
import itertools

#assumes you have a spreadsheet of scopus document eids

myKey = #type in your api key 
headers = {'accept':'application/json', 'x-els-apikey':myKey}
url = 'http://api.elsevier.com/content/abstract/eid/'

#change file name to spreadsheet with eids in it
df = pd.read_excel('scopus_doc_data.xlsx')
eids = df[['EID']].as_matrix()
eids = eids.tolist()
eids = list(itertools.chain.from_iterable(eids))

i = 0
docData = []

while i < len(eids):
	resp = requests.get(url + str(eids[i]), headers = headers)
	doc = resp.json()
	try:
		docAb = doc['abstracts-retrieval-response']['coredata']['dc:description']
		docTit = doc['abstracts-retrieval-response']['coredata']['dc:title']
		docCite = doc['abstracts-retrieval-response']['coredata']['citedby-count']
	except KeyError:
		pass
	docData.append([docAb, docTit, docCite, eids[i]])
	i += 1

with open('doc_citation_data.csv', 'w', newline='', encoding = 'utf-8') as f:
	writer = csv.writer(f)
	i = 0
	while i < len(docData):
		writer.writerow(docData[i])
		i += 1