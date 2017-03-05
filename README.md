# GeoHITS

## keywords

	1. ubuntu
	2. python
	2. Mongdb
	3. Flick yfcc100m dataset
	4. shapely, a python 3rd-party library
	5. OSM, open street map
	6. GeoHITS, a extension of HITS algrithm

## Project description

	基于Yahoo Flickr YFCC100M 数据集（包含1亿条图片及图片远数据的数据集，其中有约4800万带有地理标记的数据）
	1. 将YFCC100M数据写入MongoDB数据库。在写入的过程中对每个有地理标记的数据的经纬度进行定位，并添加country字段。
	2. 输入keyword，返回相关的结果集。
	3. 对结果集中的数据的user tags 和 country字段进行统计分析，统计不同的locations，不同的tags，以及每个location中包含的tags，构建表示tag和location之间关系的稀疏矩阵matrix（若tag在location中出现，或location中包含tag），输出locations、tags、matrix。
	4. 表示位置的向量locations（所有位置初始值为1）、表示标签的向量（所有标签的初始值为1）、表示tag和location之间包含关系的矩阵matrix 作为LocHITS算法的输入（扩展的HITS算法）。对经过迭代收敛后的locations向量，对其中的值以及其对应的location降序排序，输出结果。

### GoogleMapAPI_Get_bbox folder

	1. country: 200+个国家的名字和经纬度
	2. country_with_bbox：根据Google Map API获得对应国家的bounding－box

### WriteDataToMongoDB.py

	a python script to create mongodb and write yfcc100m dataset to mongodb

### point_in_polygon_with_shapely.py

	基于OSM（openstreetmap，admin_level＝country）数据和python第三方图形库shapely实现的全球经纬度坐标点定位。
	
### GeoHITS

	1. GeoHITS
	2. GeoHITS_s: add tag similarity
	3. GeoHITS_tf: add tag frequency


