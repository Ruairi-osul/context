from utils import BehaviourLoader, resampler
import pandas as pd
import random
import matplotlib.pyplot as plt
import seaborn as sns


def switch_plot_single(day):
    "plot shaded time series"
    pass


def switch_plot_multiple(day):
    pass


def get_random_mouse(df):
    return random.choice(df.mouseID.unique())


if __name__ == "__main__":
    p = r"D:\Context_switch_output\pilot"
    loader = BehaviourLoader(p)
    df = pd.merge(loader.load_data(), loader.load_mouse_metadata(minimum=True)).assign(
        time_min=lambda x: x.time.divide(60)
    )
    # print(df.session_name.unique())

    # test single mouse
    # df1 = df.loc[lambda x: (x.group == "exp") & (x.session_name == "D3")].loc[
    #     lambda x: x.mouseID == get_random_mouse(x)
    # ]
    # df1.plot(x="time_min", y="was_freezing")
    # plt.show()

    # test multiple mice
    print(df.group.unique())
    df1 = df.loc[lambda x: (x.group == "no shock") & (x.session_name == "D4")]
    df1 = resampler(df1, -1).assign(time=lambda x: x.time.divide(60))
    events = (
        loader.load_events()
        .loc[lambda x: (x.event_name == "context_one_on") & (x.session_name == "D4")]
        .assign(experimental_time=lambda x: x.experimental_time.divide(60))
    )

    print(events)
    # res = df1.groupby("time").was_freezing.mean().reset_index()
    sns.lineplot(data=df1, x="time", y="was_freezing")
    # res.plot(x="time", y="was_freezing")
    plt.show()

    # df1.plot(x=time, y="was")
    # print(df1)
