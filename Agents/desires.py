class Desire:
    def __init__(self, name: str, importance: float):
        self.name = name
        self.importance = importance


class MaintainDefense(Desire):
    def __init__(self):
        super().__init__('MaintainDefense', importance=1.0)


class ExecuteOffense(Desire):
    def __init__(self):
        super().__init__('ExecuteOffense', importance=1.0)


class ReturnToPosition(Desire):
    def __init__(self):
        super().__init__('ReturnToPosition', importance=1.0)
