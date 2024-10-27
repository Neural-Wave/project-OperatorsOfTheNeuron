# Note that we did not publish the lightning studio because we did not use gpus for anything.
## Setup
- Import dataset (not included in this repo)
### Using `uv`
- `pip install uv``
- Install dodiscover:
```
uv sync
cd dodiscover
uv pip install .
```
### Using `pip`
- `pip install -r requirements.txt`
- Install dodiscover:
```
cd dodiscover
pip install -e .
```
