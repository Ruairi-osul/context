from pathlib import Path
from mfreeze.oop_interface import FreezeDetector
import warnings


class MouseData:
    session_names = ["D1Morning", "D1Afternoon", "D2Morning", "D2Afternoon", "D3", "D4"]

    def __init__(self, home_dir, video_suffix="avi"):
        self.home_dir = Path(home_dir)
        self.video_suffix = video_suffix
        self.video_paths = self._get_video_paths()
        self.mouseID = self.home_dir.name

    def _get_video_paths(self):
        "Return dict with session names as keys and dict values with sub keys 'input_dir' and 'output_dir'"
        out = {}
        for session_name in MouseData.session_names:
            session_videos = [
                *(self.home_dir / session_name / "raw_bonsai_data").glob(
                    f"*.{self.video_suffix}"
                )
            ]
            if len(session_videos) != 1:
                warnings.warn(
                    f"More than one behavioural video present {session_videos}"
                )
            output_dir = self.home_dir / session_name / "behaviour_analysis"
            output_dir.mkdir(exist_ok=True)
            out[session_name] = {
                "input_dir": str(session_videos[0]),
                "output_dir": str(output_dir),
            }
        return out


def run_one_mouse(
    mouse: MouseData,
    freeze_threshold=30,
    med_filter_size=3,
    compression_factor=3,
    start_frame=0,
    verbose=True,
):
    for session in mouse.session_names:
        print(session)
        detector = FreezeDetector(
            video_path=mouse.video_paths[session]["input_dir"],
            save_video_dir=mouse.video_paths[session]["output_dir"],
            freeze_threshold=freeze_threshold,
            start_frame=start_frame,
            med_filter_size=med_filter_size,
            compression_factor=compression_factor,
        )
        detector.detect_motion()
        detector.detect_freezes()
        detector.save_video()
        (
            detector.generate_report()
            .assign(session_name=session, mouseID=mouse.mouseID)
            .to_csv(
                Path(mouse.video_paths[session]["output_dir"]) / "freeze_ts.csv",
                index=False,
            )
        )


def main():
    MAIN_DIR = Path(r"E:\Context_switch_output\pilot\data\redo")
    VIDO_SUFFIX = "avi"
    verbose = True
    mouse_dirs = MAIN_DIR.glob("B*")
    for mouse_dir in mouse_dirs:
        if verbose:
            print(mouse_dir.name)
        mouse = MouseData(mouse_dir, video_suffix=VIDO_SUFFIX)
        run_one_mouse(mouse)


if __name__ == "__main__":
    main()