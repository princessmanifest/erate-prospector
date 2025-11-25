# """Quick analysis of all 3 datasets for presentation."""
import pandas as pd

print("="*70)
print("COMBINED DATA ANALYSIS FOR PRESENTATION")
print("="*70)

print("\nLoading datasets...")
erate = pd.read_csv('data/raw/erate_data.csv')
nces = pd.read_csv('data/raw/nces_schools.csv')
imls = pd.read_csv('data/raw/imls_libraries.csv')

print(f"✓ E-Rate: {len(erate)} records")
print(f"✓ NCES Schools: {len(nces)} records")
print(f"✓ IMLS Libraries: {len(imls)} records")

print("\n" + "="*70)
print("E-RATE FINDINGS")
print("="*70)
if 'funding_year' in erate.columns:
    print(f"Funding years: {erate['funding_year'].unique()}")
if 'state' in erate.columns:
    print(f"States with E-Rate applications: {erate['state'].nunique()}")
if 'applicant_type' in erate.columns:
    print(f"\nApplicant distribution:\n{erate['applicant_type'].value_counts()}")

print("\n" + "="*70)
print("NCES SCHOOLS FINDINGS")
print("="*70)
if 'state_location' in nces.columns:
    print(f"States in dataset: {nces['state_location'].nunique()}")
if 'enrollment' in nces.columns:
    total_enroll = pd.to_numeric(nces['enrollment'], errors='coerce').sum()
    print(f"Total enrollment: {total_enroll:,.0f}")

print("\n" + "="*70)
print("IMLS LIBRARIES FINDINGS")
print("="*70)
if 'STABR' in imls.columns:
    print(f"States in dataset: {imls['STABR'].nunique()}")
if 'POPU_LSA' in imls.columns:
    total_pop = pd.to_numeric(imls['POPU_LSA'], errors='coerce').sum()
    print(f"Total population served: {total_pop:,.0f}")

print("\n" + "="*70)
print("KEY INSIGHTS FOR PRESENTATION")
print("="*70)
print(f"✓ Collected data from 3 federal sources")
print(f"✓ Total records: {len(erate) + len(nces) + len(imls):,}")
print(f"✓ Multi-year E-Rate participation data")
print(f"✓ School demographics and enrollment data")
print(f"✓ Library operational and service population data")
print(f"✓ Ready for market opportunity analysis")
print("="*70)
