from pydoc import classname
import dash
from dash import Dash, html, dcc
from dash.dependencies import Output, Input
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
from datetime import date
import plotly.express as px
import dataclean

# Read and clean data
df = pd.read_csv("data/ironhack_careers_clean.csv")
data = dataclean.clean(df)

# Start the application
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
app.title = "Ironhack Student Dashboard"

# Card components
cards = [
    dbc.Card(
        [
            html.P("Total Students", className="card-text"),
            html.H2(id='total-students', className="card-title"),
            html.H6(id='total-students-percent', className="card-title",
                    style={'color': '#31BCF5'})
        ],
        body=True,
    ),
    dbc.Card(
        [
            html.P("Students Searching", className="card-text"),
            html.H2(id='total-students-searching',
                    className="card-title", ),
            html.H6(id='total-students-searching-prcnt',
                    className="card-title", style={'color': '#31BCF5'})
        ],
        body=True,
    ),
    dbc.Card(
        [html.P("Students Hired", className="card-text"),
            html.H2(id='total-hired',
                    className="card-title"),
         html.H6(id='total-hired-prcnt',
                 className="card-title", style={'color': '#31BCF5'})
         ],
        body=True,
    ),
]

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.P(children="🖥️", className="header-emoji"),
                html.H1(children="Ironhack Analytics",
                        className="header-title"),
                html.P(
                    children="Analyze the time to job of"
                    " Ironhack Students in Lisbon"
                    " since March 2020",
                    className="header-description", style={'color': 'black'},
                ),
            ],
            className="header",
        ),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="Curriculum",
                                 className="menu-title"),
                        dcc.Dropdown(
                            id="curriculum-filter",
                            options=[{'label': 'All', 'value': 'all_values'}] + [
                                {'label': x, 'value': x} for x in np.sort(data.curriculum.unique())],
                            value='all_values',
                            clearable=False,
                            className="dropdown"
                        ),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(children="Format", className="menu-title"),
                        dcc.Dropdown(
                            id="format-filter",
                            options=[{'label': 'All', 'value': 'all_format'}] + [
                                {'label': x, 'value': x} for x in np.sort(data.format.unique())],
                            value='all_format',
                            clearable=False,
                            className="dropdown",
                        ),
                    ]
                ),
            ],
            className="menu",
        ),
        html.Br(),
        dbc.Row([dbc.Col(card) for card in cards]),
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id="graph1",
                        config={"displayModeBar": False},
                    ),
                    className="graph",
                ),
                html.Div(
                    children=dcc.Graph(
                        id="graph2",
                        config={"displayModeBar": False},
                    ),
                    className="graph",
                ),
                html.Div(
                    children=dcc.Graph(
                        id="graph3",
                        config={"displayModeBar": False},
                    ),
                    className="graph",
                ),
            ],
            className="wrapper",
        ),
        html.Hr(),
        html.P(children=[
            f"© {date.today().year} ",
            html.A("Ironhack", href="https://www.ironhack.com/en"),
            " Student Dashboard powered by ",
            html.A("Python", href="https://www.python.org"),
            " and ",
            html.A("Dash", href="https://plotly.com/dash/"),
            ". Developed with 💙 by ",
            html.A("Gonçalo Calvinho", href="https://github.com/calvinhus"),
            "  🐍",
            " and ",
            html.A("Ana Matias", href="https://github.com/ana17mat"),
            " 🐯"
        ], className="footer"),
    ]
)


@ app.callback(
    [
        Output("graph1", "figure"),
        Output("graph2", "figure"),
        Output("graph3", "figure"),
        Output('total-students', 'children'),
        Output('total-students-percent', 'children'),
        Output('total-students-searching', 'children'),
        Output('total-students-searching-prcnt', 'children'),
        Output('total-hired', 'children'),
        Output('total-hired-prcnt', 'children')
    ],
    [
        Input('curriculum-filter', 'value'),
        Input('format-filter', 'value')
    ]
)
def update_figure(curriculum, format):

    filtered = data.groupby(['curriculum', 'cohort', 'format', 'graduation_date', 'month_year']).agg(
        {'conv_applied_interview_prcnt': 'mean', 'conv_interview_hired_prcnt': 'mean', 'index': 'count'}).sort_values(by='graduation_date', ascending=True).reset_index()

    hired = data[data['hired'] == 1].groupby(['curriculum', 'graduation_date']).agg(
        {'hired': 'count'}).reset_index()

    searching = data[(data.status == 'Actively Seeking') |
                     (data.status == 'Passively Seeking')]

    total_hired = data[data['hired'] == 1]

    total_mask = ((filtered.curriculum == curriculum)
                  & (filtered.format == format))

    # Filters:
    if curriculum == 'all_values' and format == 'all_format':
        filtered = filtered
        total_students_filter = len(data)
        total_students_searching = len(searching)
        total_hired = len(total_hired)
    elif curriculum == 'all_values' and format != 'all_format':
        mask2 = (data.format == format)
        filtered = filtered.loc[(filtered.format == format), :]
        total_students_filter = len(data.loc[mask2, :])
        total_students_searching = len(searching.loc[mask2, :])
        total_hired = len(total_hired.loc[mask2, :])
    elif curriculum != 'all_values' and format == 'all_format':
        mask3 = (data.curriculum == curriculum)
        filtered = filtered.loc[(filtered.curriculum == curriculum), :]
        total_students_filter = len(data.loc[mask3, :])
        total_students_searching = len(searching.loc[mask3, :])
        total_hired = len(total_hired.loc[mask3, :])
    else:
        mask4 = ((data.format == format) & (data.curriculum == curriculum))
        filtered = filtered.loc[total_mask, :]
        total_students_filter = len(data.loc[mask4, :])
        total_students_searching = len(searching.loc[mask4, :])
        total_hired = len(total_hired.loc[mask4, :])

    # Graphs:
    fig1 = px.scatter(filtered, x="month_year",
                      y="conv_applied_interview_prcnt", color="curriculum", size="index", size_max=30,
                      labels={
                          "conv_applied_interview_prcnt": "Conversion (%)",
                          "month_year": "Cohort Date",
                          "curriculum": "Curriculum",
                          "index": "Total Students"},
                      title="Applied to Interview Conversion")

    fig2 = px.scatter(filtered, x="month_year",
                      y="conv_interview_hired_prcnt", color="curriculum", size="index", size_max=30,
                      labels={
                          "conv_interview_hired_prcnt": "Conversion (%)",
                          "month_year": "Cohort Date",
                          "curriculum": "Curriculum",
                          "index": "Total Students"},
                      title="Interview to Hired Conversion")

    fig3 = px.bar(hired, x="curriculum",
                  y="hired", barmode="group", color="curriculum", title="Percentage of Students Hired",
                  labels={
                      "hired": "Percentage",
                      "curriculum": "Curriculum"})

    fig1.update_layout(transition_duration=500)
    fig2.update_layout(transition_duration=500)
    fig3.update_layout(transition_duration=500)

    # Kpi's:
    total_students_percent = f"{total_students_filter/(len(data))*100:.2f}%"
    total_students_searching_percent = f"{total_students_searching/(len(data))*100:.2f}%"
    total_hired_percent = f"{total_hired/(len(data))*100:.2f}%"

    return fig1, fig2, fig3, \
        total_students_filter, total_students_percent, \
        total_students_searching, total_students_searching_percent, \
        total_hired, total_hired_percent


if __name__ == "__main__":
    app.run_server(debug=False)
