import pandas as pd
import matplotlib.pyplot as plt
import panel as pn
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

pn.extension('tabulator')

import hvplot.pandas

berlin_marathon = pd.read_csv('1_running_datasets/berlin_marathon_1974_2023.csv')
#data cleaning
berlin_marathon = berlin_marathon[(berlin_marathon['time'] != '–')&
                                  (berlin_marathon['time'] != 'DSQ')&
                                  (berlin_marathon['time'] != 'no time')]
berlin_marathon['time_hrs'] = pd.to_timedelta(berlin_marathon['time']).dt.total_seconds() / 3600
berlin_marathon.dropna(subset = 'time_hrs', how='any')
berlin_marathon

overall_times = pd.DataFrame(berlin_marathon.groupby('year')['time_hrs'].mean().rename('Average Times'))#.hvplot(kind = 'scatter', title = 'Average times over the years')
overall_times['Finishing times'] = berlin_marathon.groupby('year')['time_hrs'].min()
overall_times_plot = overall_times.hvplot(title = 'Average and Finishing times')


berlin_marathon_ = berlin_marathon.groupby(['country', 'gender']).size().sort_values(ascending = False)
berlin_marathon_ = berlin_marathon_[berlin_marathon_ > 1000]
berlin_marathon_plot = berlin_marathon_.hvplot(kind = 'bar', 
                                               stacked = True, 
                                               rot = 45,
                                               title = 'Where are most runners from?')
berlin_marathon_plot


berlin_marathon = berlin_marathon.dropna(subset=['country', 'gender']).sort_values(by = 'time_hrs')
berlin_marathon_ = berlin_marathon[:50].groupby(['country', 'gender']).size().sort_values(ascending = False)#.unstack(fill_value = 0)
berlin_marathon_plot = berlin_marathon_.hvplot(kind = 'bar', 
                                               stacked = True, 
                                               rot = 45,
                                               title = 'Where are the top 50 runners from?')
berlin_marathon_plot


template = pn.template.FastListTemplate(
    title = 'Berlin Marathon runners',
    sidebar = [pn.pane.Markdown("# Runners!")],
    main = [pn.Row(pn.Column(overall_times_plot, berlin_marathon_plot))]

)
template.servable();