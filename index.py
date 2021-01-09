import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from layouts import covid_layout, covid_layout_2, covid_layout_3
import callbacks
from app import server



app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
         return covid_layout
    elif pathname == '/covid-2':
         return covid_layout_2
    elif pathname == '/covid-3':
         return covid_layout_3
    else:
        return '404'

if __name__ == '__main__':
    app.run_server(debug=False)
