"""
# Notionary: Page Management Example
===================================

This example demonstrates how to find and modify Notion pages,
including content updates, property changes, and formatting.

IMPORTANT: Replace PAGE_NAME with the name of an existing Notion page.
The factory will use fuzzy matching to find the closest match to this name.
"""
import asyncio
from textwrap import dedent

from notionary import NotionPage

PAGE_NAME = "Jarvis Clipboard"


async def main():
    """Demonstrate page operations with Notionary."""
    print("📄 Notionary Page Example")
    print("========================")

    try:
        print(f"\n🔎 Finding page '{PAGE_NAME}'...")
        page = await NotionPage.from_page_name(PAGE_NAME)

        print("✨ Updating page properties...")

        # Sophisticated markdown with multiple complex elements
        markdown = dedent("""# 🚀 Advanced Project Management Dashboard

        Welcome to our comprehensive project management system. This document demonstrates various Notion block types and formatting options.

        ## 📋 Project Overview

        This section provides a high-level overview of our current projects and their status.

        !> [💡] **Important Note**: All project data is updated in real-time and reflects the current status as of the last sync.

        ### Current Active Projects

        +## 🔧 Project Alpha - Infrastructure Upgrade
        | **Project Status**: In Progress
        | **Timeline**: Q2 2024 - Q4 2024  
        | **Budget**: $150,000
        | 
        | ### Key Objectives
        | - [ ] Migrate legacy systems to cloud infrastructure
        | - [x] Complete security audit and compliance review
        | - [ ] Implement automated backup systems
        | - [x] Setup monitoring and alerting
        | 
        | ### Technical Details
        | ```python
        | # Infrastructure configuration
        | CLOUD_PROVIDER = "AWS"
        | REGIONS = ["us-east-1", "eu-west-1"] 
        | AUTO_SCALING = True
        | BACKUP_RETENTION = 30  # days
        | ```

        +## 📱 Project Beta - Mobile App Development  
        | **Project Status**: Planning Phase
        | **Timeline**: Q3 2024 - Q1 2025
        | **Budget**: $200,000
        |
        | ### Development Stack
        | - **Frontend**: React Native
        | - **Backend**: Node.js with Express
        | - **Database**: PostgreSQL with Redis cache
        | - **Authentication**: OAuth 2.0 + JWT
        |
        | ### Milestones
        | - [ ] Complete UI/UX design mockups
        | - [ ] Setup development environment
        | - [ ] Implement core authentication system
        | - [ ] Build MVP features
        | - [ ] Beta testing with internal team

        ## 📊 Performance Metrics

        | Metric | Q1 2024 | Q2 2024 | Target Q3 |
        | ------ | ------- | ------- | --------- |
        | Revenue | $250K | $280K | $320K |
        | Users | 1,200 | 1,450 | 1,800 |
        | Uptime | 99.2% | 99.7% | 99.9% |
        | Support Tickets | 45 | 32 | <25 |

        !> [⚠️] **Alert**: Revenue growth is below target. Review pricing strategy and customer acquisition funnel.

        ## 🎯 Task Management

        ### High Priority Tasks
        - [x] Complete Q2 financial review
        - [ ] Finalize vendor contracts for Q3
        - [ ] Update security protocols
        - [ ] Schedule team performance reviews

        ### Development Tasks  
        - [ ] Fix critical bug in payment processing
        - [x] Implement new user onboarding flow
        - [ ] Optimize database queries for better performance
        - [ ] Add integration tests for API endpoints

        +++ 📝 Meeting Notes Archive
        | ### Weekly Standup - March 15, 2024
        | **Attendees**: Alice, Bob, Carol, David
        | **Duration**: 45 minutes
        | 
        | #### Discussion Points
        | - Project Alpha timeline review
        | - Budget allocation for Q2
        | - New hiring requirements
        | - Security audit findings
        | 
        | #### Action Items
        | - [ ] Alice: Update project timeline
        | - [ ] Bob: Review security recommendations  
        | - [ ] Carol: Prepare hiring job descriptions
        | - [ ] David: Schedule client check-in meetings

        ## 🔄 Integrations & Tools

        We use various tools and integrations to streamline our workflow:

        ::: columns
        ::: column
        ### Development Tools
        - **Git**: GitHub Enterprise
        - **CI/CD**: Jenkins + Docker
        - **Monitoring**: DataDog
        - **Communication**: Slack

        ### Project Management
        - **Planning**: Notion (this!)
        - **Tracking**: Jira
        - **Design**: Figma
        - **Documentation**: Confluence
        :::
        ::: column
        ### Infrastructure
        - **Cloud**: AWS Multi-Region
        - **CDN**: CloudFlare
        - **Database**: RDS PostgreSQL
        - **Cache**: ElastiCache Redis

        ### Security & Compliance
        - **Auth**: Auth0
        - **Secrets**: AWS Secrets Manager
        - **Monitoring**: CloudWatch
        - **Backup**: Automated daily snapshots
        :::
        :::

        ## 📈 Financial Overview

        +### 💰 Q2 2024 Budget Breakdown
        | **Category**: Development - **Allocated**: $80,000
        | **Category**: Infrastructure - **Allocated**: $45,000  
        | **Category**: Marketing - **Allocated**: $35,000
        | **Category**: Operations - **Allocated**: $25,000
        |
        | ```javascript
        | // Budget calculation script
        | const totalBudget = 185000;
        | const categories = {
        |   development: 0.43,
        |   infrastructure: 0.24, 
        |   marketing: 0.19,
        |   operations: 0.14
        | };
        | 
        | Object.entries(categories).forEach(([cat, percent]) => {
        |   console.log(`${cat}: $${totalBudget * percent}`);
        | });
        | ```

        ---

        ## 🎯 Next Steps & Roadmap

        !> [🔔] **Reminder**: All stakeholders should review this document before the quarterly planning meeting on March 30th.

        ### Immediate Actions (Next 2 Weeks)
        1. Complete Project Alpha milestone review
        2. Finalize Project Beta technical specifications  
        3. Update team capacity planning for Q3
        4. Schedule architecture review sessions

        ### Medium-term Goals (Next Quarter)
        - Launch Project Beta MVP
        - Complete infrastructure migration
        - Implement new monitoring solutions
        - Expand team by 3 developers

        ### Long-term Vision (Next Year)
        - Scale to 10,000+ active users
        - Achieve 99.9% uptime SLA
        - Launch international markets
        - Complete Series A funding round

        **Last Updated**: @date[2024-03-15]
        **Next Review**: @date[2024-03-30]

        ---

        *This document is automatically synced with our project management systems and reflects real-time data from multiple sources.*""")

        await page.append_markdown(markdown, append_divider=True)

        print("✅ Successfully added sophisticated content with:")
        print("   • Multiple heading levels and toggleable headings")
        print("   • Callouts with different emojis and styles")
        print("   • Code blocks with syntax highlighting")
        print("   • Complex tables with financial data")
        print("   • Todo items and task management")
        print("   • Toggle sections with nested content")
        print("   • Column layouts for comparisons")
        print("   • Page mentions and date references")
        print("   • Dividers for section separation")
        print("   • Mixed formatting and special characters")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("🚀 Starting sophisticated Notionary example...")
    asyncio.run(main())
    print("✅ Sophisticated example completed!")
