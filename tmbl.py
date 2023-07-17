import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv
import os
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as patches
from matplotlib.patches import Circle
import time
import numpy as np


# Create or get the session state
def get_session_state():
    if 'session_state' not in st.session_state:
        st.session_state.session_state = {
            'filename_deleted': False
        }
    return st.session_state.session_state


# Example menu function to select a game type
def select_game_type():
    game_types = ['reg', 'all', 'playoff']  # Example game type options
    game_type_choice = st.sidebar.selectbox("Game Type", game_types)
    return game_type_choice

# Example menu function to select a statistic
def select_stat():
    stats = ['bat', 'pitch', 'field']  # Example statistic options
    stat_choice = st.sidebar.selectbox("Role stats", stats)
    return stat_choice

# Example menu function to select a qualification
def select_qualification():
    qualifications = ['0', '20', '50', '100', '150', '200','500','Qual']  # Example qualification options
    qual_choice = st.sidebar.selectbox("Qualification", qualifications)
    return qual_choice

# Example menu function to select a handedness
def select_handedness():
    handedness = ['all', 'R', 'L']  # Example handedness options
    handedness_choice = st.sidebar.selectbox("vs R/L", handedness)
    return handedness_choice

# Example menu function to select a player status
def select_player_status():
    player_statuses = ['any', 'rookie']  # Example player status options
    player_status_choice = st.sidebar.selectbox("Player Status", player_statuses)
    return player_status_choice


# Example menu function to select a record type
def select_record_type():
    record_types = ['All', 'Type 1', 'Type 2']  # Example record type options
    record_type_choice = st.sidebar.selectbox("Record Type", record_types)
    return record_type_choice


def select_statics(data):
    excluded_stats = ['#', 'Name', 'AGE', 'Role', 'Team', 'Pos']  # Columns of statistics to be excluded
    stats = [col for col in data.columns if col not in excluded_stats] 
    stat_choices = st.sidebar.multiselect("Statistic (最少四項)", stats)
    return stat_choices
    
def calculate_rank_all_players(data, statistics, stat):
    rank_data = data[statistics].rank(pct=True)
    
    if stat == 'pitch':
        pitch_cols = ['L', 'BB/9', 'HR/9', 'HR/FB%', 'ERA', 'FIP', 'XFIP', 'BS', 'ER', 'BB', 'HP', 'WP', 'BK', 'BB%', 'AVG', 'WHIP', 'BABIP']
        pitch_cols_to_reverse = list(set(statistics).intersection(set(pitch_cols)))
        if pitch_cols_to_reverse:
            rank_data[pitch_cols_to_reverse] = 1 - rank_data[pitch_cols_to_reverse]
    elif stat == 'bat':
        bat_cols = ['K%', 'K']
        bat_cols_to_reverse = list(set(statistics).intersection(set(bat_cols)))
        if bat_cols_to_reverse:
            rank_data[bat_cols_to_reverse] = 1 - rank_data[bat_cols_to_reverse]
    
    return rank_data

  
def plot_ranking(selected_players,data,pos,statistics,stat):
    # Set the plot style
    plt.style.use('seaborn')

    
    # Create a progressive color map
    cmap = mcolors.LinearSegmentedColormap.from_list('custom_cmap', [(0, 'blue'), (1, 'red')])

    
    
    # Calculate the number of rows and columns for subplots
    num_rows = (len(statistics) + 2) // 3  #Adding 2 is to consider the occupation of the title
    num_cols = min(len(statistics), 3)

    # Set the figure size
    fig, axes = plt.subplots(nrows=num_rows, ncols=num_cols, figsize=(9, 6))
    
    # Set the background as transparent
    for ax in axes.flatten():
        ax.patch.set_alpha(0)
        ax.set_xticks([])
        ax.set_yticks([])

    # 使用@st.cache_data註釋的函數將被緩存，避免重複計算
    rank_all_players = calculate_rank_all_players(data, statistics,stat)

    for i, statistic in enumerate(statistics):
        for j, player_name in enumerate(selected_players):
            #  Select data for the specific player
            player_data = data[data['Name'] == player_name]
            if len(player_data) > 0:
                # Calculate the ranking percentile for the player in other statistics
                rank_data = rank_all_players.loc[player_data.index, statistic].iloc[0]
                rank_data = rank_all_players.loc[player_data.index, statistic].iloc[0]
                rank_data = round(rank_data, 2)
                #st.text(rank_data)
                # Calculate the row and column indices
                row = i // 3
                col = i % 3

                # Create subplots
                ax = axes[row, col]

                # Set the plot settings
                height = 0.25
                ax.barh(0, 1, 1, color='gray', alpha=0)
                bar = patches.Rectangle((0, -height / 6), 1, height/3, color='gray')
                ax.add_patch(bar)

                circle_step_radius = height * 0.22
                circle_step1 = Circle((0, 0), radius=circle_step_radius, color='gray')
                ax.add_patch(circle_step1)
                circle_step2 = Circle((0.5, 0), radius=circle_step_radius, color='gray')
                ax.add_patch(circle_step2)
                circle_step3 = Circle((1, 0), radius=circle_step_radius, color='gray')
                ax.add_patch(circle_step3)

                # Add the percentage text inside the circular marker
                circle_radius = height * 0.5
                circle_x = rank_data + circle_radius / 2  
                circle_y = 0  
                circle_color = cmap(rank_data) 
                circle = Circle((circle_x, circle_y), radius=circle_radius, color=circle_color)
                ax.add_patch(circle)
                ax.text(circle_x, circle_y, f'{int((rank_data) * 100)}', ha='center', va='center', color='white', weight='bold')

                # Set the title
                ax.set_title(f"{statistic}: {player_data[statistic].iloc[0]}")
            else:
                # Set the subplot as transparent when there is no data
                ax.patch.set_alpha(0)
    # Remove extra subplots
    for i in range(len(statistics), num_rows * num_cols):
        row = i // num_cols
        col = i % num_cols
        fig.delaxes(axes[row, col])
    # Adjust the position and spacing of subplots
    fig.subplots_adjust(top=0.85, bottom=0.25, hspace=0.5)
    fig.suptitle(', '.join(selected_players)+'  '+str(pos), fontsize=16, fontweight='bold')
    fig.text(0.5, 0.05, '', fontsize=12, ha='center')
    fig.text(0.5, 0.92, f'{startyear} Regular Season PR', fontsize=12, ha='center')
    fig.text(0.5, 0.05, '', fontsize=12, ha='center')

    # Display the plot
    st.pyplot(fig)

def get_position(data, stat):
    if stat == 'pitch':
        return data['Role'].iloc[0]
    elif stat == 'bat':
        return data['Pos'].iloc[0]
    else:
        return ''
   
# Streamlit app
def main():
    # Set page title and layout
    st.set_page_config(page_title="TMBL", layout="wide")
    
    # Set the title in the center of the page
    st.markdown('<h1 style="text-align: center; font-weight: bold;">TMBL savant?</h1>', unsafe_allow_html=True)
    

    # Display the title in the sidebar
    st.sidebar.title("Filter")
    
    # Get start year from user input
    startyear = st.text_input("Enter the year:")

    # Get end year from user input
    endyear = startyear

    # Use menu functions to select values for remaining variables
    stat = select_stat()
    team = 'All'
    qual = select_qualification()
    pos = 'All'
    games = select_game_type()
    rightleft = select_handedness()
    playerstatus = select_player_status()
    timespan = 'yrs'
    startdate = '1995-03-10'
    enddate = '1995-10-27'
    records = 'All'
    types = [0, 1, 2]
    
    
    # Data dictionary to store different data
    data_dict = {}
    
    
    
    # Check if CSV file exists
    filename = f"{startyear}_{endyear}_{stat}_{games}_{playerstatus}_{qual}_{rightleft}.csv"
    if os.path.exists(filename):
        # Load data from CSV
        data = pd.read_csv(filename)
        data_dict['data'] = data
        st.sidebar.text("Download completed")
    else:
        # "Run" button
        run_button = st.sidebar.button("Run")
        if run_button:
            for i in range(3):
            
                type_value = types[i % len(types)]
                
                # Generate the URL with selected variable values
                http = f"https://atl-01.statsplus.net/tmbl/playerstats/?sort=ops,d&stat={stat}&team={team}&qual={qual}&pos={pos}&more=true&games={games}&startyear={startyear}&endyear={endyear}&rightleft={rightleft}&playerstatus={playerstatus}&timespan={timespan}&startdate={startdate}&enddate={enddate}&records={records}&type={type_value}"

                # Send HTTP request and scrape the webpage (code for scraping is commented out)
                response = requests.get(http)
                soup = BeautifulSoup(response.content, 'html.parser')
                # Parse the webpage content and extract player statistics data
                table = soup.find('table')
                data = pd.read_html(str(table))[0]
                st.text(f"Fetching data... Progress: {i + 1}/3")
         
                # Store the data in the data dictionary
                data_dict[f"data{i+1}"] = data

            # Example: Access the data
            if "data1" in data_dict:
                data1 = data_dict["data1"]
            if "data2" in data_dict:
                data2 = data_dict["data2"]
            if "data3" in data_dict:
                data3 = data_dict["data3"]
               
            data = pd.merge(data1,data2, on='Name',how='outer',suffixes=('', '_x'))
            data = pd.merge(data,data3, on='Name',how='outer',suffixes=('', '_y'))
            data=data.filter(regex=r'^(?!.*(_x|_y)$)')
            # Save data to CSV
            data.to_csv(filename, index=False)
            data_dict['data'] = data
    
            # Display the final data
            #st.dataframe(data)
        else:
            st.text("輸入年份並按下RUN")
    
    if "data" in data_dict:
        data = data_dict["data"]

        # Get a list of all player names
        player_names = data['Name'].unique().tolist()
        # Select the players to display
        selected_players = st.multiselect('Select a player', player_names)
        pos = ""
        # Select the statistics
        statistics = select_statics(data)
        # Check if stat_choices is empty
        if not statistics:
            st.warning("請選取Statistic")
            return
        if st.button("Plot"):
            if selected_players:
                for player_name in selected_players:
                    player_data = data[data['Name'] == player_name]
                    pos = get_position(player_data, stat)  
                    plot_ranking([player_name], data, pos, statistics,stat)
                    

            
        # Delete CSV file when Streamlit is closed
        if not get_session_state()['filename_deleted']:
            st.text("Waiting for Streamlit to close...")
            if st.button("Delete CSV"):
                #filename = f"{startyear}_{endyear}_{stat}_{games}_{playerstatus}.csv"
                os.remove(filename)
                get_session_state()['filename_deleted'] = True
        
        


if __name__ == "__main__":
    main()
