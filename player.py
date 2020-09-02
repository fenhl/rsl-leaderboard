from trueskill import Rating

class Player:
    def __init__(self, userid, display_name):
        self.id = userid
        self.display_name = display_name
        self.rating = Rating()
        self.display_rating = -1

    def compute_display_rating(self):
        mu = self.rating.mu
        sigma = self.rating.sigma
        self.display_rating = (mu - 2.*sigma) * 100.

    def print_line(self):
        print(self.display_name + ": " + str(self.display_rating))

    def __repr__(self):
        return repr(f"<player.Player object for {self.display_name}>")