import json, csv, os

def reprocess(filename):
	with open(filename, 'rb') as csvin:
		reader = csv.reader(csvin)
		with open(filename[:-4]+'-new.csv', 'wb') as csvout:
			writer = csv.writer(csvout)
			name = reader.next()
			writer.writerow(['Variable']+reader.next()+['Beyond'])
			data = reader.next()
			data = [int(d) for d in data]
			data.append(data[-1]-sum(data[:-1]))
			writer.writerow(name+data)
			for row in reader:
				if len(row) == 0 or row[0][-2:] == 'km':
					continue
				try:
					data = [int(d) for d in row]
					data.append(data[-1]-sum(data[:-1]))
					writer.writerow(name+data)
				except:
					name = row
if __name__ == '__main__':
	#for year,data_points in {'2001':json.loads(open('2000longformelements.json').read()),'2011':json.loads(open('2010acs5elements.json').read())}.iteritems():
	for year,data_points in {'2011':json.loads(open('2010acs5elements.json').read())}.iteritems():
		#for folder in ['135','3','3-clustered']+['region '+str(n) for n in range(1,11)]:
		for folder in ['region '+str(n) for n in range(1,11)]:
			for point in data_points:
				print 'processing',year+'/'+folder+'/'+point+'.csv'
				reprocess(year+'/'+folder+'/'+point+'.csv')
				os.rename(year+'/'+folder+'/'+point+'-new.csv', year+'/'+folder+'/'+point+'.csv')