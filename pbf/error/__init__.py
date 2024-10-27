
class Error(Exception): pass

class NoApiError(Error): pass

class ConfigError(Error): pass

class LimitExceedError(Error): pass