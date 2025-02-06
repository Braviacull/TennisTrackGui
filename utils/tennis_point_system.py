# TENNIS POINTS SYSTEM

def update_score (score):
    if score < 30:
        score += 15
    elif score == 30:
        score += 10
    elif score >= 40:
        score += 1
    return score

def assign_point (self, who_scored):
    if who_scored == 1:
        self.score[0] = update_score(self.score[0])
    elif who_scored == 2:
        self.score[1] = update_score(self.score[1])
        
    game_winner = check_game_winner(self)

    if game_winner is not None: # game_winner won the game
        self.score = [0, 0]
        update_games(self, game_winner)

def check_game_winner (self):
    game_winner = None

    if self.score[0] == 41 and self.score[1] < 40:
        game_winner = 1
    elif self.score[1] == 41 and self.score[0] < 40:
        game_winner = 2
    elif self.score[0] >= 40 and self.score[1] >= 40: # deuce
        if self.score[0] == self.score[1] + 2:
            game_winner = 1
        elif self.score[1] == self.score[0] + 2:
            game_winner = 2

    return game_winner

def update_games (self, game_winner):
    if game_winner == 1:
        self.games[0] += 1
    elif game_winner == 2:
        self.games[1] += 1

    set_winner = check_set_winner(self)

    if set_winner is not None:
        self.games = [0, 0]
        update_sets(self, set_winner)

def check_set_winner(self):
    set_winner = None

    if self.games[0] == 6 and self.games[1] < 5:
        set_winner = 1
    elif self.games[1] == 6 and self.games[0] < 5:
        set_winner = 2
    elif self.games[0] == 7 and self.games[1] == 5:
        set_winner = 1
    elif self.games[1] == 7 and self.games[0] == 5:
        set_winner = 2
    elif self.games[0] == 6 and self.games[1] == 6:
        self.tiebreak = True

    return set_winner

def assign_point_tiebreak (self, who_scored):
    if who_scored == 1:
        self.score[0] += 1
    elif who_scored == 2:
        self.score[1] += 1

    tiebreak_winner = check_tiebreak_winner(self)

    if tiebreak_winner is not None:
        self.tiebreak = False
        self.score = [0, 0]
        self.games = [0, 0]
        update_sets(self, tiebreak_winner)

def check_tiebreak_winner (self):
    tiebreak_winner = None

    if self.score[0] >= 7 and self.score[0] == self.score[1] + 2:
        tiebreak_winner = 1
    elif self.score[1] >= 7 and self.score[1] == self.score[0] + 2:
        tiebreak_winner = 2

    return tiebreak_winner

def update_sets (self, set_winner):
    if set_winner == 1:
        self.sets[0] += 1
    elif set_winner == 2:
        self.sets[1] += 1

    match_winner = check_match_winner(self)

    if match_winner is not None:
        declare_match_winner(self, match_winner)

def check_match_winner(self):
    match_winner = None

    if self.sets[0] == self.max_sets:
        match_winner = 1
    elif self.sets[1] == self.max_sets:
        match_winner = 2

    return match_winner

def declare_match_winner (self, match_winner):
    if match_winner == 1:
        self.winner = self.player1
    elif match_winner == 2:
        self.winner = self.player2

    print ("Match winner is: " + self.winner)

def recalculate_match_state (self):
    self.score = [0, 0]
    self.games = [0, 0]
    self.sets = [0, 0]
    self.winner = None
    self.tiebreak = False
    for data in self.scene_data:
        if data.point_winner is not None:
            assign_point(self, data.point_winner)
        else: break

