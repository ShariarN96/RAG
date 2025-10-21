from pathlib import Path

import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html

# Load data from CSV
data_path = Path(__file__).parent.parent.parent.parent / "output.csv"
df = pd.read_csv(data_path)
df = df.drop_duplicates()


# === 1️⃣ Load & preprocess your data ==

# Cleaning metal_count
df.loc[
    df["metal_count"].str.contains("single", case=False, na=False), "metal_count"
] = "single"
df.loc[
    df["metal_count"].str.contains("bimetallic", case=False, na=False), "metal_count"
] = "binary"

# === 2️⃣ Create all your figures (reusing your logic) ===

## Metal Count Pie Chart
counts = df["metal_count"].value_counts().reset_index()
counts.columns = ["metal_count", "Count"]
counts = counts.head(3)
fig_metal_count = px.pie(
    counts,
    names="metal_count",
    values="Count",
    title="Metal Count Distribution",
    color_discrete_sequence=px.colors.qualitative.Pastel,
)
fig_metal_count.update_traces(textinfo="label+value", textposition="inside")
fig_metal_count.update_layout(showlegend=False)

## Morphology Pie Chart
morphology_counts = df["morphology"].value_counts().reset_index()
morphology_counts.columns = ["morphology", "Count"]
morphology_counts = morphology_counts.head(5)
fig_morph = px.pie(
    morphology_counts,
    names="morphology",
    values="Count",
    title="Morphology Distribution",
    color_discrete_sequence=px.colors.qualitative.Pastel,
    hole=0.4,
)
fig_morph.update_traces(textinfo="value", textposition="inside")

## BET Surface Area
catalyst_df = df[["catalyst", "BET_surface_area_m2_per_g"]].dropna().drop_duplicates()
catalyst_df["BET_surface_area_m2_per_g"] = (
    catalyst_df["BET_surface_area_m2_per_g"].str.split().str[0].str.split(",").str[0]
)
catalyst_df["BET_surface_area_m2_per_g"] = pd.to_numeric(
    catalyst_df["BET_surface_area_m2_per_g"], errors="coerce"
)
catalyst_df = catalyst_df.sort_values(
    by="BET_surface_area_m2_per_g", ascending=False
).head(10)
fig_bet = px.bar(
    catalyst_df,
    x="BET_surface_area_m2_per_g",
    y="catalyst",
    orientation="h",
    title="Top 10 Catalysts by BET Surface Area",
    color="BET_surface_area_m2_per_g",
    color_continuous_scale="Viridis",
)
fig_bet.update_coloraxes(showscale=False)

## Tafel Slope
tafel_df = df[["catalyst", "tafel_mV_per_dec"]].dropna().drop_duplicates()
tafel_df["tafel_mV_per_dec"] = (
    tafel_df["tafel_mV_per_dec"].str.split().str[0].str.split(",").str[0]
)
tafel_df["tafel_mV_per_dec"] = pd.to_numeric(
    tafel_df["tafel_mV_per_dec"], errors="coerce"
)
tafel_df = tafel_df.sort_values(by="tafel_mV_per_dec", ascending=False).head(10)
fig_tafel = px.bar(
    tafel_df,
    x="tafel_mV_per_dec",
    y="catalyst",
    title="Top 10 Catalysts by Tafel Slope",
    color="tafel_mV_per_dec",
    color_continuous_scale="Viridis",
)
fig_tafel.update_coloraxes(showscale=False)

## Stability
stability_df = df[["catalyst", "stability_time_hours"]].dropna().drop_duplicates()
stability_df["stability_time_hours"] = pd.to_numeric(
    stability_df["stability_time_hours"], errors="coerce"
)
stability_df = stability_df.sort_values(
    by="stability_time_hours", ascending=False
).head(10)
fig_stability = px.bar(
    stability_df,
    x="stability_time_hours",
    y="catalyst",
    title="Top 10 Catalysts by Stability (hours)",
    color="stability_time_hours",
    color_continuous_scale="Viridis",
)
fig_stability.update_coloraxes(showscale=False)

## Crystallinity
crys_counts = df["crystallinity"].value_counts(dropna=False).reset_index()
crys_counts.columns = ["crystallinity", "Count"]
crys_counts.loc[1, "crystallinity"] = "Not reported/Not found"
crys_counts = crys_counts.head(5)
fig_crys = px.pie(
    crys_counts,
    names="crystallinity",
    values="Count",
    title="Crystallinity Distribution",
    color_discrete_sequence=px.colors.qualitative.Pastel,
    hole=0.4,
)

## Metal Types
metal_df = df[["catalyst", "metal_types"]].dropna().drop_duplicates()
z = []
for _, row in metal_df.iterrows():
    z.extend([x.strip() for x in str(row["metal_types"]).split(",")])
xx_df = pd.Series(z).value_counts().reset_index()
xx_df.columns = ["metal", "count"]
xx_df = xx_df.head(10)
fig_metal = px.bar(
    xx_df,
    x="metal",
    y="count",
    title="Metal Type Distribution",
    text="count",
    color="metal",
    color_discrete_sequence=px.colors.qualitative.Set2,
)
fig_metal.update_traces(textposition="outside")
fig_metal.update_layout(showlegend=False)

# === 3️⃣ Dash app layout ===

app = Dash(__name__)
app.title = "MOF Catalyst Analytics Dashboard"

app.layout = html.Div(
    style={
        "backgroundColor": "#f9f9f9",
        "fontFamily": "Arial",
        "padding": "20px",
    },
    children=[
        html.H1("MOF Catalysts Analytics Dashboard", style={"textAlign": "center"}),
        html.Div(
            [
                html.Div(dcc.Graph(figure=fig_metal_count), className="six columns"),
                html.Div(dcc.Graph(figure=fig_morph), className="six columns"),
            ],
            style={"display": "flex", "justifyContent": "space-around"},
        ),
        html.Div(
            [
                html.Div(dcc.Graph(figure=fig_bet), className="six columns"),
                html.Div(dcc.Graph(figure=fig_tafel), className="six columns"),
            ],
            style={
                "display": "flex",
                "justifyContent": "space-around",
                "marginTop": "30px",
            },
        ),
        html.Div(
            [
                html.Div(dcc.Graph(figure=fig_stability), className="six columns"),
                html.Div(dcc.Graph(figure=fig_crys), className="six columns"),
            ],
            style={
                "display": "flex",
                "justifyContent": "space-around",
                "marginTop": "30px",
            },
        ),
        html.Div(
            dcc.Graph(figure=fig_metal),
            style={"width": "80%", "margin": "40px auto"},
        ),
    ],
)

if __name__ == "__main__":
    app.run(port=8050)
