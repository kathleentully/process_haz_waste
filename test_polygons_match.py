import json, csv, urllib, time

'''
Results (8/10/2015)
2000:
  In 3km but not 135km:
  In 135km but not 3km:
    27137000300
    36063022712
    06085501300
    27053102600
    51550020600
2010:
  In 3km but not 135km:
  In 135km but not 3km:
    27053102600
    51550020600
'''


def sort_polygons(polygons):
  new_polys = set()
  for item in polygons:
    try:
      if "3.000000 km" in item["areaAroundPoint"]:
        for tract_id in item["areaAroundPoint"]["3.000000 km"]["polygons"]:
          new_polys.add(tract_id)
      if "1.000000 km" in item["areaAroundPoint"]:
        for tract_id in item["areaAroundPoint"]["1.000000 km"]["polygons"]:
          new_polys.add(tract_id)
    except:
      pass
  return new_polys

def examine_tracts():
  for year in ['2000','2010']:
    year_data = {}
    with open('20'+year[2]+'1-hazwaste.json') as haz3_file:
      haz3_set = sort_polygons(json.loads(haz3_file.read()))
      with open('20'+year[2]+'1-135-hazwaste.json') as haz135_file:
        haz135_set = sort_polygons(json.loads(haz135_file.read()))
        
        print year+':'

        print '\tIn 3km but not 135km:'
        for poly in haz3_set.difference(haz135_set):
          print '\t\t'+poly

        print '\tIn 135km but not 3km:'
        for poly in haz135_set.difference(haz3_set):
          print '\t\t'+poly


if __name__ == '__main__':
  examine_tracts()