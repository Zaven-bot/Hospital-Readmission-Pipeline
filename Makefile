# === Makefile for Readmission ML Project ===

ENV_NAME = readmission-mlflow
PYTHON = micromamba run -n $(ENV_NAME) python
MLFLOW = micromamba run -n $(ENV_NAME) mlflow

# === Create Environment ===
env:
	micromamba create -n $(ENV_NAME) -f env.yml -y

# === Activate Jupyter Lab ===
notebook:
	$(PYTHON) -m jupyter lab

# === Clean Data ===
clean-data:
	micromamba run -n readmission-mlflow python src/clean.py \
	--input data/raw/hospital_readmissions.csv \
	--output data/processed/cleaned_data.csv

# === Train the model ===
train:
	PYTHONPATH=. $(PYTHON) src/train_model.py

# === Evaluate the model ===
evaluate:
	PYTHONPATH=. $(PYTHON) src/evaluate_model.py

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
