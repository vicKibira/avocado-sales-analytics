import pandas as pd
import dash
import sqlalchemy
import dash_bootstrap_components as dbc
import plotly.express as px
from dash import dcc,html,Input,Output,State,dash_table
from dash.exceptions import PreventUpdate
import random
from sqlalchemy import create_engine
from sqlalchemy import text
from sqlalchemy.pool import NullPool,QueuePool
from flask_caching import Cache
import random
import dash_pivottable
import plotly.graph_objects as go

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY],suppress_callback_exceptions=True)

# Create a Flask cache
cache = Cache(app.server, config={
    'CACHE_TYPE': 'simple'  # Use 'redis' or other type of cache for production
})
CACHE_TIMEOUT = 300  # Cache timeout in seconds


postgres_url ="postgresql://root:root@172.18.0.2:5432/avocadosales"

engine = create_engine(postgres_url, poolclass=NullPool)
engine.connect()

#regions
with engine.connect() as connection:
    t = text('''
             with dim_regions as (
             select 
                "region" as regions
             from avo_data
             group by regions
             )
             select 
                regions
             from dim_regions
             ''')
    df = pd.read_sql(t, con=engine)
    
#coonecting to the data source to get the date,regions,total bags and total volumes
with engine.connect() as connection:
    t = text('''
             with dim_region_sales_per_date as (
             select 
                 "Date" as sale_date,
                 "region" as region,
                 sum("Total Bags")as total_bags,
                 sum("AveragePrice" * "Total Volume") as total_sales
             from avo_data
             group by sale_date, region
             )
             select 
                 sale_date,
                 region,
                 total_bags,
                 total_sales
             from dim_region_sales_per_date
             order by sale_date asc
             ''')
    df = pd.read_sql(t, con=engine)
    


navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Home", href="/home")),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem("More pages", header=True),
                dbc.DropdownMenuItem("Region Overview", href="/region"),
                dbc.DropdownMenuItem("Bags Overview", href="/bags"),
                dbc.DropdownMenuItem("About", href="/about"),
                dbc.DropdownMenuItem("Contact Us", href="/contact"),
            ],
            nav=True,
            in_navbar=True,
            label="More",
        ),
    ],
    brand="AvocadoSalesAnalytics",
    brand_href="#",
    style={'background-color': 'rgba(0, 0, 0, 0)'}
    # color="primary",
    # dark=True,
    #className="navbar-custom" # set background color to transparent
    
)
home_layout = html.Div([
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6('Total Sales', style={'textAlign':'center','color':'#008B8B'}),
                    html.P(id='total-sales', children=0, style={'textAlign':'center','color':'#008B8B'})
                ])
            ])
        ]),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6('Total Bags', style={'textAlign':'center','color':'#008B8B'}),
                    html.P(id='total-bags', children=0, style={'textAlign':'center','color':'#008B8B'}) 
                ])
            ])
        ]),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H6('Total Avocados', style={'textAlign':'center','color':'#008B8B'}),
                    html.P(id='total-avocados', children=0, style={'textAlign':'center','color':'#008B8B'})    
                ])
            ])
        ])
    ]),
    html.Br(),
    dbc.Row([
        #dcc.Dropdown(id='regions', options=[{'label': region, 'value': region} for region in df['regions']], placeholder="Select a region", className='custom-dropdown'),
        dbc.Col([
            #html.Br(),
            dcc.Graph(id='total-sales-per-region')               
        ])
   ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
           dcc.Graph(id='total-volume-per-region')
        ])
    ]),
    html.Br(),
    dbc.Row([
        dcc.Graph(id='total-bags-per-region')
    ]),
    html.Br(),
    dbc.Row([
        dcc.Graph(id='sales-per-year')
    ])
])

region_layout = html.Div([
    dbc.Row([
        dbc.Col([
            dcc.DatePickerRange(
                id="date-range",
                min_date_allowed=df["sale_date"].min(),
                max_date_allowed=df["sale_date"].max(),
                start_date=df["sale_date"].min(),
                end_date=df["sale_date"].max(),
                display_format='YYYY-MM-DD'
               #style={'color': '#ffffff', 'background-color': 'rgba(0,0,0,0)'},
            )
        ])
    ]),
    html.Br(),
    dbc.Row([
        dcc.Graph(id='scatter-plot')
    ]),
    html.Br(),
    dbc.Row([
        dcc.Graph(id='funnel-chart')
    ])

    ])


bags_layout = html.Div([
    dbc.Row([
        dcc.Graph(id='time-series')
    ])

])
about_layout = html.Div([

    dbc.Container([
        html.H6("About Avocado Sales Analytics", style={'color':'#008B8B'}),
        html.P("""
            Welcome to the Avocado Sales Analytics Dashboard. This project aims to provide comprehensive insights into avocado sales data 
            across different regions and time periods. The dashboard offers various interactive features to help users explore and understand 
            the sales trends and patterns.
        """, style={'color':'#008B8B'}),
        
        html.H6("Features", style={'color':'#008B8B'}),
        html.Ul([
            html.Li("Interactive date range selection for customized data analysis."),
            html.Li("Key performance indicators (KPIs) showing total sales, total bags, and total avocados."),
            html.Li("Visualizations including scatter plots, choropleth maps, and box plots."),
            html.Li("Funnel chart for detailed sales analysis."),
        ], style={'color':'#008B8B'}),
        
        html.H6("Data Processing and Analysis", style={'color':'#008B8B'}),
        html.P("""
            The data processing involves extracting avocado sales data from a PostgreSQL database, transforming it to derive meaningful metrics, 
            and loading it into the dashboard for visualization. Data is aggregated by regions and dates to provide various insights.
        """, style={'color':'#008B8B'}),
        
        html.H6("Technologies Used", style={'color':'#008B8B'}),
        html.Ul([
            html.Li("Dash and Plotly for creating interactive visualizations."),
            html.Li("Pandas for data manipulation."),
            html.Li("SQLAlchemy for interacting with the PostgreSQL database."),
            html.Li("PostgreSQL as the data storage backend."),
        ], style={'color':'#008B8B'}),
        
        html.H6("Insights and Findings", style={'color':'#008B8B'}),
        html.P("""
            The dashboard provides valuable insights into avocado sales trends. For example, it reveals the regions with the highest sales, 
            seasonal patterns in avocado consumption, and the relationship between total bags and total sales.
        """, style={'color':'#008B8B'}),
        
        html.H6("Future Work", style={'color':'#008B8B'}),
        html.P("""
            Future improvements could include adding more granular data, incorporating machine learning models for sales forecasting, 
            and enhancing the user interface with additional interactive elements.
        """, style={'color':'#008B8B'}),
        
        html.H6("Project Team", style={'color':'#008B8B'}),
        html.Ul([
            html.Li("Ahona Victor - Data Engineer"),
            html.Li("Kishoyian Kish - Frontend Developer"),
            html.Li("Kishoyian Kish - Project Manager"),
        ], style={'color':'#008B8B'}),
        
        # html.H6("Contact Information", style={'color':'#008B8B'}),
        # html.P("""
        #     For further questions or collaboration, please contact the project team at [its.mkato@gmail.com].
        # """, style={'color':'#008B8B'}),
    ])

])

contact_layout = html.Div([
  dbc.Container([
        html.H6("Contact Us", style={'color':'#008B8B'}),
        html.P("""
            If you have any questions, feedback, or would like to collaborate on the Avocado Sales Analytics project, 
            please reach out to us. We are always open to discussing new ideas and potential improvements.
        """, style={'color':'#008B8B'}),
        
        html.H6("Contact Information", style={'color':'#008B8B'}),
        html.P("""
            Email: its.mkato@gmail.com
        """, style={'color':'#008B8B'}),
        
        html.P("""
            Phone: +254 746267663
        """, style={'color':'#008B8B'}),
        
        html.P("""
            Address: 123 Juja, Kiambu, Kenya
        """, style={'color':'#008B8B'}),
        
        html.H6("Follow Us", style={'color':'#008B8B'}),
        html.P("""
            Stay updated with the latest news and updates by following us on social media:
        """, style={'color':'#008B8B'}),
        
        html.Ul([
            html.Li("Twitter: @AvocadoAnalytics"),
            html.Li("LinkedIn: Avocado Sales Analytics"),
            html.Li("GitHub: AvocadoAnalytics"),
        ], style={'color':'#008B8B'}),
    ])
])

app.layout = html.Div([
     navbar,
     html.Br(),
     dcc.Location(id='url'),
     html.Div(id='page-content'),
     dcc.Interval(
      id='interval-component',
      interval=60000,  # Update every second
      n_intervals=0
)
])

#callback function to return pages depending on which has been selected
@app.callback(Output('page-content','children'),
              Input('url','pathname'))
def update_pages_depending_on_the_pathname(pathname):
    if pathname == "/home":
        return home_layout
    elif pathname == "/region":
        return region_layout
    elif pathname == "/bags":
        return bags_layout
    elif pathname == "/about":
        return about_layout
    else:
        return contact_layout

#callback functions for displaying my KPIS
#total sales
@app.callback(Output('total-sales','children'),
              Input('interval-component','n_intervals'))
def update_total_sales(n):
    if n is None:
        return "Hello try again nigga"
    with engine.connect() as connection:
        t = text(
            '''
             with dim_sales as (
               select 
                   sum(("AveragePrice" * "Total Volume")) as total_sales
               from avo_data
               )
             select 
                 total_sales
             from dim_sales
            '''    )
        df = pd.read_sql(t, con=engine)

        if df is not None:
            total_sales = df['total_sales'].iloc[0]
            total_sales = '${:.2f}'.format(total_sales)
        return total_sales

#total bags
@app.callback(Output('total-bags','children'),
              Input('interval-component','n_intervals'))
def update_total_bags_sold(n):
    if n is None:
        return "Hello try again nigga"
    with engine.connect() as connection:
        t = text(
            '''
              with dim_bags as (
              select 
                 sum("Total Bags") as total_bags
              from avo_data
              )
              select
                 total_bags
              from dim_bags
    
            '''
        )
        df = pd.read_sql(t, con=engine)

        if df is not None:
            total_bags = df['total_bags']
            total_bags = total_bags.apply(lambda x: '{:.2f}'.format(x))
            #otal_bags = '{:.2f}'.format(total_bags)
        return total_bags
#total number of avocados
@app.callback(Output('total-avocados','children'),
              Input('interval-component','n_intervals'))
def update_total_avocados_sold(n):
    if n is None:
        return "Hey nigga please try again"
    with engine.connect() as connection:
        t = text(
            '''
            with dim_volume as (
               select 
                  sum("Total Volume") as total_volume
               from avo_data
               )
               select
                  total_volume
               from dim_volume
            '''
        )

        df = pd.read_sql(t, con=engine)
        if df is not None:
            total_volume = df['total_volume']
            total_volume = total_volume.apply(lambda x: '{:.2f}'.format(x))
        return total_volume
    
    #callback for plotting the charts
    #we start with the total-sales-per-region
@app.callback(Output('total-sales-per-region','figure'),
              Input('interval-component','n_intervals'))
def plot_total_sales_per_region(n):
     if n is None:
          raise PreventUpdate
     #open connection to the datasource
     with engine.connect() as connection:
            t = text('''
                     with dim_total_sales_per_region as (
                     select 
                         "region",
                         sum(("AveragePrice" * "Total Volume")) as total_sales
                     from avo_data
                     group by region
                     )
                     select 
                       region,
                       total_sales
                     from dim_total_sales_per_region
                     order by total_sales desc
                     ''')
            df = pd.read_sql(t, con=engine)
            if df is not None:
                 fig = px.bar(
                        df,
                        x='region',
                        y='total_sales',
                        title='Total Sales',
                        labels={'region': 'Region', 'total_sales': 'Total Sales'},
                        template='plotly_dark',
                        color_discrete_sequence=['#008B8B'] 
                       )
                 fig.update_traces(width=0.8)  # Adjust bar width
            
                 fig.update_layout(
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            font_color='#ffffff',
                            title_font_color='#008B8B',
                            xaxis=dict(showgrid=False, tickfont=dict(color='#008B8B')),  # X-axis color
                            yaxis=dict(showgrid=False, tickfont=dict(color='#008B8B')), # Y-axis color
                            font=dict(color='#008B8B')
                        )

            return fig      
#callback function for total volume per region
@app.callback(Output('total-volume-per-region','figure'),
             Input('interval-component','n_intervals'))
def plot_total_per_region(n):
    if n is None:
        raise PreventUpdate
    #connect to the data source
    with engine.connect() as connection:
        t = text(
            '''
            with dim_total_volume_per_region as (
            select 
                "region",
                sum("Total Volume") as total_volume
            from avo_data
            group by "region"
            )
            select
                "region",
                total_volume
            from dim_total_volume_per_region;
                        
            '''
        )
        df = pd.read_sql(t, con=engine)
        if df is not None:
            # Create line chart using Plotly Express with template
         fig = px.line(df, x='region', y='total_volume', title='Total Volume', template='plotly_dark')
         
         # Customize layout
         fig.update_layout(
             font_color='#008B8B',
             title_font_color='#008B8B',
             plot_bgcolor='rgba(0,0,0,0)',
             paper_bgcolor='rgba(0,0,0,0)',
             xaxis=dict(
                 showgrid=False,
                 tickfont=dict(color='#008B8B')  # X-axis tick font color
             ),
             yaxis=dict(
                 showgrid=False,
                 tickfont=dict(color='#008B8B')  # Y-axis tick font color
             ),
             font=dict(color='#008B8B')  # Font color for all text elements
         )
         fig.update_traces(line=dict(color='#008B8B'))  # Set line color

    return fig

#callback function for total bags per region pie chart
@app.callback(Output('total-bags-per-region','figure'),
              Input('interval-component','n_intervals'))
def plot_total_bags_per_region(n):
    if n is None:
        raise PreventUpdate
    #connect to the data source
    with engine.connect() as connection:
        t = text(
            '''
            with dim_total_bags as (
                select 
                    "region",
                    sum("Total Bags") as total_bags
                from avo_data
                group by "region"  -- Include "region" in GROUP BY clause
            )
            select 
                region,
                total_bags
            from dim_total_bags;
                        
                        '''
        )
        df = pd.read_sql(t, con=engine)
        if df is not None:
         # Plot pie chart using Plotly Express with template and customizations
        # Plot pie chart using Plotly Express with template and customizations
         fig = px.pie(df, values='total_bags', names='region', title='Total Bags Per Region', template='plotly_dark')
        
        # Customize chart colors and size
        fig.update_traces(
            marker=dict(
                colors=px.colors.sequential.Viridis  # Use Viridis color scale
            ),
            textinfo='percent+label',  # Display percentage and label
            textposition='inside',  # Place text inside pie slices
            hoverinfo='label+percent',  # Show label and percentage on hover
            pull=[0.1, 0.1, 0.1, 0.1, 0.1],  # Pull slices away from center
            hole=0.3  # Create a donut hole in the center
        )
        
        # Customize layout
        fig.update_layout(
            title_font_color='#008B8B',  # Title color
            font_color='#008B8B',  # Font color for other text
            legend_title_font_color='#008B8B',  # Legend title color
            plot_bgcolor='rgba(0,0,0,0)',  # Transparent plot background
            paper_bgcolor='rgba(0,0,0,0)',  # Transparent paper background
            width=1000,  # Width of the chart
            height=800,  # Height of the chart
        )
        
        return fig
    
#callback function for plotting the pivot table
@app.callback(Output('sales-per-year','figure'),
              Input('interval-component','n_intervals'))
def plot_pivot_table_for_sales_per_year(n):
    if n is None:
        raise PreventUpdate
    #connect to the data source
    with engine.connect() as connection:
        t = text('''
                 with dim_total_sales_per_year as(
                 select 
                     "year" as year,
                      sum(("AveragePrice" * "Total Volume")) as total_sales
                 from avo_data
                 group by year
                 )
                 select 
                   year,
                   total_sales
                 from dim_total_sales_per_year
                 ''')
        df = pd.read_sql(t, con=engine)

        if df is not None:
             fig = px.pie(df, values='total_sales', names='year', title='Total sales per  year', template='plotly_dark')


              # Customize chart colors and size
             fig.update_traces(
                 marker=dict(
                     colors=px.colors.sequential.Viridis  # Use Viridis color scale
                 ),
                 textinfo='percent+label',  # Display percentage and label
                 textposition='inside',  # Place text inside pie slices
                 hoverinfo='label+percent',  # Show label and percentage on hover
                 pull=[0.1, 0.1, 0.1, 0.1, 0.1],  # Pull slices away from center
                 hole=0.3  # Create a donut hole in the center
             )
             
             # Customize layout
             fig.update_layout(
                 title_font_color='#008B8B',  # Title color
                 font_color='#ffffff',  # Font color for other text
                 legend_title_font_color='#008B8B',  # Legend title color
                 plot_bgcolor='rgba(0,0,0,0)',  # Transparent plot background
                 paper_bgcolor='rgba(0,0,0,0)',  # Transparent paper background
                 width=1000,  # Width of the chart
                 height=800,  # Height of the chart
             )
             
        return fig
        
 #callback function for the regions dropdown
 #lets make some sctter plot now
@app.callback(Output('scatter-plot','figure'),
               [Input('date-range','start_date'),
                Input('date-range','end_date')])
def plot_scatter_plot(start_date, end_date):
    if start_date is None or end_date is None:
        raise PreventUpdate
    t = text(
        '''
            with dim_region_sales_per_date as (
            select 
                "Date" as sale_date,
                "region" as region,
                sum("Total Bags") as total_bags,
                sum("AveragePrice" * "Total Volume") as total_sales
            from avo_data
            where "Date" between :start_date and :end_date
            group by sale_date, region
        )
        select 
            sale_date,
            region,
            total_bags,
            total_sales
        from dim_region_sales_per_date
        order by sale_date asc
    '''       
    )
    df = pd.read_sql(t, con=engine, params={'start_date': start_date, 'end_date': end_date})
    if df is not None:
        # Plot choropleth map using Plotly Express
    # Plot scatter plot using Plotly Express
      # Plot scatter plot using Plotly Express
     fig = px.scatter(
        df,
        x='total_bags',  # total_bags on x-axis
        y='total_sales',  # total_sales on y-axis
        color='region',  # color by region
        size='total_bags',  # size of markers by total_bags
        template='plotly_dark',  # Use dark theme
        labels={'total_bags': 'Total Bags', 'total_sales': 'Total Sales', 'region': 'Region'},
        title='Scatter Plot of Total Sales vs Total Bags'
    )
    
    fig.update_layout(
        margin={'r': 10, 't': 50, 'l': 10, 'b': 50},  # Adjust margins as needed
        plot_bgcolor='rgba(0, 0, 0, 0)',  # Transparent plot background
        paper_bgcolor='rgba(0, 0, 0, 0)',  # Transparent paper background
        font_color='#008B8B'  # Font color for all text elements
    )
    
    
    return fig

#callback function for the funnel chart 
@app.callback(Output('funnel-chart','figure'),
               [Input('date-range','start_date'),
                Input('date-range','end_date')])
def plot_funnel_chart(start_date, end_date):
    if start_date is None or end_date is None:
        raise PreventUpdate
    t = text(
        '''
            with dim_region_sales_per_date as (
            select 
                "Date" as sale_date,
                "region" as region,
                sum("Total Bags") as total_bags,
                sum("AveragePrice" * "Total Volume") as total_sales
            from avo_data
            where "Date" between :start_date and :end_date
            group by sale_date, region
        )
        select 
            sale_date,
            region,
            total_bags,
            total_sales
        from dim_region_sales_per_date
        order by sale_date asc
    '''       
    )
    df = pd.read_sql(t, con=engine, params={'start_date': start_date, 'end_date': end_date})
    if df is not None:
         # Plot funnel chart using Plotly Express
      # Create the box plot using Plotly Express
     fig = px.box(df, x='region', y='total_sales', title='Box Plot of Total Sales by Region')

    # Customize the layout
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='#ffffff',
        title_font_color='#008B8B',
        xaxis=dict(showgrid=False, tickfont=dict(color='#008B8B')),  # X-axis color
        yaxis=dict(showgrid=False, tickfont=dict(color='#008B8B')),  # Y-axis color
        font=dict(color='#008B8B')
    )

    return fig

#callback function to plot time series analysis for total sales and total bags
@app.callback(Output('time-series','figure'),
              Input('interval-component','n_intervals')
              )
def plot_update_time_series(n):
    if n is None:
        raise PreventUpdate 
    with engine.connect() as connection:
        t = text(
           '''
               with dim_region_sales_per_date as (
               select 
                   "Date" as sale_date,
                   "region" as region,
                   sum("Total Bags") as total_bags,
                   sum("AveragePrice" * "Total Volume") as total_sales
               from avo_data
               group by sale_date, region
           )
           select 
               sale_date,
               region,
               total_bags,
               total_sales
           from dim_region_sales_per_date
           order by sale_date asc
       '''       
       )
    df = pd.read_sql(t, con=engine)
    if df is not None:
         # Create the time series plot using Plotly Express
        fig = px.line(df, x='sale_date', y='total_sales',
                      labels={'sale_date': 'Date', 'value': 'Total'},
                      title='Time Series of Total Sales and Total Bags',
                      template='plotly_dark')
        for trace in fig.data:
            trace.line.color = '#008B8B'  # Set line color
            trace.line.width = 2           # Set line width
            trace.connectgaps = True  

        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',  # Transparent background
            paper_bgcolor='rgba(0,0,0,0)',  # Transparent plot area
            font_color='#008B8B',     # Set font color
            title_font_color='#008B8B',  # Set title font color
            title_font_size=20,       # Set title font size
            title_x=0.5,              # Center the title horizontally
            title_y=0.9,              # Position the title vertically
            margin=dict(l=50, r=50, t=50, b=50),  # Adjust margins
        )


        return fig
  
if __name__ == "__main__":
    app.run_server(debug=True)