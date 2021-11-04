import maya.cmds as cmds
import math

def getMoveDirections(start, dest):
	return [dest[0] - start[0], dest[1] - start[1], dest[2] - start[0]]
	
def getDistance(start, dest):
    return math.sqrt((abs(start[0] - dest[0]))**2 + (abs(start[1] - dest[1]))**2 + (abs(start[2] - dest[2]))**2)

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

		f.write("F20000")
	
	for frame in range(90):
		cmds.select( 'pCube23' )
		selected = cmds.ls(sl=True)
		cmds.currentTime(frame)
		f.write("new frame \n")
		
		#use this for the progress bar
		totalEdges = 0    #progress bar max value
		currentEdge = 0   # progress bar current value

		for k in range(0, len(selected)):
		
			cmds.select(selected[k])
			
			#Convert that object to edges and select them
			cmds.ConvertSelectionToEdges()
			
			#get the number of edges for that object
			totalEdges += int(cmds.polyEvaluate(e=True))
		
			if(cmds.window("ExportGcode", ex = True)):
				cmds.deleteUI("ExportGcode")
			
			window = cmds.window("ExportGcode", title="ExportGcode", width=100, height=130, s = False)
			cmds.columnLayout( columnAttach=('both', 5), rowSpacing=10, columnWidth=250 )
			
			#create progress bar
			progressControl = cmds.progressBar(maxValue=100, width=100, vis = False)
			
			#show window
			cmds.showWindow(window)
			
		
		#for each object
		for k in range(0, len(selected)):
			f.write("iterate over each object \n")
			
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

			        #increment how much progress has been made
				    currentEdge += 1
			
				    #update the progress bar
				    progressInc = cmds.progressBar(progressControl, edit=True, maxValue = totalEdges, pr = currentEdge, vis = True)
				
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
			        moveDirection = getMoveDirections(currPosition, nextPosition)
			        f.write("G1 X" + str(moveDirection[0]) + " Y" + str(moveDirection[1]) + " Z" + str(moveDirection[2]) + "\n")
			        currPosition = nextPosition
			    #else move to point and draw the edge
			    else:
			        v1 = closest_edge_vertices[0]
			        v2 = closest_edge_vertices[1]
			        pp_v1 = cmds.pointPosition(v1, w = True)
			        pp_v2 = cmds.pointPosition(v2, w = True)
			        
			        if (nextPosition == pp_v1):
			            moveDirection_to_v1 = getMoveDirections(currPosition, pp_v1)
			            moveDirection_to_v2 = getMoveDirections(pp_v1, pp_v2)
			            f.write("G0 X" + str(moveDirection_to_v1[0]) + " Y" + str(moveDirection_to_v1[1]) + " Z" + str(moveDirection_to_v1[2]) + "\n")
			            f.write("G1 X" + str(moveDirection_to_v2[0]) + " Y" + str(moveDirection_to_v2[1]) + " Z" + str(moveDirection_to_v2[2]) + "\n")
			            currPosition = pp_v2
			        else:
			            moveDirection_to_v2 = getMoveDirections(currPosition, pp_v2)
			            moveDirection_to_v1 = getMoveDirections(pp_v2, pp_v1)
			            f.write("G0 X" + str(moveDirection_to_v2[0]) + " Y" + str(moveDirection_to_v2[1]) + " Z" + str(moveDirection_to_v2[2]) + "\n")
			            f.write("G1 X" + str(moveDirection_to_v1[0]) + " Y" + str(moveDirection_to_v1[1]) + " Z" + str(moveDirection_to_v1[2]) + "\n")
			            currPosition = pp_v1	
			
			#delete the duplicated object
			cmds.delete(newObj)
		
	#close the file	
	f.close()
		
	#remove the progress window
	#cmds.deleteUI("ExportGcode")
		
	#let the user know it's done
	cmds.headsUpMessage(str(filename) + " created.")
		
	#clear the selection
	cmds.select(cl=True)

exportGcode()