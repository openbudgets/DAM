import urllib.request
import datetime as datetime
import pandas as pd
import statsmodels.api as sm
import seaborn as sns
import matplotlib.pyplot as plt
import tasks.myutil as mutil
import mpld3
from json import dumps


def analyse_trend(dtable=''):
    data_table_name_lst = mutil.get_dataset_all_temporal(dtable)
    data_table = []
    dataset_name = [ele for ele in dtable.split('-') if not ele.isdigit()][0]
    tmlst=[]
    for dtable_name in data_table_name_lst:
        row = {'Year': mutil.get_time_from_filename(dtable_name),
               'Month': 1,
               'Day':  1,
               'Mean': mutil.get_mean_of_observations(dtable_name)}
        if row['Year'] != 0:
            tmlst.append(row['Year'])
            data_table.append(row)
    tmlst.sort()
    df = pd.DataFrame(data = data_table)
    df['time'] = df[['Year', 'Month', 'Day']].apply(lambda x: datetime.datetime(*x), axis=1)
    df.index = pd.DatetimeIndex(df['time'])
    df = df.drop(['Year', 'Month', 'Day'], axis=1)
    print(df)
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    ax.set_title(dataset_name)
    flow = df['Mean']
    res = sm.tsa.seasonal_decompose(flow, freq=1)
    fig = res.plot()
    output = mpld3.fig_to_dict(fig)
    #result = {'trend': res.trend.to_json(), 'observed': res.observed.to_json(), 'seasonal': res.seasonal.to_json(), 'residual': res.resid.to_json()}
    return dumps({'fig':output})


def sample_function():
    # Import the sample streamflow dataset
    data = urllib.request.urlopen('https://raw.github.com/mps9506/Sample-Datasets/master/Streamflow/USGS-Monthly_Streamflow_Bend_OR.tsv')
    df = pd.read_csv(data, sep='\t')

    # The yyyy,mm, and dd are in seperate columns, we need to make this a single column
    df['dti'] = df[['year_nu','month_nu','dd_nu']].apply(lambda x: datetime.datetime(*x),axis=1)

    # Let use this as our index since we are using pandas
    df.index = pd.DatetimeIndex(df['dti'])
    # Clean the dataframe a bit
    df = df.drop(['dd_nu','year_nu','month_nu','dti'],axis=1)
    df = df.resample('M').mean()
    print(df.head())
    fig,ax = plt.subplots(1,1, figsize=(6,4))
    flow = df['mean_va']
    flow = flow['1945-01':]

    res = sm.tsa.seasonal_decompose(flow)
    #res.trend, res.observed, res.seasonal, res.resid, res.nobs
    fig = res.plot()
    plt.show()


if __name__ == '__main__':
    sample_function()

