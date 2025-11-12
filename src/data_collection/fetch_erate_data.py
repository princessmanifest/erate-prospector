"""
USAC E-Rate Data Collection Module

This module handles fetching E-Rate funding data from the USAC Open Data API.
Data includes recipient details, commitments, approval status, and demographic information.

API Documentation: https://opendata.usac.org/
Dataset: E-Rate Recipient Details and Commitments
Endpoint: https://opendata.usac.org/resource/avi8-svp9.json
"""

import requests
import pandas as pd
import time
import os
from typing import Optional, Dict, List
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ERateDataCollector:
    """Collects E-Rate funding data from USAC Open Data API."""
    
    def __init__(self, app_token: Optional[str] = None):
        """
        Initialize the E-Rate data collector.
        
        Args:
            app_token: Optional USAC API app token for higher rate limits
        """
        self.base_url = "https://opendata.usac.org/resource/avi8-svp9.json"
        self.app_token = app_token
        self.session = requests.Session()
        
        if app_token:
            self.session.headers.update({'X-App-Token': app_token})
    
    def fetch_data(
        self,
        funding_year: Optional[int] = None,
        state: Optional[str] = None,
        applicant_type: Optional[str] = None,
        limit: int = 1000,
        offset: int = 0
    ) -> pd.DataFrame:
        """
        Fetch E-Rate data from USAC API with optional filters.
        
        Args:
            funding_year: Filter by funding year (e.g., 2024)
            state: Filter by state abbreviation (e.g., 'CA')
            applicant_type: Filter by type ('School' or 'Library')
            limit: Number of records per request (max 50000 for SODA API)
            offset: Starting record offset for pagination
            
        Returns:
            DataFrame containing E-Rate records
        """
        params = {
            '$limit': limit,
            '$offset': offset,
            '$order': 'funding_year DESC' #, entity_name
        }
        
        # Build WHERE clause for filters
        where_clauses = []
        if funding_year:
            where_clauses.append(f"funding_year = {funding_year}")
        if state:
            where_clauses.append(f"state = '{state}'")
        if applicant_type:
            where_clauses.append(f"applicant_type = '{applicant_type}'")
        
        if where_clauses:
            params['$where'] = ' AND '.join(where_clauses)
        
        try:
            logger.info(f"Fetching E-Rate data: limit={limit}, offset={offset}, filters={where_clauses}")
            response = self.session.get(self.base_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            df = pd.DataFrame(data)
            
            logger.info(f"Successfully fetched {len(df)} records")
            return df
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data: {e}")
            raise
    
    def fetch_all_years(
        self,
        start_year: int = 2016,
        end_year: int = 2024,
        state: Optional[str] = None,
        applicant_type: Optional[str] = None,
        batch_size: int = 1000
    ) -> pd.DataFrame:
        """
        Fetch E-Rate data for multiple funding years.
        
        Args:
            start_year: First funding year to fetch
            end_year: Last funding year to fetch
            state: Optional state filter
            applicant_type: Optional applicant type filter
            batch_size: Records per API request
            
        Returns:
            DataFrame containing all records across years
        """
        all_data = []
        
        for year in range(start_year, end_year + 1):
            logger.info(f"Fetching data for funding year {year}")
            offset = 0
            
            while True:
                df_batch = self.fetch_data(
                    funding_year=year,
                    state=state,
                    applicant_type=applicant_type,
                    limit=batch_size,
                    offset=offset
                )
                
                if df_batch.empty:
                    break
                
                all_data.append(df_batch)
                
                # Check if we got fewer records than requested (last page)
                if len(df_batch) < batch_size:
                    break
                
                offset += batch_size
                time.sleep(0.5)  # Rate limiting courtesy
        
        if all_data:
            result_df = pd.concat(all_data, ignore_index=True)
            logger.info(f"Total records fetched: {len(result_df)}")
            return result_df
        else:
            logger.warning("No data fetched")
            return pd.DataFrame()
    
    def get_summary_stats(self, df: pd.DataFrame) -> Dict:
        """
        Calculate summary statistics for the E-Rate dataset.
        
        Args:
            df: DataFrame with E-Rate data
            
        Returns:
            Dictionary with summary statistics
        """
        if df.empty:
            return {}
        
        stats = {
            'total_records': len(df),
            'funding_years': sorted(df['funding_year'].unique().tolist()) if 'funding_year' in df.columns else [],
            'states': df['state'].nunique() if 'state' in df.columns else 0,
            'unique_entities': df['entity_name'].nunique() if 'entity_name' in df.columns else 0,
            'applicant_types': df['applicant_type'].value_counts().to_dict() if 'applicant_type' in df.columns else {},
        }
        
        # Calculate total commitments if available
        if 'total_commitment' in df.columns:
            df['total_commitment'] = pd.to_numeric(df['total_commitment'], errors='coerce')
            stats['total_funding'] = df['total_commitment'].sum()
            stats['avg_commitment'] = df['total_commitment'].mean()
        
        return stats
    
    def save_data(self, df: pd.DataFrame, output_path: str) -> None:
        """
        Save DataFrame to CSV file.
        
        Args:
            df: DataFrame to save
            output_path: Path to output CSV file
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        logger.info(f"Data saved to {output_path}")


def main():
    """Main function to demonstrate usage."""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    # Initialize collector
    app_token = os.getenv('USAC_APP_TOKEN')
    collector = ERateDataCollector(app_token=app_token)
    
    # Example: Fetch California data for 2024
    df = collector.fetch_data(
        funding_year=2024,
        state='CA',
        limit=100
    )
    
    print(f"\nFetched {len(df)} records")
    print(f"\nColumns: {df.columns.tolist()}")
    print(f"\nFirst few records:\n{df.head()}")
    
    # Get summary stats
    stats = collector.get_summary_stats(df)
    print(f"\nSummary Statistics:\n{stats}")
    
    # Save to file
    output_dir = os.getenv('RAW_DATA_DIR', './data/raw')
    output_path = os.path.join(output_dir, 'erate_sample.csv')
    collector.save_data(df, output_path)


if __name__ == '__main__':
    main()
