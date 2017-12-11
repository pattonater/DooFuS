# For abstraction of single-byte message headers
class Message:
    DELIMITER     = "~"
    LENGTH_SIZE   = 4
    
    class Tags:
        IDENTITY       = "V"    # [id]
        HEARTBEAT      = "H"    # ["hi"]
        
        HOST_JOINED    = "T"    # [host]
        USER_INFO      = "A"    # [user1, user2, ....]
        DFS_INFO       = "D"    # [dfs_json_str]
        POKE           = "P"    # ["poke"]

        REMOVE_FILE    = "R"
        UPLOAD_FILE    = "U"    

        STORE_REPLICA  = "Z"    # [name~uploader~part~total~data]
        HAVE_REPLICA   = "W"    # [name~uploader~part~total]

        REQUEST_FILE   = "S"    # [name]
        FILE_SLICE     = "F"    # [name~part~data]

    @classmethod
    def data_to_str(cls, tag, data):
        MAX_SIZE = cls.LENGTH_SIZE

        if isinstance(data, list):
            data_str = cls.DELIMITER.join(data)
        elif isinstance(data, str):
            data_str = data
        else:
            print("data_to_str only supposrt lists and strings")
            return False

        size = str(len(data_str))
        padding = MAX_SIZE - len(size)
        size_str = padding * "0" + size
        
        msg = tag + size_str + data_str
        return msg
