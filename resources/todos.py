from flask import Blueprint, abort, g, make_response

import json

from playhouse.flask_utils import get_object_or_404

from flask_restful import (Resource, Api, reqparse, fields,
                               url_for, marshal, marshal_with)

from auth import basic_auth

import models

todo_fields = {
    'id': fields.Integer,
    'name': fields.String
}


class TodoList(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'name',
            required=True,
            help='No name provided',
            location=['form', 'json']
        )

        super().__init__()

    def get(self):
        todos = [marshal(todo, todo_fields) for todo in models.Todo.select()]
        return todos

    @marshal_with(todo_fields)
    @basic_auth.login_required
    def post(self):
        """Allows user to posts new todo's"""
        args = self.reqparse.parse_args()
        todo = models.Todo.create(user=g.user, **args)
        return todo, 201, {'location': url_for('resources.todos.todo', id=todo.id)}


class Todo(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument(
            'name',
            required=True,
            help='No name provided',
            location=['form', 'json']
        )
        super().__init__()

    @marshal_with(todo_fields)
    def get(self, id):
        """Gets all the posted todo's"""
        todo = get_object_or_404(models.Todo, models.Todo.id == id)
        return todo

    @marshal_with(todo_fields)
    @basic_auth.login_required
    def put(self, id):
        """allows user to edit posted todo's"""
        args = self.reqparse.parse_args()
        query = get_object_or_404(models.Todo, models.Todo.id == id).update(**args)
        query.execute()
        return models.Todo.get(models.Todo.id == id), 200,\
               {'location': url_for('resources.todos.todo', id=id)}

    @basic_auth.login_required
    def delete(self, id):
        """allows user to delete todo's"""
        try:
            todo = models.Todo.select().where(
                models.Todo.id == id
            ).get()
        except models.Todo.DoesNotExist:
            return make_response(json.dumps(
                {'error': 'Todo can not be deleted'}
            ), 403)

        todo.delete_instance()
        return ('', 204,
            {'location': url_for('resources.todos.todos')}
            )


todos_api = Blueprint('resources.todos', __name__)
api = Api(todos_api)
api.add_resource(
    TodoList,
    '/api/v1/todos',
    endpoint='todos'
)

api.add_resource(
    Todo,
    '/api/v1/todos/<int:id>',
    endpoint='todo'
)