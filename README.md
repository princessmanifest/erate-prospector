# Results Directory

This directory stores all model outputs, figures, and analysis results. **This directory is excluded from git** via .gitignore.

## Structure

### models/
Trained machine learning models:
- Serialized model files (.pkl, .joblib)
- Model configuration files
- Training history and logs

### figures/
Generated visualizations:
- Exploratory data analysis plots
- Geographic heat maps
- Model performance charts
- Feature importance visualizations

### tables/
Analysis outputs:
- Summary statistics (CSV/Excel)
- Model evaluation metrics
- Market opportunity scores
- Prospect prioritization lists

## Important Notes

- **Never commit this directory to git**
- All result files are gitignored
- Results are reproducible by running analysis scripts
- Document key findings in project reports
- Version control analysis scripts, not their outputs

## Regenerating Results

To recreate analysis results:

```bash
#Run Progress Report Tests with no .env file 
cd /path/to/erate-prospector
python -m venv venv
source venv/bin/activate  # for Windows: venv\Scripts\activate
pip install -r requirements.txt
python tests.py

# Run EDA
python src/analysis/exploratory_analysis.py

# Train models
python src/modeling/train_classifier.py
python src/modeling/clustering.py

# Generate visualizations
python src/visualization/create_plots.py
```

## Model Files

Trained models will be saved with naming convention:
- `{model_type}_{date}_{version}.pkl`
- Example: `random_forest_20251205_v1.pkl`

## Figures

Figures will be saved with descriptive names:
- `{analysis_type}_{detail}.png`
- Example: `geographic_cluster_heatmap_california.png`
