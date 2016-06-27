import urllib.request 
import datetime as datetime  
import pandas as pd  
import statsmodels.api as sm  
import seaborn as sns  
import matplotlib.pyplot as plt

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
