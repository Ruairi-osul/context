from pathlib import Path
import pandas as pd
import warnings


class BehaviourLoader:

    default_data_dirname = "data"
    default_metadata_dirname = "metadata"
    default_mouse_metadata_filename = "mice.xlsx"
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

    def __init__(
        self,
        home_dir: str,
        metadata_dirname=None,
        mouse_metadata_filename=None,
        session_names=None,
        data_dirname=None,
        freeze_filename=None,
        behaviour_data_dirname=None,
    ):
        self.home_dir = Path(home_dir)
        self.session_names = (
            BehaviourLoader.default_session_names
            if session_names is None
            else session_names
        )
        self.data_dirname = (
            BehaviourLoader.default_data_dirname
            if data_dirname is None
            else data_dirname
        )
        self.mice = list(
            map(lambda x: x.name, (self.home_dir.joinpath(self.data_dirname).glob("*")))
        )
        self.behaviour_data_dirname = (
            BehaviourLoader.default_behaviour_data_dirname
            if behaviour_data_dirname is None
            else behaviour_data_dirname
        )
        self.freeze_filename = (
            BehaviourLoader.default_freeze_filename
            if freeze_filename is None
            else freeze_filename
        )
        self._check_data()

        self.metadata_dirname = (
            BehaviourLoader.default_metadata_dirname
            if metadata_dirname is None
            else metadata_dirname
        )
        self.mouse_metadata_filename = (
            BehaviourLoader.default_mouse_metadata_filename
            if mouse_metadata_filename is None
            else mouse_metadata_filename
        )
        self._check_metadata()

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

    def _check_data(self):
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

    def load_data(self, mice: list = None, sessions: list = None):
        """
        Returns pandas dataframe with data from each session
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
