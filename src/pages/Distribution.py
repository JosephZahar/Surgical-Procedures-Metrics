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


def distribution_dash(account_name, procedure_name):
    df = full_df.copy()
    if account_name != 'All':
        df = df[df.account_name==account_name]
    if procedure_name != 'All':
        df = df[df.snomed_code==procedure_name]

    highest_surgeons = df.groupby('surgeon_name')['video_length'].count().reset_index().sort_values(['video_length'], ascending=False).head(10)['surgeon_name'].values
    distribution_df = df[df['surgeon_name'].isin(highest_surgeons)]
    distribution_df = distribution_df.sort_values('surgeon_name')

    surgeon_name = []
    i = 0
    for surgeon in range(len(distribution_df['surgeon_name'])):
        if surgeon == 0:
            surgeon_name.append(f'Surgeon {i+1}')
        elif list(distribution_df['surgeon_name'])[surgeon] != list(distribution_df['surgeon_name'])[surgeon-1]:
            i += 1
            surgeon_name.append(f'Surgeon {i + 1}')
        else:
            surgeon_name.append(f'Surgeon {i + 1}')


    fig1 = go.Figure()
    fig1.add_trace(go.Box(
        x=distribution_df['video_length'],
        y=surgeon_name,
        customdata = distribution_df['video_uuid'],
        name='Video Length',
        marker_color='green',
        hovertemplate='Video: %{customdata}<extra></extra>',
    ))
    fig1.add_trace(go.Box(
        x=distribution_df['summed_case_duration'],
        y=surgeon_name,
        customdata=distribution_df['video_uuid'],
        name='Case Duration',
        marker_color='gold',
        hovertemplate='Video: %{customdata}<extra></extra>',
    ))
    fig1.add_trace(go.Box(
        x=distribution_df['endoscopic_duration'],
        y=surgeon_name,
        name='Endoscopic Duration',
        customdata=distribution_df['video_uuid'],
        hovertemplate='Video: %{customdata}<extra></extra>',
        marker_color='royalblue'
    ))
    fig1.add_trace(go.Box(
        x=distribution_df['case_camerain_duration'],
        y=surgeon_name,
        name='Camera In Duration',
        customdata=distribution_df['video_uuid'],
        hovertemplate='Video: %{customdata}<extra></extra>',
        marker_color='crimson'
    ))

    fig1.update_layout(boxmode='group', showlegend=False)
    fig1.update_traces(orientation='h')
    fig1.update_layout(hovermode="y unified")



    fig2 = go.Figure()
    fig2.add_trace(go.Violin(
        x=distribution_df['video_length'],
        y=surgeon_name,
        name='Video Length',
        line_color='green',
        fillcolor='white',
        opacity=0.5
    ))
    fig2.add_trace(go.Violin(
        x=distribution_df['endoscopic_duration'],
        y=surgeon_name,
        name='Endoscopic Duration',
        line_color='royalblue',
        fillcolor='white',
        opacity=0.5
    ))
    fig2.add_trace(go.Violin(
        x=distribution_df['case_camerain_duration'],
        y=surgeon_name,
        name='Camera In Duration',
        line_color='crimson',
        fillcolor='white',
        opacity=0.5,
    ))
    fig2.add_trace(go.Violin(
        x=distribution_df['summed_case_duration'],
        y=surgeon_name,
        name='Case Duration',
        line_color='gold',
        fillcolor='white',
        opacity=0.5
    ))

    fig2.update_traces(orientation='h',  side='positive', width=2)
    fig2.update_layout(hovermode="y unified")



    fig3 = go.Figure()
    fig3.add_trace(go.Histogram(
        x=surgeon_name,
        y=distribution_df['endoscopic_duration']*100/distribution_df['video_length'],
        name='Endoscopic Duration',
        marker_color='royalblue',
        histfunc='avg',
    ))
    fig3.add_trace(go.Histogram(
        x=surgeon_name,
        y=distribution_df['summed_case_duration']*100/distribution_df['video_length'],
        name='Case Duration',
        marker_color='gold',
        histfunc='avg',
    ))
    fig3.add_trace(go.Histogram(
        x=surgeon_name,
        y=distribution_df['case_camerain_duration']*100/distribution_df['video_length'],
        name='Camera In Duration',
        marker_color='crimson',
        histfunc='avg',
    ))
    fig3.add_hline(y=100, line_width=2, line_dash="dash", line_color="black", opacity=0.8)
    fig3.update_layout(barmode='group', hovermode='x unified', title = 'Video Length Percentage per Surgeon')



    return fig1, fig2, fig3


fig1, fig2, fig3= distribution_dash(
    'All', 'All')
account_dropdown = dcc.Dropdown(options=list(set([i for i in full_df['account_name']])) + ['All'],
                                id='account_named',
                                clearable=False,
                                value='All', className="dbc",
                                placeholder='Select an Account', maxHeight=400)

procedure_dropdown = dcc.Dropdown(options=list(set([i for i in full_df['snomed_code']]))+ ['All'],
                                id='snomed_coded',
                                clearable=False,
                                value='All', className="dbc",
                                placeholder='Select a Procedure', maxHeight=100)



app = dash.Dash(__name__,meta_tags=[{"name": "viewport", "content": "width=device-width"}])

layout = dbc.Container(
    [dbc.Row(dbc.Col(html.H3('Distribution View', className='text-center text-primary, mb-3'))),
     dbc.Row([dbc.Col(account_dropdown),
              dbc.Col(procedure_dropdown)]),
     dbc.Row([
         dbc.Col([
             dcc.Graph(id='fig1d', figure=fig1,
                       style={'height': 1500,'width': 700}),
             html.Hr()
         ], width={'size': 6, 'offset': 0, 'order': 1}),
         dbc.Col([
             dcc.Graph(id='fig2d', figure=fig2,
                       style={'height': 1500, 'width': 700}),
             html.Hr()
         ], width={'size': 6, 'offset': 0, 'order': 2})],
         align="center"),

     dbc.Row([
         dbc.Col([
             dcc.Graph(id='fig3d', figure=fig3,
                       style={'height': 400}),
             html.Hr()
         ], width={'size': 14, 'offset': 0, 'order': 1})])])

