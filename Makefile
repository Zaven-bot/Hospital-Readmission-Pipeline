# === Makefile for Readmission ML Project ===
ENV_NAME = readmission-mlflow
PYTHON = micromamba run -n $(ENV_NAME) python
MLFLOW = micromamba run -n $(ENV_NAME) mlflow

# === Paths ===
RAW_DATA = data/raw/hospital_readmissions.csv
CLEANED_DATA = data/processed/cleaned_data.csv
FEATURED_DATA = data/processed/featured_data.csv
TEST_DATA = data/processed/test_data.pkl

# === Create Environment ===
env:
	micromamba create -n $(ENV_NAME) -f env.yml -y

# === Activate Jupyter Lab ===
notebook:
	$(PYTHON) -m jupyter lab

# === Clean Data ===
clean-data:
	@echo "📦 Cleaning Data..."
	PYTHONPATH=. $(PYTHON) src/clean.py --input $(RAW_DATA) --output $(CLEANED_DATA)

feature-data:
	@echo "📦 Creating Features..."
	PYTHONPATH=. $(PYTHON) src/feature_engineering.py --input $(CLEANED_DATA) --output $(FEATURED_DATA)

# === Train the model ===
# Ask dvc to check if data changed
# Add new data version if that's the case
# Document appropriate data version with model
train:
	@echo "📦 [1/3] Updating processed datasets in DVC..."
	dvc add $(CLEANED_DATA)
	dvc add $(FEATURED_DATA)
	git add $(CLEANED_DATA).dvc $(FEATURED_DATA).dvc
	git commit -m "📦 Update cleaned and featured datasets via DVC" || echo "Nothing to commit."

	@echo "🤖 [2/3] Training model on updated featured data..."
	PYTHONPATH=. $(PYTHON) src/train_model.py --input $(FEATURED_DATA) $(if $(group), --run-group $(group))

	@echo "✅ [3/3] Retrain complete. Check MLflow UI for new results!"

# === Evaluate the model ===
evaluate:
	@echo "🧪 Evaluating model from most recent run..."
	PYTHONPATH=. $(PYTHON) src/evaluate_model.py $(if $(run), --run-id $(run)) $(if $(stage), --stage $(stage)) $(if $(model), --model-name $(model)) $(if $(group), --run-group $(group))

# === Full pipeline ===
full-pipeline:
	make clean-data
	make feature-data
	make train
	make evaluate
	@echo "✅ Evaluation metrics and plots logged to MLflow!"

# === Launch MLflow UI ===
ui:
	mlflow server \
		--host 127.0.0.1 \
		--port 5000 \
		--backend-store-uri ./mlruns \
		--default-artifact-root ./mlruns \
		--serve-artifacts \
		--gunicorn-opts="--worker-class sync" 
		--workers 2

# === Clean up generated files ===
clean:
	rm -rf models/*.pkl mlruns/ __pycache__ .dvc/tmp .dvc/cache

# === Rebuild the env from scratch (⚠️ deletes current) ===
rebuild:
	micromamba remove -n $(ENV_NAME) --all -y
	make env
