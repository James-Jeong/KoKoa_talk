import socketserver
import threading
 
HOST = ''
PORT = 11111
lock = threading.Lock()

 
class User_Manager:
	def __init__(self):
		self.users = {}

	def augmentationUser(self, userName, connection, addr):
		if userName in self.users:
			connection.send('User already registered.\n'.encode())
			return None

		# Thread LOCK
		lock.acquire()
		self.users[userName] = (connection, addr)
		lock.release()

		self.sendMsgAll('[%s] CONNECTION ON' %userName)
		print('~ the number of users [%d]' %len(self.users))
		L = list(self.users.keys())
		print('~ users : [%s]' %L)
		return userName

	def deleteUser(self, userName):
		if userName not in self.users:
			return

		# Thread LOCK
		lock.acquire()
		del self.users[userName]
		lock.release()
 
		self.sendMsgAll('[%s] EXITS' %userName)
		print('~ the number of users [%d]' %len(self.users))
		L = list(self.users.keys())
		print('~ users : [%s]' %L)

	def showUser(self, userName):
		if userName not in self.users:
			return

		# Thread LOCK
		lock.acquire()
		L = list(self.users.keys())
		lock.release()

		self.sendMsg(str(L), userName)
 
	def msgHandler(self, userName, msg):
		if msg[0] != '/':
			self.sendMsgAll('[%s] %s' %(userName, msg))
			return

		if msg.strip() == '/quit':
			self.deleteUser(userName)
			return -1

		if msg.strip() == '/show':
			self.showUser(userName)
			return

	def sendMsg(self, msg, userName):
		L = list(self.users.keys())
		M = []
		for connection, addr in self.users.values():
			M.append(connection)
		N = []
		if userName in L:
			i = L.index(userName)
			M[i].send(msg.encode())

	def sendMsgAll(self, msg):
		for connection, addr in self.users.values():
			connection.send(msg.encode())

class tcpHandler(socketserver.BaseRequestHandler): # TCP 통신
	userman = User_Manager()

	def handle(self):
		print('[%s] IS CONNECTED' %self.client_address[0]) # IP 주소 출력
		
		try:
			userName = self.registerUsername()
			msg = self.request.recv(1024)
			while msg:
				print(msg.decode())
				if self.userman.msgHandler(userName, msg.decode()) == -1:
					self.request.close()
					break
				msg = self.request.recv(1024)
		except Exception as e:
			print(e)
		 
		print('[%s] CONNECTION OFF' %self.client_address[0])
		self.userman.deleteUser(userName)
 
	def registerUsername(self):
		while True:
			self.request.send('LOGIN ID:'.encode())
			userName = self.request.recv(1024)
			userName = userName.decode().strip()
			if self.userman.augmentationUser(userName, self.request, self.client_address):
				return userName

class ChatServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
	pass
		 
def runServer():
	print('~ SERVER ON')
	print('~ OFF : Ctrl + C')
	try:
		server = ChatServer((HOST, PORT), tcpHandler)
		server.serve_forever()
	except KeyboardInterrupt:
		print('~ SERVER OFF')
		server.shutdown()
		server.server_close()
 
runServer()