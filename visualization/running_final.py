#!/usr/bin/env python
# coding: utf-8

# # An Analysis of the Berlin Marathon Runners
# - How have the average times changed over the years?
# - How have the fastest times changed over the years?
# - How does age and gender affect running times
#     - Finisher times over the years
# - Where are most runners from?
# - Where are the fastest runners from?

# This project takes the Berlin Marathon dataset and analyzes it look at how running times have changed over the years, and over different age groups and genders. It also takes a look into where the top runners are from.

# In[1]:


import pandas as pd
import matplotlib.pyplot as plt
import panel as pn
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

pn.extension('tabulator')

import hvplot.pandas


# In[2]:


#format: year, country, gender, age, time
#(all participants)
berlin_marathon = pd.read_csv('1_running_datasets/berlin_marathon_1974_2023.csv')

#data cleaning
berlin_marathon = berlin_marathon[(berlin_marathon['time'] != '–')&
                                  (berlin_marathon['time'] != 'DSQ')&
                                  (berlin_marathon['time'] != 'no time')]
#convert time to hrs
berlin_marathon['time_hrs'] = pd.to_timedelta(berlin_marathon['time']).dt.total_seconds() / 3600
berlin_marathon.dropna(subset = 'time_hrs', how='any')
berlin_marathon


# In[3]:


year_slider = pn.widgets.IntSlider(name='Year slider', start=1974, end=2023, step=1, value=2023)
idf = berlin_marathon.interactive()


# ##### Average and Finishing times
# - How have average times changed over the years?
#     - Overall average time has increased. Likely due to the increase in interest in the sport.
# - How has the fastest time changed over the years?
#     - Finishing times have decreased. obvs. because records are meant to be broken.

# In[34]:


overall_times = pd.DataFrame(berlin_marathon.groupby('year')['time_hrs'].mean().rename('Average Times'))#.hvplot(kind = 'scatter', title = 'Average times over the years')
overall_times['Finishing times'] = berlin_marathon.groupby('year')['time_hrs'].min()
overall_times_plot = overall_times.hvplot(title = 'Average and Finishing times')
overall_times_plot


# ##### Where are most runners from?
# - Where do most runners come from?
#     - Germany
# - Where are the shortest times from?
#     - Kenya, followed by Ethiopia. Even tho Germany had the most participants ahaha
# - Are these two places the same?
#     - no. no they are not.

# In[5]:


runners_count = berlin_marathon.groupby(['country', 'gender']).size().sort_values(ascending = False)
runners_count = runners_count[runners_count > 1000]
runners_count_plot = runners_count.hvplot(kind = 'bar', 
                                               stacked = True, 
                                               rot = 45,
                                               title = 'Where are most runners from?')
runners_count_plot


# In[22]:


gender_selector = pn.widgets.Select(options=['All', 'male', 'female'], value='Men', name='Select Gender')
gender_selector


# In[32]:


gender_selector = pn.widgets.Select(options=['male', 'female'], value='Men', name='Select Gender')
top_50_pipeline = (
    idf[
        (idf['gender'] == gender_selector)
    ]
    .dropna(subset=['country', 'gender']).sort_values(by = 'time_hrs')[:50]
    .groupby(['country', 'gender']).size()
    .sort_values(ascending = False)
    .to_frame()
    .reset_index()
    .reset_index(drop=True)
)
top_50_plot = top_50_pipeline.hvplot(kind = 'bar', 
                       x = 'country',
                       ylabel = 'count',
                       stacked = True, 
                       rot = 45,
                       title = 'Where are the top 50 runners from?')

berlin_marathon = berlin_marathon.dropna(subset=['country', 'gender']).sort_values(by = 'time_hrs')
berlin_marathon_ = berlin_marathon[:50].groupby(['country', 'gender']).size().sort_values(ascending = False)#.unstack(fill_value = 0)
berlin_marathon_plot = berlin_marathon_.hvplot(kind = 'bar', 
                                               stacked = True, 
                                               rot = 45,
                                               title = 'Where are the top 50 runners from?')
berlin_marathon_plot

# In[56]:


plot_selector = pn.widgets.Select(options=['Top 50', 'Runner Population'], name='Select Plot')
@pn.depends(plot_selector.param.value)
def reactive_plot(selected_plot):
    if selected_plot == 'Top 50':
        return top_50_plot
    elif selected_plot == 'Runner Population':
        return runners_count_plot


# In[61]:


template = pn.template.FastListTemplate(
    title = 'Berlin Marathon runners',
    sidebar = [pn.pane.Markdown("# Runners!"),
               year_slider
              ],
    main = [pn.Row(pn.Column(overall_times_plot)),#, top_50_plot)),
           pn.Row(pn.Column(plot_selector, reactive_plot))]
)
template.servable();


# In[59]:


reactive_plot('Plot 2')


# In[ ]:




