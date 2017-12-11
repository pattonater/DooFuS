# For abstraction of single-byte message headers
class Message:
    DELIMITER     = "~"
    LENGTH_SIZE   = 4
    
    class Tags:
        IDENTITY       = "V"    
        HEARTBEAT      = "H"
        
        HOST_JOINED    = "T"
        USER_INFO      = "A"
        DFS_INFO       = "D"    #D3~jsonfile
        POKE           = "P"

        REMOVE_FILE    = "R"
        UPLOAD_FILE    = "U"    #

        STORE_REPLICA  = "Z"    #Z3~name~uploader~part~total~data
        HAVE_REPLICA   = "W"    #W3~name~uploader~part~total

        REQUEST_FILE   = "S"    #S3~name
        FILE_SLICE     = "F"    #F3~name~part~data

        
    #def valid_tag(self, message):

    # this doesnt work
    @classmethod
    def data_to_str(cls, tag, data):
        MAX_SIZE = cls.LENGTH_SIZE
        data_str = cls.DELIMITER.join(data)

        size = str(len(data_str))
        padding = MAX_SIZE - len(size)
        size_str = padding * "0" + size
        
        msg = tag + size_str + data_str
        return msg
