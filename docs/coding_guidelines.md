# Santander UK Data Team Coding Guidelines

## Overview

This document outlines the coding standards and best practices for the Data Analysis and Data Science teams at Santander UK. All code written by team members or AI assistants (including Devin) should follow these guidelines.

---

## Python Standards

### 1. Type Hints

All functions must include type hints for parameters and return values.

```python
# Good
def calculate_average_balance(accounts: list[dict]) -> float:
    """Calculate the average balance across all accounts."""
    total = sum(account['balance'] for account in accounts)
    return total / len(accounts) if accounts else 0.0

# Bad
def calculate_average_balance(accounts):
    total = sum(account['balance'] for account in accounts)
    return total / len(accounts) if accounts else 0.0
```

### 2. Docstrings

Use Google-style docstrings for all functions, classes, and modules.

```python
def identify_outliers(data: pd.DataFrame, column: str, method: str = 'iqr') -> pd.DataFrame:
    """Identify outliers in a DataFrame column.
    
    Args:
        data: Input DataFrame containing the data to analyze.
        column: Name of the column to check for outliers.
        method: Detection method, either 'iqr' or 'zscore'. Defaults to 'iqr'.
    
    Returns:
        DataFrame containing only the outlier rows.
    
    Raises:
        ValueError: If the specified column doesn't exist in the DataFrame.
        ValueError: If an invalid method is specified.
    
    Example:
        >>> df = pd.DataFrame({'amount': [10, 20, 30, 1000, 40]})
        >>> outliers = identify_outliers(df, 'amount')
        >>> len(outliers)
        1
    """
    pass
```

### 3. Code Formatting

- Maximum line length: 100 characters
- Use 4 spaces for indentation (no tabs)
- Use blank lines to separate logical sections
- Follow PEP 8 guidelines

### 4. Import Organization

Group imports in the following order, separated by blank lines:
1. Standard library imports
2. Third-party imports
3. Local application imports

```python
# Standard library
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Third-party
import pandas as pd
import numpy as np
from sqlalchemy import create_engine

# Local
from utils.validators import validate_customer_id
from models.customer import Customer
```

### 5. Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Variables | snake_case | `customer_count` |
| Functions | snake_case | `calculate_balance()` |
| Classes | PascalCase | `CustomerAnalyzer` |
| Constants | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| Private | Leading underscore | `_internal_method()` |

### 6. Error Handling

Always use specific exception types and provide meaningful error messages.

```python
# Good
def load_customer_data(file_path: str) -> pd.DataFrame:
    if not Path(file_path).exists():
        raise FileNotFoundError(f"Customer data file not found: {file_path}")
    
    try:
        return pd.read_csv(file_path)
    except pd.errors.EmptyDataError:
        raise ValueError(f"Customer data file is empty: {file_path}")

# Bad
def load_customer_data(file_path):
    try:
        return pd.read_csv(file_path)
    except:
        raise Exception("Error loading data")
```

---

## SQL Standards

### 1. Naming Conventions

- Tables: snake_case, plural (e.g., `customers`, `transactions`)
- Columns: snake_case (e.g., `customer_id`, `created_at`)
- Indexes: `idx_<table>_<column>` (e.g., `idx_customers_email`)
- Foreign keys: `fk_<table>_<referenced_table>` (e.g., `fk_transactions_customers`)

### 2. Query Formatting

```sql
-- Good: Formatted and readable
SELECT 
    c.customer_id,
    c.first_name,
    c.last_name,
    COUNT(t.transaction_id) AS transaction_count,
    SUM(t.amount) AS total_amount
FROM customers c
LEFT JOIN transactions t ON c.customer_id = t.customer_id
WHERE c.is_active = TRUE
    AND t.transaction_date >= '2024-01-01'
GROUP BY c.customer_id, c.first_name, c.last_name
HAVING COUNT(t.transaction_id) > 10
ORDER BY total_amount DESC
LIMIT 100;

-- Bad: Hard to read
SELECT c.customer_id, c.first_name, c.last_name, COUNT(t.transaction_id) AS transaction_count, SUM(t.amount) AS total_amount FROM customers c LEFT JOIN transactions t ON c.customer_id = t.customer_id WHERE c.is_active = TRUE AND t.transaction_date >= '2024-01-01' GROUP BY c.customer_id, c.first_name, c.last_name HAVING COUNT(t.transaction_id) > 10 ORDER BY total_amount DESC LIMIT 100;
```

### 3. Performance Guidelines

- Always index foreign keys
- Use appropriate data types (don't use VARCHAR for numeric data)
- Avoid SELECT * in production queries
- Use EXPLAIN to analyze query performance
- Limit result sets when possible

### 4. Security Guidelines

- Never concatenate user input directly into SQL strings
- Use parameterized queries
- Limit database user permissions to minimum required

```python
# Good: Parameterized query
cursor.execute(
    "SELECT * FROM customers WHERE customer_id = ?",
    (customer_id,)
)

# Bad: SQL injection vulnerability
cursor.execute(
    f"SELECT * FROM customers WHERE customer_id = '{customer_id}'"
)
```

---

## Git Workflow

### 1. Branch Naming

| Type | Format | Example |
|------|--------|---------|
| Feature | `feature/<ticket>-<description>` | `feature/DATA-123-customer-segmentation` |
| Bug fix | `bugfix/<ticket>-<description>` | `bugfix/DATA-456-fix-null-handling` |
| Hotfix | `hotfix/<ticket>-<description>` | `hotfix/DATA-789-critical-fix` |

### 2. Commit Messages

Use conventional commit format:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(analysis): add customer segmentation algorithm

Implements K-means clustering for customer segmentation based on
transaction patterns and account balance.

Closes DATA-123
```

```
fix(etl): handle null values in transaction amount

Previously, null amounts caused the ETL pipeline to fail.
Now they are replaced with 0 and logged for review.

Fixes DATA-456
```

### 3. Pull Request Guidelines

- PRs should be focused on a single feature or fix
- Include a clear description of changes
- Reference related tickets
- Ensure all tests pass before requesting review
- Require at least one approval before merging

---

## Testing Standards

### 1. Test Coverage

- Minimum 80% code coverage for all modules
- 100% coverage for critical business logic

### 2. Test Organization

```
tests/
    unit/
        test_validators.py
        test_transformers.py
    integration/
        test_database.py
        test_api.py
    fixtures/
        sample_data.csv
        test_config.yaml
```

### 3. Test Naming

```python
def test_<function_name>_<scenario>_<expected_result>():
    """Test description."""
    pass

# Examples
def test_calculate_balance_with_valid_transactions_returns_correct_sum():
    pass

def test_validate_customer_id_with_invalid_format_raises_value_error():
    pass
```

### 4. Fixtures and Mocking

Use pytest fixtures for test data and mock external dependencies.

```python
import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def sample_customer_data():
    return pd.DataFrame({
        'customer_id': ['SAN100001', 'SAN100002'],
        'balance': [1000.00, 2500.00]
    })

@pytest.fixture
def mock_database():
    with patch('mymodule.database.connect') as mock:
        mock.return_value = Mock()
        yield mock
```

---

## Data Processing Guidelines

### 1. Data Validation

Always validate data before processing:

```python
def validate_customer_record(record: dict) -> bool:
    """Validate a customer record has all required fields."""
    required_fields = ['customer_id', 'first_name', 'last_name', 'email']
    
    for field in required_fields:
        if field not in record or record[field] is None:
            return False
    
    if not record['customer_id'].startswith('SAN'):
        return False
    
    return True
```

### 2. Logging

Use structured logging for all data processing operations:

```python
import logging

logger = logging.getLogger(__name__)

def process_transactions(transactions: pd.DataFrame) -> pd.DataFrame:
    logger.info(
        "Starting transaction processing",
        extra={
            'record_count': len(transactions),
            'date_range': f"{transactions['date'].min()} to {transactions['date'].max()}"
        }
    )
    
    # Processing logic...
    
    logger.info(
        "Transaction processing complete",
        extra={
            'processed_count': processed_count,
            'error_count': error_count
        }
    )
```

### 3. Configuration Management

Use environment variables or configuration files for settings:

```python
from pydantic import BaseSettings

class Settings(BaseSettings):
    database_url: str
    api_key: str
    max_retries: int = 3
    batch_size: int = 1000
    
    class Config:
        env_file = '.env'

settings = Settings()
```

---

## Documentation Standards

### 1. README Files

Every project should have a README.md with:
- Project description
- Installation instructions
- Usage examples
- Configuration options
- Contributing guidelines

### 2. API Documentation

Use OpenAPI/Swagger for REST APIs:

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="Customer Analytics API",
    description="API for customer data analysis",
    version="1.0.0"
)

class CustomerSegment(BaseModel):
    """Customer segment classification result."""
    customer_id: str
    segment: str
    confidence: float
    
    class Config:
        schema_extra = {
            "example": {
                "customer_id": "SAN100001",
                "segment": "Premium",
                "confidence": 0.95
            }
        }
```

---

## Security Guidelines

### 1. Sensitive Data Handling

- Never log sensitive data (PII, credentials, etc.)
- Use encryption for data at rest and in transit
- Mask sensitive fields in outputs

```python
def mask_account_number(account_number: str) -> str:
    """Mask account number for display."""
    if len(account_number) >= 4:
        return '*' * (len(account_number) - 4) + account_number[-4:]
    return '*' * len(account_number)
```

### 2. Credential Management

- Never commit credentials to version control
- Use environment variables or secret management services
- Rotate credentials regularly

---

## Review Checklist

Before submitting code for review, ensure:

- [ ] Code follows naming conventions
- [ ] All functions have type hints and docstrings
- [ ] Unit tests are written and passing
- [ ] Code coverage meets minimum threshold
- [ ] No sensitive data is logged or exposed
- [ ] SQL queries are parameterized
- [ ] Error handling is appropriate
- [ ] Documentation is updated
- [ ] Commit messages follow conventions
