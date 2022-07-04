.DEFAULT_GOAL: run

run:
	python3 -m uvicorn main:app --reload --port 8080
.PHONY: run

dep:
	pip3 install "fastapi[all]"
	pip3 install "uvicorn[standard]"
.PHONY: dep

run_new: dep
	python3 -m uvicorn main:app --reload --port 8080
.PHONY: run_new