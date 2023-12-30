#!/usr/bin/env python
# coding: utf-8

# # An Analysis of the Berlin Marathon Runners
# - What is the Berlin marathon?
#     - The Berlin marathon is a global marathon held yearly in Berlin, Germany since 1974. The dataset in used includes running times since the marathon's inception, and we delve into how some trends in running speeds have changed over time, and what factors play into lower running times.
# - How have the average/fastest times changed over the years?
#     - The top left graph shows that the average running times have increased over the years, likely due to an increase in the interest in the running community. The final running times, however, have decrease, given the increased number of challengers.
# - How does age and gender affect running times
#     - In the bottom left, we can see that women are overall slower than men by 30 minutes on average. In terms of age (the graph can be viewed in the dropdown), the peak running times occur around 30 years.
# - Where are most runners from? Where are the fastest from. 
#     - Given that this event takes place in Berlin, most runners are from Germany. The fastest runners are from Kenya, Ethiopia. As studies have now shown, this is due to strong genetics and high-altitude training.

# This project takes the Berlin Marathon dataset and analyzes it look at how running times have changed over the years, and over different age groups and genders. It also takes a look into where the top runners are from.

# In[11]:


import pandas as pd
import matplotlib.pyplot as plt
import panel as pn
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

pn.extension('tabulator')

import hvplot.pandas


# In[12]:


#format: year, country, gender, age, time
#(all participants)
berlin_marathon = pd.read_csv('1_running_datasets/berlin_marathon_1974_2023.csv')

age_null_values = ['H', 'JU20', 'L1', 'L2', 'L', 'L3', 'D1', 'L4', 'D3', 'D2',
                  'BM','A', 'B', 'C', 'DH', 'DA', 'DB', 'DJ', 'M0', 'Ber', 'M',
                  'M<', 'Jug']

#data cleaning
berlin_marathon = berlin_marathon[~(berlin_marathon['time'].isin(['–', 'DSQ', 'no time']))&
                                  ~(berlin_marathon['age'].isin(age_null_values))]
#convert time to hrs
berlin_marathon['time_hrs'] = pd.to_timedelta(berlin_marathon['time']).dt.total_seconds() / 3600
berlin_marathon.dropna(subset = 'time_hrs', how='any')
berlin_marathon['age'] = pd.to_numeric(berlin_marathon['age'])


# In[13]:


year_slider = pn.widgets.IntSlider(name='Year slider', start=1974, end=2023, step=1, value=2023)
idf = berlin_marathon.interactive()


# ## Average and Finishing times
# - How have average times changed over the years?
#     - Overall average time has increased. Likely due to the increase in interest in the sport.
# - How has the fastest time changed over the years?
#     - Finishing times have decreased. obvs. because records are meant to be broken.

# In[14]:


overall_times = pd.DataFrame(berlin_marathon.groupby('year')['time_hrs'].mean().rename('Average Times'))#.hvplot(kind = 'scatter', title = 'Average times over the years')
overall_times['Finishing times'] = berlin_marathon.groupby('year')['time_hrs'].min()
overall_times_plot = overall_times.hvplot(title = 'Average and Finishing times', xlabel = 'year', ylabel = 'time(hrs)')
overall_times_plot


# ## Table df

# In[15]:


# berlin_marathon.interactive()


# In[27]:


marathon_table = berlin_marathon.sort_values(by = 'time_hrs').drop(columns = ['time_hrs']).dropna(subset = 'country').interactive().reset_index()
marathon_table = marathon_table.pipe(pn.widgets.Tabulator, page_size = 10, sizing_mode='stretch_width')
marathon_table


# ## How does gender affect running times?

# In[17]:


berlin_marathon.dtypes


# In[18]:


age_data_pipeline = (
    berlin_marathon
    .sort_values(by = 'year', ascending = False)
    .groupby(['age'])['time_hrs'].mean()
    .to_frame()
    .reset_index()
    .reset_index(drop=True)

)
age_data_plot = age_data_pipeline.hvplot(
    kind = 'scatter',
    title = 'Average time by age', 
    x = 'age',
    y = 'time_hrs')
age_data_plot


# ## How does gender affect times?

# In[19]:


gender_data = berlin_marathon[(berlin_marathon['gender'] != 'X') & (berlin_marathon['gender'] != '–') ]
gender_data_pipeline = (
    gender_data
    .sort_values(by = 'year')
    .groupby(['gender', 'year'])['time_hrs'].mean()
    .to_frame()
    .reset_index()
    .reset_index(drop=True)

)
gender_data_plot = gender_data_pipeline.hvplot(
    kind = 'scatter',
    by = 'gender',
    title = 'Average time by gender', 
    x = 'year',
    y = 'time_hrs')
gender_data_plot


# ### What are the average time differences

# In[20]:


time_diff = idf[(idf['gender'] != 'X') & (idf['gender'] != '–') ]
time_diff = time_diff.groupby('gender')['time_hrs'].mean().reset_index()
time_diff.iloc[0,1]-time_diff.iloc[1,1]


# ## Where are most runners from?
# - Where do most runners come from?
#     - Germany
# - Where are the shortest times from?
#     - Kenya, followed by Ethiopia. Even tho Germany had the most participants ahaha
# - Are these two places the same?
#     - no. no they are not.

# In[21]:


runners_count = berlin_marathon.groupby(['country', 'gender']).size().sort_values(ascending = False)
runners_count = runners_count[runners_count > 1000]
runners_count_plot = runners_count.hvplot(kind = 'bar', 
                                               stacked = True, 
                                               rot = 45,
                                               title = 'Where are most runners from?')
runners_count_plot


# ## Where are the top 50 runners from?

# In[22]:


gender_selector = pn.widgets.Select(options=['All', 'male', 'female'], value='Men', name='Select Gender')
gender_selector


# In[23]:


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
top_50_plot

berlin_marathon = berlin_marathon.dropna(subset=['country', 'gender']).sort_values(by = 'time_hrs')
berlin_marathon_ = berlin_marathon[:50].groupby(['country', 'gender']).size().sort_values(ascending = False)#.unstack(fill_value = 0)
berlin_marathon_plot = berlin_marathon_.hvplot(kind = 'bar', 
                                               stacked = True, 
                                               rot = 45,
                                               title = 'Where are the top 50 runners from?')
berlin_marathon_plot

# In[24]:


plot_selector_2_1 = pn.widgets.Select(options=['Average time by gender', 'Average time by age'], name='Select Plot')
@pn.depends(plot_selector_2_1.param.value)
def reactive_plot_2_1(selected_plot):
    
    if selected_plot == 'Average time by gender':
        return gender_data_plot
    elif selected_plot == 'Average time by age':
        return age_data_plot

plot_selector_2_2 = pn.widgets.Select(options=['Top 50', 'Runner Population'], name='Select Plot')
@pn.depends(plot_selector_2_2.param.value)
def reactive_plot_2_2(selected_plot):
    if selected_plot == 'Top 50':
        return top_50_plot
    elif selected_plot == 'Runner Population':
        return runners_count_plot


# In[53]:


template = pn.template.FastListTemplate(
    title = 'Berlin Marathon runners',
    sidebar = [pn.pane.Markdown("# Berlin Marathon!"),
               pn.pane.Markdown("### What is the Berlin marathon? \n "
                                " - The Berlin marathon is a global marathon held yearly in Berlin, Germany since 1974."
                                "The dataset in used includes running times since the marathon's inception, "
                                "and we delve into how some trends in running speeds have changed over time, "
                                "and what factors play into lower running times."),
               pn.pane.Markdown("### How have the average and fastest times changed over the years? \n"
                               " - The top left shows a comparison of the average and the fastest times, which have increased"
                               "over the years. This is likely due to an increase in the interest in the running community. "
                               "The final running times, however, have decreased, given the increased number of challengers. "),
               pn.pane.Markdown("### How does age and gender affect running times? \n"
                               " - In the bottom left, we can see that women are overall slower than men by 30 minutes on "
                               "average. In terms of age (the graph can be viewed in the dropdown), the peak running times "
                               "occur around 30 years."),
               pn.pane.Markdown("### Where are most runners from? \n"
                               " - Given that this event takes place in Berlin, most runners are from Germany. The fastest"
                               "runners are from Kenya and Ethiopia. As studies have now shown, this is due to strong genetics and "
                               "high-altitude training.")
              ],
    main = [pn.Row(pn.Column(overall_times_plot), pn.Column(marathon_table)),#, top_50_plot)),
           pn.Row(pn.Column(plot_selector_2_1, reactive_plot_2_1), pn.Column(plot_selector_2_2, reactive_plot_2_2))
           ])
template.servable()


# In[ ]:




