import json, urllib

request = 'http://api.census.gov/data/2010/acs5/variables'
pre_data = json.loads(urllib.urlopen(request).read())

data = {}
for x in pre_data:
	if x[0][-1] == 'E':
		data[x[0]] = x[1:]
last = 'B00'
for key in sorted(data):
	if key[:3] != last:
		#raw_input('continue?')
		last = key[:3]
	if key[:3] == last:
		print key,':',data[key]

