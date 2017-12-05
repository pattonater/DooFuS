
# For abstraction of single-byte message headers
class MessageTags:
    HEARTBEAT   = "H"
    HOST        = "T"
    VERIFY      = "V"
    JOIN        = "J" #???
    UPLOAD      = "U"
    REMOVE      = "R"
    AUTHORIZED  = "A"
    DFS         = "D"

    DELIM       = "~"

    #def valid_tag(self, message):
