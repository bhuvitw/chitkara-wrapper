import json
import datetime
import math
from fetch import get_attendance_data
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

# --- CONFIGURATION ---
TIMETABLE_FILE = "./config/timetable.json"
TARGET = 75.0  # Target Attendance Percentage

console = Console()

def load_timetable():
    try:
        with open(TIMETABLE_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def get_subject_schedule(timetable, subject_name):
    """
    Returns a list of (DayIndex, Weight) for a given subject.
    e.g., [(0, 2), (4, 1)] -> Monday 2hr, Friday 1hr
    """
    schedule = []
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    
    for day_name, classes in timetable.items():
        if day_name not in days: continue
        day_idx = days.index(day_name)
        
        for cls in classes:
            # Fuzzy match subject name
            if cls['subject'].lower() in subject_name.lower() or subject_name.lower() in cls['subject'].lower():
                schedule.append((day_idx, cls['weight']))
    
    # Sort by day index to keep order (Mon -> Sun)
    return sorted(schedule, key=lambda x: x[0])

def find_future_dates(schedule, hours_needed):
    """
    Simulates future dates until 'hours_needed' is satisfied.
    Returns a formatted string of dates: "Mon(01), Wed(03)"
    """
    if not schedule:
        return "No classes found"

    dates_found = []
    hours_accumulated = 0
    today = datetime.date.today()
    
    # Simulate up to 6 months (safeguard against infinite loops)
    for d in range(1, 180): 
        future_date = today + datetime.timedelta(days=d)
        day_idx = future_date.weekday()
        
        # Check if this day has the class
        for sched_day, weight in schedule:
            if day_idx == sched_day:
                # Found a class!
                date_str = future_date.strftime("%a")
                dates_found.append(f"{date_str}")
                hours_accumulated += weight
                
                if hours_accumulated >= hours_needed:
                    return ", ".join(dates_found)
                    
    return ", ".join(dates_found) + "..."

def main():
    with console.status("[bold green]Fetching Attendance & Simulating Future...", spinner="dots"):
        attendance = get_attendance_data()
        timetable = load_timetable()
    
    if not attendance or not timetable:
        console.print("[bold red]❌ Data missing. Run fetch.py or check timetable.json.[/bold red]")
        return

    # Create the Rich Table
    table = Table(title=f"🎓 ATTENDANCE STRATEGY (Target: {TARGET}%)", box=box.ROUNDED)

    table.add_column("Subject", style="cyan", no_wrap=True)
    table.add_column("Stats", justify="center", style="magenta")
    table.add_column("%", justify="right", style="green")
    table.add_column("Action Plan", style="white")

    for sub, info in attendance.items():
        att = info['attended']
        dell = info['delivered']
        pct = info['percent']
        
        schedule = get_subject_schedule(timetable, sub)
        
        # --- THE MATH CORE ---
        
        status_text = ""
        pct_style = "green" if pct >= TARGET else "bold red"

        if pct < TARGET:
            # DANGER ZONE
            target_ratio = TARGET / 100.0
            if target_ratio >= 1.0: 
                needed_hours = 999 
            else:
                needed_hours = math.ceil((target_ratio * dell - att) / (1 - target_ratio))
            
            dates_str = find_future_dates(schedule, needed_hours)
            
            if not schedule:
                status_text = f"[bold red]🚨 DANGER (+{needed_hours})[/bold red] [dim]Timetable missing[/dim]"
            else:
                status_text = f"[bold red]🚨 DANGER (+{needed_hours})[/bold red] [yellow]Attend: {dates_str}[/yellow]"

        else:
            # SAFE ZONE
            target_ratio = TARGET / 100.0
            bunkable_hours = int((att / target_ratio) - dell)
            
            if bunkable_hours <= 0:
                status_text = "[bold yellow]⚠️ BORDERLINE (0 bunks)[/bold yellow]"
                pct_style = "yellow"
            else:
                dates_str = find_future_dates(schedule, bunkable_hours)
                if not schedule:
                    status_text = f"[bold green]✅ SAFE (-{bunkable_hours})[/bold green] [dim]Timetable missing[/dim]"
                else:
                    status_text = f"[bold green]✅ SAFE (-{bunkable_hours})[/bold green] [blue]Bunk: {dates_str}[/blue]"

        # Add row to table
        table.add_row(
            Text(sub[:35], overflow="ellipsis"),
            f"{att}/{dell}",
            f"[{pct_style}]{pct:.1f}%[/{pct_style}]",
            status_text
        )

    console.print(table)

if __name__ == "__main__":
    main()