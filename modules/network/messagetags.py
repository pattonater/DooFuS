
# For abstraction of single-byte message headers
class MessageTags:
    HEARTBEAT   = "H"
    HOST        = "T"
    VERIFY      = "V"
    UPLOAD      = "U"
    REMOVE      = "R"
    USERS       = "A"
    DFS         = "D"
    FILE        = "F"
    EOF         = "E"
    CHUNK       = "C"
    POKE        = "P"

    DELIMITER   = "~"

    #def valid_tag(self, message):
