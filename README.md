Introduction
============

This code is used to process the output of the [Social GIS](https://github.com/GK-12/SGIS-backend) REST API.

Determining the polygons based on 50% areal apportionment
=========================================================

* For each point:
	* Build a cluster: Determine all points that are within double the maximum given distance using the GeoDjango spatial lookup ```distance_lte```/PostGIS function ```ST_Distance(poly, geom)```. For each of these points, determine any new points within double the maximum distance. Continue propagating until all points have been found.

	![An Arrangement of Points](https://raw.githubusercontent.com/kathleentully/process_haz_waste/master/example/points.png)
	As an example, consider these points. Begin at point 1.

	![Point 1 with 3 km and 6 km radii](https://raw.githubusercontent.com/kathleentully/process_haz_waste/master/example/points-step1.png)
	The red circle is a 3 km radius and the blue is a 6 km radius. The 3 km radius of the 1st point will intersect with the 3 km radius of any points within the 6 km radius. 

	![Second Round of Points](https://raw.githubusercontent.com/kathleentully/process_haz_waste/master/example/points-step2.png)
	The second round of points are then check for neighbors.

	![Third Round of Points](https://raw.githubusercontent.com/kathleentully/process_haz_waste/master/example/points-step3.png)
	And then the third, but no more points are found.
	* Remove all other points in the cluster from the list of points. This creates a list of clusters, where some clusters may only have one point.
* Now, for each cluster:
	* Create a regular twelve sided polygon around each point in the cluster. This polygon approximates a radius around each point. It covers over 95% of the area covered by an actual circle (12 polygons × cos(2pi/24) × sin(2pi/24) / pi = 95.49%). This percentage increases when points are clustered.
	* All polygons for a given distance are merged to create one polygon. 
	![An Example of a Merged Polygon](https://raw.githubusercontent.com/kathleentully/process_haz_waste/master/example/polygon.png)
	* For each cluster, the following algorithm is run:
		* Find all census tracts completely inside the polygon using GeoDjango's spatial lookup ```coveredby```/PostGIS function ```ST_CoveredBy()```. Create a working list of polygons.
		* Also find all census tracts that partially intersect with the polygon. For each of these census tracts, find the polygon created by the intersection of the radius approximation polygon and the census tract. Using GeoDjango's ```Area()``` function, determine the ratio of this new polygon to the area of the census tract. If the ratio is greater than half, this census tract is added to the list.
		* If multiple distances are being used for the analysis, the same process is repeated for the next larger distance, creating another list. All census tracts included for any smaller distances are automatically excluded. This means if a census tract is 35% covered by the smallest distance and 20% covered by the next largest distance, this census tract will be counted in the second polygon, even though only 20% is covered.
* Now that we have a list of census tracts that are categorized by distance from each site, each census tract is looked up using a census API.
	* For the year 2000, the 2000 long form census data was used. Please refer to [the variables available in this data](http://api.census.gov/data/2000/sf3/variables.html) and [the variables actually used for this analysis](2000-variables.md).
	* For the year 2010, the census abandoned the long form and created the American Consumer Survey. For this, we used the 2010 American Consumer Survey 5 year estimate. Please refer to [the variables available in this data](http://api.census.gov/data/2010/acs5/variables.html) and [the variables actually used for this analysis](2010-variables.md).