import maya.cmds as cmds
import math
import maya.OpenMaya as om

epsilon = 3e-10

def getMoveDirections(start, dest):
	return [dest[0] - start[0], dest[1] - start[1], dest[2] - start[0]]
	
def getDistance(start, dest):
    return math.sqrt((abs(start[0] - dest[0]))**2 + (abs(start[1] - dest[1]))**2 + (abs(start[2] - dest[2]))**2)
	
def getGeoList(geoList=[]):
	'''
	Return a list of geometry transform objects
	@param meshList: List of meshes to return as list. If empty, use all non intermediate meshes in the scene
	@type meshList: list
	'''
	# Check Geo List
	if not geoList:
		geoList = [cmds.listRelatives(i,p=True,pa=True)[0] for i in cmds.ls(geometry=True, ni=True, visible=True) or []]
	else:
		geoList = [geo for geo in geoList if glTools.utils.geometry.isGeometry(geo)]
	if not geoList: return []
	
	# Remove Duplicates
	geoList = list(set(geoList))
	
	# Return Result
	return geoList

# Divides curve into segments.
def eqDistanceCurveDivide(f, curvename, segmentcurveLength):
	uValeStart = 0.0
	curveLength = cmds.arclen(curvename)
	kk = (int(curveLength / segmentcurveLength))
	intCL = int(math.ceil(curveLength))
	accur = 100 * intCL
	uVale = 1.0 / accur
 
	for t in range(kk):
		for i in range(accur):
 
			pointA = cmds.pointOnCurve(curvename, top=True, pr=uValeStart, p=True )
			vecA = om.MVector(pointA[0], pointA[1], pointA[2])
			pointB = cmds.pointOnCurve(curvename, top=True, pr=uVale, p=True)
			vecB = om.MVector(pointB[0], pointB[1], pointB[2])
 
			vecC = om.MVector()
			vecC = (vecB - vecA)
			distance = vecC.length()
 
			if distance < segmentcurveLength:
				uVale += 1.0 / accur
			else:
				uValeStart = uVale
				break
		
		for i in range(len(pointB)):
			pointB[i] = round(pointB[i], 2) # round to 2 decimal places
			if (pointB[i] < epsilon and pointB[i] > -1 * epsilon): # smooth out z that are near 0
				pointB[i] = 0

		if (t is 0):
			f.write("G0 X" + str(pointB[0]) + " Y" + str(pointB[1]) + " Z" + str(pointB[2]) + "\n")		
		else:	
			f.write("G1 X" + str(pointB[0]) + " Y" + str(pointB[1]) + " Z" + str(pointB[2]) + "\n")
 
		if uValeStart >= 0.99:
			break

def processNurbs(f, nurbs):
	for k in range(len(nurbs)):
		f.write("iterate nurbs \n")
		newObj = cmds.duplicate(nurbs[k])
		cmds.select(newObj)
		eqDistanceCurveDivide(f, newObj, .2)
		#delete the duplicated object
		cmds.delete(newObj)

def processMeshObjects(f, selected):

	#for each mesh object
	for k in range(0, len(selected)):
		f.write("iterate mesh object \n")
		
		#duplicate the current mesh item
		newObj = cmds.duplicate(selected[k])
		
		cmds.select(newObj)
		
		#Convert that object to edges and select them
		cmds.ConvertSelectionToEdges()
			
		#get the number of edges selected
		numEdges = cmds.polyEvaluate( e=True )
		edges_nums = list(range(numEdges))
		
		currPosition = [0, 0, 0]
		nextPosition = [0, 0, 0]
		
		while len(edges_nums) > 0:
			closestDistance = float('inf')
			closestEdgeIndex = 0
			closest_edge_vertices = []
					
			for i in edges_nums:
			
				#get the vertices for current edge
				vertices = cmds.polyListComponentConversion(str(newObj[0]) + ".e[" + str(i) + "]", fe = True, tv = True)
				cmds.select(vertices)
			
				#store the vertices in an array
				vertices = cmds.ls(sl = True, fl = True)
				
				v1 = vertices[0]
				v2 = vertices[1]
				pp_v1 = cmds.pointPosition(v1, w = True)
				pp_v2 = cmds.pointPosition(v2, w = True)
				
				#if the current position is either one of the endpoints of the edge, set the opposite vertex as next position
				if (currPosition == pp_v1):
					nextPosition = pp_v2
					closestEdgeIndex = i
					closestDistance = 0
					break
				elif (currPosition == pp_v2):
					nextPosition = pp_v1
					closestEdgeIndex = i
					closestDistance = 0
					break
				#else find the nearest vertex
				else:		    
					distance_to_v1 = getDistance(currPosition, pp_v1)
					distance_to_v2 = getDistance(currPosition, pp_v2)
					if (distance_to_v1 < closestDistance):
						closestDistance = distance_to_v1
						nextPosition = pp_v1
						closestEdgeIndex = i
						closest_edge_vertices = vertices
					if (distance_to_v2 < closestDistance):
						closestDistance = distance_to_v2
						nextPosition = pp_v2
						closestEdgeIndex = i
						closest_edge_vertices = vertices
												
			edges_nums.remove(closestEdgeIndex)

			#if closest vertex is point itself, draw edge				
			if (closestDistance == 0):
				f.write("G1 X" + str(nextPosition[0]) + " Y" + str(nextPosition[1]) + " Z" + str(nextPosition[2]) + "\n")
				currPosition = nextPosition
			#else move to point and draw the edge
			else:
				v1 = closest_edge_vertices[0]
				v2 = closest_edge_vertices[1]
				pp_v1 = cmds.pointPosition(v1, w = True)
				pp_v2 = cmds.pointPosition(v2, w = True)

				if (nextPosition == pp_v1):
					f.write("G0 X" + str(pp_v1[0]) + " Y" + str(pp_v1[1]) + " Z" + str(pp_v1[2]) + "\n")
					f.write("G1 X" + str(pp_v2[0]) + " Y" + str(pp_v2[1]) + " Z" + str(pp_v2[2]) + "\n")
					currPosition = pp_v2
				else:
					f.write("G0 X" + str(pp_v2[0]) + " Y" + str(pp_v2[1]) + " Z" + str(pp_v2[2]) + "\n")
					f.write("G1 X" + str(pp_v1[0]) + " Y" + str(pp_v1[1]) + " Z" + str(pp_v1[2]) + "\n")
					currPosition = pp_v1	
		
		#delete the duplicated object
		cmds.delete(newObj)

def exportGcode():
	#grab the selected object(s)	
	selected = cmds.ls(sl=True)

	#only do this if there's something selected
	if(selected > 0):
	
		#bring up the file dialog so the user can tell you where to save this
		filename = cmds.fileDialog2(caption='Export selected as gcode')
		
		#find the asterik in the name (stl isn't a file type in maya)		
		extensionIndex =  str(filename[0]).find("*")
		
		#append the stl extension to the filename
		filename = str(filename[0][0: extensionIndex]) + "gcode"
		
		#open a file at the filename specified	
		f = open(str(filename), 'w')

		f.write("G0 F20000 \n")
		f.write("G1 F20000 \n")
		
	
	for frame in range(1):
		geoList = getGeoList([])
		cmds.select( geoList )
		nurbs = cmds.ls(type="nurbsCurve", visible=True)
		selected = cmds.ls(type="mesh", visible=True)
		cmds.currentTime(frame)
		f.write("new frame \n")
			
		processMeshObjects(f, selected)	
		processNurbs(f, nurbs)
		
		
	#close the file	
	f.close()
		
	#let the user know it's done
	cmds.headsUpMessage(str(filename) + " created.")
		
	#clear the selection
	cmds.select(cl=True)

exportGcode()
