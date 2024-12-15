import matplotlib.pyplot as plt
import pandas as pd
import glob
import os
import mplcursors
from matplotlib.animation import FuncAnimation

def gantt_chart_visualiser(filename):
    # Read data from the file, assuming "Priority" and "Dependencies" columns exist
    data = pd.read_csv(filename, names=["JobID", "Start", "End", "Priority", "Dependencies"])

    # Determine the scheduling type
    basename = os.path.basename(filename)
    p_basename = "Unknown Scheduling"
    if basename == "FCFSSchedulingResults.csv":
        p_basename = "FCFS Scheduling"
    elif basename == "PrioritySchedulingResults.csv":
        p_basename = "Priority Scheduling"
    elif basename == "SJFSchedulingResults.csv":
        p_basename = "SJF Scheduling"
    elif basename == "RRSchedulingResults.csv":
        p_basename = "RR Scheduling"

    # Calculate metrics
    total_time = max(data["End"]) - min(data["Start"])
    total_exec_time = sum(data["End"] - data["Start"])
    cpu_utilization = (total_exec_time / total_time) * 100
    wait_times = data["Start"] - min(data["Start"])
    avg_wait_time = wait_times.mean()
    turnaround_times = data["End"] - data["Start"]
    avg_turnaround_time = turnaround_times.mean()

    # Set up the Gantt chart figure
    fig, ax = plt.subplots()
    ax.set_xlabel('Time')
    ax.set_title(f'Gantt Chart for {p_basename}')

    # Define Y-axis ticks for each job
    tick_positions = [10 * idx + 5 for idx in range(0, len(data), 5)]
    tick_labels = data["JobID"][::5]
    ax.set_yticks(tick_positions)
    ax.set_yticklabels(tick_labels)

    # Display metrics as a table on the plot
    metrics_data = [
        ["CPU Utilization (%)", f"{cpu_utilization:.2f}"],
        ["Average Wait Time", f"{avg_wait_time:.2f}"],
        ["Average Turnaround Time", f"{avg_turnaround_time:.2f}"]
    ]
    table = ax.table(cellText=metrics_data, colLabels=["Metric", "Value"], cellLoc='center', loc='right')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.5)  # Adjust the scale if needed

    # Add tooltips
    cursor = mplcursors.cursor(ax, hover=True)
    cursor.connect(
        "add", lambda sel: sel.annotation.set_text(
            f"Job ID: {data.iloc[sel.index]['JobID']}\n"
            f"Start: {data.iloc[sel.index]['Start']}\n"
            f"End: {data.iloc[sel.index]['End']}\n"
            f"Duration: {data.iloc[sel.index]['End'] - data.iloc[sel.index]['Start']}"
        )
    )

    # Animation function with priority and dependency indicators
    def update(frame):
        ax.clear()

        # Plot up to the current time frame with priority borders
        for idx, row in data.iterrows():
            if row["Start"] <= frame:
                job_duration = min(row["End"], frame) - row["Start"]
                color = 'blue' if row["Priority"] == 'High' else 'green'
                edgecolor = 'red' if row["Priority"] == 'High' else 'black'
                linewidth = 2 if row["Priority"] == 'High' else 1
                ax.broken_barh([(row["Start"], job_duration)], (10 * idx, 9),
                               facecolors=color, edgecolor=edgecolor, linewidth=linewidth)
                ax.text(row["Start"] + job_duration / 2, 10 * idx + 5, row["JobID"], color='white', fontweight='bold')

        # Draw dependency arrows
        for idx, row in data.iterrows():
            if pd.notna(row["Dependencies"]):
                dependencies = [int(dep) for dep in row["Dependencies"].split(",")]
                for dep in dependencies:
                    dep_row = data[data["JobID"] == dep].iloc[0]
                    ax.annotate(
                        '', xy=(row["Start"], 10 * idx + 5), xytext=(dep_row["End"], 10 * data[data["JobID"] == dep].index[0] + 5),
                        arrowprops=dict(arrowstyle="->", color='gray', lw=1)
                    )

        # Update labels and title
        ax.set_xlabel('Time')
        ax.set_yticks(tick_positions)
        ax.set_yticklabels(tick_labels)
        ax.set_title(f'Gantt Chart for {p_basename} - Time: {frame}')

        # Re-apply metrics table on animation frame update
        table = ax.table(cellText=metrics_data, colLabels=["Metric", "Value"], cellLoc='center', loc='right')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 1.5)

    # Set up animation with total frames equivalent to the total time
    ani = FuncAnimation(fig, update, frames=range(int(total_time)), repeat=False, interval=100)

    # Show the animated plot
    plt.show()

# Directory containing the CSV files
csv_folder = "/Users/tanishka/Desktop/DSA Project"  # Replace with your CSV folder path

# Loop through each CSV file and visualize
for csv_file in glob.glob(os.path.join(csv_folder, "*.csv")):
    print(f"Visualizing Gantt chart for: {csv_file}")
    gantt_chart_visualiser(csv_file)
