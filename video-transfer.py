import socket
from argparse import ArgumentParser
import pickle
import struct
import cv2
import datetime

header_struct=struct.Struct('!I')

def recvall(sock,length):
	blocks=[]
	while length:
		block=sock.recv(length)
		if not block:
			raise EOFError('socket closed with %d bytes left in this block'.format(length))
		length-=len(block)
		blocks.append(block)
	return b''.join(blocks)

def get_block(sock):
	data=recvall(sock,header_struct.size)
	(block_length,)=header_struct.unpack(data)
	return recvall(sock,block_length)

def put_block(sock,message):
	block_length=len(message)
	sock.send(header_struct.pack(block_length))
	sock.send(message)

def server(address):
	sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
	sock.bind(address)
	sock.listen(1)
	print("Run this script in another window with '-c' to connect")
	sc, sockname=sock.accept()
	print('Accepted connection from',sockname)
	sc.shutdown(socket.SHUT_WR)
	cv2.namedWindow("LiveStream")
	while True:
		block=get_block(sc)
		if not block:
			break
		frameData=pickle.loads(block)
		print (frameData)
		cv2.imshow("Livestream",frameData)
		cv2.waitKey(20)
	cv2.destroyWindow("Livestream")
	sc.close()
	sock.close()

def client(address):
	#define the frame size and fps
	frame_width=680
	frame_height=480
	fps=30

	sock=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	sock.connect(address)
	sock.shutdown(socket.SHUT_RD)
	cap=cv2.VideoCapture(0)     ##open camera

	##set parameters for video file.
	startdate=datetime.datetime.now()
	startdate=datetime.datetime.strftime(startdate,"%H%M%S-%d%m%Y")
	videofile=startdate+".mp4"

	cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
	cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)
	size = (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
	fourcc = cv2.VideoWriter_fourcc(*'mp4v')
	video_writer = cv2.VideoWriter(videofile, fourcc, fps, size)
	
	## send frame to server.
	if cap.isOpened() is not True:
		print("Error opening camera.")
	else:
		ret, frame=cap.read()
		while ret:
			data=pickle.dumps(frame)
			put_block(sock,data)        ##sends it to server.
			video_writer.write(frame)   ##saves it to video file.
			ret, frame=cap.read()       ##reads next frame.
			key=cv2.waitKey(0)
			if key==27:
				break
	sock.close()

if __name__ == '__main__':
	parser=ArgumentParser(description='Transmit & recieve blocks over TCP/MPTCP')
	parser.add_argument('hostname',nargs='?',default='0.0.0.0',help='IP Address or hostname (default%(default)s)')
	parser.add_argument('-c', action='store_true',help='run as client')
	parser.add_argument('-p', type=int, metavar='port', default=8000, help='TCP port number default 8000')
	args=parser.parse_args()
	function=client if args.c else server
	function((args.hostname, args.p))
