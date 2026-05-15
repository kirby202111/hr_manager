from __future__ import annotations

from app.agent.protocol import AgentTool, Skill, _safe
from app.schemas.agent_memory import MemoryCreate, ReminderCreate
from app.services import agent_memory as memory_service

skill = Skill(
    name="memory",
    description="长期记忆管理：记住和回忆用户偏好、业务观察、待办提醒",
    applicability=(
        "需要记住用户偏好、保存业务观察、设置待办提醒、或回忆之前的对话内容时使用。适用于跨会话的上下文保持"
    ),
    tools=[
        AgentTool(
            name="recall_memories",
            description=("回忆长期记忆，可按类型、分类、主题或关键词搜索。在对话开始或需要历史上下文时调用"),
            parameters={
                "type": "object",
                "properties": {
                    "user_tag": {"type": "string", "description": "用户标识"},
                    "memory_type": {
                        "type": "string",
                        "description": "记忆类型(fact/observation/preference/reminder/context)，可选",
                    },
                    "category": {
                        "type": "string",
                        "description": "业务分类(onboarding/project/employee/analytics/general)，可选",
                    },
                    "subject": {
                        "type": "string",
                        "description": "主题标识，如employee:5，可选",
                    },
                    "keyword": {
                        "type": "string",
                        "description": "关键词搜索，可选",
                    },
                },
                "required": ["user_tag"],
            },
            fn=lambda user_tag, memory_type=None, category=None, subject=None, keyword=None: _safe(
                memory_service.recall_memories,
                user_tag,
                memory_type,
                category,
                subject,
                keyword,
            ),
        ),
        AgentTool(
            name="save_memory",
            description="保存长期记忆，用于记住重要事实、用户偏好、业务观察等",
            parameters={
                "type": "object",
                "properties": {
                    "user_tag": {"type": "string", "description": "用户标识"},
                    "memory_type": {
                        "type": "string",
                        "description": "记忆类型: fact(事实)/observation(观察)/preference(偏好)/context(上下文)",
                    },
                    "category": {
                        "type": "string",
                        "description": "业务分类: onboarding/project/employee/analytics/general",
                    },
                    "subject": {
                        "type": "string",
                        "description": "主题标识，如employee:5, project:3, user_preference",
                    },
                    "content": {
                        "type": "string",
                        "description": "记忆内容（中文）",
                    },
                    "importance": {
                        "type": "integer",
                        "description": "重要性1-5，默认3",
                        "default": 3,
                    },
                },
                "required": ["user_tag", "memory_type", "category", "subject", "content"],
            },
            fn=lambda user_tag, memory_type, category, subject, content, importance=3: _safe(
                memory_service.save_memory,
                MemoryCreate(
                    session_id="agent",
                    user_tag=user_tag,
                    memory_type=memory_type,
                    category=category,
                    subject=subject,
                    content=content,
                    source="agent_observed",
                    importance=importance,
                ),
            ),
        ),
        AgentTool(
            name="check_reminders",
            description="检查待处理的提醒事项，返回已到期的提醒列表",
            parameters={
                "type": "object",
                "properties": {
                    "user_tag": {"type": "string", "description": "用户标识"},
                },
                "required": ["user_tag"],
            },
            fn=lambda user_tag: _safe(
                memory_service.check_pending_reminders,
                user_tag,
            ),
        ),
        AgentTool(
            name="set_reminder",
            description="设置提醒事项，在指定时间提醒用户或自己跟进",
            parameters={
                "type": "object",
                "properties": {
                    "memory_id": {"type": "integer", "description": "关联的记忆ID"},
                    "trigger_at": {
                        "type": "string",
                        "description": "提醒时间，格式YYYY-MM-DD HH:MM",
                    },
                    "reminder_type": {
                        "type": "string",
                        "description": "one_time(一次) 或 recurring(重复)",
                        "default": "one_time",
                    },
                },
                "required": ["memory_id", "trigger_at"],
            },
            fn=lambda memory_id, trigger_at, reminder_type="one_time": _safe(
                memory_service.create_reminder,
                memory_id,
                ReminderCreate(
                    reminder_type=reminder_type,
                    trigger_at=trigger_at,
                ),
            ),
        ),
        AgentTool(
            name="delete_memory",
            description="删除指定的长期记忆",
            parameters={
                "type": "object",
                "properties": {
                    "memory_id": {"type": "integer", "description": "记忆ID"},
                },
                "required": ["memory_id"],
            },
            fn=lambda memory_id: _safe(memory_service.delete_memory, memory_id),
        ),
    ],
)
