import json, csv, urllib, time

totals = {}
for year in ['2000','2010']:
	totals[year] = {'within 3km':{},'not within 3km':{}}
	for key in totals[year]:
		totals[year][key] = {'land area':0,
													'population':0,
													'population density':0,
													'percent people of color':0,
													'mean household income':0,
													'percent below poverty':0,
													'mean owner-occupied housing value':0,
													'percent with a degree':0}
									
	for i in range(1,73):
		if i not in [3,7,14,43,52] and (i < 57 or i == 72) and i not in [72,11]:
			try:
				with open('all tracts for analysis/all_tracts_%s/%02d_state.csv' %(year,i)) as csv_in:
					reader = csv.DictReader(csv_in)
					for row in reader:
						category = 'within 3km' if row['within 3km'] == '1' else 'not within 3km'
						for key in row:
							if key not in ['within 3km', 'tract ID'] and row[key] != '':
								try:
									totals[year][category][key] += float(row[key])
								except:
									print 'not a float: totals[%s][%s][%s]: %s' %(year, category,key, row[key]) 
									pass
			except:
				print 'file not read: all tracts for analysis/all_tracts_%s/%02d_state.csv' %(year,i)
				pass
	print year +':'
	for typ in totals[year]:
		print '\t%s'%(typ)
		for key in totals[year][typ]:
			print '\t\t' + key + ': ' + str(totals[year][typ][key])
		print '\t\tpopulation density: %0.2f'  %(totals[year][typ]['population']/totals[year][typ]['land area']*1000)
