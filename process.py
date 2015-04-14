import simplejson as json
import urllib, csv

key = '6484813f180d34c35df3e62adf2e57459f60a566'
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
		sorted_polys[d] = {}
		for tract in sorted(polygons[d]):
			if tract[:2] not in sorted_polys[d]:
				sorted_polys[d][tract[:2]] = {tract[2:5]: [tract[5:],]}
			elif tract[2:5] not in sorted_polys[d][tract[:2]]:
				sorted_polys[d][tract[:2]][tract[2:5]] = [tract[5:],]
			else:
				sorted_polys[d][tract[:2]][tract[2:5]].append(tract[5:])
	return sorted_polys

def get_data_2011(variables, polygons):
	full_vars = {}
	for var in variables:
		request = 'http://api.census.gov/data/2010/acs5/variables/%s.json' %(var)
		try:
			data = json.loads(urllib.urlopen(request).read())
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
		request = 'http://api.census.gov/data/2010/acs5?key=%s&get=%s,NAME&for=state:*' %(key,','.join(full_vars.keys()[i:j]))
		i = j
		try:
			temp_data = json.loads(urllib.urlopen(request).read())
		except:
			print 'alert:',temp_data
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
				data = []
				i = 0
				for j in range(min(len(full_vars.keys()),VAR_LIMIT-1),len(full_vars.keys()),VAR_LIMIT-1)+[len(full_vars.keys())]:
					request = 'http://api.census.gov/data/2010/acs5?key=%s&get=%s,NAME&for=tract:%s&in=state:%s,county:%s' %(key,','.join(full_vars.keys()[i:j]),','.join(tracts),state,county)
					i = j
					try:
						temp_data = json.loads(urllib.urlopen(request).read())
					except:
						print 'alert:', temp_data
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

def main():
	stats_01, results_01, land_area_01 = run_each('01')
	with open('2001/cluster_stats.csv', 'wb') as csvfile:
		csvwriter = csv.writer(csvfile)
		for key in sorted(stats_01):
			csvwriter.writerow([key, stats_01[key]])

	stats_11, results_11, land_area_11 = run_each('11')
	with open('2011/cluster_stats.csv', 'wb') as csvfile:
		csvwriter = csv.writer(csvfile)
		for key in sorted(stats_11):
			csvwriter.writerow([key, stats_11[key]])

	vars_11 = json.loads(open('2010acs5elements.json').read())
	#for group in vars_11:
	group = "basics"
	totals_11 = get_data_2011(vars_11[group],results_11)
	with open('2011/'+group+'.csv', 'wb') as csvfile:
		csvwriter = csv.writer(csvfile)
		for key in totals_11:
			csvwriter.writerow([str(key+' : '+totals_11[key]['concept']+' : '+totals_11[key]['label'])])
			csvwriter.writerow([dist for dist in sorted(totals_11[key]) if dist not in ['concept', 'label'] ])
			csvwriter.writerow([totals_11[key][dist] for dist in sorted(totals_11[key]) if dist not in ['concept', 'label']])
			csvwriter.writerow([])
		if group == 'basics':
			csvwriter.writerow(["ALAND10 : 2010 Census land area (square meters)"])
			csvwriter.writerow([dist for dist in sorted(totals_11[key]) if dist not in ['concept', 'label'] ])
			csvwriter.writerow([land_area_11[dist] for dist in sorted(totals_11[key]) if dist not in ['concept', 'label','total']]+[9158021763139])


	stats_11_135, results_11_135, land_area_11_135 = run_each('11-135')
	with open('2011/cluster_stats.csv', 'wb') as csvfile:
		csvwriter = csv.writer(csvfile)
		for key in sorted(stats_11_135):
			csvwriter.writerow([key, stats_11_135[key]])

	for group in vars_11:
		totals_11_135 = get_data_2011(vars_11[group],results_11_135)
		with open('2011/135/'+group+'.csv', 'wb') as csvfile:
			csvwriter = csv.writer(csvfile)
			for key in totals_11_135:
				csvwriter.writerow([str(key+' : '+totals_11_135[key]['concept']+' : '+totals_11_135[key]['label'])])
				csvwriter.writerow([dist for dist in sorted(totals_11_135[key]) if dist not in ['concept', 'label'] ])
				csvwriter.writerow([totals_11_135[key][dist] for dist in sorted(totals_11_135[key]) if dist not in ['concept', 'label']])
				csvwriter.writerow([])
			if group == 'basics':
				csvwriter.writerow(["ALAND10 : 2010 Census land area (square meters)"])
				csvwriter.writerow([dist for dist in sorted(totals_11_135[key]) if dist not in ['concept', 'label'] ])
				csvwriter.writerow([land_area_11_135.get(dist,None) for dist in sorted(totals_11_135[key]) if dist not in ['concept', 'label','total']]+[9158021763139])


if __name__ == '__main__':
	main()
	print '...DONE'