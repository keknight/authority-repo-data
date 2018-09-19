##Utility file with helper functions

import json


#helper function to append json to file as valid json
def append_to_json(_dict,path): 
	with open(path, 'ab+') as f:
		f.seek(0,2)
		if f.tell() == 0:
			f.write(json.dumps([_dict]).encode())
		else:
			f.seek(-1,2)
			f.truncate()
			f.write(' , '.encode())
			f.write(json.dumps(_dict).encode())
			f.write(']'.encode())
			

#function to flatten json output 
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
	
			
#creates a number generator
#change num #= to increment by a different amount
def firstn(n):
	num = 0
	while num < n:
		yield num
		num += 25