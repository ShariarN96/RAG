import pandas as pd
import plotly.express as px

# Load data from CSV
df = pd.read_csv("output.csv")
df = df.drop_duplicates()

#### METAL COUNT ####

## Cleaning
df.loc[
    df["metal_count"].str.contains("single", case=False, na=False), "metal_count"
] = "single"
df.loc[
    df["metal_count"].str.contains("bimetallic", case=False, na=False), "metal_count"
] = "binary"

counts = df["metal_count"].value_counts().reset_index()
counts.columns = ["metal_count", "Count"]
counts = counts.head(3)
fig = px.pie(
    counts,
    names="metal_count",
    values="Count",
    title="Metal Count Distribution",
    color_discrete_sequence=px.colors.qualitative.Pastel,
)
fig.update_layout(showlegend=False)
fig.update_traces(
    textinfo="label+value",  # show category + number
    textposition="inside",  # text inside each slice
    showlegend=True,  # keep the legend visible
)
fig.show()

#### Morphology ####

morphology_counts = df["morphology"].value_counts().reset_index()
morphology_counts.columns = ["morphology", "Count"]
morphology_counts = morphology_counts.head(5)

fig = px.pie(
    morphology_counts,
    names="morphology",
    values="Count",
    title="Morphology Distribution",
    color_discrete_sequence=px.colors.qualitative.Pastel,
)
fig.update_traces(
    textinfo="value",  # show category + number
    textposition="inside",  # text inside each slice
    # showlegend=True,  # keep the legend visible
    hole=0.4,
)
fig.show()


#### Surface area ####

catalyst_df = (
    df[["catalyst", "BET_surface_area_m2_per_g"]]
    .dropna(axis=0)
    .sort_values(by="BET_surface_area_m2_per_g")
)
catalyst_df = catalyst_df.drop_duplicates()
catalyst_df["BET_surface_area_m2_per_g"] = (
    catalyst_df["BET_surface_area_m2_per_g"].str.split().str[0].str.split(",").str[0]
)
catalyst_df["BET_surface_area_m2_per_g"] = pd.to_numeric(
    catalyst_df["BET_surface_area_m2_per_g"], errors="coerce"
)
catalyst_df = catalyst_df.sort_values(
    by="BET_surface_area_m2_per_g", ascending=False
).head(10)

fig = px.bar(
    catalyst_df,
    x="BET_surface_area_m2_per_g",
    y="catalyst",
    orientation="h",
    title="Top 10 Catalysts by BET Surface Area",
    color="BET_surface_area_m2_per_g",  # 🎨 color intensity by value
    color_continuous_scale="Viridis",  # try 'Plasma', 'Cividis', 'Bluered', 'Turbo'
)

# 🧠 Styling and readability
fig.update_traces(
    text=catalyst_df["BET_surface_area_m2_per_g"].round(1),
    textposition="outside",
    marker_line_color="rgba(0,0,0,0.4)",
    marker_line_width=1.0,
)

fig.update_layout(
    width=1000,
    height=400,
    yaxis=dict(autorange="reversed"),  # largest value on top
    xaxis_title="BET Surface Area (m²/g)",
    yaxis_title="Catalyst",
    title_x=0.5,
    plot_bgcolor="white",
    paper_bgcolor="white",
    coloraxis_colorbar=dict(
        title="Surface Area (m²/g)",  # label colorbar
        thicknessmode="pixels",
        thickness=20,
        lenmode="pixels",
        len=300,
        yanchor="middle",
        y=0.5,
    ),
    font=dict(family="Arial", size=14),
    margin=dict(l=50, t=80, b=50),
)

# subtle gridlines
fig.update_xaxes(showgrid=True, gridwidth=0.5, gridcolor="lightgray")
fig.update_yaxes(showgrid=False)
fig.update_coloraxes(showscale=False)
fig.show()


## Tafel slope ###


tafel_df = (
    df[["catalyst", "tafel_mV_per_dec"]]
    .dropna(axis=0)
    .sort_values(by="tafel_mV_per_dec")
)
tafel_df["tafel_mV_per_dec"] = (
    tafel_df["tafel_mV_per_dec"].str.split().str[0].str.split(",").str[0]
)
tafel_df["tafel_mV_per_dec"] = pd.to_numeric(
    tafel_df["tafel_mV_per_dec"], errors="coerce"
)
tafel_df = tafel_df.drop_duplicates()
tafel_df = tafel_df.sort_values(by="tafel_mV_per_dec", ascending=False).head(15)
tafel_df = tafel_df[:-2]


fig = px.bar(
    tafel_df,
    x="tafel_mV_per_dec",
    y="catalyst",
    # orientation="h",
    title="Top 10 Catalysts by Tafel Slope",
    color="tafel_mV_per_dec",  # 🎨 color intensity by value
    color_continuous_scale="Viridis",  # try 'Plasma', 'Cividis', 'Bluered', 'Turbo'
)

# 🧠 Styling and readability
fig.update_traces(
    text=tafel_df["tafel_mV_per_dec"].round(1),
    textposition="outside",
    marker_line_color="rgba(0,0,0,0.4)",
    marker_line_width=1.0,
)

fig.update_layout(
    width=1000,
    height=400,
    yaxis=dict(autorange="reversed"),  # largest value on top
    xaxis_title="mvV/s",
    yaxis_title="Catalyst",
    title_x=0.5,
    plot_bgcolor="white",
    paper_bgcolor="white",
    coloraxis_colorbar=dict(
        title="Tafel Slope",  # label colorbar
        thicknessmode="pixels",
        thickness=20,
        lenmode="pixels",
        len=300,
        yanchor="middle",
        y=0.5,
    ),
    font=dict(family="Arial", size=14),
    margin=dict(l=50, t=80, b=50),
)

# subtle gridlines
fig.update_xaxes(showgrid=True, gridwidth=0.5, gridcolor="lightgray")
fig.update_yaxes(showgrid=False)
fig.update_coloraxes(showscale=False)
fig.show()


#### Stability ###


stability_df = (
    df[["catalyst", "stability_time_hours"]]
    .dropna(axis=0)
    .sort_values(by="stability_time_hours")
)

stability_df["stability_time_hours"] = pd.to_numeric(
    stability_df["stability_time_hours"], errors="coerce"
)
stability_df = stability_df.drop_duplicates()
stability_df = stability_df.sort_values(
    by="stability_time_hours", ascending=False
).head(15)
# tafel_df = tafel_df[:-2]


fig = px.bar(
    stability_df,
    x="stability_time_hours",
    y="catalyst",
    # orientation="h",
    title="Top 10 Catalysts by Tafel Slope",
    color="stability_time_hours",  # 🎨 color intensity by value
    color_continuous_scale="Viridis",  # try 'Plasma', 'Cividis', 'Bluered', 'Turbo'
)

# 🧠 Styling and readability
fig.update_traces(
    text=stability_df["stability_time_hours"].round(1),
    textposition="outside",
    marker_line_color="rgba(0,0,0,0.4)",
    marker_line_width=1.0,
)

fig.update_layout(
    width=1000,
    height=400,
    yaxis=dict(autorange="reversed"),  # largest value on top
    xaxis_title="Stability (hr)",
    yaxis_title="Catalyst",
    title_x=0.5,
    plot_bgcolor="white",
    paper_bgcolor="white",
    coloraxis_colorbar=dict(
        title="Tafel Slope",  # label colorbar
        thicknessmode="pixels",
        thickness=20,
        lenmode="pixels",
        len=300,
        yanchor="middle",
        y=0.5,
    ),
    font=dict(family="Arial", size=14),
    margin=dict(l=50, t=80, b=50),
)

# subtle gridlines
fig.update_xaxes(showgrid=True, gridwidth=0.5, gridcolor="lightgray")
fig.update_yaxes(showgrid=False)
fig.update_coloraxes(showscale=False)
fig.show()


### overpotential ##

op_df = (
    df[["catalyst", "overpotential_mV_at_10mAcm2"]]
    .dropna(axis=0)
    .sort_values(by="overpotential_mV_at_10mAcm2")
)
op_df["overpotential_mV_at_10mAcm2"] = (
    op_df["overpotential_mV_at_10mAcm2"].str.split().str[0].str.split(",").str[0]
)
op_df["overpotential_mV_at_10mAcm2"] = pd.to_numeric(
    op_df["overpotential_mV_at_10mAcm2"], errors="coerce"
)
op_df = op_df.drop_duplicates()
op_df = op_df.sort_values(by="overpotential_mV_at_10mAcm2", ascending=False).head(15)
op_df = op_df[:-2]


fig = px.bar(
    op_df,
    x="overpotential_mV_at_10mAcm2",
    y="catalyst",
    # orientation="h",
    title="Top 10 Catalysts by Tafel Slope",
    color="overpotential_mV_at_10mAcm2",  # 🎨 color intensity by value
    color_continuous_scale="Viridis",  # try 'Plasma', 'Cividis', 'Bluered', 'Turbo'
)

# 🧠 Styling and readability
fig.update_traces(
    text=op_df["overpotential_mV_at_10mAcm2"].round(1),
    textposition="outside",
    marker_line_color="rgba(0,0,0,0.4)",
    marker_line_width=1.0,
)

fig.update_layout(
    width=1000,
    height=400,
    yaxis=dict(autorange="reversed"),  # largest value on top
    xaxis_title="mvV/s",
    yaxis_title="Catalyst",
    title_x=0.5,
    plot_bgcolor="white",
    paper_bgcolor="white",
    coloraxis_colorbar=dict(
        title="Tafel Slope",  # label colorbar
        thicknessmode="pixels",
        thickness=20,
        lenmode="pixels",
        len=300,
        yanchor="middle",
        y=0.5,
    ),
    font=dict(family="Arial", size=14),
    margin=dict(l=50, t=80, b=50),
)

# subtle gridlines
fig.update_xaxes(showgrid=True, gridwidth=0.5, gridcolor="lightgray")
fig.update_yaxes(showgrid=False)
fig.update_coloraxes(showscale=False)
fig.show()


# Crystallinity##


crys_counts = df["crystallinity"].value_counts(dropna=False).reset_index()
crys_counts.columns = ["crystallinity", "Count"]
crys_counts = crys_counts.head(5)
crys_counts.loc[1, "crystallinity"] = "Not reported/Not found"

fig = px.pie(
    crys_counts,
    names="crystallinity",
    values="Count",
    title="Crystallinity Distribution",
    color_discrete_sequence=px.colors.qualitative.Pastel,
)
fig.update_traces(
    textinfo="value",  # show category + number
    textposition="inside",  # text inside each slice
    # showlegend=True,  # keep the legend visible
    hole=0.4,
)
fig.show()


### Metal dist

metal_df = df[["catalyst", "metal_types"]].dropna(axis=0).sort_values(by="metal_types")

metal_df = metal_df.drop_duplicates()

metal_df["metal_types"] = (
    metal_df["metal_types"].str.split().str[0].str.split(",").str[0]
)
z = []
for row in metal_df.iterrows():
    z.extend(row[1]["metal_types"].split(","))
z = [i.strip() for i in z]


xx = pd.Series(z).value_counts()

xx_df = pd.DataFrame(xx).reset_index()
xx_df.columns = ["metal", "count"]
xx_df = xx_df.head(10)

fig = px.bar(
    xx_df,
    x="metal",
    y="count",
    title="Top 10 Catalysts by Tafel Slope",
    text="count",
    color="metal",  # optional: different color per metal
    color_discrete_sequence=px.colors.qualitative.Set2,
)

# Add value labels
fig.update_traces(
    textposition="outside",
    marker_line_color="rgba(0,0,0,0.4)",
    marker_line_width=1,
)
# Layout cleanup
fig.update_layout(
    width=900,
    height=600,
    title_x=0.5,
    xaxis_title="Metal",
    yaxis_title="Count",
    showlegend=False,
    plot_bgcolor="white",
    paper_bgcolor="white",
    font=dict(family="Arial", size=14),
    margin=dict(l=50, r=50, t=80, b=100),
)
fig.update_coloraxes(showscale=False)
fig.show()


import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html

# === 1️⃣ Load & preprocess your data ===
df = pd.read_csv("output.csv").drop_duplicates()

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
    app.run(debug=True, port=8050)
