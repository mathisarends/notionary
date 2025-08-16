from notionary.blocks.heading.heading_markdown_node import HeadingMarkdownBlockParams
from notionary.blocks.paragraph.paragraph_markdown_node import ParagraphMarkdownBlockParams
from notionary.blocks.bulleted_list.bulleted_list_markdown_node import BulletedListMarkdownBlockParams
from notionary.blocks.table.table_markdown_node import TableMarkdownBlockParams
from notionary.blocks.numbered_list.numbered_list_markdown_node import NumberedListMarkdownBlockParams
from notionary.markdown.markdown_document_model import (
    MarkdownDocumentModel, 
    HeadingBlock, 
    ParagraphBlock, 
    BulletedListBlock,
    TableBlock,
    NumberedListBlock,
    ToggleBlock,
    ToggleBlockParams
)


def create_complex_test() -> MarkdownDocumentModel:
    """Komplexeres Beispiel mit Toggle und Tabelle."""
    return MarkdownDocumentModel(blocks=[
        # Hauptüberschrift
        HeadingBlock(params=HeadingMarkdownBlockParams(
            text="Project Documentation", 
            level=1
        )),
        
        # Einführung
        ParagraphBlock(params=ParagraphMarkdownBlockParams(
            text="This is a comprehensive project overview with advanced markdown features including tables and collapsible sections."
        )),
        
        # Schneller Überblick
        HeadingBlock(params=HeadingMarkdownBlockParams(
            text="Quick Overview", 
            level=2
        )),
        
        BulletedListBlock(params=BulletedListMarkdownBlockParams(
            texts=[
                "Modern web application",
                "Built with Python and React", 
                "Deployed on AWS",
                "Microservices architecture"
            ]
        )),
        
        # Projekt Status Tabelle
        HeadingBlock(params=HeadingMarkdownBlockParams(
            text="Project Status", 
            level=2
        )),
        
        TableBlock(params=TableMarkdownBlockParams(
            headers=["Component", "Status", "Priority", "Assignee"],
            rows=[
                ["Frontend", "✅ Complete", "High", "Alice"],
                ["Backend API", "🚧 In Progress", "High", "Bob"],
                ["Database", "✅ Complete", "Medium", "Charlie"],
                ["Testing", "📋 Planned", "Medium", "Diana"],
                ["Deployment", "📋 Planned", "Low", "Eve"]
            ]
        )),
        
        # Toggle mit verschachteltem Inhalt
        HeadingBlock(params=HeadingMarkdownBlockParams(
            text="Technical Details", 
            level=2
        )),
        
        ToggleBlock(params=ToggleBlockParams(
            title="Click to view technical specifications",
            children=[
                # Verschachtelte Inhalte im Toggle
                HeadingBlock(params=HeadingMarkdownBlockParams(
                    text="Architecture", 
                    level=3
                )),
                
                ParagraphBlock(params=ParagraphMarkdownBlockParams(
                    text="The application follows a microservices architecture with the following components:"
                )),
                
                NumberedListBlock(params=NumberedListMarkdownBlockParams(
                    texts=[
                        "React frontend with TypeScript",
                        "Python FastAPI backend",
                        "PostgreSQL database",
                        "Redis for caching",
                        "Docker containerization"
                    ]
                )),
                
                HeadingBlock(params=HeadingMarkdownBlockParams(
                    text="Performance Metrics", 
                    level=3
                )),
                
                TableBlock(params=TableMarkdownBlockParams(
                    headers=["Metric", "Target", "Current"],
                    rows=[
                        ["Response Time", "< 200ms", "150ms"],
                        ["Uptime", "99.9%", "99.8%"],
                        ["Throughput", "1000 req/s", "850 req/s"],
                        ["Memory Usage", "< 512MB", "380MB"]
                    ]
                )),
                
                ParagraphBlock(params=ParagraphMarkdownBlockParams(
                    text="All metrics are within acceptable ranges. Memory optimization is ongoing."
                ))
            ]
        )),
        
        # Fazit
        HeadingBlock(params=HeadingMarkdownBlockParams(
            text="Next Steps", 
            level=2
        )),
        
        BulletedListBlock(params=BulletedListMarkdownBlockParams(
            texts=[
                "Complete backend API development",
                "Implement comprehensive testing suite",
                "Set up CI/CD pipeline",
                "Prepare production deployment"
            ]
        )),
        
        ParagraphBlock(params=ParagraphMarkdownBlockParams(
            text="The project is on track for delivery by the end of the quarter. All critical components are either complete or in active development."
        ))
    ])


if __name__ == "__main__":
    # Test
    doc = create_complex_test()
    markdown = doc.to_markdown()
    
    print("Generated Complex Markdown:")
    print("=" * 50)
    print(markdown)
    print("=" * 50)