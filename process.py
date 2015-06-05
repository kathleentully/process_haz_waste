#import simplejson as json
import json, urllib, csv

key = json.loads(open('key.json').read())['key']
VAR_LIMIT = 50

def run_each(year,clustered=False,region=None,state=None):
	data = json.loads(open('20'+year+'-hazwaste.json').read())
	polygons = {"1.000000 km":{},"3.000000 km":{},"5.000000 km":{}}
	cluster_count = {'total_clustered':0,'total_points':0} #distribution of cluster sizes
	points = set()
	land_area = {"1.000000 km":0.,"3.000000 km":0.,"5.000000 km":0.}

	if region:
		state = json.loads(open('states.json').read())
		state = ("Region "+str(region),state["EPA Regions"]["Region "+str(region)])
	for group in data:
		for d in ["1.000000 km","3.000000 km","5.000000 km"]:
			if d in group["areaAroundPoint"]:
				if "polygons" in group["areaAroundPoint"][d] and (not clustered or len(group["areaAroundPoint"]["points"])>1):
					for poly in group["areaAroundPoint"][d]["polygons"]:
						if (state and poly[:2] in state[1]) or not state:
							try:
								polygons[d][poly] = group["areaAroundPoint"][d]["polygons"][poly] if poly not in polygons[d] else polygons[d][poly] + group["areaAroundPoint"][d]["polygons"][poly]
							except:
								polygons[d][poly] = 1.
				if "land_area" in group["areaAroundPoint"][d] and (not clustered or len(group["areaAroundPoint"]["points"])>1):
					land_area[d] += group["areaAroundPoint"][d]["land_area"]
		cluster_count["total_points"] += len(group["areaAroundPoint"]["points"])
		for p in group["areaAroundPoint"]["points"]:
			if p["id"] in points:
				print p
			else:
				points.add(p["id"])
		if len(group["areaAroundPoint"]["points"]) > 1:
			cluster_count["total_clustered"] += 1
		if len(group["areaAroundPoint"]["points"]) in cluster_count:
			cluster_count[len(group["areaAroundPoint"]["points"])] += 1
		else:
			cluster_count[len(group["areaAroundPoint"]["points"])] = 1
	for d in ["1.000000 km","3.000000 km","5.000000 km"]:
		if len(polygons[d]) == 0:
			del polygons[d]
		if land_area[d] == 0:
			del land_area[d]
	cluster_count['polygon_count'] = sum([len(polygons[l]) for l in polygons])
	return cluster_count, polygons, land_area

def sort_polygons(polygons):
	sorted_polys = {}
	for d in polygons:
		sorted_polys[d] = {}
		for tract in sorted(polygons[d]):
			if tract[:2] not in sorted_polys[d]:
				sorted_polys[d][tract[:2]] = {tract[2:5]: {tract[5:]:polygons[d][tract]}}
			elif tract[2:5] not in sorted_polys[d][tract[:2]]:
				sorted_polys[d][tract[:2]][tract[2:5]] = {tract[5:]:polygons[d][tract]}
			elif tract[5:] not in sorted_polys[d][tract[:2]][tract[2:5]]:
				sorted_polys[d][tract[:2]][tract[2:5]][tract[5:]] = polygons[d][tract]
			else:
				sorted_polys[d][tract[:2]][tract[2:5]][tract[5:]] += polygons[d][tract]
			assert sorted_polys[d][tract[:2]][tract[2:5]][tract[5:]] <= 1.
	return sorted_polys

def get_data(url,variables, polygons):
	full_vars = {}
	for var in variables:
		request = url+'/variables/%s.json' %(var)
		try:
			raw = urllib.urlopen(request).read()
			data = json.loads(raw)
		except:
			print "%s not found..." %(var)
			continue
		full_vars[var] = {'label':data['label'], 'concept':data['concept'],'total':0}
		for d in polygons:
			full_vars[var][d] = 0
	poly_map = sort_polygons(polygons)

	#get all states first
	data = None
	i = 0
	for j in range(min(len(full_vars.keys()),VAR_LIMIT-1),len(full_vars.keys()),VAR_LIMIT-1)+[len(full_vars.keys())]:
		request = url+'?key=%s&get=%s,NAME&for=state:*' %(key,','.join(full_vars.keys()[i:j]))
		i = j
		try:
			while True:
				raw = 'Not online'
				raw = urllib.urlopen(request).read()
				if raw == 'Sorry, the system is currently undergoing maintenance or is busy.  Please try again later.':
					time.sleep(5)
					print 'waiting...',
				else:
					break
			temp_data = json.loads(raw)
		except:
			print 'alert:', raw
			print 'request:', request
			print i, j, full_vars
			break
		if not data:
			data = temp_data
		else:
			for k in range(len(temp_data)):
				data[k].extend(temp_data[k])

	for var_index in range(len(data[0])):
		if data[0][var_index] in ['NAME','state']:
			continue
		for row in range(1,len(data)):
			try: 
				full_vars[data[0][var_index]]['total'] += int(data[row][var_index])
			except:
				if data[row][var_index]:
					print 'INT issue at line 94, data row:',data[row]
				continue

	data = None

	for d in poly_map:
		for state, counties in poly_map[d].iteritems():
			for county, tracts in counties.iteritems():
				for tract, proportion in tracts.iteritems():
					data = []
					i = 0
					for j in range(min(len(full_vars.keys()),VAR_LIMIT-1),len(full_vars.keys()),VAR_LIMIT-1)+[len(full_vars.keys())]:
						request = url+'?key=%s&get=%s,NAME&for=tract:%s&in=state:%s,county:%s' %(key,','.join(full_vars.keys()[i:j]),tract,state,county)
						i = j
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
						if not data:
							data = temp_data
						else:
							for k in range(len(temp_data)):
								data[k].extend(temp_data[k])
					for var_index in range(len(data[0])):
						if data[0][var_index] in ['NAME','state','county','tract']:
							continue
						for row in range(1,len(data)):
							try: 
								full_vars[data[0][var_index]][d] += float(data[row][var_index])*proportion
							except:
								if data[row][var_index]:
									print 'INT issue at line 125,',var_index,'data row:',data[row]
								continue
	return full_vars

def get_data_2000(variables, polygons):
	return get_data('http://api.census.gov/data/2000/sf3',variables,polygons)
def get_data_2011(variables, polygons):
	return get_data('http://api.census.gov/data/2010/acs5',variables,polygons)

def csv_output(folder,variables,stats,results,land_area,totals=None,prefix='',save_cluster_stats=False):
	if save_cluster_stats:
		with open(folder+'/'+prefix+'cluster_stats.csv', 'wb') as csvfile:
			csvwriter = csv.writer(csvfile)
			for key in sorted(stats):
				csvwriter.writerow([key, stats[key]])
	new = False
	if not totals:
		totals = {}
		new = True
	for group in variables:
		if new:
			if folder[2] == '1':
				totals[group] = get_data_2011(variables[group],results)
			if folder[2] == '0':
				totals[group] = get_data_2000(variables[group],results)
		with open(folder+'/'+prefix+group+'.csv', 'wb') as csvfile:
			csvwriter = csv.writer(csvfile)
			csvwriter.writerow(['Variable']+[dist for dist in sorted(totals[group][totals[group].keys()[0]]) if dist not in ['concept', 'label'] ]+['Beyond'])
			for key in totals[group]:
				csvwriter.writerow([str(key+' : '+totals[group][key]['concept']+' : '+totals[group][key]['label'])]
					+[totals[group][key][dist] for dist in sorted(totals[group][key]) if dist not in ['concept', 'label']]
					+[totals[group][key]['total']-sum([totals[group][key][dist] for dist in sorted(totals[group][key]) if dist not in ['concept', 'label','total']])])
			if group[:6] == 'basics' and folder[:4] == '2011':
				TOTAL_LAND_11 = 9158021763139
				csvwriter.writerow(["ALAND10 : 2010 Census land area (square meters)"]+
					[land_area[dist] for dist in sorted(land_area) if dist not in ['concept', 'label']]+
					[TOTAL_LAND_11, TOTAL_LAND_11-sum([land_area[dist] for dist in sorted(land_area) if dist not in ['concept', 'label']])])
			elif group[:6] == 'basics' and folder[:4] == '2001':
				TOTAL_LAND_01 = 9158021762569
				csvwriter.writerow(["ALAND00 : 2000 Census land area (square meters)"]+
					[land_area[dist] for dist in sorted(land_area) if dist not in ['concept', 'label']]+
					[TOTAL_LAND_01, TOTAL_LAND_01-sum([land_area[dist] for dist in sorted(land_area) if dist not in ['concept', 'label']])])
	return totals

def main():
	print 'Starting 2000...'

	vars_00 = json.loads(open('2000longformelements.json').read())

	stats_00_135, results_00_135, land_area_00_135 = run_each('01-135')
	csv_output('2001/135',{'basics2':vars_00['basics']},stats_00_135,results_00_135,land_area_00_135,save_cluster_stats=True)
	
	print '\t\t1 km, 3 km, 5 km processing DONE'

	if raw_input('\tRun 3 km apportionment data? (y/n)').strip().lower() in ['y','yes']:
		stats_00, results_00, land_area_00 = run_each('01-app')
		totals_00 = csv_output('2001/3-app',vars_00,stats_00,results_00,land_area_00,save_cluster_stats=True)
		print '\t\t3 km processing DONE'

	if raw_input('\tRun 3 km data? (y/n)').strip().lower() in ['y','yes']:
		stats_00, results_00, land_area_00 = run_each('01')
		totals_00 = csv_output('2001/3',vars_00,stats_00,results_00,land_area_00,save_cluster_stats=True)
		print '\t\t3 km processing DONE'

	if raw_input('\tRun 1 km, 3 km, 5 km data? (y/n)').strip().lower() in ['y','yes']:
		stats_00_135, results_00_135, land_area_00_135 = run_each('01-135')
		csv_output('2001/135',vars_00,stats_00_135,results_00_135,land_area_00_135,save_cluster_stats=True)
		print '\t\t1 km, 3 km, 5 km processing DONE'
	
	if raw_input('\tRun 3 km clustered data? (y/n)').strip().lower() in ['y','yes']:
		stats_00_clustered, results_00_clustered, land_area_00_clustered = run_each('01',clustered = True)
		totals_00_clustered = csv_output('2001/3-clustered',vars_00,stats_00_clustered,results_00_clustered,land_area_00_clustered)
		print '\t\t3 km clustered processing DONE'

	if raw_input('\tRun regional data? (y/n)').strip().lower() in ['y','yes']:
		for region in range(1,11):
			stats, results, land_area = run_each('01',region=region)
			totals = csv_output('2001/region '+str(region),vars_00,stats,results,land_area)
		print '\t\tRegional processing DONE'

	if raw_input('\tRun by state data? (y/n)').strip().lower() in ['y','yes']:
		for code,data in json.loads(open('states.json').read())['state'].iteritems():
			stats, results, land_area = run_each('01',state=(data['name'],[code]))
			totals = csv_output('2001/states',{'ethnicity':vars_00['ethnicity']},stats,results,land_area,prefix=data['name']+'-')
		print '\t\tBy state processing DONE'

	print '2000 DONE'

	print 'Starting 2010...'

	vars_11 = json.loads(open('2010acs5elements.json').read())

	if raw_input('\tRun 3 km apportionment data? (y/n)').strip().lower() in ['y','yes']:
		stats_11, results_11, land_area_11 = run_each('11-app')
		totals_11 = csv_output('2011/3-app',vars_11,stats_11,results_11,land_area_11,save_cluster_stats=True)
		print '\t\t3 km processing DONE'

	if raw_input('\tRun 3 km data? (y/n)').strip().lower() in ['y','yes']:
		stats_11, results_11, land_area_11 = run_each('11')
		totals_11 = csv_output('2011/3',vars_11,stats_11,results_11,land_area_11,save_cluster_stats=True)
		print '\t\t3 km processing DONE'

	if raw_input('\tRun 1 km, 3 km, 5 km data? (y/n)').strip().lower() in ['y','yes']:
		stats_11_135, results_11_135, land_area_11_135 = run_each('11-135')
		csv_output('2011/135',vars_11,stats_11_135,results_11_135,land_area_11_135,totals_11,save_cluster_stats=True)
		print '\t\t1 km, 3 km, 5 km processing DONE'
	
	if raw_input('\tRun 3 km clustered data? (y/n)').strip().lower() in ['y','yes']:
		stats_11_clustered, results_11_clustered, land_area_11_clustered = run_each('11',clustered = True)
		totals_11_clustered = csv_output('2011/3-clustered',vars_11,stats_11_clustered,results_11_clustered,land_area_11_clustered)
		print '\t\t3 km clustered processing DONE'

	if raw_input('\tRun regional data? (y/n)').strip().lower() in ['y','yes']:
		for region in range(1,11):
			stats, results, land_area = run_each('11',region=region)
			totals = csv_output('2011/region '+str(region),vars_11,stats,results,land_area)
		print '\t\tRegional processing DONE'

	if raw_input('\tRun by state data? (y/n)').strip().lower() in ['y','yes']:
		for code,data in json.loads(open('states.json').read())['state'].iteritems():
			stats, results, land_area = run_each('11',state=(data['name'],[code]))
			totals = csv_output('2011/states',{'ethnicity':vars_11['ethnicity']},stats,results,land_area,prefix=data['name']+'-')
		print '\t\tBy state processing DONE'

	print '2010 DONE'

if __name__ == '__main__':
	main()