import socket
from threading import Thread

HOST = 'localhost'
PORT = 9010

def rcvMsg(sock):           # runChat 에서 스레드로 구동되며 채팅 서버로부터 메시지를 수신받아 화면에 출력 sock은 채팅 서버와 연결된 tcp 소켓
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                break
            print(data.decode())
        except:
            pass

def runChat():
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as sock:      # 소켓 생성
        sock.connect((HOST,PORT))                                       # 서버 연결
        t = Thread(target=rcvMsg,args=(sock,))                          # rcvMsg()를 스레드로 구동,독립적으로 실행 가능한 스레드로 만들었다.
        t.daemon = True         # t를 생성한 메인 스레드가 종료하면 자동적으로 종료하게 해줌.
        t.start()               # 생성한 스레드 t를 구동 이제 rcvMsg(sock)은 runChat()과 관계없이 독립적으로 구동하는 스레드이다.

        while True:
            msg = input()
            if msg == '/quit':
                sock.send(msg.encode())
                break
            sock.send(msg.encode())
runChat()