# Block Artistry - backend

Create virtual environment:
```python
virtualenv venv
```

Install necessary packages:
```python
pip install -r requirements.txt
```

Run FastAPI server:
```python
 uvicorn main:app --reload
```

## How to deploy?

Create account on [https://fly.io/](https://fly.io/)

```shell
brew install flyctl
```

```shell
flyctl auth login
```

```shell
flyctl launch
```
