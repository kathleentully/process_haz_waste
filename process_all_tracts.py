import json, csv, urllib, time

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
          'P037001':'school population',#25+
          'P037014':'Male: Associate degree',
          'P037015':'Male: Bachelors degree',
          'P037016':'Male: Masters degree',
          'P037017':'Male: Professional school degree',
          'P037018':'Male: Doctorate degree',
          'P037031':'Female: Associate degree',
          'P037032':'Female: Bachelors degree',
          'P037033':'Female: Masters degree',
          'P037034':'Female: Professional school degree',
          'P037035':'Female: Doctorate degree',
        }
      },
      '2010':{
        'url':'http://api.census.gov/data/2010/acs5',
        'fields':{
          'B03002_001E':'population',
          'B03002_003E':'white',
          'B19025_001E':'aggregate income',
          'B19001_001E':'income population',
          'C17002_003E':'poverty .50 to .99',
          'C17002_002E':'poverty under .50',
          'C17002_001E':'poverty population',
          'B25079_001E':'housing value',
          'B25075_001E':'housing population',
          'B15002_001E':'school population',#25+
          'B15002_014E':'Male: Associate degree',
          'B15002_015E':'Male: Bachelors degree',
          'B15002_016E':'Male: Masters degree',
          'B15002_017E':'Male: Professional school degree',
          'B15002_018E':'Male: Doctorate degree',
          'B15002_031E':'Female: Associate degree',
          'B15002_032E':'Female: Bachelors degree',
          'B15002_033E':'Female: Masters degree',
          'B15002_034E':'Female: Professional school degree',
          'B15002_035E':'Female: Doctorate degree',
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
  skipped = {}
  for year in nfo:
    year_data = {}
    with open('20'+year[2]+'1-hazwaste.json') as haz_file:

      haz_json = sort_polygons(json.loads(haz_file.read()))
      with open('all_'+year+'.json') as all_file:
        all_json = json.loads(all_file.read())
        
        for a in sorted(all_json):
          print 'starting state '+a+'...'
          tract_info = {}
        
          for b in sorted(all_json[a]):
            print '\tcounty '+b+'...'
            tract_info[b] = {}
            for c in sorted(all_json[a][b]):
              tract_info[b][c] = {'tract ID':a+b+c,
                'within 3km':0,
                'land area':all_json[a][b][c]
                }


            request = nfo[year]['url']+'?key=%s&get=%s,NAME&for=tract:*&in=state:%s,county:%s' %(key,','.join(nfo[year]['fields'].keys()),a,b)
            i = 0
            while True:
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
                      if temp_data[row][col]:
                        tract_info[b][tract_id][nfo[year]['fields'][temp_data[0][col]]] = int(temp_data[row][col])
                      else:
                        tract_info[b][tract_id][nfo[year]['fields'][temp_data[0][col]]] = 0
                    except Exception as e:
                      print e, col, temp_data[row]
                      print '-', temp_data[0]
                break
              except Exception as e:
                print 'exception:', e
                print 'alert:', raw
                print 'request:', request
                i += 1
                if i > 10:
                  print 'giving up'
                  if a in skipped:
                    skipped[a].append(b)
                  else:
                    skipped[a] = [b]
                  break
                print 'waiting...',
                time.sleep(5)
                print 'trying again!'

          if a not in skipped:
            with open('all tracts for analysis/all_tracts_'+year+'/'+a+'_state.csv', 'wb') as csv_out:
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
                'percent with a degree'
                ])
              writer.writeheader()

              for b in sorted(all_json[a]):
                for c in sorted(all_json[a][b]):
                  if a in haz_json and b in haz_json[a] and c in haz_json[a][b]:
                    tract_info[b][c]['within 3km'] = 1

                  tract_info[b][c]['population density'] = tract_info[b][c]['population']/float(tract_info[b][c]['land area']) if tract_info[b][c]['land area']>0 else ''

                  tract_info[b][c]['percent people of color'] = (tract_info[b][c]['population'] - tract_info[b][c]['white'])/float(tract_info[b][c]['population']) if tract_info[b][c]['population']>0 else ''
                  del tract_info[b][c]['white']

                  tract_info[b][c]['mean household income'] = tract_info[b][c]['aggregate income']/float(tract_info[b][c]['income population']) if tract_info[b][c]['income population']>0 else ''
                  del tract_info[b][c]['aggregate income']
                  del tract_info[b][c]['income population']

                  if year == '2000':
                    tract_info[b][c]['percent below poverty'] = (tract_info[b][c]['poverty .75 to .99'] + tract_info[b][c]['poverty .50 to .74'] + tract_info[b][c]['poverty under .50'])/float(tract_info[b][c]['poverty population']) if tract_info[b][c]['poverty population']>0 else ''
                    del tract_info[b][c]['poverty .75 to .99']
                    del tract_info[b][c]['poverty .50 to .74']
                  elif year == '2010':
                    tract_info[b][c]['percent below poverty'] = (tract_info[b][c]['poverty .50 to .99'] + tract_info[b][c]['poverty under .50'])/float(tract_info[b][c]['poverty population']) if tract_info[b][c]['poverty population']>0 else ''
                    del tract_info[b][c]['poverty .50 to .99']
                  del tract_info[b][c]['poverty under .50']
                  del tract_info[b][c]['poverty population']

                  tract_info[b][c]['mean owner-occupied housing value'] = tract_info[b][c]['housing value']/float(tract_info[b][c]['housing population']) if tract_info[b][c]['housing population']>0 else ''
                  del tract_info[b][c]['housing value']
                  del tract_info[b][c]['housing population']

                  tract_info[b][c]['percent with a degree'] = (tract_info[b][c]['Male: Associate degree'] + tract_info[b][c]['Male: Bachelors degree'] + tract_info[b][c]['Male: Masters degree'] + tract_info[b][c]['Male: Professional school degree'] + tract_info[b][c]['Male: Doctorate degree'] + tract_info[b][c]['Female: Associate degree'] + tract_info[b][c]['Female: Bachelors degree'] + tract_info[b][c]['Female: Masters degree'] + tract_info[b][c]['Female: Professional school degree'] + tract_info[b][c]['Female: Doctorate degree']) / float(tract_info[b][c]['school population']) if tract_info[b][c]['school population']>0 else ''
                  del tract_info[b][c]['school population']
                  del tract_info[b][c]['Male: Associate degree']
                  del tract_info[b][c]['Male: Bachelors degree']
                  del tract_info[b][c]['Male: Masters degree']
                  del tract_info[b][c]['Male: Professional school degree']
                  del tract_info[b][c]['Male: Doctorate degree']
                  del tract_info[b][c]['Female: Associate degree']
                  del tract_info[b][c]['Female: Bachelors degree']
                  del tract_info[b][c]['Female: Masters degree']
                  del tract_info[b][c]['Female: Professional school degree']
                  del tract_info[b][c]['Female: Doctorate degree']

                  writer.writerow(tract_info[b][c])
              print '\t\t...DONE'
  print 'SKIPPED:',skipped
if __name__ == '__main__':
  process_all_tracts()