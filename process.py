#import simplejson as json
import json, urllib, csv

key = json.loads(open('key.json').read())['key']
VAR_LIMIT = 50

def run_each(year):
	data = json.loads(open('20'+year+'-hazwaste.json').read())
	polygons = {"1.000000 km":set(),"3.000000 km":set(),"5.000000 km":set()}
	cluster_count = {'total_clustered':0,'total_points':0} #distribution of cluster sizes
	points = set()
	land_area = {"1.000000 km":0,"3.000000 km":0,"5.000000 km":0}

	for group in data:
		for d in ["1.000000 km","3.000000 km","5.000000 km"]:
			if d in group["areaAroundPoint"]:
				if "polygons" in group["areaAroundPoint"][d]:
					polygons[d] = polygons[d] | set(group["areaAroundPoint"][d]["polygons"])
				if "land_area" in group["areaAroundPoint"][d]:
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
		print d
		sorted_polys[d] = {}
		for tract in sorted(polygons[d]):
			if tract[:2] not in sorted_polys[d]:
				sorted_polys[d][tract[:2]] = {tract[2:5]: [tract[5:],]}
			elif tract[2:5] not in sorted_polys[d][tract[:2]]:
				sorted_polys[d][tract[:2]][tract[2:5]] = [tract[5:],]
			else:
				sorted_polys[d][tract[:2]][tract[2:5]].append(tract[5:])
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
				for tract in tracts:
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
					#print data
					for var_index in range(len(data[0])):
						if data[0][var_index] in ['NAME','state','county','tract']:
							continue
						for row in range(1,len(data)):
							try: 
								full_vars[data[0][var_index]][d] += int(data[row][var_index])
							except:
								if data[row][var_index]:
									print 'INT issue at line 125,',var_index,'data row:',data[row]
								continue
	return full_vars

def get_data_2000(variables, polygons):
	return get_data('http://api.census.gov/data/2000/sf3',variables,polygons)
def get_data_2011(variables, polygons):
	return get_data('http://api.census.gov/data/2010/acs5',variables,polygons)

def csv_output(folder,variables,stats,results,land_area,totals=None):
	print 'start CSV'
	with open(folder+'/cluster_stats.csv', 'wb') as csvfile:
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
				print totals[group]
		with open(folder+'/'+group+'.csv', 'wb') as csvfile:
			csvwriter = csv.writer(csvfile)
			for key in totals[group]:
				print [dist for dist in sorted(totals[group][key]) if dist not in ['concept', 'label'] ]
				csvwriter.writerow([str(key+' : '+totals[group][key]['concept']+' : '+totals[group][key]['label'])])
				csvwriter.writerow([dist for dist in sorted(totals[group][key]) if dist not in ['concept', 'label'] ])
				csvwriter.writerow([totals[group][key][dist] for dist in sorted(totals[group][key]) if dist not in ['concept', 'label']])
				csvwriter.writerow([])
			if group == 'basics':
				csvwriter.writerow(["ALAND10 : 2010 Census land area (square meters)"])
				csvwriter.writerow([dist for dist in sorted(totals[group][key]) if dist not in ['concept', 'label'] ])
				csvwriter.writerow([land_area[dist] for dist in sorted(totals[group][key]) if dist not in ['concept', 'label','total']]+[9158021763139])
	return totals

def main():
	#stats_00, results_00, land_area_00 = run_each('01')
	vars_00 = json.loads(open('2000longformelements.json').read())
	#totals_00 = csv_output('2001/3',vars_00,stats_00,results_00,land_area_00)

	stats_00_135, results_00_135, land_area_00_135 = run_each('01-135')
	csv_output('2001/135',vars_00,stats_00_135,results_00_135,land_area_00_135)
'''
	stats_11, results_11, land_area_11 = run_each('11')
	vars_11 = json.loads(open('2010acs5elements.json').read())
	totals_11 = csv_output('2011/3',vars_11,stats_11,results_11,land_area_11)
	
	stats_11_135, results_11_135, land_area_11_135 = run_each('11-135')
	csv_output('2011/135',vars_11,stats_11_135,results_11_135,land_area_11_135,totals_11)'''

if __name__ == '__main__':
	main()
	print '...DONE'