import serial
import time

output = ""
loopNum = 0
outputBits = 0
currentTime = time.time()

f = open("RandomStreamOutput.txt", "a")

class Tree(object):
    def __init__(self):
        self.left = None
        self.right = None
        self.value = None
        
def Operation(node, y):    
    global loopNum
    loopNum += 1
    if loopNum > 15: return
    
    if node.value == "psi":
        node.value = y 

    elif node.value == "1" or node.value == "0":
        #global output
        #output += node.value
        #print(node.value, end='', flush=True)
        f.write(node.value)
        global outputBits
        global currentTime
        global intervalsRead
        global intervalTime
        outputBits += 1
        if (outputBits == 10000):
            print(str(10000/(time.time() - currentTime)) + " bits per second")
            print(str(intervalsRead/(time.time() - intervalTime)) + " intervals per second")
            print("Ratio: " + str((10000/(time.time() - currentTime))/(intervalsRead/(time.time() - intervalTime))))
            outputBits = 0
            currentTime = time.time()
            intervalsRead = 0
            intervalTime = time.time()
        node.value = y

    elif node.value == "H":
        if not node.left: #not node.right is given based on statement
            node.left = Tree()
            node.right = Tree()
            node.left.value = "psi"
            node.right.value = "psi"
        if y == "H": #HH
            node.value = "psi"
            Operation(node.left, "T")
            Operation(node.right, "H")
        if y == "T": #HT
            node.value = "1"
            Operation(node.left, "H")

            
    elif node.value == "T":
        if not node.left:
            node.left = Tree()
            node.right = Tree()
            node.left.value = "psi"
            node.right.value = "psi"
        if y == "T": #TT
            node.value = "psi"
            Operation(node.left, "T")
            Operation(node.right, "T")
        if y == "H": #TH
            node.value = "0"
            Operation(node.left, "H")
            
            
def depth(root):
    left_depth = depth(root.left) if root.left else 0
    right_depth = depth(root.right) if root.right else 0
    return max(left_depth, right_depth) + 1
            
            
        
root = Tree()
root.value = "psi"

class ReadLine:
    def __init__(self, s):
        self.buf = bytearray()
        self.s = s

    def readline(self):
        i = self.buf.find(b"\n")
        if i >= 0:
            r = self.buf[:i+1]
            self.buf = self.buf[i+1:]
            return r
        while True:
            i = max(1, min(2048, self.s.in_waiting))
            data = self.s.read(i)
            i = data.find(b"\n")
            if i >= 0:
                r = self.buf + data[:i+1]
                self.buf[0:] = data[i+1:]
                return r
            else:
                self.buf.extend(data)

ser = serial.Serial('COM5', 115200)
ser.set_buffer_size(rx_size = 115200, tx_size = 115200)
rl = ReadLine(ser)


intervalsRead = 0
intervalTime = time.time()
while True:
    try:
        timeBetween = rl.readline().decode().rstrip("\r\n")
        for i in range(0, int(timeBetween), 30):
            #inputBinary += "H"
            loopNum = 0
            Operation(root, "H")
        #inputBinary += "T" 
        loopNum = 0    
        intervalsRead += 1
        Operation(root, "T")
    except KeyboardInterrupt:
        ser.close()
        print("depth: "+ str(depth(root)))
        f.close()
        break

