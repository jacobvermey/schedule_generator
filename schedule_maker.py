"""
The `schedule_maker.py` module provides functionality to generate and manage a sports schedule for a given number of teams, games, and time slots.

The main features include:
- Generating a schedule that avoids invalid matchups and tries to balance the number of home games for each team.
- Allowing users to set time slot restrictions for each team.
- Providing a user interface to edit team names, field details, and game dates.
- Exporting the generated schedule to a CSV file.

The module defines several classes to represent the key entities in the schedule:
- `Game`: Represents a single game with a home team, away team, time slot, and date.
- `TimeSlot`: Represents a time slot with a name, field, and time.
- `Team`: Represents a team with a name, time slot restrictions, opponents, and game history.
- `GameDate`: Represents a game date with a list of games.

The `generate_schedule()` function is the main entry point for generating the schedule, and the `main_window()` function provides the user interface for interacting with the schedule.
"""

import random
import tkinter as tk
from tkinter import ttk
import csv
import os

# Example usage
number_of_teams = 0
number_of_games = 0
number_of_time_slots = 0
filename = os.path.join(os.getcwd(), "schedule.csv")

class Game:
    def __init__(self, home_team, away_team, time_slot, game_date):
        self.home_team = home_team
        self.away_team = away_team
        self.time_slot = time_slot
        self.date = game_date

class TimeSlot:
    def __init__(self, id):
        self.id = id
        self.name = f"Time Slot {id}"
        self.games = []
        self.field = "Null"
        self.time = "Null"

    def add_field(self, field):
        self.field = field

    def add_time(self, time):
        self.time = time

    def __str__(self):
        return str(self.id)

class Team:
    def __init__(self, id):
        self.id = id
        self.name = f"Team {id}"
        self.time_slot_restrictions = []
        self.opponents = []
        self.games = []
        self.invalid_opp = [self]
        self.home_games = 0
        self.matchups = []

    def add_time_slot_restriction(self, time_slot):
        self.time_slot_restrictions.append(time_slot)

    def remove_time_slot_restriction(self, time_slot):
        if time_slot in self.time_slot_restrictions:
            self.time_slot_restrictions.remove(time_slot)

    def add_invalid_opp(self, opp):
        self.invalid_opp.append(opp)

    def change_team_name(self, name):
        self.name = name

    def __str__(self):
        return self.name

class GameDate:
    def __init__(self, game_num):
        self.id = game_num
        self.date = str(game_num)
        self.games = []

    def __str__(self):
        return str(self.date)

# Init Teams
teams = []
for i in range(number_of_teams):
    teams.append(Team(i + 1))

# Init Time slots
time_slots = []
for i in range(number_of_time_slots):
    time_slots.append(TimeSlot(i + 1))

# Game Dates
game_dates = []
for i in range(number_of_games):
    game_dates.append(GameDate(i + 1))

schedule = []

def generate_schedule():
    # Clear variables
    schedule.clear()
    for team in teams:
        team.games = []
        team.matchups = []
        team.home_games = 0
        team.opponents = []

    for time_slot in time_slots:
        time_slot.games = []

    for game_date in game_dates:
        game_date.games = []

    # Check for invalid opponents
    for team in teams:
        for opp in teams:
            add_invalid_opp(team, opp)

    # Loop based on number of games
    for game_date in game_dates:
        scheduled_teams = []
        random.shuffle(teams)
        teams.sort(key=lambda team: (team.matchups.count(0)), reverse=True)
        teams.sort(key=lambda team: len(team.time_slot_restrictions), reverse=True)
        teams.sort(key=lambda team: len(team.games))

        for team in teams:
            if team not in scheduled_teams and len(game_date.games) < number_of_time_slots:
                opp_list = get_valid_opp(team, scheduled_teams)
                time_slot, opp = select_opp(opp_list, game_date.id - 1, team)
                if opp is not None:
                    home_team = team if team.home_games < opp.home_games else opp
                    away_team = opp if home_team == team else team
                    home_team.home_games += 1
                    game = Game(home_team, away_team, time_slot, game_date.date)
                    schedule.append(game)
                    team.games.append(game)
                    opp.games.append(game)
                    game_date.games.append(game)
                    time_slot.games.append(game)
                    team.opponents.append(opp)
                    opp.opponents.append(team)
                    scheduled_teams.append(team)
                    scheduled_teams.append(opp)

        teams.sort(key=lambda team: team.id)
        teams.sort(key=lambda team: len(team.games))
        swap_teams(teams, game_date)
        
        # Swap games to spread matchups

def swap_teams(teams, game_date):
    for team in teams:
        if team.opponents != []:
            team.matchups = []
            for opp in teams:
                if opp in team.invalid_opp:
                    team.matchups.append(99)
                else:
                    team.matchups.append(team.opponents.count(opp))
            opp = team.opponents[-1]
            matchup_count = team.opponents.count(opp)
            if matchup_count - 2 >= min(team.matchups):
                for game in game_date.games:
                    matchup_count = team.opponents.count(opp)
                    if matchup_count - 2 >= game.away_team.matchups[team.id - 1]:
                        if matchup_count - 2 >= game.home_team.matchups[opp.id - 1]:
                            if game.time_slot not in team.time_slot_restrictions and team.games[-1].time_slot not in game.home_team.time_slot_restrictions:
                                print(f"{team.name} Swapped With {game.home_team.name} on Game Date {game_date.date}")
                                swap_teams_in_game(team, game, opp, is_home_team=True)

                    if matchup_count - 2 >= game.home_team.matchups[team.id - 1]:
                        if matchup_count - 2 >= game.away_team.matchups[opp.id - 1]:
                            if game.time_slot not in team.time_slot_restrictions and team.games[-1].time_slot not in game.away_team.time_slot_restrictions:
                                print(f"{team.name} Swapped With {game.away_team.name} on Game Date {game_date.date}")
                                swap_teams_in_game(team, game, opp, is_home_team=False)

def swap_teams_in_game(team, game, opp, is_home_team):
    if is_home_team:
        # Adjust opponents
        game.home_team.opponents[-1] = team.opponents[-1]
        game.away_team.opponents[-1] = team
        team.opponents[-1] = game.away_team
        opp.opponents[-1] = game.home_team

        # Adjust game
        team.games[-1].home_team = game.home_team
        game.home_team.games[-1] = team.games[-1]
        team.games[-1] = game
        game.home_team = team
    else:
        # Adjust opponents
        game.home_team.opponents[-1] = team.opponents[-1]
        game.away_team.opponents[-1] = team
        team.opponents[-1] = game.away_team
        opp.opponents[-1] = game.home_team

        # Adjust game
        team.games[-1].away_team = game.home_team if team == team.games[-1].home_team else game.away_team
        game.away_team.games[-1] = team.games[-1] if team == team.games[-1].home_team else game.home_team.games[-1]
        team.games[-1] = game
        game.away_team = team if team != team.games[-1].home_team else game.home_team
def add_invalid_opp(team, opp):
    combined_invalid_time_slot = set(team.time_slot_restrictions) | set(opp.time_slot_restrictions)
    if len(combined_invalid_time_slot) == len(time_slots):
        team.add_invalid_opp(opp)

def get_valid_opp(team, scheduled_teams):
    opp_list = [opp for opp in teams if opp not in team.invalid_opp and opp not in scheduled_teams]
    opp_list.sort(key=lambda opp: count_opp_occurrence(team, opp))
    return opp_list

def count_opp_occurrence(team, opp):
    return sum(1 for t in team.opponents if t == opp)

def select_opp(opp_list, game_num, team):
    random.shuffle(time_slots)
    for opp in opp_list:
        for time_slot in time_slots:
            if len(time_slot.games) <= game_num and \
               time_slot not in opp.time_slot_restrictions and \
               time_slot not in team.time_slot_restrictions:
                return time_slot, opp
    return None, None

def open_restrictions_window():
    restrictions_window = tk.Toplevel(window)
    restrictions_window.title("Set Time Slot Restrictions")

    label = tk.Label(restrictions_window, text="Team Name")
    label.grid(row=0, column=0)

    for col, time_slot in enumerate(time_slots):
        label = tk.Label(restrictions_window, text=time_slot.name)
        label.grid(row=0, column=col + 1)

    checkboxes = []
    for r, team in enumerate(teams):
        label = tk.Label(restrictions_window, text=team.name)
        label.grid(row=r + 1, column=0)
        checkboxes_row = []
        for col, time_slot in enumerate(time_slots):
            checkbox_var = tk.IntVar(value=1 if time_slot in team.time_slot_restrictions else 0)
            checkbox = ttk.Checkbutton(restrictions_window, variable=checkbox_var, onvalue=1, offvalue=0)
            checkbox.grid(row=r + 1, column=col + 1)
            checkboxes_row.append((checkbox_var, team, time_slot, checkbox))
        checkboxes.append(checkboxes_row)

    def save_restrictions():
        for checkbox_row in checkboxes:
            for checkbox_var, team, time_slot, _ in checkbox_row:
                if checkbox_var.get() == 1:
                    team.add_time_slot_restriction(time_slot)
        restrictions_window.destroy()

    ok_button = tk.Button(restrictions_window, text="OK", command=save_restrictions)
    ok_button.grid(row=len(teams) + 1, column=0, columnspan=len(time_slots), pady=10)

def team_details():
    details_window = tk.Toplevel(window)
    details_window.title("Team Details")

    teams.sort(key=lambda team: team.id)
    time_slots.sort(key=lambda slot: slot.id)

    for team in teams:
        team.matchups = [99 if opp in team.invalid_opp else team.opponents.count(opp) for opp in teams]

    fields = set(time_slot.field for time_slot in time_slots)
    times = set(time_slot.time for time_slot in time_slots)

    label = tk.Label(details_window, text="Team Name")
    label.grid(row=0, column=0)
    label = tk.Label(details_window, text="Game Count")
    label.grid(row=0, column=1)
    label = tk.Label(details_window, text="Home Games")
    label.grid(row=0, column=2)
    label = tk.Label(details_window, text="Matchup Count")
    label.grid(row=0, column=3)
    label = tk.Label(details_window, text=fields)
    label.grid(row=0, column=4)
    label = tk.Label(details_window, text=times)
    label.grid(row=0, column=5)

    for r, team in enumerate(teams):
        field_list = [game.time_slot.field for game in team.games]
        time_list = [game.time_slot.time for game in team.games]
        field_sum = [field_list.count(field) for field in fields]
        time_sum = [time_list.count(time) for time in times]

        label = tk.Label(details_window, text=team.name)
        label.grid(row=r + 1, column=0)
        label = tk.Label(details_window, text=str(len(team.games)))
        label.grid(row=r + 1, column=1)
        label = tk.Label(details_window, text=str(team.home_games))
        label.grid(row=r + 1, column=2)
        label = tk.Label(details_window, text=team.matchups)
        label.grid(row=r + 1, column=3)
        label = tk.Label(details_window, text=field_sum)
        label.grid(row=r + 1, column=4)
        label = tk.Label(details_window, text=time_sum)
        label.grid(row=r + 1, column=5)

def name_teams():
    name_window = tk.Toplevel(window)
    name_window.title("Edit Team Names")

    entries = []
    for team in teams:
        label = tk.Label(name_window, text=f"Team {team.id}")
        label.grid(row=team.id, column=0, padx=10, pady=5)
        entry = tk.Entry(name_window, width=20)
        entry.insert(tk.END, team.name)
        entry.grid(row=team.id, column=1, padx=10, pady=5)
        entries.append(entry)

    def save_names():
        for i, entry in enumerate(entries):
            new_name = entry.get().strip()
            teams[i].name = new_name
        name_window.destroy()

    save_button = ttk.Button(name_window, text="Save", command=save_names)
    save_button.grid(row=number_of_teams + 1, column=0, columnspan=2, padx=10, pady=10)

def edit_dates():
    dates_window = tk.Toplevel(window)
    dates_window.title("Edit Game Dates")

    label = tk.Label(dates_window, text="Game Number")
    label.grid(row=0, column=0)
    label = tk.Label(dates_window, text="Date (YYYY-MM-DD)")
    label.grid(row=0, column=1)

    date_entries = []
    for game_date in game_dates:
        label = tk.Label(dates_window, text=f"Game {game_date.id}")
        label.grid(row=game_date.id, column=0)
        entry_var = tk.StringVar(value=game_date.date)
        entry = ttk.Entry(dates_window, textvariable=entry_var)
        entry.grid(row=game_date.id, column=1)
        date_entries.append((game_date, entry_var, entry))

    def save_game_dates():
        for game_date, entry_var, _ in date_entries:
            game_date.date = entry_var.get()
        dates_window.destroy()

    ok_button = tk.Button(dates_window, text="OK", command=save_game_dates)
    ok_button.grid(row=number_of_games+1, column=0, columnspan=2, pady=10)

def define_fields():
    fields_window = tk.Toplevel(window)
    fields_window.title("Edit Field Details")

    time_slots.sort(key=lambda slot: slot.id)

    label = tk.Label(fields_window, text="Name")
    label.grid(row=0, column=0, padx=10, pady=5)
    label = tk.Label(fields_window, text="Field")
    label.grid(row=0, column=1, padx=10, pady=5)
    label = tk.Label(fields_window, text="Time (HH:MM)")
    label.grid(row=0, column=2, padx=10, pady=5)

    entries = []
    for r, time_slot in enumerate(time_slots):
        label = tk.Label(fields_window, text=str(time_slot.name))
        label.grid(row=r + 1, column=0, padx=10, pady=5)
        field_entry = tk.Entry(fields_window, width=20)
        field_entry.insert(tk.END, time_slot.field)
        field_entry.grid(row=r + 1, column=1, padx=10, pady=5)
        time_entry = tk.Entry(fields_window, width=20)
        time_entry.insert(tk.END, time_slot.time)
        time_entry.grid(row=r + 1, column=2, padx=10, pady=5)
        entries.append((field_entry, time_entry))

    def save_fields():
        for i, (field_entry, time_entry) in enumerate(entries):
            new_field = field_entry.get().strip()
            new_time = time_entry.get().strip()
            time_slots[i].field = new_field
            time_slots[i].time = new_time
        fields_window.destroy()

    save_button = ttk.Button(fields_window, text="Save", command=save_fields)
    save_button.grid(row=number_of_time_slots + 1, column=0, columnspan=3, padx=10, pady=10)

def export_schedule():
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Home Team", "Away Team", "Game Time", "Field", "Date"])
        for game in schedule:
            writer.writerow([game.home_team.name, game.away_team.name, game.time_slot.time, game.time_slot.field, game.date])
    print("Schedule exported successfully to", filename)

def generate_main_window():
    global number_of_teams, number_of_time_slots, number_of_games, teams, time_slots, game_dates

    number_of_teams = int(teams_entry.get())
    number_of_time_slots = int(time_slots_entry.get())
    number_of_games = int(games_entry.get())

    # Init Teams
    teams = []
    for i in range(number_of_teams):
        teams.append(Team(i + 1))

    # Init Time slots
    time_slots = []
    for i in range(number_of_time_slots):
        time_slots.append(TimeSlot(i + 1))

    # Game Dates
    game_dates = []
    for i in range(number_of_games):
        game_dates.append(GameDate(i + 1))

    # Close the setup window
    setup_window.destroy()

    # Generate the main window
    main_window()

def main_window():
    global window
    window = tk.Tk()
    window.title("Schedule Generator")

    label = tk.Label(window, text="Follow the buttons in order, generate schedule as many times as needed to get balanced matchups, then add team, field and game details")
    label.grid(row=0, column=0, padx=10, pady=5)

    restrictions_button = tk.Button(window, text="Set Time Slot Restrictions", command=open_restrictions_window)
    restrictions_button.grid(row=1, column=0, padx=10, pady=5)

    generate_button = tk.Button(window, text="Generate Schedule", command=generate_schedule)
    generate_button.grid(row=2, column=0, padx=10, pady=5)

    details_button = tk.Button(window, text="Details", command=team_details)
    details_button.grid(row=3, column=0, padx=10, pady=5)

    teams_button = tk.Button(window, text="Name Teams", command=name_teams)
    teams_button.grid(row=4, column=0, padx=10, pady=5)

    fields_button = tk.Button(window, text="Add Field Detail", command=define_fields)
    fields_button.grid(row=5, column=0, padx=10, pady=5)

    details_button = tk.Button(window, text="Details", command=team_details)
    details_button.grid(row=6, column=0, padx=10, pady=5)

    dates_button = tk.Button(window, text="Edit Dates", command=edit_dates)
    dates_button.grid(row=7, column=0, padx=10, pady=5)

    export_button = tk.Button(window, text="Export", command=export_schedule)
    export_button.grid(row=8, column=0, padx=10, pady=5)

    # Run the GUI main loop
    window.mainloop()
    



setup_window = tk.Tk()
setup_window.title("Setup")

teams_label = tk.Label(setup_window, text="Number of Teams:")
teams_label.grid(row=0, column=0)
teams_entry = ttk.Entry(setup_window)
teams_entry.grid(row=0, column=1)

time_slots_label = tk.Label(setup_window, text="Number of Games Per Day:")
time_slots_label.grid(row=1, column=0)
time_slots_entry = ttk.Entry(setup_window)
time_slots_entry.grid(row=1, column=1)

games_label = tk.Label(setup_window, text="Number of Games:")
games_label.grid(row=2, column=0)
games_entry = ttk.Entry(setup_window)
games_entry.grid(row=2, column=1)

generate_button = tk.Button(setup_window, text="Generate", command=generate_main_window)
generate_button.grid(row=3, columnspan=2, pady=10)

setup_window.mainloop()