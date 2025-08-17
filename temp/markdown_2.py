import asyncio

from notionary import MarkdownBuilder


async def main():
    """Generate comprehensive documentation and append to Jarvis Clipboard page."""
    
    # Create a comprehensive technical documentation page
    builder = MarkdownBuilder()

    # Build complex markdown document
    result = (
        builder
        # Header section with breadcrumb
        .breadcrumb()
        .space()
        # Main title and introduction
        .h1("🚀 Advanced Project Documentation")
        .paragraph(
            "**Welcome to the comprehensive guide for our advanced software project.** This documentation covers everything from architecture to deployment, featuring interactive examples and detailed explanations."
        )
        .space()
        # Table of contents
        .table_of_contents("blue_background")
        .space()
        # Overview callout
        .callout(
            "📋 **Project Overview**: This document demonstrates all available markdown elements in a real-world documentation scenario.",
            "🎯",
        )
        .space()
        # Two-column layout: Quick stats and project status
        .columns(
            lambda col: (
                col.h2("📊 Project Statistics")
                .table(
                    ["Metric", "Value", "Status"],
                    [
                        ["Lines of Code", "125,847", "✅ Healthy"],
                        ["Test Coverage", "94.2%", "✅ Excellent"],
                        ["Dependencies", "23", "⚠️ Monitor"],
                        ["Build Time", "2.3 min", "✅ Good"],
                        ["Contributors", "12", "✅ Active"],
                    ],
                )
                .space()
                .callout("All metrics are updated daily via CI/CD pipeline.", "📈")
            ),
            lambda col: (
                col.h2("🎯 Current Sprint")
                .todo_list(
                    [
                        "Implement user authentication",
                        "Optimize database queries",
                        "Add monitoring dashboards",
                        "Update API documentation",
                        "Security audit",
                    ],
                    [True, True, False, False, False],
                )
                .space()
                .quote(
                    '"Great software is built one commit at a time." - Team Lead'
                )
            ),
            width_ratios=[0.6, 0.4],
        )
        .space()
        # Architecture section with toggleable content
        .h2("🏗️ System Architecture")
        .paragraph(
            "Our system follows a microservices architecture with event-driven communication patterns."
        )
        .toggleable_heading(
            "Database Design",
            3,
            lambda t: (
                t.paragraph(
                    "The database schema is optimized for performance and scalability:"
                )
                .code(
                    """-- User table with optimized indexes
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);""",
                    "sql",
                )
                .space()
                .callout(
                    "All tables use proper indexing strategies for optimal query performance.",
                    "⚡",
                )
            ),
        )
        .toggleable_heading(
            "API Endpoints",
            3,
            lambda t: (
                t.paragraph(
                    "RESTful API with comprehensive error handling and rate limiting:"
                )
                .table(
                    ["Endpoint", "Method", "Description", "Rate Limit"],
                    [
                        ["/api/v1/users", "GET", "List all users", "100/min"],
                        ["/api/v1/users/{id}", "GET", "Get user by ID", "1000/min"],
                        ["/api/v1/users", "POST", "Create new user", "10/min"],
                        [
                            "/api/v1/auth/login",
                            "POST",
                            "User authentication",
                            "5/min",
                        ],
                        ["/api/v1/data/export", "GET", "Export data", "1/hour"],
                    ],
                )
                .space()
                .code(
                    """# Example API usage in Python
import requests

# Authenticate user
response = requests.post('/api/v1/auth/login', {
    'email': 'user@example.com',
    'password': 'secure_password'
})

if response.status_code == 200:
    token = response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}'}
    
    # Fetch user data
    user_data = requests.get('/api/v1/users/123', headers=headers)
    print(user_data.json())""",
                    "python",
                )
            ),
        )
        .space()
        # Development workflow
        .h2("⚙️ Development Workflow")
        .paragraph(
            "Our development process ensures code quality and seamless collaboration."
        )
        .columns(
            lambda col: (
                col.h3("🔄 CI/CD Pipeline")
                .numbered_list(
                    [
                        "Code commit triggers webhook",
                        "Automated tests run in parallel",
                        "Code quality checks (linting, security)",
                        "Build Docker images",
                        "Deploy to staging environment",
                        "Run integration tests",
                        "Deploy to production (if approved)",
                    ]
                )
                .space()
                .mermaid(
                    """graph TD
    A[Code Commit] --> B[Run Tests]
    B --> C{Tests Pass?}
    C -->|Yes| D[Build Image]
    C -->|No| E[Notify Developer]
    D --> F[Deploy Staging]
    F --> G[Integration Tests]
    G --> H{Tests Pass?}
    H -->|Yes| I[Deploy Production]
    H -->|No| E""",
                    "CI/CD Pipeline Flow",
                )
            ),
            lambda col: (
                col.h3("🛠️ Development Tools")
                .callout(
                    "**IDE Setup**: VS Code with recommended extensions for optimal development experience.",
                    "💻",
                )
                .space()
                .toggle(
                    "Required VS Code Extensions",
                    lambda t: (
                        t.bulleted_list(
                            [
                                "Python Extension Pack",
                                "GitLens — Git supercharged",
                                "Docker Extension",
                                "Thunder Client (API testing)",
                                "Error Lens",
                                "Prettier - Code formatter",
                                "ESLint",
                                "Auto Rename Tag",
                            ]
                        )
                        .space()
                        .code(
                            """// VS Code settings.json
{
    "python.defaultInterpreter": "./venv/bin/python",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    },
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true
}""",
                            "json",
                        )
                    ),
                )
                .space()
                .paragraph(
                    "**Docker Development**: All services run in containers for consistency across environments."
                )
            ),
        )
        .space()
        # Monitoring and observability
        .h2("📊 Monitoring & Observability")
        .paragraph(
            "Comprehensive monitoring ensures system reliability and performance optimization."
        )
        .toggle(
            "Metrics Dashboard",
            lambda t: (
                t.paragraph(
                    "Real-time system metrics tracked across all components:"
                )
                .table(
                    [
                        "Service",
                        "CPU Usage",
                        "Memory",
                        "Response Time",
                        "Error Rate",
                    ],
                    [
                        ["API Gateway", "23%", "1.2GB", "45ms", "0.01%"],
                        ["User Service", "18%", "890MB", "32ms", "0.00%"],
                        ["Database", "35%", "2.1GB", "12ms", "0.00%"],
                        ["Cache Layer", "8%", "512MB", "2ms", "0.00%"],
                        ["Message Queue", "12%", "256MB", "8ms", "0.00%"],
                    ],
                )
                .space()
                .equation(
                    "\\text{Availability} = \\frac{\\text{Total Time} - \\text{Downtime}}{\\text{Total Time}} \\times 100\\%"
                )
                .space()
                .callout(
                    "Current system availability: **99.97%** (exceeding SLA target of 99.9%)",
                    "✅",
                )
            ),
        )
        .toggle(
            "Alert Configuration",
            lambda t: (
                t.paragraph("Automated alerting for critical system events:")
                .code(
                    """# Prometheus alerting rules
groups:
  - name: api_alerts
    rules:
    - alert: HighErrorRate
      expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
      for: 2m
      labels:
        severity: critical
      annotations:
        summary: "High error rate detected"
        description: "Error rate is {{ $value }} errors per second"
        
    - alert: HighMemoryUsage
      expr: memory_usage_percent > 90
      for: 5m
      labels:
        severity: warning
      annotations:
        summary: "High memory usage"
        description: "Memory usage is {{ $value }}%"
""",
                    "yaml",
                )
                .space()
                .bulleted_list(
                    [
                        "Slack notifications for critical alerts",
                        "PagerDuty integration for 24/7 on-call",
                        "Email summaries for daily reports",
                        "SMS alerts for severe outages",
                    ]
                )
            ),
        )
        .space()
        # Security section
        .h2("🔐 Security & Compliance")
        .paragraph(
            "Security is integrated throughout our development lifecycle and infrastructure."
        )
        .columns(
            lambda col: (
                col.h3("🛡️ Security Measures")
                .callout(
                    "**Zero Trust Architecture**: Every request is verified regardless of source.",
                    "🔒",
                )
                .space()
                .numbered_list(
                    [
                        "Multi-factor authentication (MFA)",
                        "End-to-end encryption",
                        "Regular security audits",
                        "Automated vulnerability scanning",
                        "Principle of least privilege",
                    ]
                )
                .space()
                .toggle(
                    "Encryption Standards",
                    lambda t: (
                        t.paragraph(
                            "All data encryption follows industry best practices:"
                        )
                        .table(
                            ["Data Type", "Encryption", "Key Length"],
                            [
                                ["Data at Rest", "AES-256-GCM", "256-bit"],
                                ["Data in Transit", "TLS 1.3", "256-bit"],
                                ["Database", "Transparent Encryption", "256-bit"],
                                ["Backups", "AES-256-CBC", "256-bit"],
                            ],
                        )
                        .space()
                        .code(
                            """# Example encryption implementation
from cryptography.fernet import Fernet
import base64

def encrypt_data(data: str, key: bytes) -> str:
    f = Fernet(key)
    encrypted_data = f.encrypt(data.encode())
    return base64.b64encode(encrypted_data).decode()

def decrypt_data(encrypted_data: str, key: bytes) -> str:
    f = Fernet(key)
    decoded_data = base64.b64decode(encrypted_data.encode())
    decrypted_data = f.decrypt(decoded_data)
    return decrypted_data.decode()""",
                            "python",
                        )
                    ),
                )
            ),
            lambda col: (
                col.h3("📋 Compliance")
                .paragraph(
                    "Meeting regulatory requirements across multiple jurisdictions:"
                )
                .todo_list(
                    [
                        "GDPR compliance audit",
                        "SOC 2 Type II certification",
                        "HIPAA security assessment",
                        "ISO 27001 preparation",
                        "PCI DSS Level 1 validation",
                    ],
                    [True, True, False, False, False],
                )
                .space()
                .quote(
                    '"Compliance is not a destination, but a continuous journey of improvement." - Security Officer'
                )
                .space()
                .callout("Next audit scheduled for Q2 2024", "📅")
            ),
            width_ratios=[0.55, 0.45],
        )
        .space()
        # Media and resources
        .h2("📚 Resources & Media")
        .paragraph("Additional resources for team members and stakeholders.")
        .columns(
            lambda col: (
                col.h3("🎥 Training Videos")
                .video(
                    "https://example.com/training-api-usage.mp4",
                    "API Usage Training (15 min)",
                )
                .space()
                .video(
                    "https://example.com/security-best-practices.mp4",
                    "Security Best Practices (22 min)",
                )
                .space()
                .h3("🔊 Podcast Episodes")
                .audio(
                    "https://example.com/architecture-decisions.mp3",
                    "Architecture Decision Records Discussion",
                )
            ),
            lambda col: (
                col.h3("📄 Documentation")
                .file(
                    "https://example.com/api-specification.json",
                    "OpenAPI 3.0 Specification",
                )
                .space()
                .pdf(
                    "https://example.com/architecture-guide.pdf",
                    "System Architecture Guide (v2.1)",
                )
                .space()
                .h3("🔗 External Resources")
                .bookmark(
                    "https://docs.python.org/3/",
                    "Python 3 Documentation",
                    "Official Python documentation and tutorials",
                )
                .space()
                .bookmark(
                    "https://fastapi.tiangolo.com/",
                    "FastAPI Documentation",
                    "Modern Python web framework documentation",
                )
                .space()
                .embed(
                    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                    "Team Building Event Highlights",
                )
            ),
        )
        .space()
        # Mathematical formulas
        .h2("📐 Performance Calculations")
        .paragraph("Key performance metrics and their mathematical foundations:")
        .equation(
            "\\text{Throughput} = \\frac{\\text{Requests Processed}}{\\text{Time Period}}"
        )
        .space()
        .equation(
            "\\text{Latency}_{p99} = \\text{percentile}(\\text{response\\_times}, 99)"
        )
        .space()
        .toggle(
            "Advanced Metrics",
            lambda t: (
                t.paragraph(
                    "Complex performance calculations for system optimization:"
                )
                .equation(
                    "\\text{Utilization} = \\frac{\\text{Busy Time}}{\\text{Total Time}} \\times 100\\%"
                )
                .space()
                .equation("\\text{Queue Length} = \\lambda \\times W")
                .paragraph("Where λ is arrival rate and W is average waiting time")
                .space()
                .equation(
                    "\\text{Capacity Planning} = \\text{Current Load} \\times \\frac{\\text{Growth Rate}}{\\text{Target Utilization}}"
                )
            ),
        )
        .space()
        # Final sections
        .divider()
        .space()
        .h2("🎯 Next Steps")
        .columns(
            lambda col: (
                col.h3("🚧 Immediate Actions").todo_list(
                    [
                        "Complete security audit",
                        "Optimize database queries",
                        "Update deployment scripts",
                        "Review monitoring alerts",
                    ]
                )
            ),
            lambda col: (
                col.h3("📅 Upcoming Milestones").numbered_list(
                    [
                        "Q1: Performance optimization",
                        "Q2: Security certification",
                        "Q3: Multi-region deployment",
                        "Q4: ML integration",
                    ]
                )
            ),
        )
        .space()
        .callout(
            "**Questions?** Contact the development team via Slack #dev-team or email dev@company.com",
            "💬",
        )
        .space()
        .divider()
        .paragraph("*Last updated: " + "2024-01-15" + " | Version: 2.1.0*")
        # Build the final markdown
        .build()
    )
    
    print(result)


if __name__ == "__main__":
    asyncio.run(main())