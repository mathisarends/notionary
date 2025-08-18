# Numbered List Blocks

Numbered lists organize information in sequential, ordered format. Perfect for step-by-step instructions, procedures, rankings, and any content where order matters.

## Basic Syntax

```markdown
1. First step
2. Second step
3. Third step
```

## Simple Ordered Lists

### Step-by-step Instructions

```markdown
## Installation Process

1. Download the installer from our website
2. Run the installer as administrator
3. Follow the setup wizard instructions
4. Restart your computer when prompted
5. Launch the application to verify installation
```

### Sequential Procedures

```markdown
## Database Setup

1. Install PostgreSQL server
2. Create a new database instance
3. Set up user credentials
4. Configure connection parameters
5. Test the database connection
6. Import initial schema
7. Verify data integrity
```

### Prioritized Lists

```markdown
## Development Priorities

1. Fix critical security vulnerabilities
2. Implement user authentication system
3. Add data validation and error handling
4. Optimize database query performance
5. Enhance user interface design
6. Add comprehensive documentation
7. Implement automated testing
```

## Rich Text Lists

### Formatted Instructions

```markdown
## API Integration Steps

1. **Generate API Key**: Visit the developer console and create a new API key
2. **Set Environment Variables**: Add your API key to your `.env` file
3. **Install SDK**: Run `pip install notionary-sdk` in your project
4. **Initialize Client**: Create a new client instance with your credentials
5. **Make First Call**: Test the connection with a simple API request
6. **Handle Responses**: Implement proper error handling and response parsing
```

### Detailed Procedures

```markdown
## Deployment Checklist

1. **Code Review**: Ensure all changes have been peer-reviewed
   - Check for security vulnerabilities
   - Verify coding standards compliance
   - Confirm test coverage requirements
2. **Testing**: Run comprehensive test suite
   - Execute unit tests: `pytest tests/unit/`
   - Run integration tests: `pytest tests/integration/`
   - Perform manual smoke tests
3. **Documentation**: Update all relevant documentation
   - API documentation updates
   - Changelog entries
   - User guide modifications
4. **Deployment**: Deploy to production environment
   - Create deployment backup
   - Deploy using blue-green strategy
   - Monitor system metrics
5. **Verification**: Confirm successful deployment
   - Check application health endpoints
   - Verify key functionality works
   - Monitor error rates and performance
```

## Nested Numbered Lists

### Multi-level Procedures

```markdown
## Project Setup Guide

1. **Environment Preparation**
   1. Install Python 3.8 or higher
   2. Set up virtual environment
   3. Install development dependencies
   4. Configure IDE settings
2. **Project Initialization**
   1. Clone the repository
   2. Create configuration files
   3. Set up database schema
   4. Run initial migrations
3. **Development Workflow**
   1. Create feature branch
   2. Implement changes
   3. Write comprehensive tests
   4. Submit pull request
```

### Complex Workflows

```markdown
## CI/CD Pipeline Setup

1. **Repository Configuration**
   1. Set up GitHub repository
   2. Configure branch protection rules
   3. Add required status checks
   4. Set up code owners file
2. **Build Pipeline**
   1. Create GitHub Actions workflow
   2. Configure build environments
   3. Set up dependency caching
   4. Add build artifact storage
3. **Testing Pipeline**
   1. Configure test environments
   2. Set up parallel test execution
   3. Add code coverage reporting
   4. Configure quality gates
4. **Deployment Pipeline**
   1. Set up staging environment
   2. Configure production deployment
   3. Add rollback mechanisms
   4. Set up monitoring and alerts
```

## Mixed Content Lists

### Instructions with Code

````markdown
## API Client Setup

1. **Install the SDK**
   ```bash
   pip install notionary-client
   ```
````

2. **Import required modules**
   ```python
   from notionary import NotionClient, NotionPage
   import os
   ```
3. **Initialize the client**
   ```python
   client = NotionClient(token=os.getenv('NOTION_TOKEN'))
   ```
4. **Test the connection**
   ```python
   try:
       page = await NotionPage.from_page_name("Test Page")
       print("Connection successful!")
   except Exception as e:
       print(f"Connection failed: {e}")
   ```

````

### Procedures with Examples

```markdown
## Data Validation Process
1. **Input Sanitization**
   - Remove leading/trailing whitespace
   - Convert to appropriate data types
   - Example: `user_id = int(request.form.get('user_id', 0))`
2. **Format Validation**
   - Check email format: `email_pattern.match(email)`
   - Validate phone numbers: `phone_pattern.match(phone)`
   - Verify date formats: `datetime.strptime(date_str, '%Y-%m-%d')`
3. **Business Rule Validation**
   - Check user permissions
   - Verify data constraints
   - Validate relationships between fields
4. **Error Response Generation**
   - Create standardized error messages
   - Include field-specific validation errors
   - Return appropriate HTTP status codes
````

## Programmatic Usage

### Creating Numbered Lists

```python
from notionary.blocks.numbered_list import NumberedListMarkdownNode

# Simple numbered list
steps = NumberedListMarkdownNode(
    texts=[
        "Create account",
        "Verify email address",
        "Complete profile setup",
        "Start using the platform"
    ]
)

markdown = steps.to_markdown()
```

### Dynamic List Generation

```python
def create_installation_guide(platforms):
    instructions = []
    for i, platform in enumerate(platforms, 1):
        step = f"**{platform['name']}**: {platform['instruction']}"
        if platform.get('note'):
            step += f" _{platform['note']}_"
        instructions.append(step)

    return NumberedListMarkdownNode(texts=instructions)

# Usage
install_steps = [
    {
        "name": "Windows",
        "instruction": "Run the .exe installer",
        "note": "Requires administrator privileges"
    },
    {
        "name": "macOS",
        "instruction": "Open the .dmg file and drag to Applications",
        "note": "May require security permissions"
    },
    {
        "name": "Linux",
        "instruction": "Use package manager: sudo apt install notionary"
```
