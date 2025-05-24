📊 Real-Time Dashboard: CPU Utilization and System Performance

A dynamic web-based dashboard built with Dash (Plotly) and psutil for real-time monitoring of your system's CPU, RAM, Disk, and Network performance. This tool provides instant insights into your computer's health and resource utilization, including a detailed view of top processes.

✨ Features
1. Real-Time Monitoring: Continuously updates CPU, RAM, Disk, and Network usage metrics.

2. Interactive Gauges: Visualizes current resource utilization with intuitive gauges.

3. Historical Trends: Displays line graphs showing resource usage over time for better analysis.

4. Detailed Process List: Presents a sortable table of top processes, including CPU %, Memory %, Disk I/O, status, username, and even process architecture (x64/x86).

5. User-Friendly Interface: Built with Dash, offering a clean and responsive web interface.

6. Cross-Platform Compatibility: Leverages psutil for broad OS support (Windows, macOS, Linux).

🚀 Getting Started
Follow these steps to set up and run the Real-Time System Performance Dashboard on your local machine.

Prerequisites
Make sure you have the following installed:

Python 3.11 or higher
pip (Python package manager)

Installation
Clone the repository:
git clone https://github.com/SahilSingh8848/real_time_cpu_monitor.git
cd real_time_cpu_monitor

Create a virtual environment (recommended):
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate

Install dependencies: pip install -r requirements.txt

▶️ Running the Application
Once all dependencies are installed, run the dashboard: python app.py

Then open your browser and go to: http://127.0.0.1:8050

👤 Author
Sahil Singh
GitHub: https://github.com/SahilSingh8848
