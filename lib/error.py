class ICFPError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)
