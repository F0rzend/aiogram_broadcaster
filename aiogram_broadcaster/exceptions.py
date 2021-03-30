class RunningError(ValueError):
    def __init__(self, is_running: bool = False):
        if not is_running:
            message = 'The broadcast is not running'
        else:
            message = 'The broadcast is already running'
        super().__init__(message)
