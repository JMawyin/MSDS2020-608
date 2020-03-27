import os

import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go
from dash_table import DataTable
import dash_bootstrap_components as dbc


#from chart_studio.plotly import plot, iplot
import numpy as np
import plotly
#import chart_studio
#import chart_studio.plotly as py
#from chart_studio.plotly import iplot
import plotly.offline as offline
#chart_studio.tools.set_credentials_file(username='JMawyin', api_key='dVsYl2tiVcuatLpgjJjA')
shaz13_custom_style = "mapbox://styles/shaz13/cjiog1iqa1vkd2soeu5eocy4i"
Token = "pk.eyJ1Ijoiam1hd3lpbiIsImEiOiJjazg4OGp0NDYwMmdwM2dxcHUxNWRhYzZyIn0.MCCGSyF0KPdvun3rTob3dw"



external_stylesheets = [dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

external_css = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
for css in external_css:    app.css.append_css({"external_url": css})

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

trees_url = 'https://data.cityofnewyork.us/resource/nwxe-4ae8.json'
trees = pd.read_json(trees_url)
trees = trees.dropna()

def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])



df = pd.read_csv(
    'https://gist.githubusercontent.com/chriddyp/' +
    '5d1ea79569ed194d432e56108a04d188/raw/' +
    'a9f9e8076b837d541398e999dcbac2b2826a81f8/'+
    'gdp-life-exp-2007.csv')

intro = '''This board uses data collected from the TreesCount! 2015 Street Tree Census to showcase the health
of surveyed trees on the different boroughs of NYC. The complete dataset contains 684K tree observations. However, in our example, we will only use data from 5000 trees for the total number surveyed.
'''
markdown_text1 = '''
### Research Question 1:
##### What proportion of trees are in good, fair, or poor health according to the ‘health’ variable?
Select one of the 5 different NYC boroughs to populate the map. The color coding used uses 
Green:Good, Yellow:Fair and Red:Bad to indicate the three possible tree health states indicated in the survey.
'''

markdown_text1b = '''
We can see that the distribution of healthy and not so healthy trees are distributed evenly throughout the geographic 
boundaries of the boroughs.
Surprisingly, when selecting the borough of Manhattan, we do not see any trees surveyed in the Central Park area.
'''

markdown_text2 = '''
### Research Question 2:
##### Are stewards (steward activity measured by the ‘steward’ variable) having an impact on the health of trees?
'''

markdown_text2_1 = '''
We can clearly see from the different bar plots comparing the Health state of the surveyed trees, that the more steward indicators, the higher the proportion of healthy trees. This makes sense, as the more checkups on the ongoing state of a tree can correct for damages or events that would reduce the lifespan of the trees.
'''

markdown_final= '''
* Throughout this module I have learned:
    * How to work with Dash, Flask and Plotly.
    * Figured out how to align elements together in a row and not sequentially.
    * How to map datapoints from the NY Tree survey dataset and style them.
    * How to deploy the Dash app online using Heroku. Figuring it out took as long as writing the app itself.
    
* Things to be improved:
    * Aligment of objects.
    * Re-centering of map view.
    * More insightful metrics to track tree health.
'''


app.layout = html.Div(
    [
    html.H1('DATA 608 : Module 4 (Dash)', style={'backgroundColor':'black', 'color': 'white'}),
    html.H3('Jose A. Mawyin', style={'backgroundColor':'grey', 'color': 'white'}),
    dcc.Markdown(children=intro),    
    dcc.Markdown(children=markdown_text1), 
        
    html.Label('Select a borough Name to Filter for the map to populate: '),
    dcc.Dropdown(id='dropdown', options=[
        {'label': i, 'value': i} for i in trees.boroname.unique()
    ], value = 'Queens',multi=False, placeholder='Filter by boroname...'),
        
        
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id='map')),
                #dbc.Col(html.Div(id='table1'))
                dbc.Col([dbc.Row([html.Div([html.Br(), html.Br(), html.Br(), html.Br(), html.Br()])]),dbc.Row([html.Div(id='table1')])])
            ],justify="center"
        ),
    dcc.Markdown(children=markdown_text1b),
    html.P(markdown_text1b),    

    dcc.Markdown(children=markdown_text2),
    html.Label('Select a Stewardship level to Filter and for the plot to populate: '),
    dcc.Dropdown(id='steward_select', options=[
        {'label': i, 'value': i} for i in trees.steward.unique()
    ], value = 'None', multi=False, placeholder='Filter by Stewardship Level...'),
    #html.Div(id='table2'),
    dcc.Graph(id='bar'),
    dcc.Markdown(children=markdown_text2_1),
    dcc.Markdown(children=markdown_final),
    html.Div(style={'textAlign':'center'},children='''        Jose A. Mawyin 2020.    ''')
    ],style = {'width': '100%','padding-left':'10%', 'padding-right':'10%'}
)

#style = {'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}

@app.callback(
    dash.dependencies.Output('table1', 'children'),
    [dash.dependencies.Input('dropdown', 'value')])

def display_table(dropdown_value):

    soql_url = ('https://data.cityofnewyork.us/resource/nwxe-4ae8.json?' +\
        '$select=health,count(tree_id)' +\
        '&$where=boroname=\'' + dropdown_value + '\'' +\
        '&$group=health').replace(' ', '%20')
    soql_treesV2 = pd.read_json(soql_url)
    soql_treesV2 = soql_treesV2.rename(columns={"count_tree_id": "% of Trees", "health": "--Health State"})

    total_trees = soql_treesV2["% of Trees"].sum(axis=0)
    soql_treesV2["% of Trees"] = 100*soql_treesV2["% of Trees"]/total_trees
    soql_treesV2 = soql_treesV2.round(2)
    soql_treesV2 = soql_treesV2.dropna()
    return generate_table(soql_treesV2)


# Define a function to map the values
def set_value(row_number, assigned_value):
    return assigned_value[row_number]

@app.callback(
    dash.dependencies.Output('map', 'figure'),
    [dash.dependencies.Input('dropdown', 'value')])
def update_map(dropdown_value):
    url = 'https://data.cityofnewyork.us/resource/nwxe-4ae8.json?$limit=5000&$offset=0'
    trees = pd.read_json(url)
    trees = trees.dropna()

    # Create the dictionary
    event_dictionary ={'Fair' : 'Yellow', 'Good' : 'Green', 'Poor' : 'Red'}

    # Add a new column named 'Price'
    trees['Color'] = trees['health'].apply(set_value, args =(event_dictionary, ))
    trees.Color.head(10)
    trees_s = trees[trees['boroname'] == dropdown_value]

    datamap = go.Data([go.Scattermapbox(
    lat= trees_s['latitude'] ,
    lon= trees_s['longitude'],
    customdata = trees_s['health'],
    mode='markers',
    marker=dict(
    size= 6,
    color = trees_s['Color'] ,
    showscale=False,
    opacity = .8,
    ),
    )])

    layout = go.Layout(
    autosize=True,
    mapbox= dict(accesstoken=Token,
    bearing=10,
    pitch=70,
    zoom=11,
    center= dict(lat=40.721319,
    lon=-73.987130),
    style=shaz13_custom_style),
    width=900,
    height=600,
    title = "Surveyed Trees in New York (Green:Good, Yellow:Fair and Red:Bad Health ")

    fig = dict( data=datamap, layout=layout)

    #return iplot(fig)
    return {'data': datamap, 'layout': layout}

####Steward Callback and Table####

@app.callback(
    dash.dependencies.Output('bar', 'figure'),
    [dash.dependencies.Input('steward_select', 'value')])

def display_table(steward_select_value):

    soql_url = ('https://data.cityofnewyork.us/resource/nwxe-4ae8.json?' +\
        '$select=health,count(tree_id)' +\
        '&$where=steward=\'' + steward_select_value + '\'' +\
        '&$group=health').replace(' ', '%20')
    soql_treesV2 = pd.read_json(soql_url)
    soql_treesV2 = soql_treesV2.rename(columns={"count_tree_id": "% of Trees", "health": "--Health State"})

    total_trees = soql_treesV2["% of Trees"].sum(axis=0)
    soql_treesV2["% of Trees"] = 100*soql_treesV2["% of Trees"]/total_trees
    soql_treesV2 = soql_treesV2.round(2)
    soql_trees_steward = soql_treesV2.dropna()
    soql_trees_steward = soql_trees_steward.sort_values('--Health State',ascending=False)
################
# Define a function to map the values 
    def set_value(row_number, assigned_value): 
        return assigned_value[row_number] 
# Create the dictionary 
    event_dictionary ={'Fair' : 'Yellow', 'Good' : 'Green', 'Poor' : 'Red'} 
  
# Add a new column named 'Price' 
    soql_trees_steward['Color'] = soql_trees_steward['--Health State'].apply(set_value, args =(event_dictionary, ))
    soql_treesV2 = soql_treesV2.dropna()
    bardata = [go.Bar(
            y=soql_trees_steward['% of Trees'],
            x=soql_trees_steward['--Health State'],
            marker=dict(
            color=soql_trees_steward['Color'],
            line=dict(color='rgba(246, 78, 139, 1.0)', width=3))
            
    )]
    barlayout = go.Layout(
    width=900,
    height=600,
    title = "Effect of Stewardship on Tree Health Across NYC")
    
    return {'data': bardata, 'layout': barlayout}
    





if __name__ == '__main__':
    app.run_server()
    
#https://dash-bootstrap-components.opensource.faculty.ai/docs/components/layout/
#https://community.plotly.com/t/dash-bootstrap-components-grid-system-not-working/30957
#https://community.plotly.com/t/layout-using-dash-bootstrap-components/20692
#https://plotly.com/python/horizontal-bar-charts/