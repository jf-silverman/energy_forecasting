import seaborn
import matplotlib.pyplot as plt
from statsmodels.tsa.api import SimpleExpSmoothing
import pandas as pd
import numpy as np




def mae_function(df):
    dem_ave = df.loc[df['Error'].notnull(), 'Demand'].mean()
    bias_abs = df['Error'].mean()
    bias_rel = bias_abs / dem_ave
    print('Bias: {:0.2f}, {:.2%}'.format(bias_abs, bias_rel))
    mae_abs = df['Error'].abs().mean()
    mae_rel = mae_abs / dem_ave
    print('MAE: {:0.2f}, {:.2%}'.format(mae_abs, mae_rel))
    rmse_abs = np.sqrt((df['Error'] ** 2).mean())
    rmse_rel = rmse_abs / dem_ave
    print('RMSE: {:0.2f}, {:.2%}'.format(rmse_abs, rmse_rel))






def seasonal_factors_mul(s, d, slen, cols):
    for i in range(slen):
        s[i] = np.mean(d[i:cols:slen])
    s /= np.mean(s[:slen])
    return s







def exp_smooth_funct(d, slen=12, extra_periods=1, alpha=0.4, beta=0.4, phi=0.9, gamma=0.3):
    cols = len(d)

    d = np.append(d, [np.nan] * extra_periods)

    f, a, b, s = np.full((4, cols + extra_periods), np.nan)
    s = seasonal_factors_mul(s, d, slen, cols)

    a[0] = d[0] / s[0]
    b[0] = d[1] / s[1] - d[0] / s[0]

    for t in range(1, slen):
        f[t] = (a[t - 1] + phi * b[t - 1]) * s[t]
        a[t] = alpha * d[t] / s[t] + (1 - alpha) * (a[t - 1] + phi * b[t - 1])
        b[t] = beta * (a[t] - a[t - 1]) + (1 - beta) * phi * b[t - 1]

    for t in range(slen, cols):
        f[t] = (a[t - 1] + phi * b[t - 1]) * s[t - slen]
        a[t] = alpha * d[t] / s[t - slen] + (1 - alpha) * (a[t - 1] + phi * b[t - 1])
        b[t] = beta * (a[t] - a[t - 1]) + (1 - beta) * phi * b[t - 1]
        s[t] = gamma * d[t] / a[t] + (1 - gamma) * s[t - slen]

    for t in range(cols, cols + extra_periods):
        f[t] = (a[t - 1] + phi * b[t - 1]) * s[t - slen]
        a[t] = f[t] / s[t - slen]
        b[t] = phi * b[t - 1]
        s[t] = s[t - slen]

    df_funct = pd.DataFrame.from_dict({'Demand': d, 'Forecast': f, 'Level': a, 'Trend': b, 'Season': s, 'Error': d - f})
    return df_funct








def lineplt(date_floor, date_ceil, data, xspacing, subtitle):
    df = data[(data['datetime'] > date_floor) & (data['datetime'] < date_ceil)].set_index('datetime')
    df.sort_index(ascending=True, inplace=True)
    col_list = df.columns
    for col in col_list:
        figtitle = f'{subtitle}, from {date_floor} to {date_ceil}'
        plt.figure( figsize = ( 20, 8 ) )
        seaborn.set_style("darkgrid")
        seaborn.lineplot(x=df.index, y=df[col] )
        plt.title(figtitle)
        plt.ylabel(col)
        plt.xlabel(f'{date_floor} to {date_ceil}')
        plt.ylim(bottom=0, top = 65000)
        plt.xticks(ticks=df.index[::xspacing],rotation=45)
        plt.savefig('../output/' + figtitle + '.png')
        plt.show();
        return







def bar_month(data, measure,saveas, figtitle, *args):
    df = data
    df['month_name'] = df['datetime'].dt.month_name()
    bar = df[[measure, 'month_name']].groupby(['month_name']).mean()
    plt.figure( figsize = ( 8, 8 ) )
    seaborn.barplot(
        x=bar.index,
        y=bar[measure],
        order=["January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"],
        palette = ['#cfccff','#e0ccff','#f2ccff','#faccff', '#ffcbf2','#ffcce1','#ffcccf','#ffcccf', '#ffcce1','#ffcbf2','#faccff','#f2ccff']
    )
    plt.xticks(rotation=45)
    plt.xlabel("")
    plt.ylabel('megawatts')
    plt.title(figtitle)
    plt.savefig(saveas)
    plt.show();
    return








def bar_day(data, measure, saveas, figtitle,*args):
    df = data
    df['day_name'] = df['datetime'].dt.day_name()
    bar = df[[measure, 'day_name']].groupby(['day_name']).mean()
    plt.figure( figsize = ( 8, 8 ) )
    seaborn.barplot(
        x=bar.index,
        y=bar[measure],
        order=["Sunday", "Monday", "Tuesday", "Wednesday",
               "Thursday", "Friday", "Saturday"],
        palette = ['#007EB5','#EC5064', '#F9A834', '#B4CF68',  '#00F995', '#00965A', '#2A2A2A']
    )
    plt.xticks(rotation=45)
    plt.xlabel("")
    plt.ylabel('megawatts')
    plt.ylim((0,15000))
    plt.title(figtitle)
    plt.savefig(saveas)
    plt.show();
    return







def violin_month(data, measure, saveas,figtitle, *args):
    df = data
    df['month_name'] = df['datetime'].dt.month_name()
    plt.figure(figsize=(15, 8))
    seaborn.boxplot(
        x=df['month_name'],
        y=df[measure],
        order=["January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"],
        palette = ['#cfccff','#e0ccff','#f2ccff','#faccff', '#ffcbf2','#ffcce1','#ffcccf','#ffcccf', '#ffcce1','#ffcbf2','#faccff','#f2ccff']
    )
    plt.xticks(rotation=45)
    plt.xlabel("")
    plt.ylabel('megawatts')
    plt.title(figtitle)
    plt.savefig(saveas)
    plt.show();
    return







def violin_day(data, measure, saveas, figtitle, *args ):
    df = data
    df['day_name'] = df['datetime'].dt.day_name()
    plt.figure(figsize=(20, 8))
    seaborn.violinplot(
        x=df['day_name'],
        y=df[measure],
        order=["Sunday", "Monday", "Tuesday", "Wednesday",
               "Thursday", "Friday", "Saturday"],
        palette = ['#007EB5','#EC5064', '#F9A834', '#B4CF68',  '#00F995', '#00965A', '#2A2A2A']
    )
    plt.xticks(rotation=45)
    plt.xlabel("")
    plt.ylabel('megawatts')
    plt.title(figtitle)
    plt.savefig(saveas)
    plt.show();
    return







def lineplt_oneplot(data, xspacing, subtitle):
    df = data.set_index('datetime')
    df.sort_index(ascending=True, inplace=True)
    figtitle = f'{subtitle}'
    plt.figure(figsize=(30, 8))
    seaborn.set_style("darkgrid")
    seaborn.lineplot(data=df, palette={'demand': '#007EB5', 'net_generation': '#EC5064', 'coal': '#F9A834', 'hydro': '#B4CF68',
                                       'natural_gas': '#EF8D00', 'oil': '#FFD083', 'nuclear': '#007043', 'other': '#00F995',
                                       'solar': '#00D982', 'wind': '#00965A', 'total_interchange': '#2A2A2A', 'forecast': '#84#1F9'})
    plt.ylabel('megawatts')
    plt.xlabel(f'')
    plt.ylim(bottom=-5000, top=65000)
    plt.xticks(ticks=df.index[::xspacing], rotation=45)
    plt.title(figtitle)
    plt.savefig('../output/' + figtitle + '.png')
    plt.show();
    return