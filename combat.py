class CombatManager:
    def __init__(self, player, enemy, player_turn=True, enemy_adv=1):
        self.player = player
        self.enemy = enemy
        self.player_turn = player_turn
