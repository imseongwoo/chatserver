import socketserver
import threading

HOST = ''
PORT = 15200
lock = threading.Lock()

class UserManager:
    def __init__(self):         # 생성자에서 사용자 등록 정보를 담을 사전인 self.users를 초기화. self.users는 사전자료로 구성됨
        self.users = {}

    def addUser(self,username,conn,addr):
        if username in self.users:
            conn.send('이미 등록된 사용자입니다.\n'.encode())  # username이 존재하면 클라이언트에 메시지를 인코딩해서 보내고 None 을 리턴합니다.
            return None
        # 새로운 사용자 등록
        lock.acquire() # 공용 데이터이므로 username을 추가하기 전에 락을 걸어두고 self.users를 업데이틑 하면 lock 풀기
        self.users[username]=(conn,addr)
        lock.release()

        self.sendMessageToAll('[%s]님이 입장했습니다.'%username)
        print('+++대화 참여자수 [%d]'%len(self.users))

        return username
    def removeUser(self,username):
        if username not in self.users:
            return
        lock.acquire()
        del self.users[username]
        lock.release()

        self.sendMessageToAll('[%s]님이 퇴장했습니다.'%username)
        print('---대화 참여자 수 [%d]'%len(self.users))

    def messageHandler(self,username,msg):
        if msg[0] != '/':
            self.sendMessageToAll('[%s]%s'%(username,msg))
            return
        if msg.strip() =='/quit':
            self.removeUser(username)
            return -1
    def sendMessageToAll(self,msg):
        for conn,addr in self.users.values():
            conn.send(msg.encode())         # 채팅 서버에 접속한 모든 클라이언트에게 encode() 후 메시지 전송

class MyTcpHandler(socketserver.BaseRequestHandler):
    userman = UserManager()

    def handle(self):
        print('[%s] 연결됨'%self.client_address[0])

        try:
            username = self.registerUsername()
            msg = self.request.recv(1024)
            while msg:
                print(msg.decode())
                if self.userman.messageHandler(username,msg.decode()) == -1:
                    self.request.close()
                    break
                msg = self.request.recv(1024)
        except Exception as e:
            print(e)
        print('[%s] 접속종료'%self.client_address[0])
        self.userman.removeUser(username)
    def registerUsername(self):
        while True:
            self.request.send('로그인ID:'.encode())
            username = self.request.recv(1024)
            username = username.decode().strip()
            if self.userman.addUser(username,self.request,self.client_address):
                return username

class ChatingServer(socketserver.ThreadingMixIn,socketserver.TCPServer):    #chatingserver 클래스는 상속받은 두 개 클래스의 속성을 모두 가지게 된다.
    pass    # socketserver.ThreadingMixIn 클래스는 클라이언트의 요청을 독립된 스레드로 동작시켜 처리함. 다수 동시 접속자 처리해야 하므로 비동기 처리.

def runServer():
    print('+++채팅 서버를 시작합니다.')
    print('+++채팅 서버를 끝내려면 Ctrl+C를 누르세요.')

    try:
        server = ChatingServer((HOST,PORT),MyTcpHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print('---채팅 서버를 종료합니다.')
        server.shutdown()
        server.server_close()
runServer()

