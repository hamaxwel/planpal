from flask import Flask, render_template, request, redirect, url_for, jsonify
from datetime import datetime

app = Flask(__name__)

# Sample data structure (You will likely use a database in production)
tasks = [
    {'id': 1, 'task_name': 'Task 1', 'date': '2024-12-06', 'time': '08:00', 'category': 'Work', 'status': 'in-progress'},
    {'id': 2, 'task_name': 'Task 2', 'date': '2024-12-06', 'time': '10:00', 'category': 'Personal', 'status': 'completed'},
]

# Helper function to calculate percentage
def calculate_percentage(numerator, denominator):
    if denominator == 0:
        return 0
    return (numerator / denominator) * 100

@app.route('/')
def index():
    completed_tasks = [task for task in tasks if task['status'] == 'completed']
    in_progress_tasks = [task for task in tasks if task['status'] == 'in-progress']
    
    completed_percentage = calculate_percentage(len(completed_tasks), len(tasks))
    remaining_tasks = len(in_progress_tasks)
    remaining_percentage = calculate_percentage(len(in_progress_tasks), len(tasks))
    
    return render_template(
    'index.html', 
    tasks=tasks, 
    completed_tasks=completed_tasks, 
    in_progress_tasks=in_progress_tasks,
    completed_percentage=completed_percentage, 
    remaining_tasks=remaining_tasks,
    remaining_percentage=remaining_percentage,
    rounded_remaining_percentage=round(remaining_percentage, 2) 
)


@app.route('/add', methods=['POST'])
def add_task():
    task_name = request.form.get('task_name')
    date = request.form.get('date')
    time = request.form.get('time')
    category = request.form.get('category')
    completed = 'completed' if request.form.get('completed') else 'in-progress'
    
    new_task = {
        'id': len(tasks) + 1,
        'task_name': task_name,
        'date': date,
        'time': time,
        'category': category,
        'status': completed
    }
    tasks.append(new_task)
    return redirect(url_for('index'))

@app.route('/delete/<int:task_id>', methods=['GET'])
def delete_task(task_id):
    global tasks
    tasks = [task for task in tasks if task['id'] != task_id]
    return redirect(url_for('index'))

@app.route('/complete/<int:task_id>', methods=['GET'])
def complete_task(task_id):
    for task in tasks:
        if task['id'] == task_id:
            task['status'] = 'completed'
            break
    return redirect(url_for('index'))

@app.route('/edit/<int:task_id>', methods=['GET'])
def edit_task(task_id):
    task = next((task for task in tasks if task['id'] == task_id), None)
    if task:
        return render_template('edit_task.html', task=task)
    return redirect(url_for('index'))

@app.route('/update/<int:task_id>', methods=['POST'])
def update_task(task_id):
    task_name = request.form.get('task_name')
    date = request.form.get('date')
    time = request.form.get('time')
    category = request.form.get('category')
    status = request.form.get('status')
    
    for task in tasks:
        if task['id'] == task_id:
            task['task_name'] = task_name
            task['date'] = date
            task['time'] = time
            task['category'] = category
            task['status'] = status
            break
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
