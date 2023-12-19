from flask import url_for
from app.todo.models import Todo

def test_todo_model():
    todo = Todo(title='Test Todo', description='Test description')
    assert todo.title == 'Test Todo'
    assert todo.description == 'Test description'
    assert not todo.complete

def test_create_todo(client, init_database, log_in_default_user):
    data = {
        'title': 'New Task',
        'description': 'Description of the new task'
    }
    response = client.post(url_for('todo_bp.create_todo'), data=data, follow_redirects=True)
    assert response.status_code == 200

def test_update_todo(client, init_database, log_in_default_user, todo):
    response = client.get(url_for('todo_bp.update_todo', todo_id=1), follow_redirects=True)
    updated_todo = Todo.query.filter_by(id=todo[0].id).first()
    assert response.status_code == 200
    assert updated_todo.complete

def test_delete_todo(client, init_database, log_in_default_user, todo):
    todo_id_to_delete = todo[0].id
    response = client.post(url_for('todo_bp.delete_todo', todo_id=todo_id_to_delete), follow_redirects=True)
    deleted_todo = Todo.query.get(todo_id_to_delete)
    assert response.status_code == 200
    assert deleted_todo is None