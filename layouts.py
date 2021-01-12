
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import us 
import plotly.graph_objects as go
import plotly.express as px
import dash_bootstrap_components as dbc
import yaml 
import utils as ut

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


nav_page1 = dbc.Nav(
    [
        dbc.NavItem(dbc.NavLink('Page 2: COVID-19 State by State', href='/covid-2', className='nav')),
        dbc.NavItem(dbc.NavLink("Page 3: References", href='/covid-3',className='nav')),
    ],
    fill=True, justified=True, horizontal="center"
)

nav_page2 = dbc.Nav(
    [
        dbc.NavItem(dbc.NavLink('Go to homepage', href='/', className='nav')),
        dbc.NavItem(dbc.NavLink("Page 3: References", href='/covid-3',className='nav')),
    ],
    fill=True, justified=True, horizontal="center"
)

nav_page3 = dbc.Nav(
    [
        dbc.NavItem(dbc.NavLink('Go to homepage', href='/', className='nav')),
        dbc.NavItem(dbc.NavLink('Page 2: COVID-19 State by State', href='/covid-2', className='nav')),
    ],
    fill=True, justified=True, horizontal="center"
)

################ PAGE 1 LAYOUT ################ 
covid_layout = html.Div([
    html.Div(id="hidden-get-data"),
    html.Br(), 
    html.Div([nav_page1]),
    
    html.Div([html.H1("Covid-19 Dashboard For The United States")], style={"text-align":"center",
                                                     "border":"5px black", 
                                                    #  "background-color":"#5569F1", 
                                                     "border-radius":"25px", 
                                                     "color":"white",
                                                     "font-weight":"bold"
                                                     }), 
    # Refresh data 
    html.Div([
              dcc.Interval(
                    id='get_data',
                    interval=5000*1000, # in milliseconds
                    n_intervals=0
                    ),
            html.H3(id='show-data') ],
                    id="load-data", 
                    style={'display': 'none'}),   


    html.Br(),
    html.Br(),
   
    html.Div(ut.below_title(), style={'text-align':'justify'}),

    
    html.Br(),
    html.Br(),

    html.Div(id='app-1-display-value'),
    
    html.Br(),

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
                                          
                                            html.Div(id="cases-count"),
                                            html.Div(id="cases-increase")
                            
                        ], className="six columns"),

                            html.Div([ 
                                html.Div(id="deaths-count"),
                                html.Div(id="death-increase")
                            ], className="six columns"),
                            ], className="summ1-row"), 
                            
                            html.Div([
                                html.Div([
                                    html.Div(id="tested-count"), 
                                    html.Div(id="tested-increase")
                                ], className="six columns"),
                                
                            html.Div([ 
                                html.Div(id="hospitalized-count"), 
                                html.Div(id="hospitalized-increase")
                            ], className="six columns"),

                        ], className="summ2-row")
                ]), 

    ], style={"padding-bottom":"60px",
                    "border":"2px outset black", 
                    "background-color":"#09051fea", 
                    "border-radius":"25px",
                    "border-color":"white",
                    "color":"white", 
                    "height":"300px",
                    "text-align":"center"}), 
    html.Br(),
    html.Br(),

    html.Div([html.H4("Covid-19 plots")]),
    html.Div([ut.page1_plots_text()]),

    html.Br(),
    html.Br(),

    ## Daily number of cases and deaths plot
    # Daily number of cases plot
    
    html.Div([
            dbc.Row(
                [
                dbc.Col(
                        html.Div([ut.date_radio('confirmed')], id='cases-radio-div'),
                ), 
                dbc.Col(            
                        html.Div([ut.date_radio('deaths')], id='deaths-radio-div'),    
                    ), 
                ],
            justify='start'),
            dbc.Row(
                [
                    dbc.Col( 
                              ut.confirmed_tabs(), 
                         width={"size": 5, "order":1}),


                dbc.Col(
                        ut.deaths_tabs(),
                     width={"size": 5, "order":2, "offset":1},)

                ], justify='center')     
            
    ]), 

        

   ## Daily number of tested and hospitalized plot
   # Daily number of Tested plot 
    
    html.Div([
            dbc.Row(
                [
                dbc.Col(
                        html.Div([ut.date_radio('tested')], id='tested-radio-div'),
                ), 
                dbc.Col(            
                        html.Div([ut.date_radio('hosp')], id='hosp-radio-div'),    
                    ), 
                ],
            justify='start'),
            dbc.Row(
                [
                    dbc.Col( 
                                ut.tested_tabs(), 
                         width={"size": 5, "order":1},),


                    dbc.Col(
                                ut.hosp_tabs(),
                     width={"size": 5, "order":2, "offset":1},)

                ], justify='center')     
            
    ]), 

        

        

    
    html.Br(),
    html.Div([ut.footer_text()], style={'display':'inline-block'})

])


################ PAGE 2 LAYOUT ################ 


covid_layout_2  = html.Div([
     
     # Refresh interval
     dcc.Interval(
                    id='page2-refresh',
                    interval=500*1000, # in milliseconds
                    n_intervals=0
                    ),

    html.Br(),

    html.Div(nav_page2),

    # Link to Homepage
    html.Div(id='app-1-display-value'),
    # Page title
    html.Div([html.H2("COVID-19: State by State" )]),
    
    html.Br(), 
    
    html.Div(ut.page2_below_title()), 
    
    html.Br(),
   
    html.Div(dbc.Row(
     
    dbc.Container(
    [
        
        dbc.RadioItems(options=[
                        {'value':'positive', 'label': 'Number of Infections'},
                        {'value':'death', 'label': 'Number of Deaths'}, 
                        {'value': 'totalTestResults', 'label': 'Number of people tested'},
                     ], 
            
            labelClassName="date-group-labels",
            labelCheckedClassName="date-group-labels-checked",
            className="date-group-items",
            inline=True,
            value='positive', 
            id='us-choro-radio', 
        ),
       
    ],
    className="p-3", id='us-radio-div'
)), className='three columns',  style={'display': 'block', 'width': '50%', 'margin-left': '10%','margin-right': 'auto'}),

    html.Br(),
    html.Br(),
    # US map choropleth 
    html.Div([html.H4("Hover on each state to see cumulative number of infections, deaths or people tested")], 
                         style={'display': 'block', 'width': '50%', 'margin-left': '10%','margin-right': 'auto'}),
    
   
   


    ## State cases and Deaths plots 
    html.Div([
        dbc.Row([
            dbc.Col(html.H6("Choose a State:"), width={"size":1, "order":1, "offset":1}, xs=1, align='end'),
            dbc.Col(ut.states_dropdown(), width={"size":3, "order":2}, lg=3 , align='start')     
        ], justify='center'),

        dbc.Row(
            [
            html.Div([dcc.Graph(id="main-choro")],
                        style={'width': '90%',
                                'display': 'inline'}, 
                                className="six columns plot"),  
            ]), 
        dbc.Row(
                [
                dbc.Col(
                        html.Div([ut.date_radio('state_cases')], id='scases-radio-div'),
                ), 
                dbc.Col(            
                        html.Div([ut.date_radio('state_deaths')], id='sdeaths-radio-div'),    
                    ), 
                ],
             justify='start'),

     dbc.Row(
                [
                    dbc.Col( 
                            html.Div([dcc.Graph(id="pl3")], className='plot'),
                          width={"size": 5, "order":1}),


                    dbc.Col(
                           html.Div( dcc.Graph(id="pl4"), className='plot'),
                    width={"size": 5, "order":2, "offset":1} )

                ], justify="center")     

    ]),
    html.Br(),
    html.Br(),
    # width={"size":3, "order":1, "offset":0}  width={"size":1, "order":2}
# Layout for county level choropleth and the accompanying figures  
html.Div([

        dbc.Row([html.Div([html.H4("Click on a state get a county level map")], 
                         style={'display': 'block', 'width': '50%', 'margin-left': '10%','margin-right': 'auto'}),
                ]), 
        html.Br(),
        html.Br(), 
        dbc.Row( [ 
            
            dbc.Col(html.H6("Choose a County:"), width={"size":1, "order":1, "offset":1}, xs=1, align='end'),

            dbc.Col(html.Div(id='counties-dropdown-div'), width={"size":3, "order":2}, lg=3 , align='start')], justify='center'), 
        dbc.Row(
            [
            html.Div([dcc.Graph(id="state-choro", figure=ut.counties_textbox())],
                        style={'width': '90%',
                                'display': 'inline'}, 
                                className="six columns plot colorbar-plot"),
            ], justify='center'), 
        dbc.Row([ html.Div([html.H4("Click on a county to get plots about number of infections and deaths per day ")], 
                         style={'display': 'block', 'width': '50%', 'margin-left': '10%','margin-right': 'auto'}),
                ]), 

        
        dbc.Row(
                [
                dbc.Col(
                        html.Div([ut.date_radio('county_cases')], id='scases-radio-div'),
                ), 
                dbc.Col(            
                        html.Div([ut.date_radio('county_deaths')], id='sdeaths-radio-div'),    
                    ), 
                ],
             justify='start'),


     dbc.Row(
                [
                    dbc.Col( 
                            html.Div([dcc.Graph(id='county-cases', 
                            figure=ut.counties_cases_textbox())],
                 className='county-cases plot'),
                          width={"size": 5, "order":1}),


                    dbc.Col(
                         html.Div([dcc.Graph(id='county-deaths',
                            figure=ut.counties_deaths_textbox())],
                 className='county-deaths plot'),
                    width={"size": 5, "order":2, "offset":1} )

                ], justify="center")     

    ]),

])



################ PAGE 3 LAYOUT ################ 



covid_layout_3  = html.Div([
    html.Br(),     
    html.Div(nav_page3),
    html.Br(), 
    html.Div([html.H1("References")], style={"text-align":"center",
                                                     "border":"5px black",  
                                                     "border-radius":"25px", 
                                                     "color":"white",
                                                     "font-weight":"bold"
                                                     }), 

    html.Br(),
    html.H2('Data Sources'), 

    html.Div([
                    html.Ul([
                        html.H5(html.Li(["""Main states data from: COVID Tracking project: """, html.A('https://covidtracking.com/data', href='https://covidtracking.com/data')])), 
                        html.H5(html.Li(["""County data from John Hopkins COVID database: """, html.A('https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data', href='https://github.com/CSSEGISandData/COVID-19/tree/master/csse_covid_19_data') ])), 
                        html.H5(html.Li(["""List of Geographic State Centers CSV: """, html.A('https://developers.google.com/public-data/docs/canonical/states_csv', href='https://developers.google.com/public-data/docs/canonical/states_csv')]))
                        ])

             ]),

    html.Br(),
    html.Br(),
    html.Br(),
    
    html.H4(html.Div("Dashboard by Pawan Nandakishore")),
    html.H5(html.Div(["LinkedIn: ", html.A("Pawan Nandakishore Ph.D" ,href='https://www.linkedin.com/in/pawan-nandakishore/')])), 
      
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),
    html.Br(),


])   
