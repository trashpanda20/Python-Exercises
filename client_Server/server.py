import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#AF_interent socket Sock_Stream is tcp
s.bind(("127.0.0.1", 3002))
#assigns ip address and port
s.listen()
print("Listening")
while True:
  client, address = s.accept()
  print("Connected: {}".format(address))
  message = "Howdy C!"
  client.send(message.encode("ascii"))
  client.close()
