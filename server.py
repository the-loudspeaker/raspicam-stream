import io
import socket
import struct
from PIL import Image
import matplotlib.pyplot as pl
from subprocess import Popen, PIPE
import datetime

server_socket = socket.socket()
server_socket.bind(('0.0.0.0', 9000))  #Here you can change the IP and port
server_socket.listen(0)

# naming the outputfile
startdate=datetime.datetime.now()
startdate=datetime.datetime.strftime(startdate,"%H%M%S-%d%m%Y")
videofile=startdate+".mp4"
# Writing to video file using ffmpeg.
p = Popen(['ffmpeg', '-y', '-f', 'image2pipe', '-vcodec', 'mjpeg', '-r', '8', '-i', '-', '-vcodec', 'mpeg4', '-q:v', '1', '-r', '8', videofile], stdin=PIPE)

# Accept a single connection and make a file-like object out of it
connection = server_socket.accept()[0].makefile('rb')
try:
    img = None
    while True:
        # Read the length of the image as a 32-bit unsigned int. If the
        # length is zero, quit the loop
        image_len = struct.unpack('<L', connection.read(struct.calcsize('<L')))[0]
        if not image_len:
            break
        # Construct a stream to hold the image data and read the image
        # data from the connection
        image_stream = io.BytesIO()
        image_stream.write(connection.read(image_len))
        # Rewind the stream, open it as an image with PIL and do some
        # processing on it
        image_stream.seek(0)
        image = Image.open(image_stream)
        image.save(p.stdin, 'JPEG')
        if img is None:
            img = pl.imshow(image)
        else:
            img.set_data(image)

        pl.pause(0.01)
        pl.draw()
        print('Image is %dx%d' % image.size)
        image.verify()
        print('Image is verified')
        print("warning: disconnecting from server side will lead to stream not being saved. disconnect from client side.")
finally:
    connection.close()
    server_socket.close()
