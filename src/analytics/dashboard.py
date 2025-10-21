import re
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
from dash import Dash, Input, Output, dcc, html

# Load data from CSV

data_path = Path(__file__).parent.parent.parent.parent / "output.csv"
CSV_PATH = Path(data_path)


# ---------------------------
# Utilities
# ---------------------------
def num_from_str(s):
    """Extract a numeric value from strings like '1,950 mV', '182 m2.g', '210', etc."""
    if pd.isna(s):
        return np.nan
    s = str(s)
    token = s.split()[0].split(",")[0]
    try:
        return float(token)
    except ValueError:
        m = re.search(r"(\d+\.?\d*)", s)
        return float(m.group(1)) if m else np.nan


def prepare_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Normalize metal_count
    if "metal_count" in df.columns:
        df.loc[
            df["metal_count"].str.contains("single", case=False, na=False),
            "metal_count",
        ] = "single"
        df.loc[
            df["metal_count"].str.contains("bimetallic", case=False, na=False),
            "metal_count",
        ] = "binary"

    # Numeric cleaning
    if "BET_surface_area_m2_per_g" in df.columns:
        df["BET_surface_area_m2_per_g"] = df["BET_surface_area_m2_per_g"].map(
            num_from_str
        )
    if "tafel_mV_per_dec" in df.columns:
        df["tafel_mV_per_dec"] = df["tafel_mV_per_dec"].map(num_from_str)
    if "stability_time_hours" in df.columns:
        df["stability_time_hours"] = pd.to_numeric(
            df["stability_time_hours"], errors="coerce"
        )
    if "overpotential_mV_at_10mAcm2" in df.columns:
        df["overpotential_mV_at_10mAcm2"] = df["overpotential_mV_at_10mAcm2"].map(
            num_from_str
        )

    # Metal types → list
    if "metal_types" in df.columns:
        df["metal_types_list"] = (
            df["metal_types"]
            .fillna("")
            .astype(str)
            .apply(lambda s: [t.strip() for t in s.split(",") if t.strip()])
        )

    return df


def pie_counts(df_counts, names_col, values_col, title, donut=False):
    if df_counts.empty:
        return px.pie(title=title)
    fig = px.pie(
        df_counts,
        names=names_col,
        values=values_col,
        title=title,
        hole=0.4 if donut else 0.0,
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    fig.update_traces(textinfo="label+value", textposition="inside")
    fig.update_layout(
        showlegend=False, paper_bgcolor="white", plot_bgcolor="white", title_x=0.5
    )
    return fig


def hbar_metric(df, metric_col, title, top_n=10):
    cols_needed = {"catalyst", metric_col}
    if not cols_needed.issubset(df.columns):
        return px.bar(title=title)

    dff = (
        df[list(cols_needed)]
        .dropna()
        .drop_duplicates()
        .sort_values(metric_col, ascending=False)
        .head(top_n)
    )
    if dff.empty:
        return px.bar(title=title)

    fig = px.bar(
        dff,
        x=metric_col,
        y="catalyst",
        orientation="h",
        title=title,
        color=metric_col,
        color_continuous_scale="Viridis",
    )
    fig.update_traces(
        text=dff[metric_col].round(1),
        textposition="outside",
        marker_line_color="rgba(0,0,0,0.4)",
        marker_line_width=1,
    )
    fig.update_layout(
        yaxis=dict(autorange="reversed"),
        xaxis_title=metric_col.replace("_", " ").replace("m2", "m²"),
        yaxis_title="Catalyst",
        coloraxis_showscale=False,
        paper_bgcolor="white",
        plot_bgcolor="white",
        title_x=0.5,
        margin=dict(l=220, r=40, t=70, b=40),
        height=500,
    )
    fig.update_xaxes(showgrid=True, gridwidth=0.5, gridcolor="lightgray")
    fig.update_yaxes(showgrid=False)
    return fig


def bar_metal_types(df, top_n=10):
    if "metal_types_list" not in df.columns:
        return px.bar(title="Metal Type Distribution")
    metals = []
    for lst in df["metal_types_list"]:
        metals.extend(lst)
    if not metals:
        return px.bar(title="Metal Type Distribution")

    xx_df = pd.Series(metals).value_counts().reset_index()
    xx_df.columns = ["metal", "count"]
    xx_df = xx_df.head(top_n)

    fig = px.bar(
        xx_df,
        x="metal",
        y="count",
        title="Metal Type Distribution",
        text="count",
        color="metal",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig.update_traces(
        textposition="outside", marker_line_color="rgba(0,0,0,0.4)", marker_line_width=1
    )
    fig.update_layout(
        showlegend=False,
        paper_bgcolor="white",
        plot_bgcolor="white",
        title_x=0.5,
        margin=dict(l=40, r=40, t=70, b=100),
        height=500,
    )
    return fig


# ---------------------------
# Data
# ---------------------------
if not CSV_PATH.exists():
    raise FileNotFoundError(f"Could not find {CSV_PATH.resolve()}")

df = pd.read_csv(CSV_PATH).drop_duplicates()
df = prepare_dataframe(df)

# Controls
METRIC_OPTIONS = {
    "BET Surface Area (m²/g)": "BET_surface_area_m2_per_g",
    "Tafel Slope (mV/dec)": "tafel_mV_per_dec",
    "Stability (hours)": "stability_time_hours",
    "Overpotential @10 mA/cm² (mV)": "overpotential_mV_at_10mAcm2",
}
METALCOUNT_OPTS = (
    sorted(df["metal_count"].dropna().unique()) if "metal_count" in df else []
)
MORPH_OPTS = sorted(df["morphology"].dropna().unique()) if "morphology" in df else []

# ---------------------------
# App
# ---------------------------
app = Dash(__name__)
app.title = "MOF Catalysts Analytics Dashboard"

# ─── Layout ────────────────────────────────────────────────
app.layout = html.Div(
    style={"backgroundColor": "#f9f9f9", "fontFamily": "Arial", "padding": "25px"},
    children=[
        html.H1(
            "MOF Catalysts Analytics Dashboard",
            style={"textAlign": "center", "marginBottom": "20px", "color": "#2c3e50"},
        ),
        # --- Controls Row ---
        html.Div(
            style={
                "display": "flex",
                "flexWrap": "wrap",
                "justifyContent": "center",
                "gap": "20px",
                "marginBottom": "30px",
            },
            children=[
                html.Div(
                    [
                        html.Label("Metric", style={"fontWeight": "bold"}),
                        dcc.Dropdown(
                            id="metric-dd",
                            options=[
                                {"label": k, "value": v}
                                for k, v in METRIC_OPTIONS.items()
                            ],
                            value="BET_surface_area_m2_per_g",
                            clearable=False,
                            style={"width": "220px"},
                        ),
                    ]
                ),
                html.Div(
                    [
                        html.Label("Top N", style={"fontWeight": "bold"}),
                        html.Div(
                            dcc.Slider(
                                id="topn",
                                min=5,
                                max=30,
                                step=1,
                                value=10,
                                marks={5: "5", 10: "10", 20: "20", 30: "30"},
                                tooltip={"placement": "bottom"},
                            ),
                            style={"width": "240px"},
                        ),
                    ]
                ),
                html.Div(
                    [
                        html.Label("Filter: metal_count", style={"fontWeight": "bold"}),
                        dcc.Dropdown(
                            id="mc-filter",
                            options=[{"label": v, "value": v} for v in METALCOUNT_OPTS],
                            value=[],
                            multi=True,
                            placeholder="All",
                            style={"width": "220px"},
                        ),
                    ]
                ),
                html.Div(
                    [
                        html.Label("Filter: morphology", style={"fontWeight": "bold"}),
                        dcc.Dropdown(
                            id="morph-filter",
                            options=[{"label": v, "value": v} for v in MORPH_OPTS],
                            value=[],
                            multi=True,
                            placeholder="All",
                            style={"width": "220px"},
                        ),
                    ]
                ),
            ],
        ),
        # --- Row 1 ---
        html.Div(
            style={
                "display": "flex",
                "justifyContent": "center",
                "gap": "20px",
                "flexWrap": "wrap",
            },
            children=[
                html.Div(
                    dcc.Graph(id="fig-metal-count"),
                    style={
                        "background": "white",
                        "padding": "10px",
                        "borderRadius": "10px",
                        "boxShadow": "0 2px 5px rgba(0,0,0,0.1)",
                        "width": "48%",
                    },
                ),
                html.Div(
                    dcc.Graph(id="fig-morph"),
                    style={
                        "background": "white",
                        "padding": "10px",
                        "borderRadius": "10px",
                        "boxShadow": "0 2px 5px rgba(0,0,0,0.1)",
                        "width": "48%",
                    },
                ),
            ],
        ),
        # --- Row 2 ---
        html.Div(
            style={
                "display": "flex",
                "justifyContent": "center",
                "gap": "20px",
                "flexWrap": "wrap",
                "marginTop": "20px",
            },
            children=[
                html.Div(
                    dcc.Graph(id="fig-metric"),
                    style={
                        "background": "white",
                        "padding": "10px",
                        "borderRadius": "10px",
                        "boxShadow": "0 2px 5px rgba(0,0,0,0.1)",
                        "width": "48%",
                    },
                ),
                html.Div(
                    dcc.Graph(id="fig-crys"),
                    style={
                        "background": "white",
                        "padding": "10px",
                        "borderRadius": "10px",
                        "boxShadow": "0 2px 5px rgba(0,0,0,0.1)",
                        "width": "48%",
                    },
                ),
            ],
        ),
        # --- Row 3 (Full width) ---
        html.Div(
            style={"display": "flex", "justifyContent": "center", "marginTop": "20px"},
            children=[
                html.Div(
                    dcc.Graph(id="fig-metal-types"),
                    style={
                        "background": "white",
                        "padding": "15px",
                        "borderRadius": "10px",
                        "boxShadow": "0 2px 5px rgba(0,0,0,0.1)",
                        "width": "98%",
                    },
                ),
            ],
        ),
    ],
)


# ---------------------------
# Callbacks
# ---------------------------
def apply_filters(dff, mc_values, morph_values):
    if mc_values:
        dff = dff[dff["metal_count"].isin(mc_values)]
    if morph_values:
        dff = dff[dff["morphology"].isin(morph_values)]
    return dff


@app.callback(
    Output("fig-metal-count", "figure"),
    Output("fig-morph", "figure"),
    Output("fig-metric", "figure"),
    Output("fig-crys", "figure"),
    Output("fig-metal-types", "figure"),
    Input("metric-dd", "value"),
    Input("topn", "value"),
    Input("mc-filter", "value"),
    Input("morph-filter", "value"),
)
def update_dashboard(metric_col, topn, mc_values, morph_values):
    dff = apply_filters(df, mc_values, morph_values)

    # Metal count pie (top 3)
    if "metal_count" in dff:
        mc = dff["metal_count"].value_counts().reset_index().head(3)
        mc.columns = ["metal_count", "Count"]
        fig_mc = pie_counts(
            mc, "metal_count", "Count", "Metal Count Distribution", donut=False
        )
    else:
        fig_mc = px.pie(title="Metal Count Distribution")

    # Morphology donut (top 5)
    if "morphology" in dff:
        morph = dff["morphology"].value_counts().reset_index().head(5)
        morph.columns = ["morphology", "Count"]
        fig_morph = pie_counts(
            morph, "morphology", "Count", "Morphology Distribution", donut=True
        )
    else:
        fig_morph = px.pie(title="Morphology Distribution")

    # Metric H-bar
    title_map = {
        "BET_surface_area_m2_per_g": "Top Catalysts by BET Surface Area",
        "tafel_mV_per_dec": "Top Catalysts by Tafel Slope",
        "stability_time_hours": "Top Catalysts by Stability (hours)",
        "overpotential_mV_at_10mAcm2": "Top Catalysts by Overpotential (mV @10 mA/cm²)",
    }
    fig_metric = hbar_metric(
        dff, metric_col, title_map.get(metric_col, "Top Catalysts"), top_n=topn
    )

    # Crystallinity donut (top 5, include NaN → labeled)
    if "crystallinity" in dff:
        crys = dff["crystallinity"].value_counts(dropna=False).reset_index()
        crys.columns = ["crystallinity", "Count"]
        crys["crystallinity"] = crys["crystallinity"].astype(object)
        crys.loc[crys["crystallinity"].isna(), "crystallinity"] = (
            "Not reported/Not found"
        )
        crys = crys.head(5)
        fig_crys = pie_counts(
            crys, "crystallinity", "Count", "Crystallinity Distribution", donut=True
        )
    else:
        fig_crys = px.pie(title="Crystallinity Distribution")

    # Metal types bar (top 10)
    fig_metals = bar_metal_types(dff, top_n=10)

    return fig_mc, fig_morph, fig_metric, fig_crys, fig_metals


# ---------------------------
if __name__ == "__main__":
    app.run(debug=True, port=8049)
