#!/usr/bin/python

import xmpp

class xmppInterface():
    username = ""
    password = ""
    xmppConnection = None
    incomingMessageHandler = None

    def connect(self):
        jid = xmpp.protocol.JID(self.username)
        self.xmppConnection = xmpp.Client(jid.getDomain(), debug=[])
        if self.xmppConnection.connect() == "":
            print "Failed to Connect to " + self.username + "."
            return False
        if self.xmppConnection.auth(jid.getNode(),self.password) == None:
            print "Failed to Authenticate " + self.username + "."
            return False

        self.xmppConnection.RegisterHandler('message', self.receivedMessage)
        self.xmppConnection.sendInitPresence()
        
    def update(self):
        try:
            self.xmppConnection.Process(1)
        except KeyboardInterrupt:
            return 0
        return 1
        
    def receivedMessage(self, conn, msg):
        messageSender = str(msg.getFrom())
        messageContents = str(msg.getBody())
        if (not messageContents == None and not messageContents == "" and not self.incomingMessageHandler == None):
            self.incomingMessageHandler.receivedMessage(messageSender, messageContents)
        
    def sendMessage(self, recipient, msg):
        self.xmppConnection.send(xmpp.protocol.Message(recipient, msg))
