class Ecosystem:
    def __init__(self):
        self.oxygen = 60
        self.pollution = 70
        self.biodiversity = 50
        self.temperature = 30
        self.score = 0
        self.level = 1

    def remove_plastic(self):
        self.pollution -= 10
        self.oxygen += 5
        self.biodiversity += 3
        self.score += 10

    def oil_spill(self):
        self.pollution += 15
        self.oxygen -= 10
        self.biodiversity -= 5
        self.score -= 5

    def grow_coral(self):
        if self.pollution < 40:
            self.biodiversity += 10
            self.oxygen += 5
            self.score += 15

    def check_level_up(self):
        if self.score >= 50:
            self.level = 2
        if self.score >= 100:
            self.level = 3

    def get_state(self):
        self.check_level_up()
        return {
            "oxygen": self.oxygen,
            "pollution": self.pollution,
            "biodiversity": self.biodiversity,
            "temperature": self.temperature,
            "score": self.score,
            "level": self.level
        }
