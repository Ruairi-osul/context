from utils import BehaviourLoader, resampler
import numpy as np
import random
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.ndimage import gaussian_filter1d


def switch_plot_single(df, mouseID, session="D3", sigma=None, figsize=(5, 2), ax=None):
    "plot shaded time series"
    if ax is None:
        _, ax = plt.subplots(figsize=figsize)

    if session == "D3":
        remainder = (2, 3)
    elif session == "D4":
        remainder = (0, 1)
    else:
        raise ValueError(f"Unknown session {session}")
    df = df.loc[lambda x: x.mouseID == mouseID].loc[lambda x: x.session_name == session]
    sigma = 3 * np.std(df.was_freezing)
    df = df.assign(
        time=lambda x: x.time.divide(60),
        smooth=lambda x: gaussian_filter1d(x.was_freezing, sigma),
    )
    ax = sns.lineplot(data=df, x="time", y="smooth", color="black")
    ax.fill_between(
        df.time,
        df.smooth.min(),
        df.smooth.max(),
        where=np.isin(np.floor(df.time) % 4, remainder),
        color="red",
        alpha=0.2,
        label="Shock Context",
    )
    ax.set_ylabel("Freeze Status")
    ax.set_xlabel("Time [min]")
    sns.despine()
    ax.legend()
    plt.tight_layout()
    return ax


def switch_plot_multiple(
    df, session="D4", group_col="group", sigma=None, figsize=(5, 3), ax=None
):
    if ax is None:
        _, ax = plt.subplots(figsize=figsize)

    if session == "D3":
        remainder = (2, 3)
    elif session == "D4":
        remainder = (0, 1)
    else:
        raise ValueError(f"Unknown session {session}")
    df = df.loc[lambda x: x.session_name == session]
    sigma = 3 * np.std(df.was_freezing)
    df = df.assign(
        time=lambda x: x.time.divide(60),
        smooth=lambda x: x.groupby(["mouseID", "session_name"]).was_freezing.transform(
            lambda y: gaussian_filter1d(y, sigma)
        ),
    )
    ax = sns.lineplot(
        data=df, x="time", y="smooth", hue=group_col, ci=None, linewidth=2
    )
    first_mouse = df.loc[lambda x: x.mouseID == x.mouseID.unique()[0]]
    ax.fill_between(
        first_mouse.time,
        0,
        1,
        where=np.isin(np.floor(first_mouse.time) % 4, remainder),
        color="red",
        alpha=0.2,
        label="Shock Context",
    )
    ax.set_ylabel("Freeze probability")
    ax.set_xlabel("Time [min]")
    sns.despine()
    ax.legend(bbox_to_anchor=(0.4, 1.25))
    plt.tight_layout()
    return ax


def get_random_mouse(df):
    return random.choice(df.mouseID.unique())


if __name__ == "__main__":
    p = r"D:\Context_switch_output\pilot"
    loader = BehaviourLoader(p)
    freeze, _, mouse = loader.load_combined_data()
    print(
        freeze.groupby("mouseID")
        .was_freezing.mean()
        .reset_index()
        .merge(mouse[["mouseID", "group"]])
    )
    df = resampler(freeze, -1).merge(mouse[["mouseID", "group"]])
    print(df)
    ax = switch_plot_multiple(df, session="D4", sigma=None)
    ax.set_title("Test Day 2")
    plt.show()
