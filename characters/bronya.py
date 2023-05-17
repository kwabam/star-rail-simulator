from components import Character


class Bronya(Character):
    def __init__(self, lightcone, main_stats, sub_stats, buff_target, energy_max=120, ascension=6, level=80):
        super().__init__("bronya", lightcone, main_stats, sub_stats, energy_max, ascension, level)
        self.buff_target = buff_target

    def act(self):
        damage = 0
        if self.energy >= self.energy_max:  # ult at start of turn. This gives extra turn of buff.
            damage += self.ult()
        if self.game.skill_points > 0:
            damage += self.skill()
        else:
            damage += self.basic()

        self.game.add_damage(damage)

    def basic(self):
        dmg = self.calculate_base_dmg(mv=1)
        # advance
        self.game.action_queue.append((self, self.game.time + (10000 * (1-.3))/self.get_speed()))
        self.game.add_skill_point()
        self.add_energy(20)
        print("basic damage: ", dmg)
        return dmg

    def skill(self):
        self.game.add_buff(self.buff_target, "bronya skill", "percent_dmg", 66, 1)
        self.game.skill_points -= 1
        self.add_energy(30)
        self.game.advance(self.buff_target, 100)

    def ult(self):
        self.game.add_buff(self, "bronya ult", "percent_dmg", 80, 2)
        self.game.add_buff(self, "bronya ult", "percent_penetration", 20, 2)
        self.energy = 5
        dmg = self.calculate_base_dmg(mv=4.25)
        print("ult damage: ", dmg)
        return dmg