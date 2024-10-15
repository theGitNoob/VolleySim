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


def load_position_and_team_data(path: str, threshold: int = 10) -> None:
    df = pd.read_csv(path, sep=",", encoding="latin1")
    for _, row in df.iterrows():
        name = row["Name"]
        position = row["Position"]
        team = row["Team"]
        players_dict[name]["Position"] = position
        players_dict[name]["Team"] = team


def load_attack_data(path: str, threshold: int = 10) -> None:
    df = pd.read_csv(path, sep=",", encoding="latin1")
    for _, row in df.iterrows():
        name = row["Name"]
        tot_attack = row["Tot_Attack"]
        p_attack = row["p_Attack"]
        if tot_attack < threshold:
            continue
        players_dict[name]["p_Attack"] = p_attack


def load_block_data(path: str, threshold: int = 10) -> None:
    df = pd.read_csv(path, sep=",", encoding="latin1")
    for _, row in df.iterrows():
        pt_block = row["Pt_Block"]
        tot_block = row["Tot_Block"]

        p_block = 0.0
        if not (
            pd.isna(pt_block) or pd.isna(tot_block) or tot_block == 0 or pt_block == 0
        ):
            p_block = (pt_block / tot_block) * 100.0
        if tot_block < threshold or p_block == 0.0:
            continue
        players_dict[row["Name"]]["p_Block"] = p_block


def load_dig_data(path: str, threshold: int = 10) -> None:
    df = pd.read_csv(path, sep=",", encoding="latin1")
    for _, row in df.iterrows():
        name = row["Name"]
        tot_dig = row["T_Dig"]
        p_dig = row["p_Dig"]
        if tot_dig < threshold:
            continue
        players_dict[name]["p_Dig"] = p_dig


def load_receive_data(path: str, threshold: int = 10) -> None:
    df = pd.read_csv(path, sep=",", encoding="latin1")
    for _, row in df.iterrows():
        name = row["Name"]
        tot_receive = row["Tot_Receive"]
        p_receive = row["p_Receive"]
        if tot_receive < threshold:
            continue
        players_dict[name]["p_Receive"] = p_receive


def load_serve_data(path: str, threshold: int = 10) -> None:
    df = pd.read_csv(path, sep=",", encoding="latin1")
    for _, row in df.iterrows():
        name = row["Name"]
        att_serv = row["Att_Serve"]
        tot_serve = row["Tot_Serve"]
        if tot_serve < threshold:
            continue
        players_dict[name]["p_Serve"] = (att_serv / tot_serve) * 100


def load_set_data(path: str, threshold: int = 10) -> None:
    df = pd.read_csv(path, sep=",", encoding="latin1")
    for _, row in df.iterrows():
        name = row["Name"]
        att_set = row["Att_Set"]
        tot_set = row["Tot_Set"]
        if tot_set < threshold:
            continue
        players_dict[name]["p_Set"] = (att_set / tot_set) * 100


def parse_datasets():
    load_position_and_team_data("data/VNL2024Men_Players.csv")
    load_attack_data("data/VNL2024Men_Attackers.csv")
    load_block_data("data/VNL2024Men_Blockers.csv")
    load_dig_data("data/VNL2024Men_Diggers.csv")
    load_receive_data("data/VNL2024Men_Receivers.csv")
    load_serve_data("data/VNL2024Men_Servers.csv")
    load_set_data("data/VNL2024Men_Setters.csv")

    save_data("data/VNL2024Men.csv")


def main():
    parse_datasets()


if __name__ == "__main__":
    main()
