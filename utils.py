
import pandas as pd
import numpy as np 
import us
import yaml 
from urllib.request import urlopen
import geopandas as gpd
import json 
import plotly.graph_objects as go
import dash_core_components as dcc
import plotly.express as px
import datetime
import dash_html_components as html
import dash_bootstrap_components as dbc


with open("config.yml",'r') as f: 
    config = yaml.load(f,  Loader=yaml.FullLoader)

tabs_styles = {
    'height': '44px'
}
tab_style = {
    # 'borderBottom': '1px solid #d6d6d6',
    'padding': '6px',
    'fontWeight': 'bold',
    'border-radius':'25px',
     'color': 'black'
    
}

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': '#119DFF',
    'border-radius':'25px',
    'color': 'blue',
    'padding': '6px'
}


def below_title(): 
    below_text = dcc.Markdown("""  #### The set of dashboards presented here try to capture the scale of the COVID-19 pandemic in the United States. It can be used as a means of daily updates but also to look at overall trends. The Dashboard is typically one day behind in terms of scraping the data. The data is sourced from couple of different sources which are referenced."""
                            )
    return below_text



def page1_plots_text():
    text = html.H6("""Below are 4 plots that show time evolution the pandemic. The first plot the top right is the number of new cases per day. 
        The plot to right of it is the number of deaths per day, the bottom left plot is the number of people tested per day and the bottom right plot
        the number of people hospitalized per day. Each plot has a tab that shows a plot of the cumulative number of cases. The cumulative number of cases
        is the sum of all cases up till chosen date.
        
        While to cases per day is useful information, the cumulative can help us better visualize if the pandemic is accelerating. """)
    return text

def footer_text(): 
    text = html.H6(""" The dashboard is divided into 3 pages- The first page shows overall US data, on the second page you can drill down into each state and look at the number of cases by county. The third page contains references and data sources. The county maps are overlaid over a Mapbox map to make it easier to identify where the county boundaries. While we look at these numbers, we must not forget that each number here is person. No single number or set of numbers can truly capture the loss that people have suffered through this pandemic.
     Please wear a mask and practice social distancing.""")
    return text 


def page2_below_title(): 
    return html.H5("""Get a state and county wise breakdown of COVID-19 cases. Hover over the map below to see the names of the state and see cumulative values of each metric. You can switch between three metrics below.""")


def daily_data(): 
    overall_us_df = pd.read_csv('https://api.covidtracking.com/v1/us/daily.csv')
    overall_us_df['dates_dt'] = pd.to_datetime(overall_us_df['date'], format='%Y%m%d')
    clip_columns = ['positiveIncrease',
                'deathIncrease',
                 'totalTestResultsIncrease', 
                 'hospitalizedIncrease']
    for cc in clip_columns: 
        overall_us_df[cc] = overall_us_df[cc].clip(lower=0)
    return overall_us_df


def historic_data(): 
    states_historic_df = pd.read_csv("https://api.covidtracking.com/v1/states/daily.csv")
    states_historic_df['dates_dt'] = pd.to_datetime(states_historic_df['date'], format='%Y%m%d')
    clip_columns = ['positiveIncrease',
                'deathIncrease',
                 'totalTestResultsIncrease', 
                 'hospitalizedIncrease']
    for cc in clip_columns: 
        states_historic_df[cc] = states_historic_df[cc].clip(lower=0)
    return states_historic_df


def state_totals(states_historic_df, column, all_states, all_states_abbr):
    
    state_counts = []
    for x in all_states_abbr: 
        positive_count= states_historic_df[states_historic_df['state'] == x][column].max()
        state_counts.append(positive_count)

    totals = pd.DataFrame(data=[all_states, state_counts]).T
    totals = totals.rename(columns={0:"State",1:"Totals"})
    return totals 

    

def county_level_daily(cases=True): 
    save_name = config['jh_counties_cases']
    counties_cases = pd.read_csv(config['jh_timeseries_cases'])
    if cases == False:
        counties_cases = pd.read_csv(config['jh_timeseries_deaths'])
        save_name = config['jh_counties_deaths']
    counties_cases = counties_cases.drop(columns=['UID', 'iso2', 'iso3', 'code3'])
    counties_cases = counties_cases.dropna( subset=['FIPS'])
    counties_cases['FIPS'] = counties_cases['FIPS'].astype(int) 

    true_list, indx_list = get_timecols_v1(counties_cases)
    columns_list = counties_cases.columns.tolist()
    new_columns = []
    for indx in indx_list: 
        col = columns_list[indx]
        new_col = "-".join([col.split("/")[2],col.split("/")[0],col.split("/")[1]])
        columns_list[indx] = new_col
    counties_cases.columns = columns_list
    counties_cases.to_csv(save_name, index=False )
    return counties_cases



def counties_data_json(): 

    with urlopen(config['plotly_geojson_counties']) as response:
        counties = json.load(response)
    fips_states_df = pd.read_csv("data/states_fips_code.txt", delimiter='|')
    counties_df = gpd.GeoDataFrame.from_features(counties["features"])
    counties_df['STATE'] = counties_df['STATE'].astype(int)
    counties_df = counties_df.merge(fips_states_df, on='STATE' )
    return counties_df

def get_timecols_v1(df):
    true_list = []
    indx_list = []
    for indx, col in enumerate(df.columns):
        try: 
            datetime.datetime.strptime(col,'%m/%d/%y' )
            true_list.append(True)
            indx_list.append(indx)
        except:
            true_list.append(False)
    return true_list, indx_list

def get_timecols_v2(df):
    true_list = []
    indx_list = []
    for indx, col in enumerate(df.columns):
        try: 
            datetime.datetime.strptime(col,'%y-%m-%d' )
            true_list.append(True)
            indx_list.append(indx)
        except:
            true_list.append(False)
    return true_list, indx_list

def all_counties(cases=True): 

    counties_cases = pd.read_csv(config['jh_counties_cases'])
    counties_df = counties_data_json()
    counties_df['FIPS'] = counties_df['GEO_ID'].apply(lambda x: int(x.split("US")[1]))
    merged_county_data = pd.merge(counties_df, counties_cases, left_on='FIPS', right_on='FIPS')
    merged_county_data.to_csv(config['counties_data'])




def get_zoom_level(counties_df):
    area_by_state = counties_df.groupby("STATE_NAME").agg({'CENSUSAREA': 'sum'})
    sorted_area = area_by_state.sort_values(by='CENSUSAREA').reset_index()

    zoom_levels = (-0.5*(np.linspace(0,6.5, 52)))+ 7.0
    zoom_levels = np.around(zoom_levels,2)
    ordered_states = ['District of Columbia', 'Rhode Island', 'Delaware', 'Puerto Rico',
       'Connecticut', 'Hawaii', 'New Jersey', 'Massachusetts',
       'New Hampshire', 'Vermont', 'Maryland', 'West Virginia',
       'South Carolina', 'Maine', 'Indiana', 'Kentucky', 'Virginia',
       'Ohio', 'Tennessee', 'Louisiana', 'Pennsylvania', 'Mississippi',
       'New York', 'North Carolina', 'Alabama', 'Arkansas', 'Florida',
       'Wisconsin', 'Illinois', 'Iowa', 'Michigan', 'Georgia',
       'Washington', 'Oklahoma', 'Missouri', 'North Dakota',
       'South Dakota', 'Nebraska', 'Minnesota', 'Kansas', 'Utah', 'Idaho',
       'Oregon', 'Wyoming', 'Colorado', 'Nevada', 'Arizona', 'New Mexico',
       'Montana', 'California', 'Texas', 'Alaska']

    ordered_abbr = ['DC', 'RI', 'DE', 'PR', 'CT', 'HI', 'NJ', 'MA', 'NH', 'VT', 'MD',
       'WV', 'SC', 'ME', 'IN', 'KY', 'VA', 'OH', 'TN', 'LA', 'PA', 'MS',
       'NY', 'NC', 'AL', 'AR', 'FL', 'WI', 'IL', 'IA', 'MI', 'GA', 'WA',
       'OK', 'MO', 'ND', 'SD', 'NE', 'MN', 'KS', 'UT', 'ID', 'OR', 'WY',
       'CO', 'NV', 'AZ', 'NM', 'MT', 'CA', 'TX', 'AK']
    zoom_dict = {}
    for indx,val in enumerate(ordered_abbr): 
        zoom_dict[val] = zoom_levels[indx]
    return zoom_dict 



def get_state_centers(): 
    states_centers = pd.read_csv(config['state_centers'], delimiter='\t', header=None)
    states_centers.columns = ['Abbr', 'lat', 'lon', 'State']
    return states_centers


def choropleth_state(state_name): 
    counties_df = pd.read_csv(config['counties_data'])    
    counties_df = counties_df.drop(columns=[counties_df.columns[0]])   
    covid_df = counties_df[['NAME',counties_df.columns[-1]]]
    df = counties_data_json()
    df = df.merge(covid_df, how='left', on='NAME')
    states_centers = get_state_centers() 
    df = df[df['STUSAB'] ==state_name] 
    df['id'] =  df['COUNTY'].astype(str) + '-' + df['NAME'].astype(str)
    df = df.set_index('id')
    df = df.rename(columns={df.columns[-1]:'covid_values'})

    lat_lon = states_centers[states_centers['Abbr'] == state_name][['lat', 'lon']]
    center_dict = {'lat': lat_lon['lat'].values[0],'lon': lat_lon['lon'].values[0] }
    zoom_dict =get_zoom_level(df)
    fig = px.choropleth(df,
                               geojson=df.geometry,
                               locations=df.index,
                               color='covid_values',
                                center = center_dict,
                            #   mapbox_style='open-street-map',
                            #     zoom=zoom_dict[state_name],
                            #     opacity=0.6, 
                               color_continuous_scale='rainbow'
                              
                               )
    fig.update_geos(fitbounds="locations", visible=False),
    fig.update_traces(marker_line_width=2, marker_line_color='black')
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0},
                      geo=dict(bgcolor= config['plot_color']),
                               paper_bgcolor=config['paper_color'] )

    return fig


def choropleth_state_v2(state_name):
    full_state = str(us.states.lookup(state_name))

    counties_df = pd.read_csv(config['counties_data'])    
    counties_df = counties_df.drop(columns=[counties_df.columns[0]])   
    covid_df = counties_df[['NAME',counties_df.columns[-1]]]
    fname = "data/state_geojson/{}_counties.json".format(full_state)
    with open(fname) as response:
            counties = json.load(response)
    df = gpd.GeoDataFrame.from_features(counties['features'])
    df['STATE'] = df['STATE'].astype(int)
    df = df.merge(covid_df, how='left', on='NAME')
    states_centers = get_state_centers() 
    df = df[df['STUSAB'] ==state_name] 
    df['id'] =  df['COUNTY'].astype(str) + '-' + df['NAME'].astype(str)
    df = df.set_index('id')
    df = df.rename(columns={df.columns[-1]:'covid_values'})

    lat_lon = states_centers[states_centers['Abbr'] == state_name][['lat', 'lon']]

    center_dict = {'lat': lat_lon['lat'].values[0],'lon': lat_lon['lon'].values[0] }
    zoom_dict =get_zoom_level(df)
    fig = px.choropleth_mapbox(df,
                            geojson=df.geometry,
                            locations=df.index,
                            color='covid_values',
                                center = center_dict,
                            mapbox_style='open-street-map',
                                zoom=zoom_dict[state_name],
                                opacity=0.6, 
                            color_continuous_scale='rainbow'
                            )

    fig.update_geos(fitbounds="locations", visible=False),
    fig.update_traces(marker_line_width=2, marker_line_color='black')
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0},   
                      geo=dict(bgcolor= config['plot_color']),
                      coloraxis_colorbar=dict(title=dict(text="Cumulative cases", font=dict(color='white', size=18)), tickfont=dict(size=14, color='white')))
    fig.update_layout(dict( paper_bgcolor=config['paper_color']))


    return fig
def county_cases_deaths(county_name, state_name, cases=True):
    county_name = county_name.split("-")[1]
    state_name = str(us.states.lookup(state_name))
    
    counties_cases = pd.read_csv(config['jh_counties_deaths'])
    if cases == True: 
        counties_cases = pd.read_csv(config['jh_counties_cases'])
    
    _, indx_list = get_timecols_v2(counties_cases)
    single_county_total = counties_cases[(counties_cases['Admin2'] == county_name) & (counties_cases['Province_State'] == state_name )].iloc[0,indx_list]
    county_cum_cases = single_county_total.to_frame()
    
    county_cum_cases.columns = ['cases']
    
    # New cases per day 
    county_day_cases = county_cum_cases['cases'].diff()
    county_day_cases = county_day_cases.fillna(0) 
    county_day_cases[county_day_cases < 0 ] = 0
    county_day_cases = county_day_cases.to_frame()
    county_day_cases['dates_dt']= county_day_cases.index
    county_day_cases['dates_dt'] = pd.to_datetime(county_day_cases['dates_dt'], format='%y-%m-%d')
    return county_cum_cases, county_day_cases

def plot_county_data(df, county_name, state_name, cases=True, cumulative=False ):
    if cases == True: 
        title = 'New cases per day for {} County, {}'.format(county_name, str(us.states.lookup(state_name)))
        labels = {"cases":"Total Number of new cases per day",
                     "index" : "Time"}
        if cumulative==True: 
            title = 'Cumulative number of cases for {} County, {}'.format(county_name, str(us.states.lookup(state_name)))
            labels = {"cases":"Total Number of new cases",
                     "index" : "Time"}
    else: 
        title='New deaths per day for {} County, {}'.format(county_name, str(us.states.lookup(state_name)))
        labels = {"cases":"Total Number of new deaths per day",
                                    "index" : "Time"}
        if cumulative==True: 
            title='Cumulative deaths per day for {} County, {}'.format(county_name, str(us.states.lookup(state_name)))
            labels = {"cases":"Total Number of new deaths",
                                    "index" : "Time"}
               
    county_fig = px.bar(df, 
                            x=df.index, 
                            y='cases', 
                            labels=labels,
                            title= title
                           )
    county_fig.update_yaxes(autorange=True, fixedrange=False)
    county_fig.update_xaxes(nticks=20)
    county_fig.update_layout(dict(paper_bgcolor=config['paper_color'],
                                         plot_bgcolor=config['plot_color'],
                                         font_color="white" ))
    county_fig.update_traces(marker_color=config['bar_color'],  marker_line_color=config['marker_line_color'])                            
    county_fig.update_xaxes(nticks=20, showgrid=False, gridcolor='grey', mirror=True, gridwidth=1, linecolor='grey', linewidth=3,  zeroline= True)
    county_fig.update_yaxes(showgrid=False, gridcolor='grey',  mirror=True, gridwidth=0.1, linecolor='grey', linewidth=3,  zeroline= True)
            
    return county_fig



def counties_textbox():
        
    # Text box to asking user to select a state
    df= pd.DataFrame.from_dict({'x':[0], 'mock':[0]})
    mock_plot = px.scatter(df, y="mock")

    mock_plot.add_annotation(
        text="Select a State to display the counties",
        font=dict(size=20),
        showarrow=False,
        xref="paper",
        yref="paper",
        x= 0.52,
        y=0.5,

    )
    mock_plot.update_layout(dict(paper_bgcolor=config['paper_color'],
                                            plot_bgcolor=config['paper_color'],
                                            font_color="white" ))
    mock_plot.update_traces(marker_color=config['bg_color'])                            
    mock_plot.update_xaxes(nticks=20, showgrid=False, visible=False,  showticklabels=False, zeroline= False)
    mock_plot.update_yaxes(showgrid=False, showticklabels=False, visible=False, zeroline= False)
    return mock_plot

    
def counties_cases_textbox():
        
    # Text box to asking user to select a state
    df = pd.DataFrame.from_dict({'x':[0], 'mock':[0]})
    mock_plot = px.scatter(df, y="mock")

    mock_plot.add_annotation(
        text="Select a County to display number of cases per day",
        font=dict(size=20),
        showarrow=False,
        xref="paper",
        yref="paper",
        x=0.2,
        y=0.4,

    )
    mock_plot.update_layout(dict(paper_bgcolor=config['paper_color'],
                                            plot_bgcolor=config['paper_color'],
                                            font_color="white" ))
    mock_plot.update_traces(marker_color=config['bg_color'])                            
    mock_plot.update_xaxes(nticks=20, showgrid=False, visible=False,  showticklabels=False, zeroline= False)
    mock_plot.update_yaxes(showgrid=False, showticklabels=False, visible=False, zeroline= False)
    return mock_plot


def counties_deaths_textbox():
        
    # Text box to asking user to select a state
    df= pd.DataFrame.from_dict({'x':[0], 'mock':[0]})
    mock_plot = px.scatter(df, y="mock")
    mock_plot.add_annotation(
        text="Select a County to display number of deaths per day",
        font=dict(size=20), 
        showarrow=False,
        xref="paper",
        yref="paper",
        x=0.55,
        y=0.4,

    )
    mock_plot.update_layout(dict(paper_bgcolor=config['paper_color'],
                                            plot_bgcolor=config['paper_color'],
                                            font_color="white" ))
    mock_plot.update_traces(marker_color=config['bg_color'])                            
    mock_plot.update_xaxes(nticks=20, showgrid=False, visible=False,  showticklabels=False, zeroline= False)
    mock_plot.update_yaxes(showgrid=False, showticklabels=False, visible=False, zeroline= False)
    return mock_plot





def date_filter(df, range_choice): 
    """
        Filter the input data in df by date choice. Date choice
        options are: week, month, three_months, six_months, all_time

    :param df: Entire dataset with all columns
    :type df: DataFrame
    :param range_choice: User selected date range choice
    :type range_choice: string
    :return: Return a filtered dataframe based on range_choice
    :rtype: DataFrame
    """
    # filter by date range
    # filter by week 
    dt_upper = df['dates_dt'].max()
    if range_choice == "week":   
        
        dt_lower  = dt_upper - datetime.timedelta(days=7)
        overall_range = df[(df['dates_dt']>= dt_lower) & (df['dates_dt']<= dt_upper)]

    elif range_choice == "month":
    # filter by last month
        dt_lower  = dt_upper - datetime.timedelta(weeks=4)
        overall_range = df[(df['dates_dt']>= dt_lower) & (df['dates_dt']<= dt_upper)]

    elif range_choice == "three_months":
    # Last three months
        three_months = pd.date_range(end=dt_upper, periods=3, freq='MS')
        dt_lower = three_months[0]
        overall_range = df[(df['dates_dt']>= dt_lower) & (df['dates_dt']<= dt_upper)]

    elif range_choice == "six_months":
    # Last six months
        six_months = pd.date_range(end=dt_upper, periods=6, freq='MS')
        dt_lower = six_months[0]
        overall_range = df[(df['dates_dt']>= dt_lower) & (df['dates_dt']<= dt_upper)]
    elif range_choice == "all_time": 
        overall_range = df 

    return overall_range



def date_radio(plot_name): 
    """
        Generate the RadioItem object for plots
    """
    id_dict= {'confirmed': 'cases-radio',
            'deaths': 'deaths-radio',
            'tested': 'tested-radio',
            'hosp': 'hosp-radio',
            'state_cases': 'states-cases-radio', 
            'state_deaths':'states-deaths-radio',
            'county_cases':'county-cases-radio', 
            'county_deaths':'county-deaths-radio'}

    radio_btn =  dbc.Container(
        [
            
            dbc.RadioItems(options=[{'label': "Last Week", 'value': 'week'}, 
                  {'label': "Last month", 'value': 'month'},
                  {'label': "Three months", 'value': 'three_months'},
                  {'label': "Six months", 'value': 'six_months'},
                  {'label': "All time", 'value': 'all_time'}], 
                
                labelClassName="date-group-labels-v2",
                labelCheckedClassName="date-group-labels-checked-v2",
                className="date-group-items",
                inline=True,
                value='week', 
                id=id_dict[plot_name], 
            ),
        
        ],
        className="p-3", id='fpage-radio-div'
    )


    return radio_btn

    


def confirmed_tabs(): 
    confirmed_div = html.Div([
                dcc.Tabs(id='confirmed_tabs',
                        value='tab-1',
                        children=[
                                
                                    dcc.Tab(label='Per-day', value='tab-1', style=tab_style, selected_style=tab_selected_style),
                                    dcc.Tab(label='Cumulative', value='tab-2', style=tab_style, selected_style=tab_selected_style),
                                ]),
                        
                dcc.Graph(id='pl1'),
                ],
                className=" plot ")

    return confirmed_div



def deaths_tabs():
    deaths_div = html.Div([
                            dcc.Tabs(id='deaths_tabs',
                                    value='tab-1',
                                    children=[
                                        dcc.Tab(label='Per-day', value='tab-1', style=tab_style, selected_style=tab_selected_style),
                                        dcc.Tab(label='Cumulative', value='tab-2', style=tab_style, selected_style=tab_selected_style),
                                    ]),
                            dcc.Graph(id='pl2')
                    
                    ],
                    className=" plot"),

    return deaths_div



def tested_tabs(): 

    tested_div = html.Div([dcc.Tabs(id='tested_tabs',
                     value='tab-1',
                     children=[
                        dcc.Tab(label='Per-day', value='tab-1', style=tab_style, selected_style=tab_selected_style),
                        dcc.Tab(label='Cumulative', value='tab-2', style=tab_style, selected_style=tab_selected_style),
                        ]),
            
            dcc.Graph(id='pl_tested'),
            ],
           className="plot")


    return tested_div


def hosp_tabs():
    hosp_div = html.Div([
    dcc.Tabs(id='hospitalized_tabs',
             value='tab-1',
             children=[
                        dcc.Tab(label='Per-day', value='tab-1', style=tab_style, selected_style=tab_selected_style),
                        dcc.Tab(label='Cumulative', value='tab-2', style=tab_style, selected_style=tab_selected_style),
                    ]),
    dcc.Graph(id='pl_hospitalized')
    ],
     className="plot")



    return hosp_div