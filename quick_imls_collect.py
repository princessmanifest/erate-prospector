# """Quick IMLS library data collection for presentation."""
import requests
import pandas as pd

print("=" * 70)
print("COLLECTING IMLS LIBRARY DATA")
print("=" * 70)

# Use IMLS open data portal API instead
api_url = "https://data.imls.gov/resource/fpin-fu7m.json"

print("\nFetching library data from IMLS Open Data Portal...")
print("Collecting 500 library records...")

try:
    params = {
        '$limit': 500,
        '$order': 'stabr'
    }

    response = requests.get(api_url, params=params, timeout=30)

    print(f"Status code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data)

        print(f"\n✓ Total IMLS records collected: {len(df)}")
        print(f"\nColumns ({len(df.columns)} total): {df.columns.tolist()[:15]}...")
        print(f"\nSample data:\n{df.head()}")

        # Save
        output_path = './data/raw/imls_libraries.csv'
        df.to_csv(output_path, index=False)
        print(f"\n✓ Saved to {output_path}")

        # Quick stats
        print(f"\n--- QUICK STATS ---")
        print(f"Total libraries: {len(df)}")

        # Check for state column
        state_cols = ['stabr', 'state', 'STABR']
        for col in state_cols:
            if col in df.columns:
                print(f"States represented: {df[col].nunique()}")
                print(f"Top 5 states:\n{df[col].value_counts().head()}")
                break

        # Check for population column
        pop_cols = ['popu_lsa', 'population', 'POPU_LSA']
        for col in pop_cols:
            if col in df.columns:
                total_pop = pd.to_numeric(df[col], errors='coerce').sum()
                if total_pop > 0:
                    print(f"Total population served: {total_pop:,.0f}")
                break

        print("=" * 70)

    else:
        print(f"\n✗ Error: {response.status_code}")
        print(f"Response: {response.text[:300]}")

except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback

    traceback.print_exc()