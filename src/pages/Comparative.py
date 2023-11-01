# import desired libraries
import pandas as pd
import plotly.io as pio
pio.templates.default = "simple_white"
import pathlib
import plotly.graph_objects as go
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
import dash
import warnings
warnings.filterwarnings("ignore")

PATH = pathlib.Path(__file__).parent.parent
DATA_PATH = PATH.joinpath("data").resolve()
case_duration_df = pd.read_csv(DATA_PATH.joinpath('complete_videos.csv'))
endoscopic_duration_df = pd.read_csv(DATA_PATH.joinpath('endoscopic_dur_df_2.csv'))

full_df = pd.merge(case_duration_df, endoscopic_duration_df, on="video_uuid", how="inner")
full_df['video_length'] = full_df['video_length'].apply(lambda x: round(x/60000, 2))
full_df['summed_case_duration'] = full_df['summed_case_duration'].apply(lambda x: round(x/60000, 2))
full_df['endoscopic_duration'] = full_df['endoscopic_duration'].apply(lambda x: round(x/60000, 2))
full_df['case_camerain_duration'] = full_df['case_camerain_duration'].apply(lambda x: round(x/60000, 2))


def comparative_dash(account_name, procedure_name, procedure1, procedure2):
    df = full_df.copy()
    if account_name != 'All':
        df = df[df.account_name==account_name]
    if procedure_name != 'All':
        df1 = df[df.snomed_code==procedure_name]
    else:
        df1 = df.copy()


    indicators_df = df[
        ['endoscopic_duration', 'video_length', 'summed_case_duration', 'case_camerain_duration']].mean()

    indicators_comparative= go.Figure()
    indicators_comparative.add_trace(go.Indicator(
        mode="number+gauge",
        value=indicators_df['summed_case_duration']/indicators_df['video_length']*100,
        number={'suffix': " %"},
        title={"text": "<br><span style='font-size:0.9em;color:black'>Case vs Video Length </span>"},
        gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "green"}},
        domain={'row': 0, 'column': 0}))

    indicators_comparative.add_trace(go.Indicator(
        mode="number+gauge",
        value=indicators_df['endoscopic_duration']/indicators_df['video_length']*100,
        number={'suffix': " %"},
        title={"text": "<span style='font-size:0.9em;color:black'>Endoscopic vs Video Duration </span>"},
        gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "royalblue"}},
        domain={'row': 0, 'column': 1}))

    indicators_comparative.add_trace(go.Indicator(
        mode="number+gauge",
        value=indicators_df['summed_case_duration']/indicators_df['endoscopic_duration']*100,
        number={'suffix': " %"},
        title={"text": "<span style='font-size:0.9em;color:black'> Case vs Endoscopic Duration </span>"},
        gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "gold"}},
        domain={'row': 0, 'column': 2}))

    indicators_comparative.add_trace(go.Indicator(
        mode="number+gauge",
        value=indicators_df['case_camerain_duration']/indicators_df['endoscopic_duration']*100,
        number={'suffix': " %"},
        gauge={'axis': {'range': [0, 10]}, 'bar': {'color': "crimson"}},
        title={"text": "<span style='font-size:0.9em;color:black'> Camera In vs Endoscopic Duration </span>"},
        domain={'row': 0, 'column': 3}))

    indicators_comparative.update_layout(
        grid={'rows': 1, 'columns': 4, 'pattern': "independent"},
        margin=dict(l=50, r=50, t=30, b=30)
    )

    highest_surgeons = df1.groupby('surgeon_name')['video_length'].count().reset_index().sort_values(['video_length'], ascending=False).head(10)['surgeon_name'].values

    surgeon_name = [f"Surgeon {i+1}" for i in range(len(highest_surgeons))]


    fig1 = go.Figure()
    for i in range(len(highest_surgeons)):
        fig1.add_trace(go.Violin(x=df1['surgeon_name'][df1['surgeon_name'] == highest_surgeons[i]],
                                y=df1['video_length'][df1['surgeon_name'] == highest_surgeons[i]],
                                name=surgeon_name[i], line_color='green',customdata=df1['video_uuid'][df1['surgeon_name'] == highest_surgeons[i]],
                                hovertemplate='Video: %{customdata}<extra></extra>',
                                meanline_visible=True))
    fig1.update_layout(showlegend=False)
    fig1.update_layout(hovermode="x unified")
    fig1.update_layout(
        xaxis=dict(
            tickmode='array',
            tickvals=highest_surgeons,
            ticktext=surgeon_name
        )
    )

    fig2 = go.Figure()
    for i in range(len(highest_surgeons)):
        fig2.add_trace(go.Violin(x=df1['surgeon_name'][df1['surgeon_name'] == highest_surgeons[i]],
                                 y=df1['summed_case_duration'][df1['surgeon_name'] == highest_surgeons[i]],
                                 customdata=df1['video_uuid'][df1['surgeon_name'] == highest_surgeons[i]],
                                 hovertemplate='Video: %{customdata}<extra></extra>',
                                 name=surgeon_name[i], line_color='gold',
                                 meanline_visible=True))
    fig2.update_layout(showlegend=False)
    fig2.update_layout(hovermode="x unified")
    fig2.update_layout(
        xaxis=dict(
            tickmode='array',
            tickvals=highest_surgeons,
            ticktext=surgeon_name
        )
    )

    fig3 = go.Figure()
    for i in range(len(highest_surgeons)):
        fig3.add_trace(go.Violin(x=df1['surgeon_name'][df1['surgeon_name'] == highest_surgeons[i]],
                                 y=df1['endoscopic_duration'][df1['surgeon_name'] == highest_surgeons[i]],
                                 name=surgeon_name[i], line_color='royalblue',
                                 customdata=df1['video_uuid'][df1['surgeon_name'] == highest_surgeons[i]],
                                 hovertemplate='Video: %{customdata}<extra></extra>',
                                 meanline_visible=True))
    fig3.update_layout(showlegend=False)
    fig3.update_layout(hovermode="x unified")
    fig3.update_layout(
        xaxis=dict(
            tickmode='array',
            tickvals=highest_surgeons,
            ticktext=surgeon_name
        )
    )

    fig4 = go.Figure()
    for i in range(len(highest_surgeons)):
        fig4.add_trace(go.Violin(x=df1['surgeon_name'][df1['surgeon_name'] == highest_surgeons[i]],
                                 y=df1['case_camerain_duration'][df1['surgeon_name'] == highest_surgeons[i]],
                                 name=surgeon_name[i], line_color='crimson',
                                 customdata=df1['video_uuid'][df1['surgeon_name'] == highest_surgeons[i]],
                                 hovertemplate='Video: %{customdata}<extra></extra>',
                                 meanline_visible=True))
    fig4.update_layout(showlegend=False)
    fig4.update_layout(hovermode="x unified")
    fig4.update_layout(
        xaxis=dict(
            tickmode='array',
            tickvals=highest_surgeons,
            ticktext=surgeon_name
        )
    )

    procedures = [procedure1, procedure2]
    colors_vid = ["green", "lime"]
    colors_case = ["gold", "orange"]
    colors_end = ["royalblue", "blue"]
    colors_cam = ["crimson", "red"]
    fig5 = go.Figure()
    for procedure, color in zip(procedures,colors_vid):
        fig5.add_trace(go.Violin(x=df['snomed_code'][df['snomed_code'] == procedure],
                                 y=df['video_length'][df['snomed_code'] == procedure],
                                 name=procedure, line_color=color,customdata=df['video_uuid'][df['snomed_code'] == procedure],
                                 hovertemplate='Video: %{customdata}<extra></extra>',
                                 meanline_visible=True))
    fig5.update_xaxes(showticklabels=False)
    fig5.update_layout(legend=dict(
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ))
    fig5.update_layout(hovermode="x unified")

    fig6 = go.Figure()
    for procedure, color in zip(procedures,colors_case):
        fig6.add_trace(go.Violin(x=df['snomed_code'][df['snomed_code'] == procedure],
                                 y=df['summed_case_duration'][df['snomed_code'] == procedure],
                                 name=procedure, line_color=color,
                                 customdata=df['video_uuid'][df['snomed_code'] == procedure],
                                 hovertemplate='Video: %{customdata}<extra></extra>',
                                 meanline_visible=True))
    fig6.update_xaxes(showticklabels=False)
    fig6.update_layout(legend=dict(
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ))
    fig6.update_layout(hovermode="x unified")

    fig7 = go.Figure()
    for procedure, color in zip(procedures,colors_end):
        fig7.add_trace(go.Violin(x=df['snomed_code'][df['snomed_code'] == procedure],
                                 y=df['endoscopic_duration'][df['snomed_code'] == procedure],
                                 name=procedure, line_color=color,
                                 customdata=df['video_uuid'][df['snomed_code'] == procedure],
                                 hovertemplate='Video: %{customdata}<extra></extra>',
                                 meanline_visible=True))
    fig7.update_xaxes(showticklabels=False)
    fig7.update_layout(legend=dict(
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ))
    fig7.update_layout(hovermode="x unified")

    fig8 = go.Figure()
    for procedure, color in zip(procedures,colors_cam):
        fig8.add_trace(go.Violin(x=df['snomed_code'][df['snomed_code'] == procedure],
                                 y=df['case_camerain_duration'][df['snomed_code'] == procedure],
                                 name=procedure, line_color=color,
                                 customdata=df['video_uuid'][df['snomed_code'] == procedure],
                                 hovertemplate='Video: %{customdata}<extra></extra>',
                                 meanline_visible=True))
    fig8.update_xaxes(showticklabels=False)
    fig8.update_layout(legend=dict(
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ))
    fig8.update_layout(hovermode="x unified")

    return fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8, indicators_comparative



fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8, indicators_comparative = comparative_dash('All',
                                                                                          'All',
                                                                                          'laparoscopic_radical_prostatectomy_using_robotic_assistance',
                                                                                          'laparoscopic_partial_excision_of_kidney_using_robotic_assistance')
account_dropdown = dcc.Dropdown(options=sorted(list(set([i for i in full_df['account_name']])), key=lambda x: int(x[9:])) + ['All'],
                                id='account_namee',
                                clearable=False,
                                value='All', className="dbc",
                                placeholder='Select an Account', maxHeight=400)

procedure_dropdown = dcc.Dropdown(options=sorted(list(set([i for i in full_df['snomed_code']])), key=lambda x: int(x[10:]))+ ['All'],
                                id='snomed_codee',
                                clearable=False,
                                value='All', className="dbc",
                                placeholder='Select a Procedure', maxHeight=100)
procedure1_dropdown = dcc.Dropdown(options=sorted(list(set([i for i in full_df['snomed_code']])), key=lambda x: int(x[10:])),
                                id='procedure1e',
                                clearable=False,
                                value='Procedure 4', className="dbc",
                                placeholder='Select Procedure 1', maxHeight=100)
procedure2_dropdown = dcc.Dropdown(options=sorted(list(set([i for i in full_df['snomed_code']])), key=lambda x: int(x[10:])),
                                id='procedure2e',
                                clearable=False,
                                value='Procedure 6', className="dbc",
                                placeholder='Select Procedure 2', maxHeight=100)



app = dash.Dash(__name__,meta_tags=[{"name": "viewport", "content": "width=device-width"}])

layout = dbc.Container(
    [dbc.Row(dbc.Col(html.H3('Comparative View', className='text-center text-primary, mb-3'))),
     dbc.Row([dbc.Col(account_dropdown),
              dbc.Col(procedure_dropdown),
              dbc.Col(procedure1_dropdown),
              dbc.Col(procedure2_dropdown)]),
     dbc.Row([
         dbc.Col([
             dcc.Graph(id='indicators_comparative', figure=indicators_comparative,
                       style={'height': 300}),
             html.Hr()
         ], width={'size': 12, 'offset': 0, 'order': 1})]),

     dbc.Row([html.H4('Video Length', className='text-center text-primary, mb-3'), html.P('Recording Start Time to Recording End time Duration', className='text-center text-primary, mb-3'),
         dbc.Col([
             dcc.Graph(id='fig1e', figure=fig1,
                       style={'height': 500}),
             html.Hr()
         ], width={'size': 6, 'offset': 0, 'order': 1}),
         dbc.Col([
             dcc.Graph(id='fig5e', figure=fig5,
                       style={'height': 500}),
             html.Hr()
         ], width={'size': 6, 'offset': 0, 'order': 2})],
         align="center"),

    dbc.Row([html.H4('Case Duration', className='text-center text-primary, mb-3'), html.P('Port Insertion to Operation Finished Duration', className='text-center text-primary, mb-3'),
         dbc.Col([
             dcc.Graph(id='fig2e', figure=fig2,
                       style={'height': 500}),
             html.Hr()
         ], width={'size': 6, 'offset': 0, 'order': 1}),
         dbc.Col([
             dcc.Graph(id='fig6e', figure=fig6,
                       style={'height': 500}),
             html.Hr()
         ], width={'size': 6, 'offset': 0, 'order': 2})],
         align="center"),

    dbc.Row([html.H4('Endoscopic Duration', className='text-center text-primary, mb-3'), html.P('First Camera In to Last Camera Out Duration', className='text-center text-primary, mb-3'),
         dbc.Col([
             dcc.Graph(id='fig3e', figure=fig3,
                       style={'height': 500}),
             html.Hr()
         ], width={'size': 6, 'offset': 0, 'order': 1}),
         dbc.Col([
             dcc.Graph(id='fig7e', figure=fig7,
                       style={'height': 500}),
             html.Hr()
         ], width={'size': 6, 'offset': 0, 'order': 2})],
         align="center"),

    dbc.Row([html.H4('Camera In Duration', className='text-center text-primary, mb-3'), html.P('Camera Inside Patient Duration', className='text-center text-primary, mb-3'),
         dbc.Col([
             dcc.Graph(id='fig4e', figure=fig4,
                       style={'height': 500}),
             html.Hr()
         ], width={'size': 6, 'offset': 0, 'order': 1}),
         dbc.Col([
             dcc.Graph(id='fig8e', figure=fig8,
                       style={'height': 500}),
             html.Hr()
         ], width={'size': 6, 'offset': 0, 'order': 2})],
         align="center")])

