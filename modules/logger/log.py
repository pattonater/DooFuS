import logging, sys

# Log class meant to facilitate logging in other modules. To use this class
# add 'logger = None' and 'log = None' to the top of your file, and in __init__
# add 'log = Log()' and 'self._logger = log.get_logger()'
# from there, make calls to the self._logger instead of using print
# ie. self._logger.info("print this with info level")
# or  self._logger.debug("this one is debug level")
# check out network.py or doofus.py or ask me

class Log:

    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)
        
        formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
        
        self._dh = logging.FileHandler('logs/debug.log')
        self._dh.setLevel(logging.NOTSET)
        self._dh.setFormatter(formatter)
        
        self._ih = logging.FileHandler('logs/info.log')
        self._ih.setLevel(logging.INFO)
        self._ih.setFormatter(formatter)
        
        self._ch = logging.StreamHandler(sys.stdout)
        self._ch.setLevel(logging.WARNING)
        self._ch.setFormatter(formatter)
        
        self._logger.addHandler(self._dh)
        self._logger.addHandler(self._ih)
        self._logger.addHandler(self._ch)
    
        
    def get_logger(self):
        return self._logger
        
    def toggle_info(self):
        if self._logger.handlers[2].level != logging.INFO:
            self._logger.handlers[2].setLevel(logging.INFO)
            self._logger.info("Log level set to INFO")
        else:
            self._logger.info("Log level set to WARNING")
            self._logger.handlers[2].setLevel(logging.WARNING)
            
    
    def toggle_debug(self):
        if self._logger.handlers[2].level != logging.DEBUG:
            self._logger.handlers[2].setLevel(logging.DEBUG)
            self._logger.info("Log level set to DEBUG")
        else:
            self._logger.info("Log level set to WARNING")
            self._logger.handlers[2].setLevel(logging.WARNING)
            

