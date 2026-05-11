from app.agent.protocol import AgentTool, Skill
from app.services import knowledge_base as kb_service

skill = Skill(
    name="knowledge_base",
    description="电子车间知识库查询与管理",
    applicability="用户询问电子车间操作规程、安全规范、设备使用指南、质检标准等文档内容时使用，"
                  "或需要向知识库添加、查看、删除文档时使用",
    tools=[
        AgentTool(
            name="search_knowledge_base",
            description="在知识库中搜索与查询语义相关的文档片段，返回最相关的内容、来源和相似度评分",
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索查询，用自然语言描述想查找的内容"},
                    "top_k": {"type": "integer", "description": "返回结果数量，默认5"},
                },
                "required": ["query"],
            },
            fn=lambda query, top_k=5: kb_service.search_documents(query, top_k),
        ),
        AgentTool(
            name="add_document_to_knowledge_base",
            description="将文本文档添加到知识库，系统会自动分块、生成向量并存储",
            parameters={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "文档标题"},
                    "content": {"type": "string", "description": "文档正文内容"},
                    "source": {"type": "string", "description": "文档来源标识"},
                },
                "required": ["title", "content"],
            },
            fn=lambda title, content, source="": kb_service.add_document_from_text(
                title=title, content=content, source=source,
            ),
        ),
        AgentTool(
            name="list_knowledge_base_documents",
            description="列出知识库中所有文档及其分块数量",
            parameters={"type": "object", "properties": {}, "required": []},
            fn=lambda: kb_service.list_documents(),
        ),
        AgentTool(
            name="delete_knowledge_base_document",
            description="从知识库中删除指定文档及其所有分块",
            parameters={
                "type": "object",
                "properties": {
                    "doc_id": {"type": "string", "description": "要删除的文档ID"},
                },
                "required": ["doc_id"],
            },
            fn=lambda doc_id: kb_service.delete_document(doc_id),
        ),
    ],
)
