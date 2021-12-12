# lightbot

Scripts used for cable driven robot that allows for real-time control and premade animation via Maya

`script.py` transforms Maya meshes and curves into cartesian XYZ coordinates

`gcode_parser.py` parses through the input file containing XYZ coordinates and converts them into cable coordinates so that lightbot can move to the correct position

`export_coordinate.py` takes in pixel coordinates from the terminal (sent from browser via Flask), converts them to cartesian coordinates, then converts them to lightbot coordinates and writes it to the printer

[Final Presentation.pdf](https://github.com/lxcyqx/lightbot/files/7698020/Final.Presentation.pdf)

https://user-images.githubusercontent.com/29609837/145697772-524a072f-ac6a-48ea-8ea5-c1638831ccfb.MOV

