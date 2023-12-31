# vqe-by-indirect-ctl
Variational Quantum Eigensolver by Indirect Control


### requirements

- python `>=3.10,<3.12`
- poetry `>=1.4.0`

### Installation

```
poetry install
```

### Usage

#### Initialize

```
poetry run python src/main.py --config config/xxxx.yml --init True
```

#### Run

```
poetry run python src/main.py --config config/xxxx.yml
```

### Linting and testing

We use following tools for linting and testing.
Please make sure to run those tools and check if your code passes them.

#### Import formatting

```
poetry run isort .
```

#### Code formatting

```
poetry run black .
```

#### Linting

```
poetry run flake8
```

#### Type checking

```
poetry run mypy .
```

#### Testing

```
poetry run pytest
```