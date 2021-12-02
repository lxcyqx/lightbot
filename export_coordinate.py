from flask import Flask,request
import sys
import serial
import math
app = Flask(__name__)
printer = serial.Serial('/tmp/printer')

@app.route('/position',methods=['GET'])
def getPosition():
    x = request.args.get('x')
    y = request.args.get('y')
    #print((x,y))
    newX =float(x)/4 -50
    newY =float(y)/4 -50
    #print(newX,newY)

    if(-100 < newX and newX < 100):
        if(-100 < newY and newY < 100):
            line = "G0 X"+str(newX) + " Y" + str(newY) + " Z 80 \n \r"
            print(line)
            byteString = line.encode('UTF-8')
            printer.write(byteString)
            print(printer.readline())
    # Now here we get the position, put your control code below
    # 
    #return ""

def main():
    app.run(host='0.0.0.0',port=5000)
    #printer.open() 
    print(printer.is_open)


if __name__ == "__main__":
    sys.exit(main())

