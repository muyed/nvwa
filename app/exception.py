class NoLoginException(BaseException):
    def __init__(self):
        self.msg = 'no login'

    def __str__(self):
        return self.msg

