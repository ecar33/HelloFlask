import unittest

from app import create_app, db
from app.config import TestingConfig
from models import Movie, User

class WatchlistTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestingConfig)

        with self.app.app_context():
            user = User(name='Test', username='test')
            user.set_password('123')
            movie = Movie(title='Test Movie Title', year='2019')
            db.session.add_all([user, movie])
            db.session.commit()

            self.client = self.app.test_client() 
            self.runner = self.app.test_cli_runner()  

    def tearDown(self):
        return
    
    def test_app_exist(self):
        self.assertIsNotNone(self.app)

    def test_app_is_testing(self):
        self.assertTrue(self.app.config['TESTING'])

    # def test_404_page(self):
    #     with self.app.app_context():
    #         response = self.client.get('/nothing')
    #         data = response.get_data(as_text=True)
    #         self.assertIn('Page Not Found - 404', data)
    #         self.assertIn('Go Back', data)
    #         self.assertEqual(response.status_code, 404) 
    
    # def test_index_page(self):
    #     with self.app.app_context():
    #         response = self.client.get('/')
    #         data=response.get_data(as_text=True)
    #         self.assertIn('')

    # def test_movie_page(self):
    #     with self.app.app_context():
    #         response = self.client.get('/movies')
    #         data = response.get_data(as_text=True)
    #         self.assertIn('Test\'s List', data)
    #         self.assertIn('Test Movie Title', data)
    #         self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()