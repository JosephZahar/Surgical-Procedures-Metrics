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

def composition_dash(account_name, procedure_name):
    df = full_df.copy()
    if account_name != 'All':
        df = df[df.account_name==account_name]
    if procedure_name != 'All':
        df = df[df.snomed_code==procedure_name]

    composition_df = df[['endoscopic_duration', 'video_length', 'summed_case_duration', 'case_camerain_duration']].mean()
    composition_df['video_length'] = round(composition_df['video_length'],2)
    composition_df['summed_case_duration'] = round(composition_df['summed_case_duration'],2)
    composition_df['endoscopic_duration'] = round(composition_df['endoscopic_duration'],2)
    composition_df['case_camerain_duration'] = round(composition_df['case_camerain_duration'],2)

    data = pd.DataFrame({'Duration': [composition_df['video_length'], composition_df['endoscopic_duration'], composition_df['summed_case_duration'], composition_df['case_camerain_duration']],
                         'Label': ["Video Length", "Endoscopic Duration", "Case Duration", "Camera In Duration"],
                         'colors': ["green", "royalblue", "gold", "red"]})
    data = data.sort_values(['Duration'], ascending=False)
    fig1 = go.Figure(go.Sunburst(
        labels=data['Label'].values,
        parents=[""] + list(data['Label'][:-1]),
        values=data['Duration'].values,
        branchvalues='total',
        marker=dict(colors=data['colors'].values))
    )
    fig1.update_layout(showlegend=False, title='Hierarchical View')


    fig2 = go.Figure()
    fig2.add_trace(go.Bar(x=[0],
                          y=[composition_df['summed_case_duration']*100/composition_df['video_length']],
                          name='Case Duration',
                          marker_color='gold',
                          text=f"Case <br> Duration: <br> <br> {round(composition_df['summed_case_duration']*100/composition_df['video_length'],2)}%",
                          ))
    fig2.add_trace(go.Bar(x=[0],
                          y=[composition_df['endoscopic_duration']*100/composition_df['video_length']],
                          name='Endoscopic Duration',
                          marker_color='royalblue',
                          text=f"Endoscopic <br> Duration: <br> <br> {round(composition_df['endoscopic_duration']*100/composition_df['video_length'],2)}%",
                          ))
    fig2.add_trace(go.Bar(x=[0],
                          y=[composition_df['case_camerain_duration']*100/composition_df['video_length']],
                          name='Camera In Duration',
                          marker_color='crimson',
                          text=f"Camera In <br> Duration: <br> <br> {round(composition_df['case_camerain_duration']*100/composition_df['video_length'],2)}%",
                          ))

    fig2.update_xaxes(showticklabels=False)
    fig2.update_layout(barmode='group', title='Video Length Percentage')
    fig2.add_hline(y=100, line_width=2, line_dash="dash", line_color="black", opacity=0.8)

    composition_df['idle_time'] = composition_df['video_length'] - composition_df['summed_case_duration']
    composition_df['case_cameraout_duration'] = composition_df['summed_case_duration'] - composition_df['case_camerain_duration']
    composition_df['?'] = composition_df['summed_case_duration'] - composition_df['endoscopic_duration']
    fig3 = go.Figure(go.Sankey(
        arrangement="snap",
        node={
            "label": ["Video Length", "Case Duration", "Idle Time", "Camera In Duration", "Camera Out Duration"],
            "x": [0.1, 0.4, 0.35, 0.7, 0.65],
            "y": [0.3, 0.5, 1, 0.7, -0.1],
            "color": ["green", "gold", "black", "crimson", "orange"],
            'pad': 20},  # 10 Pixels
        link={
            "source": [0, 0, 1, 1],
            "target": [1, 2, 3, 4],
            "value": [composition_df['summed_case_duration'], composition_df['idle_time'], composition_df['case_camerain_duration'], composition_df['case_cameraout_duration']]}))
    fig3.update_layout(title='Duration Breakdown')

    indicators_composition = go.Figure()
    indicators_composition.add_trace(go.Indicator(
        mode="number",
        value=len(df),
        number={'suffix': " videos"},
        title={"text": "<br><span style='font-size:0.9em;color:black'> Number of Videos </span>"},
        domain={'row': 0, 'column': 0}))

    indicators_composition.add_trace(go.Indicator(
        mode="number+gauge",
        value=len(df)* 100 / len(full_df),
        number={'suffix': " %"},
        title={"text": "<span style='font-size:0.9em;color:black'> Percentage of Total Videos </span>"},
        gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "#1010EB"}},
        domain={'row': 1, 'column': 0}))

    indicators_composition.update_layout(
        grid={'rows': 2, 'columns': 1, 'pattern': "independent"},
        margin=dict(l=130, r=130, t=0, b=0)
    )

    return fig1, fig2, fig3, indicators_composition

account_names = list(set(i for i in full_df['account_name'])) + ['All']
procedure_names = list(set(i for i in full_df['snomed_code'])) + ['All']

fig1, fig2, fig3, indicators_composition = composition_dash(
    'All', 'All')
account_dropdown = dcc.Dropdown(options=account_names,
                                id='account_namec',
                                clearable=False,
                                value='All', className="dbc",
                                placeholder='Select an Account', maxHeight=1000)

procedure_dropdown = dcc.Dropdown(options=procedure_names,
                                id='snomed_codec',
                                clearable=False,
                                value='All', className="dbc",
                                placeholder='Select a Procedure', maxHeight=100)



app = dash.Dash(__name__,meta_tags=[{"name": "viewport", "content": "width=device-width"}])

layout = dbc.Container(
    [dbc.Row(dbc.Col(html.H3('Composition View', className='text-center text-primary, mb-3'))),
     dbc.Row([dbc.Col(account_dropdown),
              dbc.Col(procedure_dropdown)]),

     dbc.Row([dbc.Col([html.P(),
              html.P(),
              html.H5(html.U('Surgical Procedure Metrics - Definitions:')),
              html.Li([html.Strong('Video Length:'), html.Span('The length of the recorded video, encompassing both inside and outside the patient')]),
              html.Li([html.Strong('Case Duration:'), html.Span('The length of the surgical procedure from the start to the end of the procedure')]),
              html.Li([html.Strong('Endoscopic Duration:'), html.Span('The length of time since the first camera in until the last camera out,')]),
              html.Li([html.Strong('Camera In Duration:'), html.Span('The length of time where the camera is inside the patient')]),]
                      ), dbc.Col([
             dcc.Graph(id='indicators_composition', figure=indicators_composition,
                       style={'height': 250}),
             html.Hr()
         ], width={'size': 4})]),


     dbc.Row([
         dbc.Col([
             dcc.Graph(id='fig1c', figure=fig1,
                       style={'height': 700}),
             html.Hr()
         ], width={'size': 6, 'offset': 0, 'order': 1}),
         dbc.Col([
             dcc.Graph(id='fig2c', figure=fig2,
                       style={'height': 700}),
             html.Hr()
         ], width={'size': 6, 'offset': 0, 'order': 2})],
         align="center"),

     dbc.Row([
         dbc.Col([
             dcc.Graph(id='fig3c', figure=fig3,
                       style={'height': 500}),
             html.Hr()
         ], width={'size': 12, 'offset': 0, 'order': 1})])])

