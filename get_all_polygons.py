from gis_csdt.models import *
import json

def run():
  for (year, num) in [('2000',16),('2010',9)]:
    polys = MapPolygon.objects.filter(dataset_id=num)
    polys = polys.values('remote_id','field1')
    with open('all_'+year+'.json', 'wb') as outfile:
      pd = {}
      for p in polys:
        if p['remote_id'][:2] not in pd:
          pd[p['remote_id'][:2]]={}
        if p['remote_id'][2:5] not in pd[p['remote_id'][:2]]:
          pd[p['remote_id'][:2]][p['remote_id'][2:5]]={}
        pd[p['remote_id'][:2]][p['remote_id'][2:5]][p['remote_id'][5:]]=p['field1']
      json.dump(pd,outfile)


