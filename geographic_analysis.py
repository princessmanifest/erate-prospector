# """
# Geographic Opportunity Analysis - E-Rate Market Intelligence
# Creates state-level heatmap showing high-value consulting targets
# """
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

print("="*70)
print("GEOGRAPHIC OPPORTUNITY ANALYSIS")
print("="*70)

# Load data
erate = pd.read_csv('data/raw/erate_data.csv')
nces = pd.read_csv('data/raw/nces_schools.csv')
imls = pd.read_csv('data/raw/imls_libraries.csv')

print("\n1. DATA PREPARATION")
print("-"*70)

# Extract state mappings
state_abbrev_to_name = {
    'AL': 'Alabama', 'AK': 'Alaska', 'AZ': 'Arizona', 'AR': 'Arkansas',
    'CA': 'California', 'CO': 'Colorado', 'CT': 'Connecticut', 'DE': 'Delaware',
    'FL': 'Florida', 'GA': 'Georgia', 'HI': 'Hawaii', 'ID': 'Idaho',
    'IL': 'Illinois', 'IN': 'Indiana', 'IA': 'Iowa', 'KS': 'Kansas',
    'KY': 'Kentucky', 'LA': 'Louisiana', 'ME': 'Maine', 'MD': 'Maryland',
    'MA': 'Massachusetts', 'MI': 'Michigan', 'MN': 'Minnesota', 'MS': 'Mississippi',
    'MO': 'Missouri', 'MT': 'Montana', 'NE': 'Nebraska', 'NV': 'Nevada',
    'NH': 'New Hampshire', 'NJ': 'New Jersey', 'NM': 'New Mexico', 'NY': 'New York',
    'NC': 'North Carolina', 'ND': 'North Dakota', 'OH': 'Ohio', 'OK': 'Oklahoma',
    'OR': 'Oregon', 'PA': 'Pennsylvania', 'RI': 'Rhode Island', 'SC': 'South Carolina',
    'SD': 'South Dakota', 'TN': 'Tennessee', 'TX': 'Texas', 'UT': 'Utah',
    'VT': 'Vermont', 'VA': 'Virginia', 'WA': 'Washington', 'WV': 'West Virginia',
    'WI': 'Wisconsin', 'WY': 'Wyoming', 'DC': 'District of Columbia'
}

# METRIC 1: School Poverty Indicator (Simplified)
print("\nCalculating poverty indicators from NCES data...")
# Use direct_certification as poverty proxy
if 'direct_certification' in nces.columns:
    nces['direct_certification'] = pd.to_numeric(nces['direct_certification'], errors='coerce')
    nces['enrollment'] = pd.to_numeric(nces['enrollment'], errors='coerce')
    
    # Calculate average poverty rate from sample
    avg_nslp_rate = (nces['direct_certification'].sum() / nces['enrollment'].sum()) * 100
    print(f"✓ Calculated average NSLP rate: {avg_nslp_rate:.1f}%")
    
    # Use national average for all states (since we only have 5 states in NCES sample)
    nslp_by_state = None
else:
    avg_nslp_rate = 35.0  # National average
    nslp_by_state = None
    
print(f"✓ Using national poverty indicator for analysis")

# METRIC 2: Library Financial Capacity (from IMLS)
print("Calculating library capacity...")
if 'State Name' in imls.columns and 'Total Revenue In Thousands' in imls.columns:
    imls['Total Revenue In Thousands'] = pd.to_numeric(imls['Total Revenue In Thousands'], errors='coerce')
    lib_capacity = imls[['State Name', 'Total Revenue In Thousands', 'Public Library Count']].copy()
    lib_capacity.columns = ['state_name', 'total_revenue_k', 'library_count']
    print(f"✓ Library financial data for {len(lib_capacity)} states")

# METRIC 3: E-Rate Activity (from USAC) - placeholder since we have limited state coverage
print("Analyzing E-Rate participation...")
erate_activity = pd.DataFrame({
    'state_name': ['California', 'Texas', 'Florida', 'New York', 'Illinois'],
    'erate_applications': [250, 200, 180, 150, 120]  # Sample data
})

# MERGE ALL METRICS
print("\n2. CREATING OPPORTUNITY SCORES")
print("-"*70)

# Start with IMLS (most complete state coverage)
opportunity_df = lib_capacity.copy()

# Add poverty indicator (use national average since NCES has limited coverage)
opportunity_df['nslp_rate'] = avg_nslp_rate  # Apply to all states

# Clean data - Remove NATIONAL aggregation row
opportunity_df = opportunity_df[opportunity_df['total_revenue_k'] > 0].copy()
opportunity_df = opportunity_df[opportunity_df['state_name'].str.upper() != 'NATIONAL'].copy()

print(f"✓ Cleaned dataset: {len(opportunity_df)} states/territories")

# Normalize metrics to 0-100 scale
def normalize_score(series):
    if series.max() == series.min():
        return pd.Series([50] * len(series))
    return ((series - series.min()) / (series.max() - series.min())) * 100

# Revenue capacity score (higher = more resources for E-Rate consulting)
opportunity_df['capacity_score'] = normalize_score(opportunity_df['total_revenue_k'])

# Library count score (more libraries = larger market)
opportunity_df['market_size_score'] = normalize_score(opportunity_df['library_count'])

# Calculate composite opportunity score
# Capacity (50%) + Market Size (30%) + Poverty indicator (20%)
opportunity_df['opportunity_score'] = (
    opportunity_df['capacity_score'] * 0.5 +      # 50% weight on financial capacity
    opportunity_df['market_size_score'] * 0.3 +   # 30% weight on market size
    50.0 * 0.2                                      # 20% base score for poverty (applied uniformly)
)

# Rank states
opportunity_df = opportunity_df.sort_values('opportunity_score', ascending=False)

print(f"\n✓ Opportunity scores calculated for {len(opportunity_df)} states/territories")
print("\nTop 10 High-Opportunity States:")
print(opportunity_df[['state_name', 'opportunity_score', 'nslp_rate', 'total_revenue_k']].head(10).to_string(index=False))

# 3. CREATE VISUALIZATIONS
print("\n3. GENERATING VISUALIZATIONS")
print("-"*70)

# Create figure with subplots
fig = plt.figure(figsize=(16, 10))

# Plot 1: Top 15 Opportunity States (Bar Chart)
ax1 = plt.subplot(2, 2, 1)
top15 = opportunity_df.head(15)
colors = plt.cm.RdYlGn_r(normalize_score(top15['opportunity_score']) / 100)
ax1.barh(range(len(top15)), top15['opportunity_score'], color=colors)
ax1.set_yticks(range(len(top15)))
ax1.set_yticklabels(top15['state_name'])
ax1.set_xlabel('Opportunity Score (0-100)', fontsize=11)
ax1.set_title('Top 15 States - E-Rate Consulting Opportunity', fontsize=13, fontweight='bold')
ax1.invert_yaxis()
ax1.grid(axis='x', alpha=0.3)

# Plot 2: Capacity vs Market Size Scatter
ax2 = plt.subplot(2, 2, 2)
scatter = ax2.scatter(
    opportunity_df['library_count'], 
    opportunity_df['total_revenue_k'],
    s=opportunity_df['opportunity_score']*3,
    c=opportunity_df['opportunity_score'],
    cmap='RdYlGn_r',
    alpha=0.6,
    edgecolors='black',
    linewidth=0.5
)
ax2.set_xlabel('Number of Libraries', fontsize=11)
ax2.set_ylabel('Total Revenue ($K)', fontsize=11)
ax2.set_title('Market Size vs Financial Capacity', fontsize=13, fontweight='bold')
plt.colorbar(scatter, ax=ax2, label='Opportunity Score')

# Annotate top 5 states
top5 = opportunity_df.head(5)
for idx, row in top5.iterrows():
    ax2.annotate(
        row['state_name'], 
        (row['library_count'], row['total_revenue_k']),
        fontsize=8,
        alpha=0.7
    )

# Plot 3: Opportunity Score Distribution
ax3 = plt.subplot(2, 2, 3)
ax3.hist(opportunity_df['opportunity_score'], bins=15, color='steelblue', edgecolor='black', alpha=0.7)
ax3.axvline(opportunity_df['opportunity_score'].median(), color='red', linestyle='--', linewidth=2, label='Median')
ax3.axvline(opportunity_df['opportunity_score'].mean(), color='orange', linestyle='--', linewidth=2, label='Mean')
ax3.set_xlabel('Opportunity Score', fontsize=11)
ax3.set_ylabel('Number of States', fontsize=11)
ax3.set_title('Distribution of Market Opportunities', fontsize=13, fontweight='bold')
ax3.legend()
ax3.grid(axis='y', alpha=0.3)

# Plot 4: Quadrant Analysis (Capacity vs Market Size)
ax4 = plt.subplot(2, 2, 4)
median_libs = opportunity_df['library_count'].median()
median_revenue = opportunity_df['total_revenue_k'].median()

# Define high-opportunity quadrant
high_opportunity = opportunity_df[
    (opportunity_df['library_count'] > median_libs) & 
    (opportunity_df['total_revenue_k'] > median_revenue)
]

ax4.scatter(
    opportunity_df['library_count'], 
    opportunity_df['total_revenue_k'],
    s=100,
    c='lightgray',
    alpha=0.5,
    edgecolors='black',
    linewidth=0.5
)
ax4.scatter(
    high_opportunity['library_count'],
    high_opportunity['total_revenue_k'],
    s=150,
    c='red',
    alpha=0.7,
    edgecolors='black',
    linewidth=1,
    label='High Priority'
)
ax4.axhline(median_revenue, color='blue', linestyle='--', alpha=0.5)
ax4.axvline(median_libs, color='blue', linestyle='--', alpha=0.5)
ax4.set_xlabel('Number of Libraries', fontsize=11)
ax4.set_ylabel('Total Revenue ($K)', fontsize=11)
ax4.set_title('Market Segmentation Quadrant', fontsize=13, fontweight='bold')
ax4.legend()

# Add quadrant labels
ax4.text(median_libs*0.5, median_revenue*1.3, 'Small\nMarket', ha='center', fontsize=9, alpha=0.6)
ax4.text(median_libs*1.3, median_revenue*1.3, 'HIGH PRIORITY\n(Large + Well-Funded)', ha='center', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig('/mnt/user-data/outputs/geographic_opportunity_analysis.png', dpi=300, bbox_inches='tight')
print("\n✓ Saved: geographic_opportunity_analysis.png")

# Export data for presentation
opportunity_df.to_csv('/mnt/user-data/outputs/opportunity_scores_by_state.csv', index=False)
print(" Saved: opportunity_scores_by_state.csv")

print("\n" + "="*70)
print("ANALYSIS COMPLETE")
print("="*70)
print(f"\nKey Insights:")
print(f"  • Identified {len(high_opportunity)} high-priority states")
print(f"  • Top oPportunity state: {opportunity_df.iloc[0]['state_name']}")
print(f"  • Average opportunity score: {opportunity_df['opportunity_score'].mean():.1f}")
print(f"  • Score range: {opportunity_df['opportunity_score'].min():.1f} - {opportunity_df['opportunity_score'].max():.1f}")
