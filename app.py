import dash
from dash import Dash, html, dcc
from dash.dependencies import Output, Input
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np


#url = "https://raw.githubusercontent.com/realpython/materials/master/python-dash/additional_files/avocado.csv"
# data = pd.read_csv(url, index_col=0)
# data = data.query("type == 'conventional' and curriculum == 'Albany'")

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
            html.P("Students Searching", className="card-text"),
            html.H2(
                f"{len(searching)}/{len(data)}({(len(searching) / len(data))*100:.2f}%) ", className="card-title"),

        ],
        body=True,
    ),
    dbc.Card(
        [html.P("Students Hired", className="card-text"),
            html.H2(
                f"{len(hired)}/{len(data)} ({(len(hired) / len(data))*100:.2f}%) ", className="card-title"),

         ],
        body=True,
    ),
]


app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.P(children="🖥️", className="header-emoji"),
                html.H1(children="IronHack Analytics",
                        className="header-title"),
                # html.Img(src=app.get_asset_url("ih_logo.png"),
                #          style={"float": "top-left", "height": 150}),
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
        dbc.Row([dbc.Col(card) for card in cards]),
        html.Br(),
        html.Br(),
        html.Br(),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(children="curriculum",
                                 className="menu-title"),
                        dcc.Dropdown(
                            id="curriculum-filter",
                            options=[
                                {"label": curriculum, "value": curriculum}
                                for curriculum in np.sort(data.curriculum.unique())
                            ],
                            value="UXUI",
                            clearable=False,
                            className="dropdown",
                        ),
                    ]
                ),
                html.Div(
                    children=[
                        html.Div(children="Type", className="menu-title"),
                        dcc.Dropdown(
                            id="type-filter",
                            options=[
                                {"label": cohort, "value": cohort}
                                for cohort in data.cohort.unique()
                            ],
                            value="LIS-DATAFT-Oct2021",
                            clearable=False,
                            searchable=False,
                            className="dropdown",
                        ),
                    ],
                ),
                html.Div(
                    children=[
                        html.Div(
                            children="Date Range", className="menu-title"
                        ),
                        dcc.DatePickerRange(
                            id="date-range",
                            min_date_allowed=data.graduation_date.min().date(),
                            max_date_allowed=data.graduation_date.max().date(),
                            start_date=data.graduation_date.min().date(),
                            end_date=data.graduation_date.max().date(),
                        ),
                    ]
                ),
            ],
            className="menu",
        ),
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id="price-chart",
                        config={"displayModeBar": False},
                    ),
                    className="card",
                ),
                html.Div(
                    children=dcc.Graph(
                        id="volume-chart",
                        config={"displayModeBar": False},
                    ),
                    className="card",
                ),
            ],
            className="wrapper",
        ),
    ]
)


@app.callback(
    [Output("price-chart", "figure"), Output("volume-chart", "figure")],
    [
        Input("curriculum-filter", "value"),
        Input("type-filter", "value"),
        Input("date-range", "start_date"),
        Input("date-range", "end_date"),
    ],
)
def update_charts(curriculum, cohort, start_date, end_date):
    mask = (
        (data.curriculum == curriculum)
        & (data.cohort == cohort)
        & (data.graduation_date >= start_date)
        & (data.graduation_date <= end_date)
    )
    filtered_data = data.loc[mask, :]
    price_chart_figure = {
        "data": [
            {
                "x": filtered_data["graduation_date"],
                "y": filtered_data["cohort"],
                "type": "lines",
                "hovertemplate": "$%{y:.2f}<extra></extra>",
            },
        ],
        "layout": {
            "title": {
                "text": "Average Price of Avocados",
                "x": 0.05,
                "xanchor": "left",
            },
            "xaxis": {"fixedrange": True},
            "yaxis": {"tickprefix": "$", "fixedrange": True},
            "colorway": ["#17B897"],
        },
    }

    volume_chart_figure = {
        "data": [
            {
                "x": filtered_data["graduation_date"],
                "y": filtered_data["hired"],
                "type": "lines",
            },
        ],
        "layout": {
            "title": {"text": "Avocados Sold", "x": 0.05, "xanchor": "left"},
            "xaxis": {"fixedrange": True},
            "yaxis": {"fixedrange": True},
            "colorway": ["#E12D39"],
        },
    }
    return price_chart_figure, volume_chart_figure


if __name__ == "__main__":
    app.run_server(debug=True)
