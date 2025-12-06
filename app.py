import dash
from dash import html, dcc, Dash, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import dash_ag_grid as dag

# ---------- Load Data ----------
df = pd.read_excel("DMD.xlsx")

# Fix date formatting (YYYYMMDD → datetime)
df["Date"] = pd.to_datetime(
    df["Date"].astype(str).str.zfill(8),
    format="%Y%m%d",
    errors="coerce"
)
df["Year"] = df["Date"].dt.year
df["Month"] = df["Date"].dt.month

# ---------- Global Consistent Color Coding ----------
unique_types = sorted(df["Type"].dropna().unique())
base_colors = px.colors.qualitative.Dark24

color_map = {
    beer_type: base_colors[i % len(base_colors)]
    for i, beer_type in enumerate(unique_types)
}

# ---------- Dash App ----------
app = Dash(
    __name__,
    use_pages=False,
    external_stylesheets=[dbc.themes.CYBORG],
    title="DMD: Food & Beer Club Dashboard",
    suppress_callback_exceptions=True
)

# ---------- Layout ----------
app.layout = html.Div([

    # ---------- Splash Screen Layer ----------
    html.Div(
        id="splash-screen",
        children=[
            html.Img(
                id="splash-logo",
                src="/assets/dmd_logo.png",
            )
        ]
    ),

    # ---------- Main Application ----------
    dbc.Container(
        id="main-content",
        fluid=True,
        children=[

            # Header Row
            dbc.Row(
                [
                    dbc.Col(
                        html.Div(
                            [
                                html.Img(
                                    src="/assets/dmd_logo.png",
                                    style={"height": "120px", "margin-right": "20px"},
                                ),
                            ],
                            style={"display": "flex", "justify-content": "center"},
                        ),
                        width=2,
                    ),
                    dbc.Col(
                        html.H1(
                            "🍺 DMD — Food & Beer Club Dashboard",
                            className="text-center",
                            style={"margin-top": "30px", "font-weight": "bold"},
                        ),
                        width=10,
                    ),
                ],
                align="center",
            ),

            html.Hr(),

            # ---------- YEAR FILTER ----------
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.Label("Filter by Year:", style={"font-weight": "bold"}),
                            dcc.Dropdown(
                                id="year-filter",
                                options=[
                                    {"label": y, "value": y}
                                    for y in sorted(df["Year"].dropna().unique())
                                ],
                                value=[],
                                multi=True,
                                placeholder="Select one or more years...",
                                style={"color": "black"},
                            ),
                        ],
                        width=4,
                    )
                ],
                style={"margin-bottom": "20px"},
            ),

            # ---------- Tabs ----------
            dbc.Tabs(
                [
                    dbc.Tab(label="📊 Dashboard Overview", tab_id="dashboard"),
                    dbc.Tab(label="📋 Full Beer Database", tab_id="table"),
                    dbc.Tab(label="📈 Analytics", tab_id="analytics"),
                    dbc.Tab(label="📝 Notes Overview", tab_id="notes"),
                ],
                id="tabs",
                active_tab="dashboard",
            ),

            html.Br(),
            html.Div(id="tab-content", children=[]),
        ],
    )
])


# ---------- Tab Content Callback ----------
@app.callback(
    Output("tab-content", "children"),
    Input("tabs", "active_tab"),
    Input("year-filter", "value"),
)
def render_tab_content(active_tab, selected_years):

    # -------- FILTER DATAFRAME --------
    if selected_years:
        dff = df[df["Year"].isin(selected_years)]
    else:
        dff = df.copy()

    # ---------- Chart Function (with unified colors) ----------
    def ranked_chart(column, title):
        dff_sorted = dff.sort_values(column, ascending=False).head(15)

        fig = px.bar(
            dff_sorted,
            x="Navn",
            y=column,
            color="Type",
            color_discrete_map=color_map,
            title=title,
            text=column,
            template="plotly_dark",
        )

        # Force Plotly to respect sort order
        fig.update_layout(
            xaxis={"categoryorder": "array", "categoryarray": dff_sorted["Navn"].tolist()}
        )

        return fig

    # ---------- Dashboard Charts ----------
    fig_top_beers = ranked_chart("Total", "Top Rated Beers")
    fig_funk = ranked_chart("Funk (0-5)", "Ranking by Funk")
    fig_design = ranked_chart("Design (0-5)", "Ranking by Design")
    fig_worth = ranked_chart("Worth (0-10)", "Ranking by Worth")
    fig_value4coin = ranked_chart("Value4Coin (0-10)", "Ranking by Value4Coin")
    fig_flavour = ranked_chart("Flavour (0-10)", "Ranking by Flavour Score")
    fig_total = ranked_chart("Total", "Overall Total Score Ranking")

    # Flavour distribution
    fig_flavour_dist = px.box(
        dff[dff['Type'].isin(dff['Type'].value_counts()[lambda x: x >= 3].index)],
        x="Type",
        y="Flavour (0-10)",
        color="Type",
        color_discrete_map=color_map,
        title="Flavour Score Distribution by Type",
        template="plotly_dark",
    )

    # ---------- Notes Table ----------
    df_notes = dff[dff["Note"].notna() & (dff["Note"].astype(str).str.strip() != "")]
    df_notes_grouped = (
        df_notes.groupby("Date")
        .agg({"Note": "first", "Navn": lambda x: ", ".join(sorted(x))})
        .reset_index()
    )

    if not df_notes_grouped.empty:
        df_notes_grouped["Date"] = df_notes_grouped["Date"].dt.strftime("%Y-%m-%d")

    df_notes_grouped.rename(columns={"Navn": "Beers"}, inplace=True)

    # ---------- Render Tabs ----------
    # Dashboard
    if active_tab == "dashboard":
        return dbc.Container(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            dbc.Card(
                                dbc.CardBody([dcc.Graph(figure=fig_top_beers)]),
                                style={"background-color": "#111"},
                            ),
                            width=6,
                        ),
                        dbc.Col(
                            dbc.Card(
                                dbc.CardBody([dcc.Graph(figure=fig_flavour_dist)]),
                                style={"background-color": "#111"},
                            ),
                            width=6,
                        ),
                    ]
                ),

                html.Br(),

                dbc.Row(
                    [
                        dbc.Col(dbc.Card(dbc.CardBody([dcc.Graph(figure=fig_funk)]), style={"background-color": "#111"}), width=6),
                        dbc.Col(dbc.Card(dbc.CardBody([dcc.Graph(figure=fig_design)]), style={"background-color": "#111"}), width=6),
                    ]
                ),

                html.Br(),

                dbc.Row(
                    [
                        dbc.Col(dbc.Card(dbc.CardBody([dcc.Graph(figure=fig_worth)]), style={"background-color": "#111"}), width=6),
                        dbc.Col(dbc.Card(dbc.CardBody([dcc.Graph(figure=fig_value4coin)]), style={"background-color": "#111"}), width=6),
                    ]
                ),

                html.Br(),

                dbc.Row(
                    [
                        dbc.Col(dbc.Card(dbc.CardBody([dcc.Graph(figure=fig_flavour)]), style={"background-color": "#111"}), width=6),
                        dbc.Col(dbc.Card(dbc.CardBody([dcc.Graph(figure=fig_total)]), style={"background-color": "#111"}), width=6),
                    ]
                ),
            ],
            fluid=True,
        )

    # Full Database Table
    if active_tab == "table":
        return html.Div(
            [
                html.H3("📋 Beer Database"),
                dag.AgGrid(
                    rowData=dff.to_dict("records"),
                    columnDefs=[{"field": col} for col in dff.columns],
                    defaultColDef={"filter": True, "sortable": True, "resizable": True},
                    className="ag-theme-alpine-dark",
                    style={"height": "700px", "width": "100%"},
                ),
            ]
        )

    # Analytics
    if active_tab == "analytics":

        # ========== 1. RADAR: AVERAGE SCORES OVERALL ==========
        radar_df = pd.DataFrame({
            "Metric": ["Flavour", "Funk", "Design", "Worth", "Value4Coin"],
            "Score": [
                dff["Flavour (0-10)"].mean(),
                dff["Funk (0-5)"].mean(),
                dff["Design (0-5)"].mean(),
                dff["Worth (0-10)"].mean(),
                dff["Value4Coin (0-10)"].mean(),
            ]
        })

        fig_radar = px.line_polar(
            radar_df,
            r="Score",
            theta="Metric",
            line_close=True,
            title="Overall Rating Profile (Radar Chart)",
            template="plotly_dark"
        )
        fig_radar.update_traces(fill="toself")

        # ========== 2. RADAR: BY BEER TYPE ==========
        type_means = (
            dff.groupby("Type")[["Flavour (0-10)", "Funk (0-5)", "Design (0-5)",
                                 "Worth (0-10)", "Value4Coin (0-10)"]]
            .mean()
            .reset_index()
        )

        fig_radar_types = px.line_polar(
            type_means.melt(id_vars="Type", var_name="Metric", value_name="Score"),
            r="Score",
            theta="Metric",
            color="Type",
            title="Beer Type Comparison (Radar Chart)",
            template="plotly_dark",
            color_discrete_map=color_map
        )
        fig_radar_types.update_traces(fill=None)

        # ========== 3. CORRELATION HEATMAP ==========
        corr = dff[[
            "Flavour (0-10)", "Funk (0-5)", "Design (0-5)",
            "Worth (0-10)", "Value4Coin (0-10)",
        ]].corr()

        fig_corr = px.imshow(
            corr,
            text_auto=True,
            title="Correlation Between Rating Dimensions",
            color_continuous_scale="Plasma",
            template="plotly_dark",
        )

        # ========== 4. SCATTER MATRIX (PAIRPLOT) ==========
        fig_matrix = px.scatter_matrix(
            dff,
            dimensions=[
                "Flavour (0-10)", "Funk (0-5)", "Worth (0-10)",
                "Value4Coin (0-10)"
            ],
            color="Type",
            color_discrete_map=color_map,
            title="Relationship Between Rating Dimensions (Scatter Matrix)",
            template="plotly_dark",
        )

        # ========== 5. TOP BREWERIES ==========
        brewery_scores = (
            dff.groupby("Bryghus")["Total"]
            .mean()
            .sort_values(ascending=False)
            .head(12)
            .reset_index()
        )

        fig_breweries = px.bar(
            brewery_scores,
            x="Bryghus",
            y="Total",
            title="Top Breweries by Average Total Score",
            text="Total",
            template="plotly_dark",
        )

        # ========== 6. BEER TYPE COUNTS + AVERAGE ==========
        type_stats = (
            dff.groupby("Type")[["Total"]]
            .agg(["count", "mean"])
            .reset_index()
        )
        type_stats.columns = ["Type", "Count", "AvgTotal"]

        fig_type_count = px.bar(
            type_stats,
            x="Type",
            y="Count",
            title="How Many Beers Per Type?",
            template="plotly_dark",
        )

        fig_type_avg = px.bar(
            type_stats,
            x="Type",
            y="AvgTotal",
            title="Average Total Score by Beer Type",
            template="plotly_dark",
        )

        # ========== RETURN LAYOUT ==========
        return dbc.Container([
            
            # Row 1: Radar Charts
            dbc.Row([
                dbc.Col(dbc.Card(dbc.CardBody([dcc.Graph(figure=fig_radar)]), style={"background-color": "#111"}), width=6),
                dbc.Col(dbc.Card(dbc.CardBody([dcc.Graph(figure=fig_radar_types)]), style={"background-color": "#111"}), width=6),
            ]),
            html.Br(),

            # Row 2: Correlation + Scatter Matrix
            dbc.Row([
                dbc.Col(dbc.Card(dbc.CardBody([dcc.Graph(figure=fig_corr)]), style={"background-color": "#111"}), width=4),
                dbc.Col(dbc.Card(dbc.CardBody([dcc.Graph(figure=fig_matrix)]), style={"background-color": "#111"}), width=8),
            ]),
            html.Br(),

            # Row 3: Top Breweries
            dbc.Row([
                dbc.Col(dbc.Card(dbc.CardBody([dcc.Graph(figure=fig_breweries)]), style={"background-color": "#111"}), width=12),
            ]),
            html.Br(),

            # Row 4: Beer Type Stats
            dbc.Row([
                dbc.Col(dbc.Card(dbc.CardBody([dcc.Graph(figure=fig_type_count)]), style={"background-color": "#111"}), width=6),
                dbc.Col(dbc.Card(dbc.CardBody([dcc.Graph(figure=fig_type_avg)]), style={"background-color": "#111"}), width=6),
            ]),
        ], fluid=True)


    # Notes
    if active_tab == "notes":
        return html.Div(
            [
                html.H3("📝 Notes Overview"),
                dag.AgGrid(
                    rowData=df_notes_grouped.to_dict("records"),
                    columnDefs=[
                        {"field": "Date", "sortable": True},
                        {"field": "Note", "wrapText": True, "autoHeight": True},
                        {"field": "Beers", "wrapText": True, "autoHeight": True},
                    ],
                    defaultColDef={"filter": True, "sortable": True, "resizable": True},
                    className="ag-theme-alpine-dark",
                    style={"height": "600px", "width": "100%"},
                ),
            ]
        )


# ---------- Run ----------
if __name__ == "__main__":
    app.run(debug=True)
