# Contributing to MVMeta

We welcome contributions to the MVMeta package! This document provides guidelines for contributing.

## Development Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/mvmeta.git
cd mvmeta
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install in development mode:
```bash
pip install -e ".[dev]"
```

## Code Style

- Follow PEP 8 guidelines
- Use Black for code formatting: `black mvmeta/`
- Use type hints where appropriate
- Write docstrings in NumPy style

## Testing

Run tests using pytest:
```bash
pytest tests/ -v
```

For coverage report:
```bash
pytest tests/ --cov=mvmeta --cov-report=html
```

## Adding New Features

1. Create a new branch: `git checkout -b feature-name`
2. Implement your feature with tests
3. Ensure all tests pass
4. Update documentation
5. Submit a pull request

## Documentation

- Update docstrings for new functions/classes
- Add examples to demonstrate usage
- Update README.md if needed
- Add methodology details to docs/methodology.md

## Pull Request Process

1. Ensure your code passes all tests
2. Update documentation
3. Add yourself to contributors list
4. Describe your changes clearly in the PR

## Questions?

Open an issue for questions or discussions.

Thank you for contributing!
