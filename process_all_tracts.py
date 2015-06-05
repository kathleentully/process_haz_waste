import json, csv, urllib

key = json.loads(open('key.json').read())['key']
nfo = {'2000':{
        'url':'http://api.census.gov/data/2000/sf3',
        'fields':{
          'P007001':'population',
          'P007003':'white',
          'P067001':'aggregate income',
          'P058001':'income population',
          'P088004':'poverty .75 to .99',
          'P088003':'poverty .50 to .74',
          'P088002':'poverty under .50',
          'P088001':'poverty population',
          'H081001':'housing value',
          'H084001':'housing population',
        }
      },
      '2010':{
        'url':'http://api.census.gov/data/2010/acs5',
        'fields':{
        }
      }
    }
def sort_polygons(polygons):
  new_polys = {}
  for item in polygons:
    try:
      for tract_id in item["areaAroundPoint"]["3.000000 km"]["polygons"]:
        if tract_id[:2] not in new_polys:
          new_polys[tract_id[:2]] = {tract_id[2:5]: {tract_id[5:]:True}}
        elif tract_id[2:5] not in new_polys[tract_id[:2]]:
          new_polys[tract_id[:2]][tract_id[2:5]] = {tract_id[5:]:True}
        elif tract_id[5:] not in new_polys[tract_id[:2]][tract_id[2:5]]:
          new_polys[tract_id[:2]][tract_id[2:5]][tract_id[5:]] = True
    except:
      pass
  return new_polys

def process_all_tracts():
  for year in ['2000']:
    year_data = {}
    with open('20'+year[2]+'1-hazwaste.json') as haz_file:

      haz_json = sort_polygons(json.loads(haz_file.read()))
      with open('all_'+year+'.json') as all_file:
        all_json = json.loads(all_file.read())
        with open('all_tracts_'+year+'.csv', 'wb') as csv_out:
          fieldnames = ['first_name', 'last_name']
          writer = csv.DictWriter(csv_out, fieldnames=[
            'tract ID',
            'within 3km',
            'land area',
            'population',
            'population density',
            'percent people of color',
            'mean household income',
            'percent below poverty',
            'mean owner-occupied housing value',
            ])
          writer.writeheader()
         
          for a in ['36']:
            for b in ['083']:
              tract_info = {}
              for c in all_json[a][b]:
                tract_info[c.encode('UTF-8')] = {'tract ID':a+b+c,
                  'within 3km':0,
                  'land area':all_json[a][b][c]
                  }


              request = nfo[year]['url']+'?key=%s&get=%s,NAME&for=tract:*&in=state:%s,county:%s' %(key,','.join(nfo[year]['fields'].keys()),a,b)
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

                for row in range(1,len(temp_data)):
                  tract_id = '0'*(6 - len(temp_data[row][-1])) + temp_data[row][-1]
                  for col in range(len(temp_data[row])-4):
                    try:
                      tract_info[tract_id][nfo[year]['fields'][temp_data[0][col]]] = int(temp_data[row][col])
                    except Exception as e:
                      print e, col, temp_data[row]


              except:
                print 'alert:', raw
                print 'request:', request
                break

              for c in all_json[a][b]:
                if a in haz_json and b in haz_json[a] and c in haz_json[a][b]:
                  tract_info[c]['within 3km'] = 1

                tract_info[c]['population density'] = tract_info[c]['population']/float(tract_info[c]['land area'])

                tract_info[c]['percent people of color'] = (tract_info[c]['population'] - tract_info[c]['white'])/float(tract_info[c]['population'])
                del tract_info[c]['white']

                tract_info[c]['mean household income'] = tract_info[c]['aggregate income']/float(tract_info[c]['income population']) if tract_info[c]['income population']>0 else 0
                del tract_info[c]['aggregate income']
                del tract_info[c]['income population']

                tract_info[c]['percent below poverty'] = (tract_info[c]['poverty .75 to .99'] + tract_info[c]['poverty .50 to .74'] + tract_info[c]['poverty under .50'])/float(tract_info[c]['poverty population']) if tract_info[c]['poverty population']>0 else 0
                del tract_info[c]['poverty .75 to .99']
                del tract_info[c]['poverty .50 to .74']
                del tract_info[c]['poverty under .50']
                del tract_info[c]['poverty population']

                tract_info[c]['mean owner-occupied housing value'] = tract_info[c]['housing value']/float(tract_info[c]['housing population']) if tract_info[c]['housing population']>0 else 0
                del tract_info[c]['housing value']
                del tract_info[c]['housing population']

                writer.writerow(tract_info[c])




if __name__ == '__main__':
  process_all_tracts()