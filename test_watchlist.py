import unittest
from app import create_app
from app.extensions import db
from app.config import TestingConfig
from app.models import GameDetails, Movie, User

class WatchlistTestCase(unittest.TestCase):

    # Setup run before every test
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

    # Teardown run after every test
    def tearDown(self):
        with self.app.test_request_context():
            db.session.remove()
            db.drop_all()
            db.session.close()

    # Helper function to login
    def login(self):
        self.client.post('/login', data=dict(
            username='test',
            password='123'
        ), follow_redirects=True)

    # Helper function to log out
    def logout(self):
        self.client.post('/logout', follow_redirects=True)

    # Testing app functionality
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
        self.assertIn('ecar33\'s List', data)
        self.assertIn('Test Movie Title', data)
        self.assertEqual(response.status_code, 200)
    
    def test_games_page(self):
        response = self.client.get('/games', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('ecar33\'s List', data)
        self.assertIn('Test Game Title', data)
        self.assertEqual(response.status_code, 200)
    
    def test_add_movie(self):
        self.login()
        response = self.client.post('/movies/add', data=dict(
            title='New Movie',
            year='2019'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item added', data)
        self.assertIn('New Movie', data)

        response = self.client.post('/movies/add', data=dict(
            title='New Movie 2',
            year='200'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item added', data)
        self.assertNotIn('New Movie 2', data)

        response = self.client.post('/movies/add', data=dict(
            title='',
            year='1234'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item added', data)
    
    def test_delete_movie(self):
        self.login()
        response = self.client.post('/movies/delete/1', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item deleted', data)

        response = self.client.post('movies/delete2', follow_redirects=True)
        data=response.get_data(as_text=True)
        self.assertNotIn('Item deleted', data)

    def test_edit_movie(self):
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
    
    def test_signup_form(self):
        response = self.client.post('/signup', data=dict(
            username='testuser',
            password='12345678',
            confirm_password='12345678'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('User succesfully created', data)

        response = self.client.post('/signup', data=dict(
            username='testuser',
            password='12345678',
            confirm_password='12345678'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('User succesfully created!', data)
        self.assertIn('Username already exists, use a different one', data)

        response = self.client.post('/signup', data=dict(
            username='testuser',
            password='123',
            confirm_password='123'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('User succesfully created!', data)

        response = self.client.post('/signup', data=dict(
            username='tr',
            password='123456789',
            confirm_password='1234578'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('User succesfully created!', data)

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

    # Testing CLI
    def test_initdb_command(self):
        result = self.runner.invoke(args=['initdb'])
        self.assertIn('Initialized database.', result.output)

    def test_admin_command(self):
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            result = self.runner.invoke(args=['admin', '--username', 'grey', '--password', '123'])
            self.assertIn('Creating user...', result.output)
            self.assertIn('Done.', result.output)
            self.assertEqual(User.query.count(), 1)
            self.assertEqual(User.query.first().username, 'grey')
            self.assertTrue(User.query.first().validate_password('123'))

    def test_admin_command_update(self):
        with self.app.app_context():
            result = self.runner.invoke(args=['admin', '--username', 'peter', '--password', '456'])
            self.assertIn('Updating user...', result.output)
            self.assertIn('Done.', result.output)
            self.assertEqual(User.query.count(), 1)
            self.assertEqual(User.query.first().username, 'peter')
            self.assertTrue(User.query.first().validate_password('456'))

if __name__ == '__main__':
    unittest.main()