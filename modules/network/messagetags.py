
# For abstraction of single-byte message headers
class MessageTags:
    HEARTBEAT   = "H"
    HOST        = "T"
    VERIFY      = "V"
    JOIN        = "J"
    FILE        = "F"
    DFS         = "D"

    DELIM       = "~"

    #def valid_tag(self, message):
