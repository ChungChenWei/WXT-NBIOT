from datetime import datetime as dtmdtm
from datetime import timedelta as dt

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.dates import DateFormatter, DayLocator, HourLocator

from config.path_config import L0_PATH, PICT_DIR, mkdir_if_not_exist
from config.wxt_config import WXT_META


def base():
    f, ax = plt.subplots(1, 1, figsize=(12, 6), constrained_layout=True)
    return f, ax


def add_meta(ax: plt.Axes, end_time: dtmdtm, date, station, fs=20):
    ax.set_title(f"{station}", fontsize=fs)
    ax.set_title(
        f"data: {end_time.strftime('%Y/%m/%d %H:%M:%S')}\nplot: {dtmdtm.now().strftime('%Y/%m/%d %H:%M:%S')}",
        loc="right",
        fontsize=fs - 12,
    )
    xdate = dtmdtm.strptime(date, "%Y%m%d")
    ax.set_xlim(xdate + dt(hours=8), xdate + dt(hours=8 + 24))
    ymin, ymax = ax.get_ylim()
    for xs, xe in zip(timeseries[:-1][idx_stop], timeseries[1:][idx_stop]):
        ax.fill_betweenx(np.linspace(ymin, ymax), [xs], [xe], color="red", alpha=0.2)
    ax.grid()


def set_formatter(ax: plt.Axes):
    ax.xaxis.set_major_formatter(DateFormatter("%H"))
    ax.xaxis.set_major_locator(HourLocator(interval=1))
    ax.xaxis.set_minor_locator(DayLocator(interval=1))
    ax.xaxis.set_minor_formatter(DateFormatter("%m/%d"))

    axt = ax.secondary_xaxis("top")
    axt.xaxis.set_major_formatter(DateFormatter("%m/%d"))
    axt.xaxis.set_major_locator(DayLocator(interval=1))


def add_temp(ax: plt.Axes, df: pd.DataFrame, name, ax_c="b"):
    ax.plot(df.index, df[name], "--", color=ax_c, zorder=10)
    ax.spines["left"].set_color(ax_c)
    ax.set_ylabel("Temperature [oC]", color=ax_c)
    ax.tick_params("y", colors=ax_c)
    ymin_ax, ymax_ax = ax.get_ylim()
    ax.set_yticks(np.arange(0, 50, 1))
    ax.set_ylim(ymin_ax, ymax_ax)


def add_rh(ax: plt.Axes, df: pd.DataFrame, name, ax_c="r"):
    ax.plot(df.index, df[name], "--", color=ax_c, zorder=10)
    ax.spines["right"].set_color(ax_c)
    ax.spines["left"].set_visible(False)
    ax.set_ylabel("Relative Humidity [%]", color=ax_c)
    ax.tick_params("y", colors=ax_c)
    ymin, ymax = ax.get_ylim()
    ax.set_yticks(np.arange(0, 100, 5))
    ax.set_ylim(ymin, ymax)


def add_accrain(ax: plt.Axes, dfh: pd.DataFrame, name, ax_c="k"):
    ax.bar(dfh.sum().index + dt(minutes=30), dfh.sum()[name].to_numpy(), color=ax_c, width=0.01, alpha=0.5)
    ax.spines["right"].set_position(("axes", 1.08))
    ax.spines["left"].set_visible(False)
    ax.set_ylabel("Accumulated Rain Fall [mm]", color=ax_c)


def add_datacnt(ax: plt.Axes, dfh: pd.DataFrame, name, date):
    dfh = dfh.count()[name]
    ridx = pd.date_range(date, freq="1H", periods=25) + dt(hours=8)
    dfh = dfh.reindex(ridx)
    dfh = dfh.fillna(0)
    ax.spines["left"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.spines["top"].set_position(("axes", 0.975))
    ax.tick_params("both", which="both", color="none")
    ax.set_xticks(np.arange(25) + 0.5)
    ax.set_xlim(0, 24)
    ax.set_xticklabels(dfh.to_numpy(dtype=int), color="r")


def plot_TUR(df: pd.DataFrame, date, station):
    f, ax = base()

    meta = WXT_META[station]

    TEMP = meta["TEMP"]
    RH = meta["RH"]
    ACCR = meta["ACCR"]

    add_temp(ax, df, TEMP)
    add_rh(ax.twinx(), df, RH)
    add_accrain(ax.twinx(), dfh, ACCR)
    add_datacnt(ax.twiny(), dfh, ACCR, date)

    add_meta(ax, df.index[-1], date, station)

    set_formatter(ax)
    mkdir_if_not_exist(PICT_DIR / date)
    plt.savefig(PICT_DIR / date / f"{date}_{station}_TUR.png")


if __name__ == "__main__":
    utc = dtmdtm.utcnow()
    targets = [(utc - dt(minutes=10)).strftime("%Y%m%d"), utc.strftime("%Y%m%d")]
    for date in targets:
        for station_file in (L0_PATH / date).glob("*.csv"):
            print(station_file)
            station = station_file.stem

            df = pd.read_csv(L0_PATH / date / f"{station}.csv", index_col="datetime")
            df.index = pd.DatetimeIndex(df.index) + dt(hours=8)

            dfh = df.resample("1H")

            timeseries = df.index
            timediff = timeseries[1:] - timeseries[:-1]
            idx_stop = timediff > dt(minutes=5)

            plot_TUR(df, date, station)
