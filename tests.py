"""
Test Suite for E-Rate Prospector Project

This file contains tests to verify data collection functionality
for the progress report submission.
"""

import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from src.data_collection.fetch_erate_data import ERateDataCollector


class TestERateDataCollection(unittest.TestCase):
    """Test cases for E-Rate data collection."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.collector = ERateDataCollector()
    
    def test_initialization(self):
        """Test that collector initializes correctly."""
        self.assertIsNotNone(self.collector)
        self.assertEqual(
            self.collector.base_url,
            "https://opendata.usac.org/resource/avi8-svp9.json"
        )
    
    def test_initialization_with_token(self):
        """Test initialization with app token."""
        collector = ERateDataCollector(app_token="test_token")
        self.assertEqual(
            collector.session.headers.get('X-App-Token'),
            'test_token'
        )
    
    @patch('src.data_collection.fetch_erate_data.requests.Session.get')
    def test_fetch_data_success(self, mock_get):
        """Test successful data fetch."""
        # Mock API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                'entity_name': 'Test School District',
                'funding_year': '2024',
                'state': 'CA',
                'applicant_type': 'School',
                'total_commitment': '50000'
            }
        ]
        mock_get.return_value = mock_response
        
        # Fetch data
        df = self.collector.fetch_data(funding_year=2024, limit=1)
        
        # Assertions
        self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df), 1)
        self.assertEqual(df.iloc[0]['entity_name'], 'Test School District')
    
    @patch('src.data_collection.fetch_erate_data.requests.Session.get')
    def test_fetch_data_with_filters(self, mock_get):
        """Test data fetch with multiple filters."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_get.return_value = mock_response
        
        # Fetch with filters
        df = self.collector.fetch_data(
            funding_year=2024,
            state='CA',
            applicant_type='Library',
            limit=100
        )
        
        # Verify API was called
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        params = call_args[1]['params']
        
        # Check that WHERE clause includes our filters
        self.assertIn('$where', params)
        self.assertIn('funding_year = 2024', params['$where'])
        self.assertIn("state = 'CA'", params['$where'])
        self.assertIn("applicant_type = 'Library'", params['$where'])
    
    def test_get_summary_stats_empty(self):
        """Test summary stats with empty DataFrame."""
        df = pd.DataFrame()
        stats = self.collector.get_summary_stats(df)
        self.assertEqual(stats, {})
    
    def test_get_summary_stats(self):
        """Test summary statistics calculation."""
        # Create test data
        df = pd.DataFrame({
            'funding_year': [2024, 2024, 2023],
            'state': ['CA', 'CA', 'NY'],
            'entity_name': ['School A', 'School B', 'School A'],
            'applicant_type': ['School', 'School', 'Library'],
            'total_commitment': ['10000', '20000', '15000']
        })
        
        stats = self.collector.get_summary_stats(df)
        
        self.assertEqual(stats['total_records'], 3)
        self.assertEqual(stats['states'], 2)
        self.assertEqual(stats['unique_entities'], 2)
        self.assertIn('School', stats['applicant_types'])
        self.assertIn('Library', stats['applicant_types'])
    
    @patch('src.data_collection.fetch_erate_data.os.makedirs')
    @patch('pandas.DataFrame.to_csv')
    def test_save_data(self, mock_to_csv, mock_makedirs):
        """Test data saving functionality."""
        df = pd.DataFrame({'col1': [1, 2, 3]})
        output_path = './data/raw/test.csv'
        
        self.collector.save_data(df, output_path)
        
        mock_makedirs.assert_called_once()
        mock_to_csv.assert_called_once_with(output_path, index=False)


class TestAPIConnectivity(unittest.TestCase):
    """Test actual API connectivity (integration test)."""
    
    def test_api_accessible(self):
        """Test that USAC API is accessible and returns data."""
        collector = ERateDataCollector()
        
        try:
            # Fetch just 1 record to test connectivity
            df = collector.fetch_data(limit=1)
            
            # Basic assertions
            self.assertIsInstance(df, pd.DataFrame)
            print(f"\n✓ API Connection Successful")
            print(f"✓ Fetched {len(df)} record(s)")
            
            if not df.empty:
                print(f"✓ Available columns: {', '.join(df.columns.tolist())}")
                print(f"✓ Sample data:\n{df.head()}")
            
        except Exception as e:
            self.fail(f"API connection failed: {e}")


def run_tests():
    """Run all tests and print results."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestERateDataCollection))
    suite.addTests(loader.loadTestsFromTestCase(TestAPIConnectivity))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
