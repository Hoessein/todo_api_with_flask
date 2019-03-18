import base64
import json
import unittest

import models
from app import app

MODELS = models.Todo, models.User


TEST_HEADERS = {
    'content-type': 'application/json',

}

TEST_USER = {
    'username': 'test_user',
    'email': 'test_@email.com',
    'password': 'test_password'
}


TEST_AUTH = b'test_user:test_password'


class SetUpClass(unittest.TestCase):
    def setUp(self):

        self.app = app.test_client()

        models.initialize()

        self.user = models.User.create_user(
            TEST_USER['username'],
            TEST_USER['email'],
            TEST_USER['password']
        )

        self.headers = {
            'content-type': TEST_HEADERS['content-type'],
            'Authorization': 'Basic %s' % base64.b64encode(TEST_AUTH).decode()
        }

    def tearDown(self):
        models.DATABASE.drop_tables(MODELS)
        models.DATABASE.close()


class TestPages(SetUpClass):
    def test_home_page(self):
        """tests if the homepage shows up"""
        resp = self.app.get('/',  headers=self.headers)
        self.assertEqual(resp.status_code, 200)

    def test_todo_page(self):
        """tests if the to_do page shows up """
        resp = self.app.get('/api/v1/todos',  headers=self.headers)
        self.assertEqual(resp.status_code, 200)

    def test_token_page(self):
        """tests if the token page can be accessed"""
        resp = self.app.get('/api/v1/users/token',  headers=self.headers)
        self.assertEqual(resp.status_code, 200)


class TestUserResource(SetUpClass):
    def test_users_post_methods(self):
        """Tests if a user can be created"""
        resp = self.app.post(
            '/api/v1/users',
            headers=self.headers,
            data=json.dumps({
                'username': 'test',
                'email': 'test@todo.com',
                'password': 'password',
                'verify_password': 'password'
            }))

        self.assertEqual(resp.status_code, 201)

        data = {'username': 'test'}

        self.assertEqual(json.loads(resp.data), data)

    def test_users_post_bad_password(self):
        """Tests if error message is shown
        when te user attempts to create a user
        with the wrong password confirmation"""
        resp = self.app.post(
            '/api/v1/users',
            headers=self.headers,
            data=json.dumps({
                'username': 'test',
                'email': 'test@todo.com',
                'password': 'pasword',
                'verify_password': 'password'
            }))

        self.assertEqual(resp.status_code, 400)

        data = {'error': 'Password and password verification do not match'}

        self.assertEqual(json.loads(resp.data), data)


class TestTodoResource(SetUpClass):
    def test_todolist_get_method(self):
        """Tests if all to_do's are shown"""
        self.todo = models.Todo.create(
            name='test',
            user=self.user
        )

        self.todo1 = models.Todo.create(
            name='test2',
            user=self.user
        )

        resp = self.app.get('/api/v1/todos',
                            headers=self.headers
                            )
        data = {'id': 1, 'name': 'test'}
        data2 = {'id': 2, 'name': 'test2'}

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(json.loads(resp.data), [data, data2])

    def test_todo_get_method(self):
        """tests if a single to_do shows up"""
        self.todo = models.Todo.create(
            name='test',
            user=self.user
        )

        resp = self.app.get('/api/v1/todos/1',
                            headers=self.headers
                            )

        data = {'id': 1, 'name': 'test'}

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(json.loads(resp.data), data)

    def test_todos_post_method(self):
        """tests if a to_do can be posted"""
        resp = self.app.post('/api/v1/todos',
                             headers=self.headers,
                             data=json.dumps(
                                 {'name': 'test'}
                                 ))

        self.assertEqual(resp.status_code, 201)

        data = {'id': 1, 'name': 'test'}

        self.assertEqual(json.loads(resp.data), data)
        self.assertEqual(models.Todo.name, 'test')
        self.assertEqual(models.Todo.id, 1)

    def test_todo_put_method(self):
        """Tests if a to_do can be edited"""
        self.todo = models.Todo.create(
            name='test',
            user=self.user
        )

        resp = self.app.put('/api/v1/todos/1',
                            headers=self.headers,
                            data=json.dumps({
                                'id': '1',
                                'name': 'test_edited'})
                            )

        self.assertEqual(resp.status_code, 200)

        data = {'id': 1, 'name': 'test_edited'}

        self.assertEqual(json.loads(resp.data), data)

    def test_todo_delete_method(self):
        """Tests if a to_do can be deleted"""
        self.test_task = models.Todo.create(
            name='test_todo1',
            user=self.user)

        resp = self.app.delete('/api/v1/todos/1',
                               headers=self.headers
                               )

        self.assertEqual(resp.status_code, 204)

    def test_unavailable_todo_delete_method(self):
        """"Attempts to delete a to_do that doesn't exist"""
        self.test_task = models.Todo.create(
            name='test_todo1',
            user=self.user)

        resp = self.app.delete('/api/v1/todos/888888',
                               headers=self.headers
                               )

        self.assertEqual(resp.status_code, 403)


if __name__ == "__main__":
    unittest.main()
