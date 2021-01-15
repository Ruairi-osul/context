from pathlib import Path
import pandas as pd
import warnings
import re
import numpy as np


class BehaviourLoader:

    default_session_names = [
        "D1Morning",
        "D1Afternoon",
        "D2Morning",
        "D2Afternoon",
        "D3",
        "D4",
    ]
    default_behaviour_data_dirname = "behaviour_analysis"
    default_freeze_filename = "freeze_ts.csv"
    default_raw_data_dirname = "raw_bonsai_data"

    def __init__(
        self,
        home_dir: str,
        metadata_dirname="metadata",
        mouse_metadata_filename="mice.xlsx",
        session_names=None,
        mice=None,
        data_dirname="data",
        raw_data_dirname="raw_bonsai_data",
        freeze_filename="freeze_ts.csv",
        behaviour_data_dirname="behaviour_analysis",
        combined_data_dirname="combined_data",
    ):
        self.home_dir = Path(home_dir)
        self.session_names = (
            BehaviourLoader.default_session_names
            if session_names is None
            else session_names
        )
        self.data_dirname = data_dirname
        if not mice:
            self.mice = list(
                map(
                    lambda x: x.name,
                    (self.home_dir.joinpath(self.data_dirname).glob("*")),
                )
            )
        else:
            self.mice = mice
        self.behaviour_data_dirname = behaviour_data_dirname
        self.freeze_filename = freeze_filename
        self._check_processed_data()

        self.raw_data_dirname = raw_data_dirname
        self._check_raw_data()

        self.metadata_dirname = metadata_dirname
        self.mouse_metadata_filename = mouse_metadata_filename
        self._check_metadata()

        self.combined_data_dirname = combined_data_dirname

    def _check_metadata(self):
        metadata_dir = self.home_dir / self.metadata_dirname
        if not metadata_dir.exists():
            warnings.warn(f"Could not find metadata dir: {str(metadata_dir)}")
        else:
            mouse_metadata_file = metadata_dir / self.mouse_metadata_filename
            if not mouse_metadata_file.exists():
                warnings.warn(
                    f"Could not find mouse metadata file: {str(mouse_metadata_file)}"
                )

    def _check_raw_data(self):
        # TODO
        pass

    def _check_processed_data(self):
        "Check that data exists for all mice on each session"
        for mouse in self.mice:
            for session in self.session_names:
                data_file = (
                    self.home_dir
                    / self.data_dirname
                    / mouse
                    / session
                    / self.behaviour_data_dirname
                    / self.freeze_filename
                )
                if not data_file.exists():
                    warnings.warn(
                        f"Expected data file not found: {str(data_file)}.\nData could be not yet analysed"
                    )

    def load_events(self, mice: list = None, sessions: list = None):
        if mice is not None:
            if not set(mice).issubset(set(self.mice)):
                raise ValueError(f"Unknown mice passed. Known mice: {self.mice}")
        else:
            mice = self.mice
        if sessions is not None:
            if not set(sessions).issubset(set(self.session_names)):
                raise ValueError(f"Unknown mice passed. Known mice: {self.mice}")
        else:
            sessions = self.session_names
        df_list = []
        for mouse in mice:
            for session in sessions:
                csv_files = (
                    self.home_dir
                    / self.data_dirname
                    / mouse
                    / session
                    / self.raw_data_dirname
                ).glob("*.csv")
                file_name = next(
                    filter(lambda x: re.search("events", str(x.name)), csv_files)
                )
                df = (
                    pd.read_csv(file_name, names=["event_name", "timepoint"])
                    .assign(
                        mouseID=mouse,
                        session_name=session,
                        timepoint=lambda x: pd.to_datetime(x.timepoint),
                        experimental_time_not_aligned=lambda x: (
                            x.timepoint - x.timepoint.min()
                        ).dt.total_seconds(),
                        experimental_time=lambda x: np.round(
                            x.experimental_time_not_aligned
                            - x.loc[
                                lambda x: x.event_name == "experiment_start"
                            ].experimental_time_not_aligned.values[0],
                            2,
                        ),
                    )
                    .drop("experimental_time_not_aligned", axis=1)
                )
                df_list.append(df)
        return pd.concat(df_list)

    def load_freeze_data(self, mice: list = None, sessions: list = None):
        """
        Returns pandas dataframe with freeze data from each session
        """
        if mice is not None:
            if not set(mice).issubset(set(self.mice)):
                raise ValueError(f"Unknown mice passed. Known mice: {self.mice}")
        else:
            mice = self.mice
        if sessions is not None:
            if not set(sessions).issubset(set(self.session_names)):
                raise ValueError(f"Unknown mice passed. Known mice: {self.mice}")
        else:
            sessions = self.session_names
        df_list = []
        for mouse in mice:
            for session in sessions:
                data_file = (
                    self.home_dir
                    / self.data_dirname
                    / mouse
                    / session
                    / self.behaviour_data_dirname
                    / self.freeze_filename
                )
                df_list.append(pd.read_csv(data_file))
        return pd.concat(df_list)

    def load_mouse_metadata(self, minimum=False):
        "return a pandas dataframe of mouse metadata"
        file_name = self.home_dir / self.metadata_dirname / self.mouse_metadata_filename
        df = pd.read_excel(file_name, engine="openpyxl")
        if minimum:
            df = df[["Mouse ID", "GROUP"]]
        df = df.rename(columns={"GROUP": "group", "Mouse ID": "mouseID"})
        return df

    @staticmethod
    def _load_assert_single(files, pattern, name):
        files = filter(lambda x: re.search(re.escape(pattern), x.name), files)
        df = pd.read_csv(next(files))
        try:
            next(files)
        except StopIteration:
            pass
        else:
            raise ValueError(f"More than one {name} dataset found")
        return df

    def load_combined_data(self):
        data_paths = list((self.home_dir / self.combined_data_dirname).glob("*.csv"))
        df_freeze = self._load_assert_single(data_paths, "freeze", "freeze")
        df_events = self._load_assert_single(data_paths, "events", "events")
        df_mouse_meta = self._load_assert_single(
            data_paths, "mouse_metadata", "mouse_metadata"
        )
        return df_freeze, df_events, df_mouse_meta


def resampler(df, digits=0):
    return df.pipe(
        lambda x: x.groupby(["mouseID", "session_name", np.round(x.time, digits)])
        .was_freezing.mean()
        .reset_index()
    )


if __name__ == "__main__":
    p = r"D:\Context_switch_output\pilot"
    loader = BehaviourLoader(p)
    f, e, m = loader.load_combined_data()
    print(m)
