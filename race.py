import trueskill
import tools
import json

class Race:
    def __init__(self, filepath, asyn=False):


        if asyn:
            self.init_asyn(filepath)
        else:
            self.init_racetime(filepath)

        self.tabledata = []
        self.htmltable = ""


    def init_racetime(self, filepath):
        """ Initalize a race using data scraped from racetime api """
        with open(filepath, 'r') as fin:
            data = json.load(fin)

        self.slug = data['slug']
        self.race_materials_name = None
        self.datetime = data["ended_at"]
        self.entrants = [{
                "userid": entr['user']['id'],
                "place": entr['place'],
                "display_name": entr['user']['name'],
                "status": entr['status']['value'],
                "finish_time": entr['finish_time']
            } for entr in data['entrants']]
        self.on_racetime = True


    def init_asyn(self, filepath):
        print(filepath)
        with open(filepath, 'r') as fin:
            data = fin.readlines()
        data = [line.strip() for line in data]

        self.slug = data[0]
        self.race_materials_name = data[1]
        self.datetime = data[2]
        self.entrants = [{
                "userid": row.split(',')[0].split('/')[-1],
                "place": int(row.split(',')[1]) if row.split(',')[1] != 'null' else None,
                "display_name": row.split(',')[2],
                "status": row.split(',')[3],
                "finish_time": row.split(',')[4]
            } for row in data[3:]]
        
        for entr in self.entrants:
            if entr['finish_time'] == 'null':
                entr['finish_time'] = None
        self.on_racetime = False

    def build_html(self):
        self.htmltable += "\t<ol class=\"ol-table\">\n"
        self.htmltable += "\t\t<span class=\"table-header\">\n"
        self.htmltable += f"\t\t\t<h4>{tools.slug_with_link(self.slug, self.on_racetime)}</h4>\n"
        if self.race_materials_name is not None:
            self.htmltable += "\t\t\t<span class=\"race-materials\">"
            self.htmltable += f"(<a href=\"/race_materials/{self.race_materials_name}_patch.zpf\" class=\"a-materials\" download>Download Patch</a>) "
            self.htmltable += f"(<a href=\"/race_materials/{self.race_materials_name}_spoiler.json\" class=\"a-materials\" download>Download Spoiler</a>)"
            self.htmltable += "</span>\n"
        self.htmltable += f"\t\t\t<span class=\"race-date\">{tools.pretty_race_date(self.datetime)}</span>\n"
        self.htmltable += "\t\t</span>\n"
        for player in self.tabledata:
            self.htmltable += "\t\t<li class=\"li-table\">\n"
            self.htmltable += f"\t\t\t<span class=\"placement\">{tools.pretty_placement(player['place'])}</span>\n"
            self.htmltable += f"\t\t\t<span class=\"player-name\">{player['name']}</span>\n"
            self.htmltable += f"\t\t\t<span class=\"finish-time\">{tools.pretty_finish_time(player['finish_time'])}</span>\n"
            self.htmltable += f"\t\t\t<span class=\"rating-delta\">{tools.format_delta(player['delta'])}</span>\n"
            self.htmltable += "\t\t</li>\n"
        self.htmltable += "\t</ol>\n"


    def build_table(self, playerlist, placement, start_ratings, end_ratings):
        """ Build dict to display race in webpage. """
        for i in range(len(playerlist)):
            pname = playerlist[i].display_name
            entr = [x for x in self.entrants if x['display_name'] == pname][0]

            # If ff, overwrite placement
            if entr['status'] == 'dnf':
                placement[i] = None

            srate = start_ratings[i][0]
            erate = end_ratings[i][0]
            self.tabledata.append(
                {
                    "place": placement[i],
                    "name": pname,
                    "finish_time": entr["finish_time"],
                    "rating": round((srate.mu - 2.*srate.sigma) * 100.),
                    "delta": round((erate.mu - 2.*erate.sigma) * 100.) - round((srate.mu - 2.*srate.sigma) * 100.)
                }
            )
        self.build_html()


    def rate(self, playerlist, placement):
        """ Given a list of players and race placement, compute ratings using trueskill """
        start_ratings = [(player.rating,) for player in playerlist]
        end_ratings = trueskill.rate(start_ratings, ranks=placement)
        for i in range(len(end_ratings)):
            playerlist[i].rating = end_ratings[i][0]
            playerlist[i].compute_display_rating()
        self.build_table(playerlist, placement, start_ratings, end_ratings)
