import json, csv, urllib, time

totals = {}
for year in ['2000','2010']:
	totals[year] = {'within 3km':{},'not within 3km':{}}
	for key in totals[year]:
		totals[year][key] = {'tract ID':0.,
				                'within 3km':0.,
				                'land area':0.,
				                'population':0.,
				                'population density':0.,
				                'white':0., 
				                'percent people of color':0.,
				                'aggregate income':0.,
				                'income population':0.,
				                'mean household income':0.,
				                'poverty under 1':0., 
				                'poverty population':0.,
				                'percent below poverty':0.,
				                'housing value':0.,
				                'housing population':0., 
				                'mean owner-occupied housing value':0.,
				                'school population':0., 
				                'with a degree':0.,
				                'percent with a degree':0}
									
	for i in range(1,73):
		if i not in [3,7,14,43,52] and (i < 57 or i == 72) and i not in [72,11]:
			try:
				with open('all tracts for analysis/all_tracts_%s/raw/%02d_state.csv' %(year,i)) as csv_in:
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
	for typ in totals[year]:
		for key in ['land area','population','population density','white','percent people of color','aggregate income','income population','mean household income','poverty under 1','poverty population','percent below poverty','housing value','housing population','mean owner-occupied housing value','school population','with a degree','percent with a degree']:
			print '%s\t%s\t%s\t%13d' %(year,typ,key,totals[year][typ][key])
		
