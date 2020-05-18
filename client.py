from libs.socket import tcpSocketClientApp as tscApp
clientApp = tscApp(('localhost', 6868))

# from socket import *
#
# ADDRESS = ('localhost', 6868)
# bufsize = 1024
# print(AF_INET, SOCK_STREAM)
# client = socket()
# client.connect(ADDRESS)
# # while True:
# #     data = raw_input()
# #     if not data or data == 'exit':
# #         break
# #     client.send('%s\r\n' % data)
# #     data = client.recv(bufsize)
# #     if not data:
# #         break
# #     print data.strip()
# while True:
#     # 发收消息
#     msg = input('请你输入命令>>：').strip()
#     if not msg:continue
#     if msg =='quit':break
#     client.send(msg.encode('utf-8'))
#     data = client.recv(1024)
#     print('收到服务端发来的消息：%s' % data.decode('utf-8'))
#
# client.close()
