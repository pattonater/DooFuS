
# For abstraction of single-byte message headers
class MessageTags:
    HEARTBEAT   = "H"
    HOST        = "T" # someone has joined the network
    VERIFY      = "V" # used to verify legal user
#    JOIN        = "J" #???
    UPLOAD      = "U" # sent when new file is being uploaded to tell nodes that file has been uploaded
    REMOVE      = "R" # telling nodes to remove a given file from network
    AUTHORIZED  = "A" # list of authorized users
    DFS         = "D" # how to send metadata
    FILE        = "F" # start of file
    EOF         = "E" # end of file
    CHUNK       = "C" # intermediate stuff
    POKE        = "P"

    DELIMITER   = "~"

    #def valid_tag(self, message):
