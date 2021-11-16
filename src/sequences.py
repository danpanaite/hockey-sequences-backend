import pandas as pd


def init_sequence_data(db):
    csv_df = pd.read_csv("olympic_womens_dataset.csv")

    plays = pd.DataFrame()
    plays["game_date"] = csv_df["game_date"]
    plays["home_team"] = clean_team_name(csv_df, "Home Team")
    plays["home_team_skaters"] = csv_df["Home Team Skaters"]
    plays["home_team_goals"] = csv_df["Home Team Goals"]
    plays["away_team"] = clean_team_name(csv_df, "Away Team")
    plays["away_team_skaters"] = csv_df["Away Team Skaters"]
    plays["away_team_goals"] = csv_df["Away Team Goals"]
    plays["team"] = clean_team_name(csv_df, "Team")
    plays["clock"] = csv_df["Clock"]
    plays["period"] = csv_df["Period"]
    plays["x_coord"] = csv_df["X Coordinate"]
    plays["y_coord"] = csv_df["Y Coordinate"]
    plays["event"] = csv_df["Event"]
    plays["player"] = csv_df["Player"]
    plays["detail_1"] = csv_df["Detail 1"]
    plays["detail_2"] = csv_df["Detail 2"]
    plays["detail_3"] = csv_df["Detail 3"]
    plays["detail_4"] = csv_df["Detail 4"]
    plays["player_2"] = csv_df["Player 2"]
    plays["x_coord_2"] = csv_df["X Coordinate 2"]
    plays["y_coord_2"] = csv_df["Y Coordinate 2"]

    plays["seconds_elapsed"] = csv_df.apply(
        lambda row: row.Period * 1200
        - (int(row["Clock"].split(":")[0]) * 60 + int(row["Clock"].split(":")[1])),
        axis=1,
    )

    grouped_plays = plays.groupby(["game_date", "home_team", "away_team"])
    sequences = pd.DataFrame()

    for name, group in grouped_plays:
        sequence_idx = 0
        start_play = group.iloc[0]
        start_play_index = 0
        sequence_team = group.iloc[0]["team"]
        sequence_id = f"{name[0]}_{sequence_team}_{sequence_idx}"

        for index, (play) in enumerate(group.itertuples(index=False)):
            if play.team != sequence_team:
                sequences = sequences.append(
                    {
                        "id": sequence_id,
                        "game_date": play.game_date,
                        "period": start_play["period"],
                        "team": start_play["team"],
                        "start_clock": start_play["clock"],
                        "start_time": start_play["seconds_elapsed"],
                        "end_time": play.seconds_elapsed,
                        "events": ",".join(
                            group[start_play_index:index]["event"].unique()
                        ),
                    },
                    ignore_index=True,
                )

                if index < len(group.index) - 1:
                    start_play = group.iloc[index + 1]
                    start_play_index = index + 1
                    sequence_idx += 1
                    sequence_team = play.team
                    sequence_id = f"{name[0]}_{sequence_team}_{sequence_idx}"

    plays.to_sql("plays", db, if_exists="replace")
    sequences.to_sql("play_sequences", db, if_exists="replace")

    games = pd.DataFrame(
        grouped_plays.groups.keys(), columns=["game_date", "home_team", "away_team"]
    )
    games.to_sql("games", db, if_exists="replace")


def clean_team_name(df, key):
    return df[key].str.replace("Olympic (Women) - ", "", regex=False)
