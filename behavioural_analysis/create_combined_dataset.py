from utils import BehaviourLoader, add_context_col
from pathlib import Path

if __name__ == "__main__":
    p = r"D:\Context_switch_output\pilot"
    outdir = Path(p) / "combined_data"
    loader = BehaviourLoader(p)
    mice = loader.load_mouse_metadata()
    freeze = loader.load_freeze_data()
    events = loader.load_events()
    events.to_csv(outdir / "events.csv", index=False)
    freeze.to_csv(outdir / "freeze_data.csv", index=False)
    mice.to_csv(outdir / "mouse_metadata.csv", index=False)
    df = (
        freeze.merge(mice[["mouseID", "Cohort", "group"]])
        .pipe(add_context_col)
        .to_csv(outdir / "freeze_with_meta.csv", index=False)
    )
