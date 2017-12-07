
# For abstraction of single-byte message headers
class MessageTags:
    HEARTBEAT   = "H"
    HOST        = "T"
    VERIFY      = "V"
#    JOIN        = "J" #???
    UPLOAD      = "U"
    REMOVE      = "R"
    AUTHORIZED  = "A"
    DFS         = "D"
    FILE        = "F"
    EOF         = "E"
    CHUNK       = "C"
    POKE        = "P"

    DELIMITER   = "~"

    #def valid_tag(self, message):
