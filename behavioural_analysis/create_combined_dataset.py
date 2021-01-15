from utils import BehaviourLoader
from pathlib import Path

if __name__ == "__main__":
    p = r"D:\Context_switch_output\pilot"
    outdir = Path(p) / "combined_data"
    loader = BehaviourLoader(p)
    loader.load_mouse_metadata().to_csv(outdir / "mouse_metadata.csv", index=False)
    data = loader.load_data().to_csv(outdir / "freeze_data.csv", index=False)
    events = loader.load_events().to_csv(outdir / "events.csv", index=False)
