#!/usr/bin/python

import simpleXMPPInterface
import sys
import os
import time
import subprocess

class nonBlockingReader():
    inputSource = None
    
    if subprocess.mswindows:
        reader = None

        import threading
        class readerThread(threading.Thread):
            readFrom = None
            buf = ""
            bufCursor = 0
            
            def run(self):
                while True:
                    readData = self.readFrom.read(1)
                    self.buf = self.buf + readData
            
            def getIncrementalBuffer(self):
                result = self.buf[self.bufCursor:len(self.buf)]
                self.bufCursor += len(result)
                
                return result

        def getReaderThread(self):
            if (self.reader == None):
                self.reader = self.readerThread()        
                self.reader.daemon = True
                self.reader.readFrom = self.inputSource
                self.reader.start()                
            return self.reader
        
        def readAsMuchAsPossible(self):
            return self.getReaderThread().getIncrementalBuffer()
    else:
        def nonBlockingReadByte(self):
            import select

            inputready, outputready, exceptready = select.select([self.inputSource], [], [], 0) 
            for p in inputready:
                return p.read(1)
            return ""
        
        def readAsMuchAsPossible(self):
            result = ""
            readData = self.nonBlockingReadByte()
            while not (readData == ""):
                result += readData
                readData = self.nonBlockingReadByte()
            
            return result

class XMPP_REPL():
    replProcess = None
    replCommandLine = []
    xmppInstance = None
    pipeReaderOut = None
    pipeReaderErr = None
    remoteUsername = ""
    
    def startREPL(self):
        self.replProcess = subprocess.Popen(self.replCommandLine,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        self.pipeReaderOut = nonBlockingReader()
        self.pipeReaderOut.inputSource = self.replProcess.stdout
        self.pipeReaderErr = nonBlockingReader()
        self.pipeReaderErr.inputSource = self.replProcess.stderr
        
    def startXMPP(self, username, password, remoteUsername):
        self.xmppInstance = simpleXMPPInterface.xmppInterface()
        self.xmppInstance.username = username
        self.xmppInstance.password = password
        self.remoteUsername = remoteUsername
        self.xmppInstance.incomingMessageHandler = self
        self.xmppInstance.connect()
        self.GoOn()
        
    def GoOn(self):
        while self.xmppInstance.update() and self.replProcess.returncode == None:
            readData = self.pipeReaderOut.readAsMuchAsPossible()
            if not (readData == ""):
                self.sendMessage(readData)
            readData = self.pipeReaderErr.readAsMuchAsPossible()
            if not (readData == ""):
                self.sendMessage(readData)
    
            try:
                time.sleep(0.05)
            except KeyboardInterrupt:
                pass

    def sendMessage(self, messageContents):
        self.xmppInstance.sendMessage(self.remoteUsername, messageContents)
        
    def receivedMessage(self, sender, messageContents):
        if (sender.startswith(self.remoteUsername) and self.replProcess.returncode == None):
            try:
                self.replProcess.stdin.write(messageContents + "\n")
                self.replProcess.stdin.flush()
            except IOError:
                self.receiveMessageWithNoREPL(messageContents + "\n")
        
    def receiveMessageWithNoREPL(self, msg):
        if (msg == "//restart\n"):
            self.sendMessage("Restarting Process.")
            self.startREPL()
            self.sendMessage("Restart Complete.")
        else:
            self.sendMessage("Remote Process is not available. Use //restart to restart it.")

def startXMPP_REPL(commandLine, username, password, remoteUsername):
    repl = XMPP_REPL()
    repl.replCommandLine = commandLine
    repl.startREPL()
    repl.startXMPP(username, password, remoteUsername)
