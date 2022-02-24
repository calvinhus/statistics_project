import dash
from dash import Dash, html, dcc
from dash.dependencies import Output, Input
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
from datetime import date
import plotly.express as px

data = pd.read_csv("data/ironhack_careers_clean.csv")

data["graduation_date"] = pd.to_datetime(
    data["graduation_date"], format="%Y-%m-%d")

data.sort_values("graduation_date", inplace=True)

searching = data.query(
    "status == 'Actively Seeking' or status == 'Passively Seeking'")

hired = data.query(
    "hired == 1")

# Start the application
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server
app.title = "Ironhack Student Dashboard"

# Card components
cards = [
    dbc.Card(
        [
            html.P("Total Students", className="card-text"),
            html.H2(f"{len(data)}",
                    className="card-title"),
            html.H6("100%", className="card-title",
                    style={'color': '#31BCF5'})
        ],
        body=True,
    ),
    dbc.Card(
        [
            html.P("Students Searching", className="card-text"),
            html.H2(f"{len(searching)}",
                    className="card-title", ),
            html.H6((f"{(len(searching) / len(data))*100:.2f}%"),
                    className="card-title", style={'color': '#31BCF5'})
        ],
        body=True,
    ),
    dbc.Card(
        [html.P("Students Hired", className="card-text"),
            html.H2(f"{len(hired)}",
                    className="card-title"),
         html.H6((f"{(len(hired) / len(data))*100:.2f}%"),
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
                    className="header-description",
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
                            options=[
                                {"label": curriculum, "value": curriculum}
                                for curriculum in np.sort(data.curriculum.unique())
                            ],
                            value="",
                            clearable=False,
                            className="dropdown",
                        ),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(children="Format", className="menu-title"),
                        dcc.Dropdown(
                            id="format-filter",
                            options=[
                                {"label": format, "value": format}
                                for format in np.sort(data.format.unique())],
                            value="",
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
                    className="card",
                ),
                html.Div(
                    children=dcc.Graph(
                        id="graph2",
                        config={"displayModeBar": False},
                    ),
                    className="card",
                ),
                html.Div(
                    children=dcc.Graph(
                        id="graph3",
                        config={"displayModeBar": False},
                    ),
                    className="card",
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
            "  🐍"
        ], className="footer"),
    ]
)


@app.callback(
    [Output("graph1", "figure"), Output(
        "graph2", "figure"), Output("graph3", "figure")],
    [Input('curriculum-filter', 'value'), Input('format-filter', 'value')])
def update_figure(year, month):
    # filtered_df = data[data.year == selected_year]

    filtered_df = data.groupby(['curriculum', 'cohort', 'month_year']).agg(
        {'conv_applied_interview': 'mean', 'conv_interview_hired': 'mean', 'index': 'count'}).reset_index()

    hired = data[data['hired'] == 1]
    hired_df = pd.DataFrame({
        "curriculum": [h for h in hired.curriculum],
        "count": [h for h in hired.hired]
    })
    fig1 = px.scatter(filtered_df, x="month_year",
                      y="conv_applied_interview", color="curriculum", size="index", size_max=30,
                      labels={
                          "conv_applied_interview": "Conversion",
                          "month_year": "Cohort Date",
                          "curriculum": "Curriculum"},
                      title="Applied to Interview Conversion")
    # color="curriculum", hover_name="cohort", size=
    # log_x=True, size_max=55)
    fig2 = px.scatter(filtered_df, x="month_year",
                      y="conv_interview_hired", color="curriculum", size="index", size_max=30,
                      labels={
                          "conv_interview_hired": "Conversion",
                          "month_year": "Cohort Date",
                          "curriculum": "Curriculum"},
                      title="Interview to Hired Conversion")

    fig3 = px.bar(hired_df, x="curriculum",
                  y="count", barmode="group", color="curriculum", title="Percentage of Students Hired",
                  labels={
                      "count": "Percentage",
                      "curriculum": "Curriculum"})

    fig1.update_layout(transition_duration=500)
    fig2.update_layout(transition_duration=500)
    fig3.update_layout(transition_duration=500)

    return fig1, fig2, fig3


if __name__ == "__main__":
    app.run_server(debug=True)
