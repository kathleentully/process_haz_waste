import csv, os

fips_to_state = {
   "01": "Alabama",
   "02": "Alaska",
   "04": "Arizona",
   "05": "Arkansas",
   "06": "California",
   "08": "Colorado",
   "09": "Connecticut",
   "10": "Delaware",
   "11": "District of Columbia",
   "12": "Florida",
   "13": "Geogia",
   "15": "Hawaii",
   "16": "Idaho",
   "17": "Illinois",
   "18": "Indiana",
   "19": "Iowa",
   "20": "Kansas",
   "21": "Kentucky",
   "22": "Louisiana",
   "23": "Maine",
   "24": "Maryland",
   "25": "Massachusetts",
   "26": "Michigan",
   "27": "Minnesota",
   "28": "Mississippi",
   "29": "Missouri",
   "30": "Montana",
   "31": "Nebraska",
   "32": "Nevada",
   "33": "New Hampshire",
   "34": "New Jersey",
   "35": "New Mexico",
   "36": "New York",
   "37": "North Carolina",
   "38": "North Dakota",
   "39": "Ohio",
   "40": "Oklahoma",
   "41": "Oregon",
   "42": "Pennsylvania",
   "44": "Rhode Island",
   "45": "South Carolina",
   "46": "South Dakota",
   "47": "Tennessee",
   "48": "Texas",
   "49": "Utah",
   "50": "Vermont",
   "51": "Virginia",
   "53": "Washington",
   "54": "West Virginia",
   "55": "Wisconsin",
   "56": "Wyoming",
   "72": "Puerto Rico"
}

def state_name(fips_number):
	code = '{:0>2d}'.format(fips_number)
	if code not in fips_to_state:
		print 'Look up fips code {0}'.format(code)
		return 'Unknown'
	return fips_to_state[code]

def extract_clustered():
	results = {'2000': {}, 
			   '2010': {} }
	for yr in results.keys():
		for i in range(73):
			filename = 'all tracts for analysis-dec2015/raw_all_tracts_{0}/{1:0>2d}_state.csv'.format(yr, i)
			if os.path.isfile(filename):
				results[yr][i] = list()
				with open(filename, 'rb') as haz_file:
					rdr = csv.reader(haz_file, delimiter=',')
					row1 = next(rdr)
					if row1[2] != 'clustered':
						print 'uh oh!'
					else:
						for row in rdr:
							if row[2] == '1':
								results[yr][i].append(row[0])

	with open('12031016_clustered_tracts.txt','wb') as outfile:
		for yr in results.keys():
			outfile.write(yr + ':\n')
			for i in results[yr].keys():
				outfile.write('\t{0} - {1}: {2}\n'.format(i, state_name(i), ', '.join(results[yr][i]) if len(results[yr][i]) > 0 else 'None'))

if __name__ == '__main__':
	extract_clustered()