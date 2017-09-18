import socket,asyncore
import string

import logging
import logging.config

logging.config.fileConfig("logger.conf")
logger = logging.getLogger("proxy")

def debugstring(inbuf,iline,ilength):
    s = "\nDebug Information from Line:[%s],string length:[%s]\n"%(iline,ilength)
    print s
    logger.info("\nDebug Information from Line:[%s],string length:[%s]\n"%(iline,ilength))

    k = int(ilength/0xFFFF)
    for l in range(0,k+1):
        s = '-'*84
        tmp = "[%02d BEGIN]"%(k+1)
        s = s[:35] + tmp + s[45:]
        print s
        logger.info(s)

        if l == k:
            rlength = ilength%0xFFFF
        else:
            rlength = 0xFFFF

        j = 0
        for i in range(0,rlength):
            if j == 0:
                s = ' '*84
                tmp = "%04X:"%i
                s = tmp + s[6:]
                tmp = "%04X:"%(i+15)
                s = s[:74] + tmp
            tmp = "%02X "%ord(inbuf[i])
            offset = j*3 + 7 + (j>7)
            s = s[:offset] + tmp + s[offset+3:]
            if (inbuf[i] in string.printable) and ord(inbuf[i]) != 9 and ord(inbuf[i]) != 10:
                offset = j+56+(j>7)
                s = s[:offset] + inbuf[i] + s[offset+1:]
            else:
                offset = j+56+(j>7)
                s = s[:offset] + '.' + s[offset+1:]
            j+= 1
            if j == 16:
                print s
                logger.info(s)
                j = 0
            
        if j and rlength:
            print s
        s = '-'*84
        tmp = "[%02d END]"%(k+1)
        s = s[:36] + tmp + s[44:]
        print s
        logger.info(s)

class forwarder(asyncore.dispatcher):
    def __init__(self, ip, port, remoteip,remoteport,backlog=5):
        asyncore.dispatcher.__init__(self)
        self.remoteip=remoteip
        self.remoteport=remoteport
        self.create_socket(socket.AF_INET,socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((ip,port))
        self.listen(backlog)

    def handle_accept(self):
        conn, addr = self.accept()
        print '--- Connect --- '
        logger.info("--- Connect --- ")
        sender(receiver(conn),self.remoteip,self.remoteport)

class receiver(asyncore.dispatcher):
    def __init__(self,conn):
        asyncore.dispatcher.__init__(self,conn)
        self.from_remote_buffer=''
        self.to_remote_buffer=''
        self.sender=None

    def handle_connect(self):
        pass

    def handle_read(self):
        read = self.recv(4096)
        print 'receiver %04i -->'%len(read)
        logger.info("receiver %04i -->"%len(read))
        debugstring(read ,1,len(read))
        self.from_remote_buffer += read

    def writable(self):
        return (len(self.to_remote_buffer) > 0)

    def handle_write(self):
        debugstring(self.to_remote_buffer,4,len(self.to_remote_buffer))
        sent = self.send(self.to_remote_buffer)
        print 'receiver %04i <--'%sent
        logger.info("receiver %04i <--"%sent)
        self.to_remote_buffer = self.to_remote_buffer[sent:]

    def handle_close(self):
        print 'handle_close 1'
        logger.info("handle_close 1")
        self.close()
        #if self.sender:
        #    self.sender.close()

class sender(asyncore.dispatcher):
    def __init__(self, receiver, remoteaddr,remoteport):
        asyncore.dispatcher.__init__(self)
        self.receiver=receiver
        receiver.sender=self
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((remoteaddr, remoteport))

    def handle_connect(self):
        pass

    def handle_read(self):
        read = self.recv(4096)
        print 'sender <-- %04i'%len(read)
        logger.info("sender <-- %04i"%len(read))
        debugstring(read,3,len(read))
        self.receiver.to_remote_buffer += read

    def writable(self):
        return (len(self.receiver.from_remote_buffer) > 0)

    def handle_write(self):
        sent = self.send(self.receiver.from_remote_buffer)
        print 'sender --> %04i'%sent
        logger.info("sender --> %04i"%sent)
        #debugstring(sent,1,len(sent))
        self.receiver.from_remote_buffer = self.receiver.from_remote_buffer[sent:]

    def handle_close(self):
        print 'handle_close 2'
        logger.info("handle_close 2")
        self.close()
        #self.receiver.close()

if __name__=='__main__':
    import optparse
    parser = optparse.OptionParser()

    parser.add_option(
        '-l','--local-ip',
        dest='local_ip',default='127.0.0.1',
        help='Local IP address to bind to')
    parser.add_option(
        '-p','--local-port',
        type='int',dest='local_port',default=80,
        help='Local port to bind to')
    parser.add_option(
        '-r','--remote-ip',dest='remote_ip',
        help='Local IP address to bind to')
    parser.add_option(
        '-P','--remote-port',
        type='int',dest='remote_port',default=80,
        help='Remote port to bind to')
    options, args = parser.parse_args()

    forwarder(options.local_ip,options.local_port,options.remote_ip,options.remote_port)
    asyncore.loop()
