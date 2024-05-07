# while True:
        # receive data stream. it won't accept data packet greater than 1024 bytes
        #data = conn.recv(1024).decode()
        #if not data:
            # if data is not received break
        #    break
        #print("from connected user: " + str(data))
        #data = input(' -> ')
        #conn.send(data.encode())  # send data to the client
		
import LGymConnect as LGymC
import time

class LGymClient:
    def __init__(self, host, port, id):
        self.host = host
        self.port = port
        self.id = id
        self.lgconnectClinet = LGymC.LGymConnect(self.host,self.port,1,40960)

    def connect(self):
        self.lgconnectClinet.clientProgram()
        data = self.lgconnectClinet.clientRecive()
        if self._cheackReciveMsg(data):
            self.lgconnectClinet.clientSend("command=hello&id="+str(self.id )+"\r\n")
            data = self.lgconnectClinet.clientRecive()
            return self._cheackReciveMsg(data)
        return False

    
    def _cheackReciveMsg(self, data):
        data = str(data).strip()
        if not data:
            print("Connection lost")
            return False
        elif data.startswith("error"):
            print("Error de conexión "+str(data))
            return False
        elif data != "ok":
            print("Error de conexión "+str(data))
            return False
        return True
    
    def _processMetricsMsg(self, data):
        attributes = self._ParseDataToAttributes(data)
        if self.IsCommand("metrics",attributes) :
            idsStr = attributes["ids"]
            timeStr = attributes["time"]
            checkpointStr = attributes["checkpoints"]
            collisionsStr = attributes["collisions"]
            ids = self._parseArray(";",idsStr,"string")
            time = self._parseArray(";",timeStr,"float")
            checkpoint = self._parseArray(";",checkpointStr,"int")
            collisions = self._parseArray(";",collisionsStr,"int")
            dictionary = {}
            dictionary["ids"]=ids;
            dictionary["time"]=time;
            dictionary["checkpoints"]=checkpoint;
            dictionary["collisions"]=collisions;
            return dictionary
        return False

    def _parseArray(self, token, arr, type):
        arrSplited = arr.split(token)
        for i in range(0,len(arrSplited)):
            if type == "int" :
                arrSplited[i] = int(arrSplited[i].strip())
            elif type == "float" :
                arrSplited[i] = arrSplited[i].replace(",",".")
                arrSplited[i] = float(arrSplited[i].strip())
            else:
                arrSplited[i] = arrSplited[i].strip()
        return arrSplited


    def IsCommand(self, comm, attributes):
        return attributes["command"] == comm

    
    def _ParseDataToAttributes(self,data):
        dictionary = { }
        data = str(data).strip()
        attributes = data.split("&")
        for a in attributes:
            command=a.split("=")
            dictionary[command[0].strip()] = command[1].strip()
        return dictionary

    def commandInit(self):
        self.lgconnectClinet.clientSend("command=init&id="+str(self.id )+"\r\n")
        data = self.lgconnectClinet.clientRecive()
        return self._cheackReciveMsg(data)
    
    def addCustomAgent(self,id,agent):
        self.lgconnectClinet.clientSend("command=addagent&id="+str(self.id )+"&format=custom&type=mlpc&agentid="+id+"&agent="+agent+"\r\n")
        data = self.lgconnectClinet.clientRecive()
        return self._cheackReciveMsg(data)
    
    def commandReset(self):
        self.lgconnectClinet.clientSend("command=reset&id="+str(self.id )+"\r\n")
        data = self.lgconnectClinet.clientRecive()
        return self._cheackReciveMsg(data)
    
    def ReciveMetrics(self):
        data = self.lgconnectClinet.clientRecive()
        dictionary = self._processMetricsMsg(data)
        if not dictionary:
            self.lgconnectClinet.clientSend("error=01&name=bad format\r\n")
        else:
            self.lgconnectClinet.clientSend("ok\r\n")
        return dictionary

    def close(self):
        self.lgconnectClinet.clientClose()
        

print("LGymClientInit")
for i in range(0,2):
    print("iniciando la iteracion "+str(i))
    client = LGymClient(LGymC.getHostName(),80,"1")
    if client.connect():
        print("conexion establecida con el servidor")
        file1 = open("trained_model_1.txt", "r")
        agent=file1.read()
        agent=agent.replace("\n",";")
        print("Añadiendo agentes")
        if client.addCustomAgent("1",agent):
            print("Agent 1 added")
            if client.addCustomAgent("2",agent):
                print("Agent 2 added")
                if client.commandInit():
                    print("Inicializado")
                    dictionary = client.ReciveMetrics()
                    print("Metricas recibidas")
                    print(dictionary)
                    if client.commandReset():
                        print("Reseteamos el nivel")
        print("Finalizado")
    client.close()
    time.sleep(2)
print("LGymClientClose")	