# lightbot

`script.py` transforms Maya meshes and curves into cartesian XYZ coordinates

`gcode_parser.py` parses through the input file containing XYZ coordinates and converts them into cable coordinates so that lightbot can move to the correct position

`export_coordinate.py` takes in pixel coordinates from the terminal (sent from browser via Flask), converts them to cartesian coordinates, then converts them to lightbot coordinates and writes it to the printer


https://user-images.githubusercontent.com/29609837/145697631-613363bc-bb50-41fb-9c20-848c11f8978e.MOV

