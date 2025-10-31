# Contributing to QuantEvolve

Thank you for considering contributing to QuantEvolve! This document provides guidelines and information for contributors.

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)

---

## 🤝 Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow:

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on what is best for the community
- Show empathy towards other community members

---

## 🎯 How Can I Contribute?

### Reporting Bugs

Before creating a bug report, please check existing issues to avoid duplicates. When creating a bug report, include:

- **Description**: Clear description of the bug
- **Steps to Reproduce**: Minimal steps to reproduce the behavior
- **Expected Behavior**: What you expected to happen
- **Actual Behavior**: What actually happened
- **Environment**: Python version, OS, relevant package versions
- **Logs**: Relevant error messages or logs

**Bug Report Template**:
```markdown
**Description**
A clear description of the bug.

**To Reproduce**
Steps to reproduce:
1. Run command '...'
2. See error

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- OS: [e.g., macOS 14.0]
- Python: [e.g., 3.10.5]
- QuantEvolve version: [e.g., 0.1.0]

**Logs**
```
paste relevant logs here
```
```

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Use Case**: Clear description of the problem you're trying to solve
- **Proposed Solution**: How you'd like to solve it
- **Alternatives**: Other solutions you've considered
- **Additional Context**: Screenshots, examples, references

### Contributing Code

Areas where contributions are especially welcome:

1. **Strategy Categories**: Additional strategy families (e.g., machine learning-based, options strategies)
2. **Backtesting Enhancements**:
   - Corporate action handling (splits, dividends)
   - Alternative data integration
   - Multi-asset portfolio strategies
3. **Visualization Tools**:
   - Feature map visualization
   - Evolution progress tracking
   - Strategy performance dashboards
4. **Performance Optimization**:
   - Parallel evolution across islands
   - Vectorization improvements
   - Caching optimizations
5. **Validation & Robustness**:
   - Walk-forward optimization
   - Monte Carlo validation
   - Regime-specific testing

---

## 🛠️ Development Setup

### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then:
git clone https://github.com/YOUR-USERNAME/QuantEvolve.git
cd QuantEvolve
```

### 2. Create Development Environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov black flake8 mypy
```

### 3. Set Up Environment

```bash
# Copy environment template
cp .env.example .env

# Add your API key
echo "OPENROUTER_API_KEY=your-key-here" >> .env
```

### 4. Create Feature Branch

```bash
git checkout -b feature/your-feature-name
# Or for bug fixes:
git checkout -b fix/bug-description
```

---

## 🔄 Pull Request Process

### Before Submitting

1. **Run tests**: Ensure all tests pass
   ```bash
   pytest tests/ -v
   ```

2. **Format code**: Use black for formatting
   ```bash
   black src/ tests/
   ```

3. **Lint code**: Check with flake8
   ```bash
   flake8 src/ tests/ --max-line-length=100
   ```

4. **Type check** (optional but recommended):
   ```bash
   mypy src/ --ignore-missing-imports
   ```

5. **Update documentation**: Add docstrings, update README if needed

### Submitting Pull Request

1. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: Add feature description"
   ```

   Use conventional commit messages:
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation changes
   - `test:` Test additions or changes
   - `refactor:` Code refactoring
   - `perf:` Performance improvements
   - `chore:` Maintenance tasks

2. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Open Pull Request** on GitHub with:
   - **Title**: Clear, concise description
   - **Description**:
     - What changes were made
     - Why the changes are needed
     - How to test the changes
     - Any breaking changes
   - **Link to Issue**: Reference related issues

### Pull Request Template

```markdown
## Description
Brief description of changes

## Motivation and Context
Why is this change needed? What problem does it solve?

## How Has This Been Tested?
- [ ] Test A
- [ ] Test B

## Types of Changes
- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature causing existing functionality to change)
- [ ] Documentation update

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Comments added to hard-to-understand areas
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] No new warnings
```

### Review Process

- Maintainers will review your PR
- Address feedback by pushing new commits
- Once approved, maintainers will merge

---

## 📝 Coding Standards

### Python Style Guide

Follow PEP 8 with these specifics:

- **Line Length**: 100 characters (not 80)
- **Indentation**: 4 spaces (not tabs)
- **Imports**: Organized in three groups:
  1. Standard library
  2. Third-party packages
  3. Local modules

  ```python
  import sys
  from typing import List, Dict

  import numpy as np
  import pandas as pd

  from src.core.feature_map import Strategy
  from src.utils.logger import get_logger
  ```

### Naming Conventions

- **Classes**: `PascalCase` (e.g., `FeatureMap`, `ResearchAgent`)
- **Functions/Methods**: `snake_case` (e.g., `generate_hypothesis`, `run_backtest`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `MAX_ITERATIONS`, `DEFAULT_ALPHA`)
- **Private members**: Prefix with `_` (e.g., `_internal_method`)

### Documentation

#### Docstrings

Use Google-style docstrings:

```python
def sample_parent(self, island_id: int, alpha: float = 0.5) -> Optional[Strategy]:
    """
    Sample parent strategy from island.

    Balances exploitation (sampling best strategies) with exploration
    (sampling diverse strategies) using parameter alpha.

    Args:
        island_id: Island identifier to sample from
        alpha: Probability of sampling from feature map (best parent)
              vs entire population (diverse parent). Range [0, 1].

    Returns:
        Sampled parent strategy, or None if island is empty

    Example:
        >>> parent = db.sample_parent(island_id=0, alpha=0.5)
        >>> print(parent.strategy_id)
        'strat_123456789'
    """
    # Implementation
```

#### Type Hints

Add type hints to all functions:

```python
from typing import List, Dict, Optional, Tuple

def calculate_metrics(
    returns: pd.Series,
    signals_list: List[pd.Series]
) -> Dict[str, float]:
    """Calculate performance metrics"""
    # Implementation
```

### Error Handling

- Use specific exceptions, not bare `except`
- Log errors with context
- Provide actionable error messages

```python
try:
    data = self.load_data(symbol)
except FileNotFoundError as e:
    logger.error(f"Data file not found for {symbol}: {e}")
    raise ValueError(f"Cannot load data for {symbol}. "
                    f"Please ensure {symbol}.csv exists in data directory.")
```

---

## 🧪 Testing Guidelines

### Writing Tests

- Use `pytest` framework
- Place tests in `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`

```python
# tests/test_feature_map.py
import pytest
from src.core.feature_map import FeatureMap, Strategy

def test_feature_map_initialization():
    """Test feature map creates correct dimensions"""
    dimensions = [...]
    fm = FeatureMap(dimensions)

    assert fm.archive.shape == (16, 16, 16)
    assert fm.get_filled_cells() == 0

def test_strategy_addition():
    """Test adding strategy to feature map"""
    fm = FeatureMap(dimensions)
    strategy = Strategy(...)

    added = fm.add(strategy)

    assert added is True
    assert fm.get_filled_cells() == 1
```

### Test Coverage

- Aim for >80% coverage on core modules
- Test both success and failure paths
- Include edge cases

```bash
# Run with coverage
pytest --cov=src --cov-report=html tests/
```

### Integration Tests

For components requiring LLM or backtesting:

```python
@pytest.mark.integration
def test_full_evolution_cycle():
    """Integration test for complete evolution"""
    # Test with mock LLM or real API (slower)
```

Run integration tests separately:
```bash
pytest -m integration
```

---

## 📖 Documentation

### Code Comments

- Explain **why**, not **what**
- Good: `# Use alpha=0.5 to balance exploitation vs exploration per paper Section 5.2.1`
- Bad: `# Set alpha to 0.5`

### README Updates

If your changes affect usage:
- Update relevant sections in README.md
- Add examples if introducing new features
- Update configuration documentation

### Docstring Updates

Ensure all public functions/classes have docstrings:
- Purpose of function/class
- Parameters with types
- Return value
- Example usage (for complex functions)
- Any exceptions raised

---

## 🚀 Release Process

(For maintainers)

1. Update version in `src/__init__.py`
2. Update CHANGELOG.md
3. Create release tag: `git tag v0.2.0`
4. Push tag: `git push origin v0.2.0`
5. Create GitHub release with notes

---

## 💡 Getting Help

- **Questions**: Open a [GitHub Discussion](https://github.com/your-repo/QuantEvolve/discussions)
- **Bugs**: Open a [GitHub Issue](https://github.com/your-repo/QuantEvolve/issues)
- **Chat**: Join our community (link TBD)

---

## 📄 License

By contributing, you agree that your contributions will be licensed under the same MIT License that covers this project.

---

## 🙏 Thank You!

Your contributions make QuantEvolve better for everyone. We appreciate your time and effort!

**Happy Contributing! 🎉**
