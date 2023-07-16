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
# Example menu function to select a team
#def select_team():
    teams = ['All', 'ABS', 'PAW', 'FA','GG','YP']  # Example team options
    team_choice = st.sidebar.selectbox("Team", teams)
    return team_choice

# Example menu function to select a position
def select_position():
    positions = ['All', 'Position 1', 'Position 2', 'Position 3']  # Example position options
    position_choice = st.sidebar.selectbox("Position", positions)
    return position_choice

# Example menu function to select a game type
def select_game_type():
    game_types = ['reg', 'all', 'playoff']  # Example game type options
    game_type_choice = st.sidebar.selectbox("Game Type", game_types)
    return game_type_choice

# Example menu function to select a statistic
def select_stat():
    stats = ['bat', 'pitch', 'field']  # Example statistic options
    stat_choice = st.sidebar.selectbox("Statistic", stats)
    return stat_choice

# Example menu function to select a qualification
def select_qualification():
    qualifications = ['0', '25', '50', '100', '250', '500']  # Example qualification options
    qual_choice = st.sidebar.selectbox("Qualification", qualifications)
    return qual_choice

# Example menu function to select a handedness
def select_handedness():
    handedness = ['all', 'R', 'L']  # Example handedness options
    handedness_choice = st.sidebar.selectbox("Handedness", handedness)
    return handedness_choice

# Example menu function to select a player status
def select_player_status():
    player_statuses = ['any', 'rookie']  # Example player status options
    player_status_choice = st.sidebar.selectbox("Player Status", player_statuses)
    return player_status_choice

# Example menu function to select a time span
#def select_time_span():
    time_spans = ['yrs', 'dates']  # Example time span options
    time_span_choice = st.sidebar.selectbox("Time Span", time_spans)
    return time_span_choice


# Example menu function to select a record type
def select_record_type():
    record_types = ['All', 'Type 1', 'Type 2']  # Example record type options
    record_type_choice = st.sidebar.selectbox("Record Type", record_types)
    return record_type_choice

# Example menu function to select a record type
#def select_type_type():
    #type_types = ['0', '1', '2', '3']  # Example record type options
    #type_type_choice = st.sidebar.selectbox("0-dashboard 1-standard 2-advanced", type_types)
    #return type_type_choice

def calculate_rank_all_players(data, statistics):
    return data[statistics].rank(pct=True)

def plot_ranking1(selected_players,data,pos):
    # 设置图表样式
    plt.style.use('seaborn')

    # 图表尺寸
    #fig, axes = plt.subplots(nrows=4, ncols=3, figsize=(9, 6))
    
    # 创建渐进色映射
    cmap = mcolors.LinearSegmentedColormap.from_list('custom_cmap', [(0, 'blue'), (1, 'red')])

    # 搜寻指标
    statistics = ['WRC+', 'WOBA', 'BB%', 'K%', 'OPS', 'BABIP', 'HR','H','R','ISO']
    
    # 计算子图的行数和列数
    num_rows = (len(statistics) + 2) // 3  # 加2是为了考虑标题的占用
    num_cols = min(len(statistics), 3)

    # 图表尺寸
    fig, axes = plt.subplots(nrows=num_rows, ncols=num_cols, figsize=(9, 6))
    
    # 设置背景为透明
    for ax in axes.flatten():
        ax.patch.set_alpha(0)
        ax.set_xticks([])
        ax.set_yticks([])

    # 使用@st.cache_data註釋的函數將被緩存，避免重複計算
    rank_all_players = calculate_rank_all_players(data, statistics)

    for i, statistic in enumerate(statistics):
        for j, player_name in enumerate(selected_players):
            # 选择特定球员的数据
            player_data = data[data['Name'] == player_name]
            if len(player_data) > 0:
                # 计算特定球员在其他指标上的排名百分比
                rank_data = rank_all_players.loc[player_data.index, statistic].iloc[0]
                rank_data = round(rank_data, 2)
                #st.text(rank_data)
                # 计算行和列索引
                row = i // 3
                col = i % 3

                # 创建子图
                ax = axes[row, col]

                # 图表设置
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

                # 添加百分比文本在圆形标记内部
                circle_radius = height * 0.5
                circle_x = rank_data + circle_radius / 2  # 圆形标记的x坐标
                circle_y = 0  # 圆形标记的y坐标
                circle_color = cmap(rank_data)  # 使用渐进色映射确定圆形标记的颜色
                circle = Circle((circle_x, circle_y), radius=circle_radius, color=circle_color)
                ax.add_patch(circle)
                ax.text(circle_x, circle_y, f'{int((rank_data) * 100)}', ha='center', va='center', color='white', weight='bold')

                # 设置标题
                ax.set_title(f"{statistic}: {player_data[statistic].iloc[0]}")
            else:
                # 没有数据时将子图设为透明
                ax.patch.set_alpha(0)
    # 删除多余的子图
    for i in range(len(statistics), num_rows * num_cols):
        row = i // num_cols
        col = i % num_cols
        fig.delaxes(axes[row, col])
    fig.suptitle(', '.join(selected_players)+'  '+str(pos), fontsize=16, fontweight='bold')
    fig.text(0.5, 0.92, '1995 Regular Season PR  (Min 25 PA)', fontsize=12, ha='center')
    fig.text(0.5, 0.33, 'Ranked by Pos  (Min 25 IP)', fontsize=12, ha='center')

    # 显示图表
    st.pyplot(fig)

#def plot_ranking(selected_players, data, pos):
    num_rows = len(selected_players)  # Each player has one row for subplot
    num_cols = 1  # One column for subplot
    fig, axes = plt.subplots(nrows=num_rows, ncols=num_cols, figsize=(10, 5 * num_rows))

    cmap = mcolors.LinearSegmentedColormap.from_list('custom_cmap', [(0, 'blue'), (1, 'red')])
    
    # 設置透明背景並移除刻度線
    for ax in axes.ravel():
        ax.patch.set_alpha(0)
        ax.set_xticks([])
        ax.set_yticks([])
    # 搜寻指标
    statistics = ['WRC+', 'WOBA', 'BB%', 'K%', 'OPS', 'BABIP', 'HR','H','R','ISO']
    # 使用@st.cache_data註釋的函數將被緩存，避免重複計算
    rank_all_players = calculate_rank_all_players(data, statistics)
    
    # 将axes转换为numpy数组
    axes = np.array(axes)
    
    # 如果只有一行子图，则将axes转换为一维数组
    if num_rows == 1:
        axes = axes.ravel()

    for j, player_name in enumerate(selected_players):
        player_data = data[data['Name'] == player_name]
        
        if num_rows > 1:
            ax = axes[j]  # 每個球員對應一個子圖
        else:
            ax = axes
        
        if len(player_data) > 0:
            # 繪製圖表
            # 计算特定球员在其他指标上的排名百分比
            rank_data = rank_all_players.loc[player_data.index, statistics].iloc[0]
            rank_data = round(rank_data, 2)
            #st.text(rank_data)
            # 计算行和列索引
            row = j // 3
            col = j % 3

            # 创建子图
            ax = axes[row, col]

            # 图表设置
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

            # 添加百分比文本在圆形标记内部
            circle_radius = height * 0.5
            circle_x = rank_data + circle_radius / 2  # 圆形标记的x坐标
            circle_y = 0  # 圆形标记的y坐标
            circle_color = cmap(rank_data)  # 使用渐进色映射确定圆形标记的颜色
            circle = Circle((circle_x, circle_y), radius=circle_radius, color=circle_color)
            ax.add_patch(circle)
            ax.text(circle_x, circle_y, f'{int((rank_data) * 100)}', ha='center', va='center', color='white', weight='bold')

            # 设置标题
            ax.set_title(f"{statistic}: {player_data[statistic].iloc[0]}")
        else:
            # 没有数据时将子图设为透明
            ax.patch.set_alpha(0)
    
    # 刪除多餘的子圖
    for i in range(num_players, num_rows * 2):
        if num_rows > 1:
            fig.delaxes(axes[i])
    
    # 顯示圖表
    st.pyplot(fig)    
# Streamlit app
def main():
    # Set page title and layout
    st.set_page_config(page_title="Filter", layout="wide")

    # Display the title in the sidebar
    st.sidebar.title("Filter")
    
    # Get start year from user input
    startyear = st.text_input("Enter the year:")

    # Get end year from user input
    endyear = startyear

    # Use menu functions to select values for remaining variables
    stat = select_stat()
    team = 'All'
    qual = '0'
    pos = select_position()
    games = select_game_type()
    rightleft = select_handedness()
    playerstatus = select_player_status()
    timespan = 'yrs'
    startdate = '1995-03-10'
    enddate = '1995-10-27'
    records = 'all'
    types = [0, 1, 2]
    
    
    # Data dictionary to store different data
    data_dict = {}
    
    
    
    # Check if CSV file exists
    filename = f"{startyear}_{endyear}_{stat}_{games}_{playerstatus}.csv"
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
                
                time.sleep(3)
                # Generate the URL with selected variable values
                http = f"https://atl-01.statsplus.net/tmbl/playerstats/?sort=ops,d&stat={stat}&team={team}&qual={qual}&pos={pos}&more=true&games={games}&startyear={startyear}&endyear={endyear}&rightleft={rightleft}&playerstatus={playerstatus}&timespan={timespan}&startdate={startdate}&enddate={enddate}&records={records}&type={type_value}"

                # Send HTTP request and scrape the webpage (code for scraping is commented out)
                response = requests.get(http)
                soup = BeautifulSoup(response.content, 'html.parser')
                # 解析网页内容并提取球员统计数据
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
            
            # Save data to CSV
            data.to_csv(filename, index=False)
            data_dict['data'] = data
    
            # Display the final data
            #st.dataframe(data)
        else:
            st.text("輸入年份並按下RUN")
    
    if "data" in data_dict:
        data = data_dict["data"]

        # 获取所有球员名称列表
        player_names = data['Name'].unique().tolist()
        # 选择要显示的球员
        selected_players = st.multiselect('Select a player', player_names)
        pos = ""
    
        
        if st.button("Plot"):
            if selected_players:
                #pos = data[data['Name'] == selected_players[0]]['Pos'].iloc[0]
                #plot_ranking(selected_players, data,pos)
                for player_name in selected_players:
                    #player_data = data[data['Name'] == player_name]
                    #statistic = select_stat()
                    #rank_data = calculate_rank_all_players(data, statistic)
                    #fig = plot_chart(player_data, statistic, rank_data)
                    #st.pyplot(fig)
                    #plot_ranking(selected_players,data,pos)
                    
                    player_data = data[data['Name'] == player_name]
                    plot_ranking1([player_name], data, pos)
                    

            
        # Delete CSV file when Streamlit is closed
        #if not get_session_state()['filename_deleted']:
            #st.text("Waiting for Streamlit to close...")
            #if st.button("Delete CSV"):
                #filename = f"{startyear}_{endyear}.csv"
                #os.remove(filename)
                #get_session_state()['filename_deleted'] = True
        
        


if __name__ == "__main__":
    main()
