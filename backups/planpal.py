from flask import Flask, render_template, request, redirect, jsonify
import json
import os
from datetime import datetime

app = Flask(__name__)

# Global variable to store tasks
tasks = []

# Load tasks from a JSON file
def load_tasks(filename="tasks.json"):
    global tasks
    try:
        with open(filename, "r") as file:
            tasks = json.load(file)
    except FileNotFoundError:
        tasks = []
    except Exception as e:
        print(f"Error loading tasks: {e}")
        tasks = []

# Save tasks to a JSON file
def save_tasks(filename="tasks.json"):
    try:
        with open(filename, "w") as file:
            json.dump(tasks, file, indent=4)
    except Exception as e:
        print(f"Error saving tasks: {e}")

# Generate a backup of the tasks
backup_dir = "backups"
os.makedirs(backup_dir, exist_ok=True)

def backup_tasks(filename="tasks.json"):
    backup_file = os.path.join(backup_dir, "tasks_backup.json")
    try:
        with open(backup_file, "w") as file:
            json.dump(tasks, file, indent=4)
    except Exception as e:
        print(f"Error creating backup: {e}")

@app.route("/")
def home():
    load_tasks()  # Load tasks at the beginning
    return render_template("index.html", tasks=tasks)

@app.route("/add", methods=["POST"])
def add_task():
    task_name = request.form["task_name"]
    date = request.form["date"]
    time = request.form["time"]
    category = request.form["category"]
    completed = request.form.get("completed") == "true"
    amount = request.form.get("amount", "")
    transaction_description = request.form.get("transaction_description", "")

    # Validate form input
    if not task_name or not date or not time:
        return redirect("/")  # Redirect if task_name, date, or time is missing

    task = {
        "task_name": task_name,
        "date": date,
        "time": time,
        "category": category,
        "status": "completed" if completed else "in-progress",
        "amount": amount,
        "transaction_description": transaction_description
    }

    tasks.append(task)
    save_tasks()  # Save tasks to the file
    backup_tasks()  # Backup the tasks
    return redirect("/")

@app.route("/complete/<int:task_id>")
def complete_task(task_id):
    if 0 <= task_id < len(tasks):
        tasks[task_id]["status"] = "completed"
        save_tasks()  # Save tasks after modification
        backup_tasks()  # Backup the tasks
    return redirect("/")

@app.route("/in-progress/<int:task_id>")
def in_progress_task(task_id):
    if 0 <= task_id < len(tasks):
        tasks[task_id]["status"] = "in-progress"
        save_tasks()  # Save tasks after modification
        backup_tasks()  # Backup the tasks
    return redirect("/")

@app.route("/delete/<int:task_id>")
def delete_task(task_id):
    if 0 <= task_id < len(tasks):
        tasks.pop(task_id)  # Remove task at the given index
        save_tasks()  # Save tasks after modification
        backup_tasks()  # Backup the tasks
    return redirect("/")

@app.route("/edit/<int:task_id>", methods=["GET", "POST"])
def edit_task(task_id):
    if 0 <= task_id < len(tasks):
        task = tasks[task_id]
        if request.method == "POST":
            # Update task data from form
            task["task_name"] = request.form["task_name"]
            task["date"] = request.form["date"]
            task["time"] = request.form["time"]
            task["category"] = request.form["category"]
            task["status"] = "completed" if request.form.get("completed") == "true" else "in-progress"
            task["amount"] = request.form.get("amount", "")
            task["transaction_description"] = request.form.get("transaction_description", "")
            save_tasks()  # Save tasks after modification
            backup_tasks()  # Backup the tasks
            return redirect("/")
        
        return render_template("edit.html", task=task)  # Pass task to the template for editing
    return redirect("/")  # If task_id is invalid, redirect to home

@app.route("/summary")
def summary():
    completed_tasks = [task for task in tasks if task['status'] == 'completed']
    in_progress_tasks = [task for task in tasks if task['status'] == 'in-progress']
    return render_template("summary.html", completed_tasks=completed_tasks, in_progress_tasks=in_progress_tasks)

@app.route("/data/visualize")
def visualize():
    completed = sum(1 for task in tasks if task["status"] == "completed")
    in_progress = len(tasks) - completed
    return jsonify({"completed": completed, "in_progress": in_progress})

@app.route("/filter", methods=["GET"])
def filter_tasks():
    category = request.args.get('category', '')
    filtered_tasks = [task for task in tasks if category.lower() in task["category"].lower()]
    return render_template("index.html", tasks=filtered_tasks)

@app.errorhandler(Exception)
def handle_error(error):
    # Log the error for debugging purposes
    print(f"Error occurred: {error}")
    return render_template("error.html", error_message=str(error)), 500

if __name__ == "__main__":
    load_tasks()  # Load tasks when the app starts
    app.run(debug=True)
