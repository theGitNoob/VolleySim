# load some csv file
import csv
from collections import defaultdict

import pandas as pd


def create_default_player_stats() -> dict:
    return {
        "p_Attack": 0.0,
        "p_Block": 0.0,
        "p_Dig": 0.0,
        "p_Set": 0.0,
        "p_Serve": 0.0,
        "p_Receive": 0.0,
    }


players_dict: defaultdict[str, dict] = defaultdict(create_default_player_stats)


def load_data(path: str, cols: list[str]) -> None:
    df = pd.read_csv(path, sep=",", usecols=cols, encoding="latin1")
    for _, row in df.iterrows():
        name = row["Name"]
        if name not in players_dict:
            players_dict[name] = {}
        for col in cols[1:]:
            val = row[col]
            if pd.isna(val):
                val = 0.0
            players_dict[name][col] = val


def save_data(file_path: str) -> None:
    with open(file_path, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "Name",
                "Team",
                "Position",
                "p_Attack",
                "p_Block",
                "p_Dig",
                "p_Set",
                "p_Serve",
                "p_Receive",
            ]
        )
        # Write the player stats
        for name, stats in players_dict.items():
            writer.writerow(
                [
                    name,
                    stats.get("Team"),
                    stats.get("Position"),
                    stats.get("p_Attack", 0.0),
                    stats.get("p_Block", 0.0),
                    stats.get("p_Dig", 0.0),
                    stats.get("p_Set", 0.0),
                    stats.get("p_Serve", 0.0),
                    stats.get("p_Receive", 0.0),
                ]
            )


def parse_datasets():
    load_data("data/VNL2024Men_Players.csv", ["Name", "Team", "Position", "Height"])
    load_data("data/VNL2024Men_Attackers.csv", ["Name", "Team", "p_Attack"])
    load_data("data/VNL2024Men_Blockers.csv", ["Name", "Team", "p_Block"])
    load_data("data/VNL2024Men_Diggers.csv", ["Name", "Team", "p_Dig"])
    load_data("data/VNL2024Men_Setters.csv", ["Name", "Team", "p_Set"])
    load_data("data/VNL2024Men_Servers.csv", ["Name", "Team", "p_Serve"])
    load_data("data/VNL2024Men_Receivers.csv", ["Name", "Team", "p_Receive"])

    save_data("data/VNL2024Men.csv")


def main():
    parse_datasets()


if __name__ == "__main__":
    main()
