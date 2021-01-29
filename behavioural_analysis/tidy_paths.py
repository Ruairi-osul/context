from pathlib import Path


def main():
    "Add raw data files to subdir with session dir called 'raw_bonsai_data"
    master_dir = Path(r"E:\Context_switch_output\pilot\data\proper")
    sub_dirname = "raw_bonsai_data"
    # iterate over mice
    for d in master_dir.glob("B*"):
        # iterate over sessions
        for sd in d.glob("D*"):
            target_dir = sd.joinpath(sub_dirname)
            target_dir.mkdir(exist_ok=True)
            current_paths = list(sd.glob("*.*"))
            destinations = map(lambda x: target_dir.joinpath(x.name), current_paths)
            for current, destination in zip(current_paths, destinations):
                current.replace(destination)


if __name__ == "__main__":
    main()