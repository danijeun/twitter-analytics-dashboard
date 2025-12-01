import dash
from dash import dcc, html, Input, Output, dash_table, clientside_callback, ClientsideFunction
import pandas as pd
import plotly.graph_objs as go

df = pd.read_csv('ProcessedTweets.csv')

def clean_tweet(tweet):
    if pd.isna(tweet):
        return ""
    
    tweet_str = str(tweet)
    
    if (tweet_str.startswith("['") and tweet_str.endswith("']")) or \
       (tweet_str.startswith('["') and tweet_str.endswith('"]')):
        tweet_str = tweet_str[2:-2]
        if ',' in tweet_str and tweet_str.count("'") > 2:
            parts = tweet_str.split("',")
            if parts:
                tweet_str = parts[0].strip()
                if tweet_str.startswith("'") or tweet_str.startswith('"'):
                    tweet_str = tweet_str[1:]
                if tweet_str.endswith("'") or tweet_str.endswith('"'):
                    tweet_str = tweet_str[:-1]
    
    if tweet_str.startswith("b'") or tweet_str.startswith('b"'):
        if tweet_str.startswith("b'"):
            tweet_str = tweet_str[2:]
            if tweet_str.endswith("'"):
                tweet_str = tweet_str[:-1]
        elif tweet_str.startswith('b"'):
            tweet_str = tweet_str[2:]
            if tweet_str.endswith('"'):
                tweet_str = tweet_str[:-1]
        
        try:
            tweet_str = tweet_str.replace('\\n', '\n').replace('\\t', '\t').replace('\\r', '\r')
            tweet_str = tweet_str.encode('latin-1').decode('utf-8', errors='ignore')
        except:
            tweet_str = tweet_str.replace('\\n', ' ').replace('\\t', ' ').replace('\\r', ' ')
            try:
                tweet_str = bytes(tweet_str, 'latin-1').decode('utf-8', errors='ignore')
            except:
                pass
    
    tweet_str = tweet_str.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    
    tweet_str = ' '.join(tweet_str.split())
    
    return tweet_str

df['RawTweet'] = df['RawTweet'].apply(clean_tweet)

months = sorted(df['Month'].unique().tolist())

app = dash.Dash(__name__)
app.layout = html.Div([
    html.Div([
        html.Div([
            html.Label('Month', style={'marginRight': '10px', 'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='month-dropdown',
                options=[{'label': month, 'value': month} for month in months],
                value=months[0] if months else None,
                style={'width': '150px', 'display': 'inline-block'}
            )
        ], style={'display': 'inline-block', 'marginRight': '30px'}),
        
        html.Div([
            html.Label('Sentiment Score', style={'marginBottom': '5px', 'fontWeight': 'bold', 'display': 'block'}),
            dcc.RangeSlider(
                id='sentiment-slider',
                min=-1.0,
                max=1.0,
                step=0.01,
                value=[-1.0, 1.0],
                marks={-1.0: '-1.00', 1.0: '1.00'},
                tooltip={"placement": "bottom", "always_visible": True}
            )
        ], style={'display': 'inline-block', 'width': '300px', 'marginRight': '30px', 'verticalAlign': 'top'}),
        
        html.Div([
            html.Label('Subjectivity Score', style={'marginBottom': '5px', 'fontWeight': 'bold', 'display': 'block'}),
            dcc.RangeSlider(
                id='subjectivity-slider',
                min=0.0,
                max=1.0,
                step=0.01,
                value=[0.0, 1.0],
                marks={0.0: '0.00', 1.0: '1.00'},
                tooltip={"placement": "bottom", "always_visible": True}
            )
        ], style={'display': 'inline-block', 'width': '300px', 'verticalAlign': 'top'})
    ], style={'padding': '20px', 'backgroundColor': '#f8f9fa', 'borderBottom': '1px solid #dee2e6', 'textAlign': 'center'}),
    
    html.Div([
        dcc.Graph(
            id='scatter-plot',
            config={
                'displayModeBar': True,
                'modeBarButtonsToRemove': ['autoScale2d', 'hoverClosestCartesian', 'hoverCompareCartesian'],
                'displaylogo': False,
                'modeBarButtonsToAdd': ['select2d', 'lasso2d'],
                'toImageButtonOptions': {
                    'format': 'png',
                    'filename': 'custom_image',
                    'height': 500,
                    'width': 700,
                    'scale': 1
                },
                'editable': False,
                'staticPlot': False
            }
        )
    ], style={'padding': '20px', 'height': '500px', 'backgroundColor': 'white'}),
    
    html.Div([
        html.Div(id='content-table')
    ], style={'padding': '20px'}),
    
    html.Div(id='modebar-positioner', style={'display': 'none'})
])

@app.callback(
    Output('scatter-plot', 'figure'),
    [Input('month-dropdown', 'value'),
     Input('sentiment-slider', 'value'),
     Input('subjectivity-slider', 'value')]
)
def update_scatter_plot(selected_month, sentiment_range, subjectivity_range):
    filtered_df = df[df['Month'] == selected_month].copy()
    
    filtered_df = filtered_df[
        (filtered_df['Sentiment'] >= sentiment_range[0]) & 
        (filtered_df['Sentiment'] <= sentiment_range[1])
    ]
    
    filtered_df = filtered_df[
        (filtered_df['Subjectivity'] >= subjectivity_range[0]) & 
        (filtered_df['Subjectivity'] <= subjectivity_range[1])
    ]
    
    original_indices = filtered_df.index.values
    filtered_df_reset = filtered_df.reset_index(drop=True)
    
    customdata_array = [[idx] for idx in original_indices]
    
    fig = go.Figure(data=go.Scattergl(
        x=filtered_df_reset['Dimension 1'],
        y=filtered_df_reset['Dimension 2'],
        mode='markers',
        marker=dict(
            size=8,
            color='#333333',
            opacity=0.8,
            line=dict(width=0)
        ),
        customdata=customdata_array,
        hovertemplate='<extra></extra>'
    ))
    
    fig.update_layout(
        xaxis=dict(
            showgrid=True, 
            gridcolor='lightgray',
            zeroline=False, 
            showticklabels=False, 
            title=''
        ),
        yaxis=dict(
            showgrid=True, 
            gridcolor='lightgray',
            zeroline=False, 
            showticklabels=False, 
            title=''
        ),
        plot_bgcolor='#f5f5f5',
        paper_bgcolor='white',
        margin=dict(l=40, r=60, t=40, b=40),
        hovermode='closest',
        dragmode='lasso',
        title=''
    )
    
    return fig
@app.callback(
    Output('content-table', 'children'),
    [Input('scatter-plot', 'selectedData'),
     Input('month-dropdown', 'value'),
     Input('sentiment-slider', 'value'),
     Input('subjectivity-slider', 'value')]
)
def update_content_table(selected_data, selected_month, sentiment_range, subjectivity_range):
    filtered_df = df[df['Month'] == selected_month].copy()
    
    filtered_df = filtered_df[
        (filtered_df['Sentiment'] >= sentiment_range[0]) & 
        (filtered_df['Sentiment'] <= sentiment_range[1])
    ]
    
    filtered_df = filtered_df[
        (filtered_df['Subjectivity'] >= subjectivity_range[0]) & 
        (filtered_df['Subjectivity'] <= subjectivity_range[1])
    ]
    
    display_df = None
    
    if selected_data and 'points' in selected_data and len(selected_data['points']) > 0:
        try:
            selected_indices = []
            for point in selected_data['points']:
                idx = None
                
                if 'customdata' in point:
                    idx = point['customdata']
                    if isinstance(idx, (list, tuple)) and len(idx) > 0:
                        idx = idx[0]
                    elif hasattr(idx, '__iter__') and not isinstance(idx, (str, int, float)):
                        try:
                            idx_list = list(idx)
                            if len(idx_list) > 0:
                                idx = idx_list[0]
                            else:
                                idx = None
                        except:
                            idx = None
                    elif isinstance(idx, (int, float)):
                        idx = int(idx)
                    else:
                        idx = None
                
                if idx is None and 'pointNumber' in point:
                    point_num = point['pointNumber']
                    if point_num is not None and point_num < len(filtered_df):
                        idx = filtered_df.iloc[point_num].name
                
                if idx is not None:
                    try:
                        idx = int(idx)
                        selected_indices.append(idx)
                    except (ValueError, TypeError):
                        pass
            
            if selected_indices:
                display_df = df.loc[df.index.isin(selected_indices)].copy()
                display_df = display_df[
                    (display_df['Month'] == selected_month) &
                    (display_df['Sentiment'] >= sentiment_range[0]) & 
                    (display_df['Sentiment'] <= sentiment_range[1]) &
                    (display_df['Subjectivity'] >= subjectivity_range[0]) & 
                    (display_df['Subjectivity'] <= subjectivity_range[1])
                ]
        except (KeyError, TypeError, IndexError, AttributeError) as e:
            pass
    
    if display_df is not None and not display_df.empty:
        display_df = display_df.reset_index(drop=True)
        table_data = display_df[['RawTweet']].to_dict('records')
    else:
        table_data = []
    table = dash_table.DataTable(
        id='tweet-table',
        columns=[
            {'name': 'RawTweet', 'id': 'RawTweet', 'type': 'text'}
        ],
        data=table_data,
        style_cell={
            'textAlign': 'center',
            'padding': '10px',
            'fontFamily': 'Arial, sans-serif',
            'fontSize': '14px',
            'whiteSpace': 'normal',
            'height': 'auto',
            'border': '1px solid #dee2e6'
        },
        style_cell_conditional=[
            {
                'if': {'column_id': 'RawTweet'},
                'textAlign': 'center',
                'width': 'auto'
            }
        ],
        style_as_list_view=True,
        style_data={
            'whiteSpace': 'normal',
            'height': 'auto',
            'lineHeight': '1.5',
            'textAlign': 'center'
        },
        style_data_conditional=[
            {
                'if': {'column_id': 'RawTweet'},
                'textAlign': 'center'
            }
        ],
        style_header={
            'backgroundColor': 'white',
            'fontWeight': 'bold',
            'textAlign': 'center',
            'border': '1px solid #dee2e6'
        },
        page_size=10,
        page_action='native'
    )
    
    return table

app.clientside_callback(
    """
    function(figure) {
        if (figure) {
            setTimeout(function() {
                var modebars = document.querySelectorAll('.modebar');
                modebars.forEach(function(modebar) {
                    modebar.style.setProperty('right', '5px', 'important');
                    modebar.style.setProperty('left', 'auto', 'important');
                    modebar.style.setProperty('position', 'absolute', 'important');
                    modebar.style.setProperty('top', '10px', 'important');
                    modebar.style.setProperty('opacity', '1', 'important');
                    modebar.style.setProperty('visibility', 'visible', 'important');
                    modebar.style.setProperty('display', 'flex', 'important');
                    modebar.style.setProperty('flex-direction', 'column', 'important');
                    modebar.style.setProperty('align-items', 'flex-start', 'important');
                    modebar.style.setProperty('gap', '12px', 'important');
                    modebar.style.setProperty('width', 'auto', 'important');
                    modebar.style.setProperty('height', 'auto', 'important');
                });

                var groups = document.querySelectorAll('.modebar-group, .modebar-btn-group');
                groups.forEach(function(group, index, array) {
                    group.style.setProperty('display', 'flex', 'important');
                    group.style.setProperty('flex-direction', 'column', 'important');
                    group.style.setProperty('align-items', 'flex-start', 'important');
                    group.style.setProperty('gap', '8px', 'important');
                    group.style.setProperty('position', 'relative', 'important');

                    if (index === array.length - 1) {
                        group.style.setProperty('margin-bottom', '0', 'important');
                        group.style.setProperty('padding-bottom', '0', 'important');
                        group.style.setProperty('border-bottom', 'none', 'important');
                    } else {
                        group.style.setProperty('margin-bottom', '20px', 'important');
                        group.style.setProperty('padding-bottom', '10px', 'important');
                        group.style.setProperty('border-bottom', '2px solid rgba(0, 0, 0, 0.15)', 'important');
                    }

                    var children = group.querySelectorAll('*');
                    children.forEach(function(child) {
                        child.style.setProperty('position', 'static', 'important');
                        child.style.setProperty('transform', 'none', 'important');
                    });
                });

                var buttons = document.querySelectorAll('.modebar-btn');
                buttons.forEach(function(btn) {
                    btn.style.setProperty('position', 'static', 'important');
                    btn.style.setProperty('margin', '0 0 4px 0', 'important');
                    btn.style.setProperty('padding', '6px', 'important');
                    btn.style.setProperty('display', 'block', 'important');
                    btn.style.setProperty('width', '36px', 'important');
                    btn.style.setProperty('height', '36px', 'important');
                    btn.style.setProperty('min-width', '36px', 'important');
                    btn.style.setProperty('min-height', '36px', 'important');
                    btn.style.setProperty('transform', 'none', 'important');
                    btn.style.setProperty('left', 'auto', 'important');
                    btn.style.setProperty('top', 'auto', 'important');
                    btn.style.setProperty('right', 'auto', 'important');
                    btn.style.setProperty('bottom', 'auto', 'important');

                    var svg = btn.querySelector('svg');
                    if (svg) {
                        svg.style.setProperty('transform', 'scaleY(-1)', 'important');
                        svg.removeAttribute('transform');

                        var paths = svg.querySelectorAll('path');
                        paths.forEach(function(path) {
                            path.style.setProperty('transform', 'none', 'important');
                            path.removeAttribute('transform');
                        });
                    }
                });
            }, 500);
        }
        return '';
    }
    """,
    Output('modebar-positioner', 'children'),
    Input('scatter-plot', 'figure'),
    prevent_initial_call=False
)

server = app.server

if __name__ == '__main__':
    app.run(debug=True)

