class Rule:
    def __init__(self, rule_id: str, weight: float, description: str = ''):
        self.id = rule_id
        self.weight = weight
        self.description = description

    def evaluate(self, agent):
        pass

    def __str__(self):
        return f"Rule {self.id} has weight {self.weight}: {self.description}"
