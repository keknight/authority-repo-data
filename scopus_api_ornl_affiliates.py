import csv
import requests
import json

#creates a generator 
def firstn(n):
	num = 0
	while num < n:
		yield num
		num += 100

#enter your Scopus api key in myKey and your expected number of results in amt
myKey = #type in your api key
headers = {'accept':'application/json', 'x-els-apikey':myKey}
data, data2, data3, x = []
amt = 10812 #to do: auto-update this according to total results from first query

#the query is for ORNL's ID in Scopus, change if looking for other inst ID
url = 'https://api.elsevier.com/content/search/author?start='
query = '&query=AF-ID%2860024266%29' 
start = list(firstn(amt))

i = 0
while i < len(start):
	resp = requests.get(url + str(start[i]) + query, headers = headers)
	auth_data = resp.json()
	for item in auth_data['search-results']['entry']:
		fName = item['preferred-name']['given-name']
		lName = item['preferred-name']['surname']
		orcid = item.get('orcid', 'no orcid listed')
		eid = item.get('eid', 'no eid')
		id = item.get('dc:identifier', 'no identifier')
		docs = item.get('document-count', 'no docs listed')
		data.append([fName, lName, orcid, eid, id, docs])
	i += 1


i = 0	
while i < len(data2):
	fName = data2[i]['author-retrieval-response'][0]['author-profile']['preferred-name']['given-name']
	lName = data2[i]['author-retrieval-response'][0]['author-profile']['preferred-name']['surname']
	initials = data2[i]['author-retrieval-response'][0]['author-profile']['preferred-name']['initials']
	indName = data2[i]['author-retrieval-response'][0]['author-profile']['preferred-name']['indexed-name']
	try: 
		affName = data2[i]['author-retrieval-response'][0]['author-profile']['affiliation-history']['affiliation']
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
	data2.append([fName, lname, initials, indName, orgData])
	i += 1

i = 0	
while i < len(data3):
	name = data3[i][0]
	surname = data3[i][1]
	inis = data3[i][2]
	indNm = data3[i][3]
	try: 
		j = 0
		while j < len(data3[i][4]):
			inst = data3[i][4][j][0]
			inst2 = data3[i][4][j][1]
			inst3 = data3[i][4][j][2]
			inst4 = data3[i][4][j][3]
			x.append([name, surname, inis, indNm, inst, inst2, inst3, inst4])
			j += 1
	except KeyError:
		pass
	i += 1
with open('author_aff_data.csv', 'w', newline='', encoding = 'utf-8') as f:
	writer = csv.writer(f)
	i = 0
	while i < len(x):
		writer.writerow(x[i])
		i += 1