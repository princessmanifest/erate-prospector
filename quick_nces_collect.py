# """Quick NCES school data collection for presentation."""
import requests
import pandas as pd
import time

print("=" * 70)
print("COLLECTING NCES SCHOOL DATA")
print("=" * 70)

# Try the correct Urban Institute API endpoint
base_url = "https://educationdata.urban.org/api/v1/schools/ccd/directory/2022"

print("\nFetching school data from NCES via Urban Institute API...")
print("Trying 2022 data (most recent stable year)...")

try:
    # Try a simple request first
    params = {
        'per_page': 500
    }

    print(f"\nFetching data...")
    response = requests.get(base_url, params=params, timeout=30)

    print(f"Status code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()

        # The API returns data in 'results' key
        if isinstance(data, dict) and 'results' in data:
            results = data['results']
        elif isinstance(data, list):
            results = data
        else:
            results = [data]

        if results:
            df = pd.DataFrame(results)

            print(f"\n✓ Total NCES records collected: {len(df)}")
            print(f"\nColumns ({len(df.columns)} total): {df.columns.tolist()[:10]}...")
            print(f"\nSample data:\n{df.head()}")

            # Save
            output_path = './data/raw/nces_schools.csv'
            df.to_csv(output_path, index=False)
            print(f"\n✓ Saved to {output_path}")

            # Quick stats
            print(f"\n--- QUICK STATS ---")
            print(f"Total schools: {len(df)}")

            # Try different possible column names
            state_cols = ['state_location', 'state', 'state_name', 'fips']
            for col in state_cols:
                if col in df.columns:
                    print(f"States represented: {df[col].nunique()}")
                    break

            enroll_cols = ['enrollment', 'total_students']
            for col in enroll_cols:
                if col in df.columns:
                    total_enrollment = pd.to_numeric(df[col], errors='coerce').sum()
                    print(f"Total enrollment: {total_enrollment:,.0f}")
                    break

            print("=" * 70)
        else:
            print("\n✗ No results found in response")
    else:
        print(f"\n✗ Error: {response.status_code}")
        print(f"Response: {response.text[:200]}")

except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback

    traceback.print_exc()