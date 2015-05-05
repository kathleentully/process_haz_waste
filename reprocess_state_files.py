import json, urllib, csv

key = json.loads(open('key.json').read())['key']
VAR_LIMIT = 50

def main():
	for year, white, total, url in [('2001','P007003 : P7. Hispanic or Latino by Race [17] : Total:  Not Hispanic or Latino:  White alone','P007001 : P7. Hispanic or Latino by Race [17] : Total population','http://api.census.gov/data/2000/sf3'),('2011','B03002_003E : B03002.  Hispanic or Latino by Race : Not Hispanic or Latino:!!White alone','B03002_001E : B03002.  Hispanic or Latino by Race : Total:','http://api.census.gov/data/2010/acs5')]:
		get = white[:white.index(':')].strip() + ',' + total[:white.index(':')].strip()
		with open(year+'/states/compiled-states.csv', 'wb') as outfile:
			writer = csv.writer(outfile)
			writer.writerow(['State',
				'3 km - Not Hispanic or Latino:  White alone',
				'3 km - Total population',
				'3 km - People of Color',
				'3 km - Percent People of Color',
				'Total - Not Hispanic or Latino:  White alone',
				'Total - Total population',
				'Total - People of Color',
				'Total - Percent People of Color',
				'Beyond - Not Hispanic or Latino:  White alone',
				'Beyond - Total population',
				'Beyond - People of Color',
				'Beyond - Percent People of Color'])
			for code,data in json.loads(open('states.json').read())['state'].iteritems():
				with open(year+'/states/'+data['name']+'-ethnicity.csv', 'rb') as csvin:
					reader = csv.reader(csvin)
					state_data = {}
					line = reader.next()
					if line[1] == 'total':
						#there are no polygons included
						state_data = {'Not Hispanic or Latino:  White alone':[0],'Total population':[0]}
					else:
						for line in reader:
							if line[0] == white:
								state_data['Not Hispanic or Latino:  White alone'] = [float(line[1])]
							elif line[0] == total:
								state_data['Total population'] = [float(line[1])]

					request = url+'?key=%s&get=%s,NAME&for=state:%s' %(key,get,code)
					try:
						while True:
							raw = urllib.urlopen(request).read()
							if raw.strip() == 'Sorry, the system is currently undergoing maintenance or is busy.  Please try again later.':
								time.sleep(5)
								print 'waiting...',
							else:
								break
						temp_data = json.loads(raw)
					except:
						print 'alert:', raw
						print 'request:', request
						break
					if temp_data:
						state_data['Not Hispanic or Latino:  White alone'].append(float(temp_data[1][0]))
						state_data['Total population'].append(float(temp_data[1][1]))
						state_data['Not Hispanic or Latino:  White alone'].append(state_data['Not Hispanic or Latino:  White alone'][1] - state_data['Not Hispanic or Latino:  White alone'][0])
						state_data['Total population'].append(state_data['Total population'][1] - state_data['Total population'][0])



					writer.writerow([data['name'],
						float(state_data['Not Hispanic or Latino:  White alone'][0]),
						float(state_data['Total population'][0]),
						float(state_data['Total population'][0]) - float(state_data['Not Hispanic or Latino:  White alone'][0]),
						0 if float(state_data['Total population'][0]) == 0 else 
						(float(state_data['Total population'][0]) - float(state_data['Not Hispanic or Latino:  White alone'][0]))/float(state_data['Total population'][0]),
						float(state_data['Not Hispanic or Latino:  White alone'][1]),
						float(state_data['Total population'][1]),
						float(state_data['Total population'][1]) - float(state_data['Not Hispanic or Latino:  White alone'][1]),
						(float(state_data['Total population'][1]) - float(state_data['Not Hispanic or Latino:  White alone'][1]))/float(state_data['Total population'][1]),
						float(state_data['Not Hispanic or Latino:  White alone'][2]),
						float(state_data['Total population'][2]),
						float(state_data['Total population'][2]) - float(state_data['Not Hispanic or Latino:  White alone'][2]),
						(float(state_data['Total population'][2]) - float(state_data['Not Hispanic or Latino:  White alone'][2]))/float(state_data['Total population'][2])])


		print 'By state reprocessing DONE'

if __name__ == '__main__':
	main()