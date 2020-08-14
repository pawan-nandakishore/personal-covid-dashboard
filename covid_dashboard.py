import pandas as pd 
import os 
import numpy as np
import plotly.express as px
import datetime
import plotly.graph_objects as go
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import us 
import flask

server = flask.Flask(__name__) # define flask app.server

# Get daily data 
overall_us_df = pd.read_csv('https://api.covidtracking.com/v1/us/daily.csv')
overall_us_df['dates_dt'] = pd.to_datetime(overall_us_df['date'], format='%Y%m%d')
clip_columns = ['positiveIncrease',
                'deathIncrease',
                 'totalTestResultsIncrease', 
                 'hospitalizedIncrease']
for cc in clip_columns: 
    overall_us_df[cc] = overall_us_df[cc].clip(lower=0)

states_historic_df = pd.read_csv("https://api.covidtracking.com/v1/states/daily.csv")
states_historic_df['dates_dt'] = pd.to_datetime(states_historic_df['date'], format='%Y%m%d')

for cc in clip_columns: 
    states_historic_df[cc] = states_historic_df[cc].clip(lower=0)


all_states = [x.name for x  in us.states.STATES]
all_states_abbr = [x.abbr for x  in us.states.STATES]
state_counts = []
for x in all_states_abbr: 
    positive_count= states_historic_df[states_historic_df['state'] == x]['positive'].max()
    state_counts.append(positive_count)
 
state_totals = pd.DataFrame(data=[all_states, state_counts]).T
state_totals = state_totals.rename(columns={0:"State",1:"Totals"})

def set_zero(df, column): 
    df.loc[df[column] < 0, column] = 0  
    return df


## main choropleth plot
main_choropleth = go.Figure(data=go.Choropleth(
    locations= all_states_abbr, # Spatial coordinates
    z = state_totals['Totals'].astype(float), # Data to be color-coded
    locationmode = 'USA-states', # set of locations match entries in `locations`
    colorscale = 'Reds',
    colorbar_title = "Number of Cases",
))

main_choropleth.update_layout(
    title_text = 'Total Covid 19 across US states',
    geo_scope='usa', # limite map scope to USA
)


## State cases counts
perday_state = states_historic_df[states_historic_df['state'] == 'CA']
confirmed_fig = px.bar(perday_state,
                        x='dates_dt',
                        y='positiveIncrease',
                        labels={"positiveIncrease":"Total Number of new cases",
                                "dates_dt" : "Time"},
                        title='Daily counts for California')
confirmed_fig.update_xaxes(nticks=20)

## State death counts 
perday_state = states_historic_df[states_historic_df['state'] == 'CA']
title = "Daily Death counts for {}".format("California")
deaths_fig = px.bar(perday_state,
                    x='dates_dt', 
                    y='deathIncrease', 
                     labels={"deathIncrease":"Total Number of new deaths",
                                "dates_dt" : "Time"},
                    title=title)
deaths_fig.update_xaxes(nticks=20)


external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

tabs_styles = {
    'height': '44px'
}
tab_style = {
    'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold',
    'border-radius':'25px',
    
}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#119DFF',
    'border-radius':'25px',
    'color': 'white',
    'padding': '6px'
}



############################ BEGIN APP ##############################################
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, server=server)
app.layout = html.Div([
      
    html.Div([html.H1("Covid-19 Dashboard For United States")], style={"text-align":"center",
                                                     "border":"5px black", 
                                                     "background-color":"#5569F1", 
                                                     "border-radius":"25px", 
                                                     "color":"white",
                                                     "font-weight":"bold"
                                                     }), 


    # Refresh data 
    html.Div([
              dcc.Interval(
                    id='get_data',
                    interval=20*1000, # in milliseconds
                    n_intervals=0
                    ),
            html.H3(id='show-data') ],
                    id="load-data", 
                    style={'display': 'none'}),   

    html.Div([
                html.Div([html.H3("Covid-19 Summary")]),
                html.Div([

                    dcc.Interval(
                                id='update-summary',
                                interval=2000*1000, # in milliseconds
                                n_intervals=0
                                ),

                            html.Div([
                            html.Div([
                                html.Div(id="cases-count")
                            ], className="six columns"),

                            html.Div([ 
                                html.Div(id="deaths-count")
                            ], className="six columns"),
                            ], className="summ1-row"), 
                            html.Div([
                            html.Div([
                                html.Div(id="tested-count")
                            ], className="six columns"),
                            
                            html.Div([ 
                                html.Div(id="hospitalized-count")
                            ], className="six columns"),

                        ], className="summ2-row")
                ]), 

    ], style={"padding-bottom":"50px",
                    "border":"2px outset black", 
                    "background-color":"#5569F1", 
                    "border-radius":"25px", 
                    "color":"white", 
                    "height":"200px",
                    "text-align":"center"}), 
    
    html.Div([html.H4("Covid-19 data per day")]),
    ## Daily number of cases and deaths plot
    # Daily number of cases plot
    html.Div([
        html.Div([
            dcc.Tabs(id='confirmed_tabs',
                     value='tab-1',
                     children=[
                        dcc.Tab(label='Linear', value='tab-1', style=tab_style, selected_style=tab_selected_style),
                        dcc.Tab(label='Cumulative', value='tab-2', style=tab_style, selected_style=tab_selected_style),
                        ]),
            
         dcc.Graph(id='pl1'),
            ],
           className="six columns"),
    # Daily number of deaths plot
    html.Div([
    dcc.Tabs(id='deaths_tabs',
             value='tab-1',
             children=[
                        dcc.Tab(label='Linear', value='tab-1', style=tab_style, selected_style=tab_selected_style),
                        dcc.Tab(label='Cumulative', value='tab-2', style=tab_style, selected_style=tab_selected_style),
                    ]),
    dcc.Graph(id='pl2')
    ],
     className="six columns"),
    ],className="cases-deaths-row"), 
   ## Daily number of tested and hospitalized plot
   # Daily number of Tested plot 
    html.Div([
        html.Div([
            dcc.Tabs(id='tested_tabs',
                     value='tab-1',
                     children=[
                        dcc.Tab(label='Linear', value='tab-1', style=tab_style, selected_style=tab_selected_style),
                        dcc.Tab(label='Cumulative', value='tab-2', style=tab_style, selected_style=tab_selected_style),
                        ]),
            
         dcc.Graph(id='pl_tested'),
            ],
           className="six columns"),
    # Daily number of hospitalized plot
    html.Div([
    dcc.Tabs(id='hospitalized_tabs',
             value='tab-1',
             children=[
                        dcc.Tab(label='Linear', value='tab-1', style=tab_style, selected_style=tab_selected_style),
                        dcc.Tab(label='Cumulative', value='tab-2', style=tab_style, selected_style=tab_selected_style),
                    ]),
    dcc.Graph(id='pl_hospitalized')
    ],
     className="six columns"),
    ],className="tested-hospitalized-row"),
    
    # US map choropleth 
    html.Div([html.H4("Click on each state to see confirmed cases and deaths")]),
    html.Div([dcc.Graph(id="main-choro",
                        figure=main_choropleth)],
                        style={'width': '100%',
                                'display': 'inline'}, 
                                className="six columns"),  
    html.Div([
    # Small plot 1
    html.Div([dcc.Graph(id="pl3", figure=confirmed_fig)], className="six columns"),  
    # Small plot 2 
    html.Div([dcc.Graph(id="pl4", figure=deaths_fig )], className="six columns"),  
    ], className="state-row"),

    html.Footer(id="data-source",
        children=[html.H4(dcc.Link("Data Source: Covid Tracking project",
                                    href='https://covidtracking.com/'))] )    

])

##################### END APP ######################################################
## All CALLBACKS


@app.callback([Output('cases-count', 'children'),
              Output('deaths-count', 'children'),
              Output('tested-count', 'children'),
              Output('hospitalized-count', 'children')],  
              [Input('update-summary', 'n_intervals')])
def update_summary_metrics(n): 
    total_cases =  "Total cases: " + str(int(overall_us_df['positive'].loc[0])) 
    total_deaths = "Total deaths: " + str(int(overall_us_df['death'].loc[0]))
    total_tested = "Total tested: " + str(int(overall_us_df['total'].loc[0]))
    total_hospitalized = "Total Hospitalized: " + str(int(overall_us_df['hospitalized'].loc[0]))
     
    cases_div = html.H4([total_cases])
    deaths_div = html.H4([total_deaths])
    tested_div = html.H4([total_tested])
    hosp_div = html.H4([total_hospitalized])
    return  [cases_div, deaths_div, tested_div, hosp_div]

@app.callback(Output('pl3', 'figure'),
             [Input('main-choro','clickData')])
def display_states_cases(clickData):
    single_state = clickData['points'][0]['location']
    
    perday_state = states_historic_df[states_historic_df['state'] == single_state]
    title = "Daily counts for {}".format(single_state)
    state_fig = px.bar(perday_state, 
                       x='dates_dt',
                       y='positiveIncrease',
                       labels={"positiveIncrease":"Total Number of new cases",
                                "dates_dt" : "Time"},
                       title=title)
    state_fig.update_xaxes(nticks=20)
    return state_fig


@app.callback(Output('pl4', 'figure'),
             [Input('main-choro','clickData')])
def display_state_deathsa(clickData):
    single_state = clickData['points'][0]['location']
    perday_state = states_historic_df[states_historic_df['state'] == single_state]
    title = "Death counts for {}".format(single_state)
    state_fig = px.bar(perday_state, 
                       x='dates_dt', 
                       y='deathIncrease', 
                       labels={"deathIncrease":"Total Number of new deaths",
                                "dates_dt" : "Time"},
                       title=title)
    state_fig.update_xaxes(nticks=20)
    return state_fig


@app.callback(Output('pl1', 'figure'),
              [Input('confirmed_tabs', 'value')])
def render_confirmed(tab):
    if tab == 'tab-1':
        dc_fig = px.bar(overall_us_df, 
                        x='dates_dt', 
                        y='positiveIncrease', 
                        labels={"positiveIncrease":"Total Number of new casess",
                                "dates_dt" : "Time"},
                        title='New cases per day for US')
        dc_fig.update_xaxes(nticks=20)
        return dc_fig
    elif tab == 'tab-2':
        dc_fig = px.scatter(overall_us_df, 
                        x='dates_dt', 
                        y='positive', 
                        labels={"positive":"Cumulative total number of cases",
                                "dates_dt" : "Time"},
                        title='New cases per day for US')
        dc_fig.update_xaxes(nticks=20)
        return dc_fig

    
@app.callback(Output('pl2', 'figure'),
              [Input('deaths_tabs', 'value')])
def render_deaths(tab):
    if tab == 'tab-1':
        dc_fig = px.bar(overall_us_df, 
                        x='dates_dt', 
                        y='deathIncrease', 
                        labels={"deathIncrease":"Total Number of deaths",
                                "dates_dt" : "Time"},
                        title='Death count per day for US')
        dc_fig.update_xaxes(nticks=20)
        return dc_fig
    elif tab == 'tab-2':
        dc_fig = px.scatter(overall_us_df, 
                        x='dates_dt', 
                        y='death',
                         labels={"death":"Cumulative total Number of deaths",
                                "dates_dt" : "Time"},
                        title='Cumulative Death count per day for US')
        dc_fig.update_xaxes(nticks=20)
        return dc_fig
   

@app.callback(Output('pl_tested', 'figure'),
              [Input('tested_tabs', 'value')])
def render_tested(tab):
    if tab == 'tab-1':
        tested_fig = px.bar(overall_us_df, 
                            x='dates_dt', 
                            y='totalTestResultsIncrease', 
                             labels={"totalTestResultsIncrease":"Total Number of people tested",
                                "dates_dt" : "Time"},
                            title='Total number of people tested per day for US')
        tested_fig.update_xaxes(nticks=20)
        return tested_fig
    elif tab == 'tab-2':
        tested_fig = px.scatter(overall_us_df, 
                            x='dates_dt', 
                            y='total', 
                            labels={"total":"Cumulative number of people tested",
                                "dates_dt" : "Time"},
                            title='Cumulative number of people tested per day for US')
        tested_fig.update_xaxes(nticks=20)
        return tested_fig

    
@app.callback(Output('pl_hospitalized', 'figure'),
              [Input('hospitalized_tabs', 'value')])
def render_content(tab):
    if tab == 'tab-1':
        hosp_fig = px.bar(overall_us_df,
                         x='dates_dt', 
                         y='hospitalizedIncrease', 
                        labels={"hospitalizedIncrease":"Total Number of people hospitalized",
                                "dates_dt" : "Time"},
                         title='Total number of people hospitalized per day for US')
        hosp_fig.update_xaxes(nticks=20)
        return hosp_fig

    elif tab == 'tab-2':
        hosp_fig = px.scatter(overall_us_df, 
                          x='dates_dt', 
                          y='hospitalized', 
                          labels={"hospitalized":"Cumulative Total Number of people hospitalized",
                                "dates_dt" : "Time"},
                          title='Cumulative Total number of people hospitalized per day for US')
        hosp_fig.update_xaxes(nticks=20)
        return hosp_fig


@app.callback(Output('load-data', 'children'),
              [Input('get_data', 'n_intervals')])
def get_data(n): 
    global overall_us_df 
    overall_us_df = pd.read_csv('https://api.covidtracking.com/v1/us/daily.csv')
    overall_us_df['dates_dt'] = pd.to_datetime(overall_us_df['date'], format='%Y%m%d')
    clip_columns = ['positiveIncrease',
                'deathIncrease',
                 'totalTestResultsIncrease', 
                 'hospitalizedIncrease']
    for cc in clip_columns: 
        overall_us_df[cc] = overall_us_df[cc].clip(lower=0)
    overall_us_df.loc[overall_us_df['positiveIncrease'] < 0, 'positiveIncrease'] = 0 
    overall_us_df.loc[overall_us_df['deathIncrease'] < 0, 'deathIncrease'] = 0 

    global states_historic_df
    states_historic_df = pd.read_csv("https://api.covidtracking.com/v1/states/daily.csv")
    states_historic_df['dates_dt'] = pd.to_datetime(states_historic_df['date'], format='%Y%m%d')
    states_historic_df.loc[states_historic_df['deathIncrease'] < 0, 'deathIncrease'] = 0 
    states_historic_df.loc[states_historic_df['positiveIncrease'] < 0, 'positiveIncrease'] = 0 
    
if __name__== "__main__": 
    app.run_server(debug=True)  # Turn off reloader if inside Jupyter
