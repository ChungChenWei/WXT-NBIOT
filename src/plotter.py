import sys
from datetime import datetime as dtmdtm
from datetime import timedelta as dt

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.dates import DateFormatter, DayLocator, HourLocator

from config.path_config import MERGE_PATH, PICT_DIR, mkdir_if_not_exist
from config.wxt_config import WXT_META


def base():
    f, ax = plt.subplots(1, 1, figsize=(12, 6), constrained_layout=True)
    return f, ax


def add_meta(ax: plt.Axes, end_time: dtmdtm, df: pd.DataFrame, date, station, diff=5, fs=20):
    timeseries = df.index
    timediff = timeseries[1:] - timeseries[:-1]
    idx_stop = timediff > dt(minutes=diff)

    ax.set_title(f"{station}", fontsize=fs)
    ax.set_title(
        f"data: {end_time.strftime('%Y/%m/%d %H:%M:%S')}\nplot: {dtmdtm.now().strftime('%Y/%m/%d %H:%M:%S')}",
        loc="right",
        fontsize=fs - 12,
    )
    xdate = dtmdtm.strptime(date, "%Y%m%d")
    ax.set_xlim(xdate, xdate + dt(hours=24))
    ymin, ymax = ax.get_ylim()
    for xs, xe in zip(timeseries[:-1][idx_stop], timeseries[1:][idx_stop]):
        ax.fill_betweenx(np.linspace(ymin, ymax), [xs], [xe], color="red", alpha=0.2)
    ax.set_ylim(ymin, ymax)
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
    return ax


def add_rh(ax: plt.Axes, df: pd.DataFrame, name, ax_c="r"):
    ax.plot(df.index, df[name], "--", color=ax_c, zorder=10)
    ax.spines["right"].set_color(ax_c)
    ax.spines["left"].set_visible(False)
    ax.set_ylabel("Relative Humidity [%]", color=ax_c)
    ax.tick_params("y", colors=ax_c)
    ymin, ymax = ax.get_ylim()
    ax.set_yticks(np.arange(0, 101, 5))
    ax.set_ylim(ymin, ymax)
    return ax


def add_accrain(ax: plt.Axes, dfh: pd.DataFrame, name, ax_c="k"):
    ax.bar(dfh.sum().index + dt(minutes=30), dfh.sum()[name].to_numpy(), color=ax_c, width=0.01, alpha=0.5)
    ax.spines["right"].set_position(("axes", 1.08))
    ax.spines["left"].set_visible(False)
    ax.set_ylabel("Accumulated Rain Fall [mm]", color=ax_c)
    return ax


def add_datacnt(ax: plt.Axes, dfh: pd.DataFrame, name, date, freq="1H"):
    dfh = dfh.count()[name]
    if freq == "1H":
        periods = 24 + 1
        ax.set_xticks(np.arange(periods) + 0.5)
        ax.set_xlim(0, 24)
    elif freq == "10T":
        periods = 24 * 6 + 1
        ax.set_xticks(np.arange(periods) + 0.1)
        ax.set_xlim(0, 24 * 6)
    ridx = pd.date_range(date, freq=freq, periods=periods)
    dfh = dfh.reindex(ridx)
    dfh = dfh.fillna(0)

    ax.spines["left"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.spines["top"].set_position(("axes", 0.975))
    ax.tick_params("both", which="both", color="none")
    ax.set_xticklabels(dfh.to_numpy(dtype=int), color="r")


def add_arithmetic_wind_speed(ax: plt.Axes, df: pd.DataFrame, name, ax_c="b"):
    ax.plot(df.index, df[name], "-", color=ax_c, zorder=10)
    ax.set_ylabel("arithmetic mean [m/s]", color=ax_c)
    ax.spines["left"].set_color(ax_c)
    ax.tick_params("y", colors=ax_c)
    return ax


def add_vector_wind_speed(ax: plt.Axes, df: pd.DataFrame, ax_c="r"):
    df["WS"] = np.sqrt(df["U"] ** 2 + df["V"] ** 2)
    ax.plot(df.index, df["WS"], "--", color=ax_c, zorder=10)
    ax.set_ylabel("vector mean [m/s]", color=ax_c)
    ax.spines["left"].set_visible(False)
    ax.spines["right"].set_color(ax_c)
    ax.tick_params("y", colors=ax_c)
    return ax


def add_wind_direction(ax: plt.Axes, df: pd.DataFrame, ax_c="k"):
    df["WD"] = (np.rad2deg(np.arctan2(-df["V"], -df["U"])) + 360) % 360
    ax.plot(df.index, df["WD"], "o", color=ax_c, zorder=10)
    ax.set_ylabel("vectro wind direction [o]", color=ax_c)
    ax.spines["left"].set_visible(False)
    ax.spines["right"].set_position(("axes", 1.08))
    ax.spines["right"].set_color(ax_c)
    ax.tick_params("y", colors=ax_c)
    ax.set_ylim(0, 360)
    ax.set_yticks(np.arange(0, 361, 45))
    return ax


def add_wind_direction_var(ax: plt.Axes, df: pd.DataFrame, name, ax_c="b"):
    ax.plot(df.index, df[name], "x", color=ax_c, zorder=10)
    ax.set_ylabel("direct wind direction [o]", color=ax_c)
    ax.spines["left"].set_color(ax_c)
    ax.tick_params("y", colors=ax_c)
    ax.set_ylim(0, 360)
    ax.set_yticks(np.arange(0, 361, 45))
    return ax


def plot_TUR(df: pd.DataFrame, date, station):
    dfh = df.resample("1H")

    f, ax = base()

    meta = WXT_META[station]

    TEMP = meta["TEMP"]
    RH = meta["RH"]
    ACCR = meta["ACCR"]

    ax_t = add_temp(ax, df, TEMP)
    ax_t.set_ylim(16, 36)
    ax_rh = add_rh(ax.twinx(), df, RH)
    ax_rh.set_ylim(30, 100)
    ax_acc = add_accrain(ax.twinx(), dfh, ACCR)
    _, ymax_acc = ax_acc.get_ylim()
    ax_acc.set_ylim(0, max(12, ymax_acc))
    add_datacnt(ax.twiny(), dfh, ACCR, date)

    add_meta(ax, df.index[-1], df, date, station)

    set_formatter(ax)
    mkdir_if_not_exist(PICT_DIR / date)
    plt.savefig(PICT_DIR / date / f"{date}_{station}_TUR.png")
    plt.close()


def plot_WS(df: pd.DataFrame, date, station):
    meta = WXT_META[station]
    WS = meta["WS"]

    df10m = df.resample("10T")
    mean_df10m = df10m.mean()
    mean_df10m.index = mean_df10m.index + dt(minutes=10)

    f, ax = base()

    ax_ari = add_arithmetic_wind_speed(ax, mean_df10m, WS)
    ax_vec = add_vector_wind_speed(ax.twinx(), mean_df10m)
    ymin_ari, ymax_ari = ax_ari.get_ylim()
    ymin_vec, ymax_vec = ax_vec.get_ylim()
    ymin = min(ymin_ari, ymin_vec) - 0.5
    ymax = min(ymax_ari, ymax_vec) + 0.5
    ax_ari.set_ylim(ymin, ymax)
    ax_vec.set_ylim(ymin, ymax)

    add_datacnt(ax.twiny(), df.resample("1H"), WS, date)
    add_meta(ax, df.index[-1], mean_df10m.dropna(subset=[WS]), date, station, diff=10)

    set_formatter(ax)
    mkdir_if_not_exist(PICT_DIR / date)
    plt.savefig(PICT_DIR / date / f"{date}_{station}_WS.png")
    plt.close()


def plot_WD(df: pd.DataFrame, date, station):
    meta = WXT_META[station]
    WD = meta["WD"]

    df10m = df.resample("10T")
    mean_df10m = df10m.mean()
    mean_df10m.index = mean_df10m.index + dt(minutes=10)

    f, ax = base()

    add_wind_direction_var(ax, mean_df10m, WD)
    add_wind_direction(ax.twinx(), mean_df10m)

    add_datacnt(ax.twiny(), df.resample("1H"), WS, date)
    add_meta(ax, df.index[-1], mean_df10m.dropna(subset=[WD]), date, station, diff=10)

    set_formatter(ax)
    mkdir_if_not_exist(PICT_DIR / date)
    plt.savefig(PICT_DIR / date / f"{date}_{station}_WD.png")
    plt.close()


def plot_WSWD(df: pd.DataFrame, date, station):
    meta = WXT_META[station]
    WS = meta["WS"]
    WD = meta["WD"]

    df10m = df.resample("10T")
    mean_df10m = df10m.mean()
    mean_df10m.index = mean_df10m.index + dt(minutes=10)

    df1h = df.resample("1H")
    mean_df1h = df1h.mean()
    mean_df1h.index = mean_df1h.index + dt(minutes=30)

    f, ax = base()

    ax_ari = add_arithmetic_wind_speed(ax, mean_df10m, WS)
    ax_vec = add_vector_wind_speed(ax.twinx(), mean_df10m)
    ymin_ari, ymax_ari = ax_ari.get_ylim()
    ymin_vec, ymax_vec = ax_vec.get_ylim()
    ymin = min(ymin_ari, ymin_vec, 0)
    ymax = max(ymax_ari, ymax_vec, 5)
    ax_ari.set_ylim(ymin, ymax)
    ax_vec.set_ylim(ymin, ymax)

    # add_wind_direction_var(ax, mean_df10m, WD)
    add_wind_direction(ax.twinx(), mean_df10m)

    plt.barbs(
        mean_df1h.index, [315] * len(mean_df1h.index), mean_df1h["U"] * 1.94, mean_df1h["V"] * 1.94,
    )

    add_datacnt(ax.twiny(), df.resample("1H"), WS, date)
    add_meta(ax, df.index[-1], mean_df10m.dropna(subset=[WD]), date, station, diff=10)

    set_formatter(ax)
    mkdir_if_not_exist(PICT_DIR / date)
    plt.savefig(PICT_DIR / date / f"{date}_{station}_WSWD.png")
    plt.close()


def plot_UV(df: pd.DataFrame, date, station):
    df10m = df.resample("10T")
    mean_df10m = df10m.mean()

    f, ax = base()

    ax.plot(mean_df10m.index, mean_df10m["U"], "-b")
    ax.plot(mean_df10m.index, mean_df10m["V"], "-r")
    add_datacnt(ax.twiny(), df.resample("1H"), WS, date)
    add_meta(ax, df.index[-1], mean_df10m.dropna(subset=["U"]), date, station, diff=10)

    set_formatter(ax)
    mkdir_if_not_exist(PICT_DIR / date)
    plt.savefig(PICT_DIR / date / f"{date}_{station}_UV.png")
    plt.close()


if __name__ == "__main__":
    utc = dtmdtm.utcnow()
    targets = [(utc - dt(minutes=10)).strftime("%Y%m%d"), utc.strftime("%Y%m%d")]
    if targets[0] == targets[1]:
        targets.pop(0)
    if len(sys.argv) > 1 and sys.argv[1] == "all":
        series = pd.date_range("20230412", dtmdtm.now())
        targets = [t.strftime("%Y%m%d") for t in series]
    elif len(sys.argv) > 1:
        targets = sys.argv[1:]
    print(targets)
    for date in targets:
        for station_file in (MERGE_PATH / date).glob("*.csv"):
            print(station_file)
            station = station_file.stem

            df = pd.read_csv(MERGE_PATH / date / f"{station}.csv", index_col="datetime")
            df.index = pd.DatetimeIndex(df.index)

            meta = WXT_META[station]
            WS = meta["WS"]
            WD = meta["WD"]

            df["U"] = -df[WS] * np.sin(np.deg2rad(df[WD]))
            df["V"] = -df[WS] * np.cos(np.deg2rad(df[WD]))

            # plot_WS(df, date, station)
            # plot_WD(df, date, station)
            # plot_UV(df, date, station)
            plot_TUR(df, date, station)
            plot_WSWD(df, date, station)
