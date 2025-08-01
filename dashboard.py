# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                             options = [{'label':'All Sites','value': 'ALL'},
                                                        {'label': 'CCAFS LC-40','value':'CCAFS LC-40'},
                                                        {'label': 'VAFB SLC-4E','value':'VAFB SLC-4E'},
                                                        {'label': 'KSC LC-39A','value':'KSC LC-39A'},
                                                        {'label': 'CCAFS SLC-40','value':'CCAFS SLC-40'}],
                                            value = 'ALL',
                                            placeholder = 'Select a Launch Site Here',
                                            searchable = True),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min = 0,max = 10000, step = 1000,
                                                marks = {0:'0',
                                                         2500 : '2500',
                                                         5000:'5000',
                                                         7500:'7500',
                                                         10000:'10000'},
                                                value = [0,10000]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart',component_property='figure'),
              Input(component_id='site-dropdown',component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        filtered_df = spacex_df[spacex_df["class"] == 1]
        site_counts = filtered_df["Launch Site"].value_counts().reset_index()
        site_counts.columns = "Launch Site",'Successful Launches:'
        fig = px.pie(site_counts,values='Successful Launches:',names='Launch Site',title='Successful launches by Launch Site')
        return fig
    else:
        filtered_df = spacex_df[spacex_df["Launch Site"] == entered_site]
        class_counts = filtered_df['class'].value_counts().reset_index()
        class_counts.columns = ['class', 'Launches']
        class_counts['class'] = class_counts['class'].map({1: 'Success', 0: 'Failure'})
        fig = px.pie(class_counts, 
                     values='Launches', 
                     names='class', 
                     title=f'Success vs Failure for {entered_site}')
        return fig
    
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    Input(component_id='payload-slider', component_property='value'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_scatter(payload_range, selected_site):
    min_, max_ = payload_range

    # Filter by payload range
    payload_filter = (spacex_df["Payload Mass (kg)"] >= min_) & (spacex_df["Payload Mass (kg)"] <= max_)

    if selected_site == "ALL":
        filtered_df = spacex_df[payload_filter]
    else:
        site_filter = spacex_df['Launch Site'] == selected_site
        filtered_df = spacex_df[payload_filter & site_filter]

    # Scatter plot
    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title=f"Payload vs Launch Success for {'All Sites' if selected_site == 'ALL' else selected_site}",
        labels={'class': 'Launch Outcome (1 = Success, 0 = Failure)'}
    )
    return fig


# Run the app
if __name__ == '__main__':
    app.run()
