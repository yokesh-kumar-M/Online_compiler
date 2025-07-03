from django.test import TestCase, Client
from django.urls import reverse
import json

class CompilerTestCase(TestCase):
    def setUp(self):
        self.client = Client()
    
    def test_index_page_loads(self):
        """Test that the main page loads successfully"""
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Advanced Python Online Compiler')
    
    def test_simple_code_execution(self):
        """Test basic code execution"""
        code = 'print("Hello, World!")'
        response = self.client.post(reverse('run_code'), {
            'code': code,
            'mode': 'safe'
        })
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertIn('Hello, World!', data['output'])
    
    def test_code_validation(self):
        """Test code validation functionality"""
        # Valid code
        valid_code = 'print("Valid code")'
        response = self.client.post(reverse('validate_code'), {
            'code': valid_code
        })
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['valid'])
        
        # Invalid code (restricted import)
        invalid_code = 'import os\nos.system("ls")'
        response = self.client.post(reverse('validate_code'), {
            'code': invalid_code
        })
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertFalse(data['valid'])
    
    def test_save_and_load_code(self):
        """Test save and load functionality"""
        code = 'print("Test code")'
        filename = 'test.py'
        
        # Save code
        response = self.client.post(reverse('save_code'), {
            'code': code,
            'filename': filename
        })
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        
        # Load code
        response = self.client.post(reverse('load_code'), {
            'filename': filename
        })
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertEqual(data['code'], code)
    
    def test_list_saved_codes(self):
        """Test listing saved codes"""
        # Save a code first
        self.client.post(reverse('save_code'), {
            'code': 'print("test")',
            'filename': 'test.py'
        })
        
        # List saved codes
        response = self.client.get(reverse('list_saved_codes'))
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertIn('test.py', data['files'])
    
    def test_get_examples(self):
        """Test getting code examples"""
        response = self.client.get(reverse('get_examples'))
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.content)
        self.assertTrue(data['success'])
        self.assertIn('examples', data)
        self.assertIn('hello_world', data['examples'])
    
    def test_security_restrictions(self):
        """Test security restrictions"""
        # Test restricted imports
        dangerous_codes = [
            'import os\nos.system("ls")',
            'import subprocess\nsubprocess.call("ls")',
            'exec("print(1)")',
            'eval("1+1")',
        ]
        
        for code in dangerous_codes:
            response = self.client.post(reverse('run_code'), {
                'code': code,
                'mode': 'safe'
            })
            self.assertEqual(response.status_code, 200)
            
            data = json.loads(response.content)
            self.assertFalse(data['success'])
    
    def test_error_handling(self):