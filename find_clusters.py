#import simplejson as json
import json, urllib, csv

key = json.loads(open('key.json').read())['key']
VAR_LIMIT = 50

def find_points(year,num):
	data = json.loads(open('20'+year+'-hazwaste.json').read())
	point_list = []
	for point in data:
		if len(point['areaAroundPoint']['points']) >= num:
			point_list.append(point['point_id'])
	return point_list
if __name__ == '__main__':
	while True:
		try:
			num = int(raw_input('Find all clusters larger than what number? ').strip())
			break
		except:
			print 'Please enter an integer. Try again'

	points = find_points('01',num)
	if len(points) == 0:
		print 'No points found for 2001'
	else:
		print '2001:',', '.join(points)
	points = find_points('11',num)
	if len(points) == 0:
		print 'No points found for 2011'
	else:
		print '2011:',', '.join(points)