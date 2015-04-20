import json, urllib

#full_vars = {}
last = ''
for year, stuff in {'2000':[json.loads(open('2000longformelements.json').read()),'http://api.census.gov/data/2000/sf3'],'2010':[json.loads(open('2010acs5elements.json').read()),'http://api.census.gov/data/2010/acs5']}.iteritems():
	print year, 'Variables\n' + ('='*14)
	#full_vars[year] = {}
	for group, variables in stuff[0].iteritems():
		#full_vars[year][group] = {}
		print
		print "#",group
		print
		for var in variables:
			request = stuff[1]+'/variables/%s.json' %(var)
			try:
				raw = urllib.urlopen(request).read()
				data = json.loads(raw)
			except:
				print "%s not found..." %(var)
				continue
			if last != data['concept']:
				print "##",data['concept']
				print
				last = data['concept']
			print '*',var,'-',data['label']
			#full_vars[year][var] = {'label':data['label'], 'concept':data['concept'],'total':0}
#print full_vars