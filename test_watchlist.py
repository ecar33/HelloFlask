import unittest

from app import create_app
from app.extensions import db
from app.config import TestingConfig
from app.models import GameDetails, Movie, User

class WatchlistTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestingConfig)

        with self.app.app_context():
            db.create_all()
            user = User(name='Test', username='test')
            user.set_password('123')
            movie = Movie(title='Test Movie Title', year='2019')
            game = GameDetails(name='Test Game Title', metacritic='79')
            db.session.add_all([user, movie, game])
            db.session.commit()

            self.client = self.app.test_client() 
            self.runner = self.app.test_cli_runner()
    
    def login(self):
        self.client.post('/login', data=dict(
            username='test',
            password='123'
        ), follow_redirects=True)
    
    def logout(self):
        self.client.post('/logout', follow_redirects=True)
        
    def tearDown(self):
        with self.app.test_request_context():
            db.drop_all()
            db.session.close()
    
    def test_app_exist(self):
        self.assertIsNotNone(self.app)

    def test_app_is_testing(self):
        self.assertTrue(self.app.config['TESTING'])

    def test_login(self):
        response = self.client.post('/login', data=dict(
            username='test',
            password='123'
        ), follow_redirects=True)

        data = response.get_data(as_text=True)
        self.assertIn('Test sucessfully logged in.', data)
        self.assertIn('Index', data)
        self.assertIn('Logout', data)
        self.assertIn('Settings', data)

        response = self.client.get('/movies', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Edit', data)
        self.assertIn('Delete', data)
        self.assertIn('Add', data)
        self.assertIn('form method="POST"', data)

        response = self.client.post('/login', data=dict(
            username='test',
            password='abc'
        ), follow_redirects=True)

        data = response.get_data(as_text=True)
        self.assertNotIn('Test sucessfully logged in.', data)
        self.assertIn('Invalid username or password', data)

        
        response = self.client.post('/login', data=dict(
            username='',
            password=''
        ), follow_redirects=True)

        self.assertNotIn('Test sucessfully logged in.', data)

    def test_404_page(self):
        response = self.client.get('/nothing')
        data = response.get_data(as_text=True)
        self.assertIn('Page Not Found - 404', data)
        self.assertIn('Go Back', data)
        self.assertEqual(response.status_code, 404) 
    
    def test_index_page(self):
        response = self.client.get('/')
        data=response.get_data(as_text=True)
        self.assertIn('Welcome to my awesome homepage.', data)

    def test_movie_page(self):
        response = self.client.get('/movies', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Evan\'s List', data)
        self.assertIn('Test Movie Title', data)
        self.assertEqual(response.status_code, 200)
    
    def test_games_page(self):
        response = self.client.get('/games', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Evan\'s List', data)
        self.assertIn('Test Game Title', data)
        self.assertEqual(response.status_code, 200)
    
    def test_create_item(self):
        self.login()
        response = self.client.post('/movies/add', data=dict(
            title='New Movie',
            year='2019'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item added', data)
        self.assertIn('New Movie', data)

        response = self.client.post('/movies/add', data=dict(
            title='New Movie2',
            year=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item added', data)
        self.assertNotIn('New Movie2', data)
    
    def test_delete_item(self):
        self.login()
        response = self.client.post('/movies/delete/1', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item deleted', data)

        response = self.client.post('movies/delete2', follow_redirects=True)
        data=response.get_data(as_text=True)
        self.assertNotIn('Item deleted', data)

    def test_edit_item(self):
        self.login()
        response = self.client.post('/movies/edit/1', data=dict(
            title='New Movie Name',
            year='1999'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Successfully updated!', data)
        
        response = self.client.post('/movies/edit/1', data=dict(
            title='New Movie Name',
            year=''
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Invalid input.', data)
    
    def test_login_protect(self):
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertNotIn('Logout', data)
        self.assertNotIn('Settings', data)

        response = self.client.get('/movies', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Edit', data)
        self.assertNotIn('Delete', data)
        self.assertNotIn('Add', data)
    
    def test_logout(self):
        self.login()
        response = self.client.get('/logout', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Goodbye', data)
        self.assertNotIn('Settings', data)
        self.assertNotIn('Logout', data)

        response= self.client.get('/movies', follow_redirects=True)
        self.assertNotIn('Edit', data)
        self.assertNotIn('Delete', data)
        self.assertNotIn('Add', data)
    
    def test_settings(self):
        self.login()
        response = self.client.post('/settings', data=dict(
            name='Test1'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Name change successful.', data)
        self.assertIn('Test1', data)

if __name__ == '__main__':
    unittest.main()