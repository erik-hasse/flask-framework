from flask import Flask, render_template, request, redirect
import requests
from bokeh.plotting import figure, output_file, reset_output, save
import pandas as pd
import os

app = Flask(__name__)

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/graph', methods=['POST'])
def graph():
  key = os.environ.get('AV_KEY')
  ticker = request.form['stockTicker']
  url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={}&apikey={}'.format(ticker,key)
  r = requests.get(url)
  d = r.json()
  df = pd.DataFrame.from_dict(d['Time Series (Daily)'],orient='index')
  df.index = pd.to_datetime(df.index)
  df = df[df.index.isin(pd.date_range( start=pd.datetime.now().date() - pd.Timedelta('31 days'),
                                         end=pd.datetime.now().date()
                                     ))]

  df.columns = map(lambda x: x.split()[1], df.columns)
  colors = {'close': 'blue', 'open': 'orange', 'high': 'green','low': 'red'}

  reset_output()
  output_file('templates/graph.html')
  
  p = figure(width=800,height=350,x_axis_type='datetime')

  features = request.form.getlist('features')

  for column in df.columns:
    if column in features:
      p.line(df.index,df[column],line_width=1,color='black')
      p.circle(df.index,df[column],size=7,color=colors[column],legend=column)

  p.title.text = '{} Closing Price'.format(ticker)
  p.legend.location = 'top_left'
  p.grid.grid_line_alpha = 0
  p.xaxis.axis_label = 'Date'
  p.yaxis.axis_label = 'Price'
  p.ygrid.band_fill_color = 'lightgrey'
  p.ygrid.band_fill_alpha = 0.4

  save(p)

  return render_template('graph.html')
  

@app.route('/about')
def about():
  return render_template('about.html')

if __name__ == '__main__':
  port = int(os.environ.get("PORT",5000))
  app.run(host='0.0.0.0',port=port, debug=True)
