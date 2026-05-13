"""模拟数据填充脚本 - 电子车间员工管理系统"""

import os
import random
import sys
from datetime import date, datetime, time, timedelta

# Ensure project root is on sys.path so `app` is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database import SessionLocal, Base, engine
from app.database_migration import migrate_schema
from app.models import (
    Attendance,
    Department,
    Employee,
    EmployeeSkill,
    SkillCatalog,
    Leave,
    Payroll,
    PerformanceCycle,
    PerformanceReview,
    Project,
    ProjectSkillRequirement,
    ProjectMember,
    ProjectTimesheet,
)

# ── 电子车间部门 ──────────────────────────────────────────────
DEPARTMENTS = [
    {"name": "生产部", "description": "负责电子产品组装、焊接与测试", "manager": "王建国"},
    {"name": "品质部", "description": "负责来料检验、制程管控与成品检测", "manager": "李明辉"},
    {"name": "工程部", "description": "负责工艺改进、设备维护与SOP编制", "manager": "张伟东"},
    {"name": "仓储物流部", "description": "负责物料收发、库存管理与成品发货", "manager": "陈志强"},
    {"name": "行政人事部", "description": "负责招聘、培训、考勤与后勤保障", "manager": "刘芳"},
    {"name": "研发部", "description": "负责新产品设计、样机试制与技术文档", "manager": "赵海涛"},
]

# ── 员工姓名池 ────────────────────────────────────────────────
EMPLOYEE_NAMES = [
    "王建国", "李明辉", "张伟东", "陈志强", "刘芳", "赵海涛",
    "周磊", "吴秀英", "孙浩", "杨丽", "朱军", "何晓燕",
    "林涛", "黄艳", "马超", "罗敏", "谢勇", "韩雪梅",
    "唐志刚", "冯玉兰", "曹鹏", "邓丽华", "许强", "彭小兰",
    "肖伟", "田静", "袁波", "蒋秀芳", "蔡明", "潘红",
    "余斌", "叶丽萍", "范晓东", "钟文", "姚华", "卢秀珍",
    "廖建军", "邵英", "孔维", "汤美玲", "严刚", "邹艳",
    "熊飞", "金秀兰", "陆强", "郝丽", "段明", "雷小燕",
]

# 部门对应的薪资范围 (base)
DEPT_SALARY_RANGES = {
    "生产部": (4500, 7500),
    "品质部": (5000, 8000),
    "工程部": (6000, 12000),
    "仓储物流部": (4000, 6500),
    "行政人事部": (4500, 8000),
    "研发部": (8000, 15000),
}

# 部门对应的员工人数
DEPT_EMPLOYEE_COUNTS = {
    "生产部": 15,
    "品质部": 8,
    "工程部": 6,
    "仓储物流部": 5,
    "行政人事部": 4,
    "研发部": 10,
}

# 请假类型
LEAVE_TYPES = [
    ("sick", "病假"),
    ("annual", "年假"),
    ("personal", "事假"),
    ("other", "其他"),
]

LEAVE_REASONS = {
    "sick": ["感冒发烧", "肠胃不适", "牙痛就医", "身体检查"],
    "annual": ["回老家探亲", "旅游休假", "家庭聚会", "个人休假"],
    "personal": ["家中有事", "办理证件", "房屋搬迁", "陪护家人"],
    "other": ["其他原因"],
}

LEAVE_STATUSES = ["approved", "approved", "approved", "pending", "rejected"]

# ── 员工技能配置 ────────────────────────────────────────────────
DEPT_SKILLS = {
    "生产部": [
        {"skill_name": "SMT贴片操作", "proficiency_level": "advanced", "years_of_experience": None, "certification": None},
        {"skill_name": "波峰焊操作", "proficiency_level": "intermediate", "years_of_experience": None, "certification": None},
        {"skill_name": "手工焊接", "proficiency_level": "expert", "years_of_experience": None, "certification": "IPC-A-610"},
        {"skill_name": "产品组装", "proficiency_level": "advanced", "years_of_experience": None, "certification": None},
        {"skill_name": "功能测试", "proficiency_level": "intermediate", "years_of_experience": None, "certification": None},
        {"skill_name": "5S管理", "proficiency_level": "beginner", "years_of_experience": None, "certification": None},
    ],
    "品质部": [
        {"skill_name": "IPC-A-610检验", "proficiency_level": "expert", "years_of_experience": None, "certification": "IPC-A-610 CIS"},
        {"skill_name": "来料检验(IQC)", "proficiency_level": "advanced", "years_of_experience": None, "certification": None},
        {"skill_name": "示波器使用", "proficiency_level": "intermediate", "years_of_experience": None, "certification": None},
        {"skill_name": "SPC统计制程管控", "proficiency_level": "advanced", "years_of_experience": None, "certification": None},
        {"skill_name": "万用表操作", "proficiency_level": "advanced", "years_of_experience": None, "certification": None},
    ],
    "工程部": [
        {"skill_name": "AutoCAD", "proficiency_level": "advanced", "years_of_experience": None, "certification": None},
        {"skill_name": "PLC编程", "proficiency_level": "intermediate", "years_of_experience": None, "certification": None},
        {"skill_name": "设备维修", "proficiency_level": "advanced", "years_of_experience": None, "certification": None},
        {"skill_name": "SOP编制", "proficiency_level": "expert", "years_of_experience": None, "certification": None},
        {"skill_name": "FMEA分析", "proficiency_level": "intermediate", "years_of_experience": None, "certification": None},
    ],
    "仓储物流部": [
        {"skill_name": "ERP系统操作", "proficiency_level": "intermediate", "years_of_experience": None, "certification": None},
        {"skill_name": "叉车操作", "proficiency_level": "advanced", "years_of_experience": None, "certification": "叉车操作证"},
        {"skill_name": "库存管理", "proficiency_level": "intermediate", "years_of_experience": None, "certification": None},
    ],
    "行政人事部": [
        {"skill_name": "劳动法规", "proficiency_level": "advanced", "years_of_experience": None, "certification": None},
        {"skill_name": "招聘面试", "proficiency_level": "intermediate", "years_of_experience": None, "certification": None},
        {"skill_name": "Office办公软件", "proficiency_level": "expert", "years_of_experience": None, "certification": None},
    ],
    "研发部": [
        {"skill_name": "C/C++", "proficiency_level": "advanced", "years_of_experience": None, "certification": None},
        {"skill_name": "Python", "proficiency_level": "intermediate", "years_of_experience": None, "certification": None},
        {"skill_name": "Altium Designer", "proficiency_level": "expert", "years_of_experience": None, "certification": None},
        {"skill_name": "嵌入式开发", "proficiency_level": "advanced", "years_of_experience": None, "certification": None},
        {"skill_name": "电路仿真", "proficiency_level": "intermediate", "years_of_experience": None, "certification": None},
        {"skill_name": "信号完整性分析", "proficiency_level": "beginner", "years_of_experience": None, "certification": None},
        {"skill_name": "EMC设计", "proficiency_level": "intermediate", "years_of_experience": None, "certification": None},
    ],
}

PROFICIENCY_LEVELS = ["beginner", "intermediate", "advanced", "expert"]

# 技能分类映射
SKILL_CATEGORIES = {
    "SMT贴片操作": "生产操作",
    "波峰焊操作": "生产操作",
    "手工焊接": "生产操作",
    "产品组装": "生产操作",
    "功能测试": "生产操作",
    "5S管理": "生产操作",
    "IPC-A-610检验": "品质检验",
    "来料检验(IQC)": "品质检验",
    "示波器使用": "品质检验",
    "SPC统计制程管控": "品质检验",
    "万用表操作": "品质检验",
    "AutoCAD": "工程技术",
    "PLC编程": "工程技术",
    "设备维修": "工程技术",
    "SOP编制": "工程技术",
    "FMEA分析": "工程技术",
    "ERP系统操作": "仓储物流",
    "叉车操作": "仓储物流",
    "库存管理": "仓储物流",
    "劳动法规": "行政管理",
    "招聘面试": "行政管理",
    "Office办公软件": "行政管理",
    "C/C++": "研发技术",
    "Python": "研发技术",
    "Altium Designer": "研发技术",
    "嵌入式开发": "研发技术",
    "电路仿真": "研发技术",
    "信号完整性分析": "研发技术",
    "EMC设计": "研发技术",
}

# ── 项目种子数据 ──────────────────────────────────────────────
PROJECTS_DATA = [
    {
        "name": "智能质检系统开发",
        "description": "基于机器视觉的PCB板自动检测系统，替代人工目检",
        "status": "active",
        "start_date": date(2026, 3, 1),
        "end_date": date(2026, 8, 31),
    },
    {
        "name": "产线MES系统集成",
        "description": "将现有生产线设备接入MES系统，实现生产数据实时采集",
        "status": "active",
        "start_date": date(2026, 4, 15),
        "end_date": date(2026, 10, 31),
    },
    {
        "name": "新产品NPI导入",
        "description": "新一代通信模块的试产与量产导入",
        "status": "planning",
        "start_date": date(2026, 6, 1),
        "end_date": date(2026, 12, 31),
    },
]


def random_time_around(base_hour: int, base_minute: int, spread_minutes: int = 30) -> time:
    """生成基准时间前后 spread_minutes 分钟内的随机时间"""
    total_minutes = base_hour * 60 + base_minute + random.randint(-spread_minutes, spread_minutes)
    total_minutes = max(0, min(23 * 60 + 59, total_minutes))
    return time(total_minutes // 60, total_minutes % 60)


def seed_departments(session) -> dict[str, int]:
    """创建部门，返回 {部门名: id}"""
    dept_ids = {}
    for dept_data in DEPARTMENTS:
        dept = Department(**dept_data)
        session.add(dept)
    session.flush()

    for dept in session.query(Department).all():
        dept_ids[dept.name] = dept.id
    return dept_ids


def seed_employees(session, dept_ids: dict[str, int]) -> list[dict]:
    """创建员工，返回 [{id, name, department_id, salary}, ...]"""
    name_idx = 0
    employees = []

    for dept_name, count in DEPT_EMPLOYEE_COUNTS.items():
        salary_lo, salary_hi = DEPT_SALARY_RANGES[dept_name]
        for _ in range(count):
            if name_idx >= len(EMPLOYEE_NAMES):
                break
            name = EMPLOYEE_NAMES[name_idx]
            name_idx += 1
            salary = round(random.uniform(salary_lo, salary_hi), 2)
            emp = Employee(
                name=name,
                department_id=dept_ids[dept_name],
                salary=salary,
            )
            session.add(emp)
            employees.append({"name": name, "dept_name": dept_name, "salary": salary})

    session.flush()

    # 重新读取以获取自增 id
    emp_records = session.query(Employee).all()
    for i, emp in enumerate(emp_records):
        employees[i]["id"] = emp.id
        employees[i]["department_id"] = emp.department_id

    return employees


def seed_attendance(session, employees: list[dict]):
    """为每位员工生成近 30 个工作日的考勤记录"""
    today = date.today()
    work_dates = []
    d = today - timedelta(days=44)  # 往前多取一些，跳过周末后约 30 个工作日
    while d <= today:
        if d.weekday() < 5:  # 周一到周五
            work_dates.append(d)
        d += timedelta(days=1)
    work_dates = work_dates[-30:]  # 取最近 30 个工作日

    for emp in employees:
        for d in work_dates:
            # 10% 概率缺勤
            if random.random() < 0.10:
                continue

            # 生成签到时间：8:30 ± 30min
            check_in = random_time_around(8, 30, 30)

            # 5% 概率只有签到无签退
            if random.random() < 0.05:
                check_out = None
                status = "normal"
                work_hours = None
            else:
                check_out = random_time_around(18, 0, 45)
                # 计算工时
                in_min = check_in.hour * 60 + check_in.minute
                out_min = check_out.hour * 60 + check_out.minute
                work_hours = round((out_min - in_min) / 60, 1)
                # 判断状态
                is_late = check_in > time(9, 0)
                is_early = check_out < time(18, 0)
                if is_late:
                    status = "late"
                elif is_early:
                    status = "early_leave"
                else:
                    status = "normal"

            record = Attendance(
                employee_id=emp["id"],
                date=d,
                check_in=check_in,
                check_out=check_out,
                status=status,
                work_hours=work_hours,
            )
            session.add(record)


def seed_leaves(session, employees: list[dict]):
    """为部分员工生成请假记录"""
    today = date.today()

    for emp in employees:
        # 每位员工 0~3 条请假
        leave_count = random.randint(0, 3)
        for _ in range(leave_count):
            leave_type, leave_type_name = random.choice(LEAVE_TYPES)
            reason = random.choice(LEAVE_REASONS[leave_type])

            # 随机生成最近 60 天内的请假
            start_offset = random.randint(1, 60)
            start_date = today - timedelta(days=start_offset)
            days = random.randint(1, 5)
            end_date = start_date + timedelta(days=days - 1)

            # 确保不超过今天
            if end_date > today:
                end_date = today
                days = (end_date - start_date).days + 1

            status = random.choice(LEAVE_STATUSES)
            approver = None
            approved_at = None
            if status == "approved":
                approver = random.choice(["王建国", "刘芳", "李明辉"])
                approved_at = datetime(
                    start_date.year, start_date.month, start_date.day,
                    random.randint(8, 17), random.randint(0, 59),
                )

            record = Leave(
                employee_id=emp["id"],
                leave_type=leave_type,
                leave_type_name=leave_type_name,
                start_date=start_date,
                end_date=end_date,
                days=days,
                reason=reason,
                status=status,
                approver=approver,
                approved_at=approved_at,
                created_at=datetime(
                    start_date.year, start_date.month, start_date.day,
                    random.randint(8, 12), random.randint(0, 59),
                ),
            )
            session.add(record)


def seed_payrolls(session, employees: list[dict]):
    """为每位员工生成近 3 个月的薪资记录"""
    today = date.today()
    months = []
    for i in range(1, 4):
        m = today.month - i
        y = today.year
        while m <= 0:
            m += 12
            y -= 1
        months.append(f"{y:04d}-{m:02d}")
    months.reverse()

    for emp in employees:
        base = emp["salary"]
        for month in months:
            # 奖金：0 ~ 30% 底薪
            bonuses = round(random.uniform(0, base * 0.3), 2)
            # 扣款：0 ~ 10% 底薪
            deductions = round(random.uniform(0, base * 0.1), 2)
            net_salary = round(base + bonuses - deductions, 2)

            # 支付日期：次月 10 号
            year, mon = month.split("-")
            pay_year, pay_mon = int(year), int(mon) + 1
            if pay_mon > 12:
                pay_mon = 1
                pay_year += 1
            payment_date = date(pay_year, pay_mon, 10)

            # 最近的月份可能还没发
            if month == months[-1] and random.random() < 0.3:
                status = "pending"
                payment_date = None
            else:
                status = "paid"

            record = Payroll(
                employee_id=emp["id"],
                month=month,
                base_salary=base,
                bonuses=bonuses,
                deductions=deductions,
                net_salary=net_salary,
                status=status,
                payment_date=payment_date,
                created_at=datetime.now() - timedelta(days=random.randint(1, 90)),
            )
            session.add(record)


def seed_performance(session, employees: list[dict]):
    """创建考核周期和绩效评分"""
    today = date.today()

    # 创建 2 个考核周期
    cycles_data = [
        {
            "name": "2025年度上半年考核",
            "start_date": date(2025, 1, 1),
            "end_date": date(2025, 6, 30),
            "description": "2025年上半年绩效考核",
            "status": "closed",
        },
        {
            "name": "2025年度下半年考核",
            "start_date": date(2025, 7, 1),
            "end_date": date(2025, 12, 31),
            "description": "2025年下半年绩效考核",
            "status": "active",
        },
    ]

    cycle_ids = []
    for cd in cycles_data:
        cycle = PerformanceCycle(
            **cd,
            created_at=datetime.now() - timedelta(days=random.randint(60, 180)),
        )
        session.add(cycle)
    session.flush()

    for c in session.query(PerformanceCycle).all():
        cycle_ids.append(c.id)

    # 评分等级映射
    def rating_to_level(rating: float) -> str:
        if rating >= 4.5:
            return "excellent"
        if rating >= 3.5:
            return "good"
        if rating >= 2.5:
            return "average"
        return "poor"

    RATING_COMMENTS = {
        "excellent": [
            "工作表现突出，多次解决生产难题，团队标杆",
            "技术能力过硬，主动承担关键项目，成果显著",
            "工作积极主动，效率高，品质意识强",
        ],
        "good": [
            "工作认真负责，完成各项任务指标",
            "技能水平良好，能独立处理常见问题",
            "团队协作好，按时交付工作成果",
        ],
        "average": [
            "基本完成本职工作，有待提升效率",
            "工作态度尚可，需加强技能学习",
            "能配合团队工作，主动性需提高",
        ],
        "poor": [
            "工作效率偏低，需加强培训和督导",
            "多次出现操作失误，需重点改进",
            "出勤率偏低，影响团队进度",
        ],
    }

    reviewers = ["王建国", "李明辉", "张伟东", "赵海涛", "刘芳"]

    for emp in employees:
        for cycle_id in cycle_ids:
            # 随机评分 2.0 ~ 5.0
            rating = round(random.uniform(2.0, 5.0), 1)
            level = rating_to_level(rating)
            comment = random.choice(RATING_COMMENTS[level])

            review = PerformanceReview(
                employee_id=emp["id"],
                cycle_id=cycle_id,
                rating=rating,
                rating_level=level,
                reviewer=random.choice(reviewers),
                comments=comment,
                created_at=datetime.now() - timedelta(days=random.randint(10, 60)),
            )
            session.add(review)


def seed_skills(session, employees: list[dict], catalog_ids: dict[str, int]):
    """为每位员工生成 2~4 项技能"""
    for emp in employees:
        dept_name = emp["dept_name"]
        dept_skills = DEPT_SKILLS.get(dept_name, [])
        if not dept_skills:
            continue

        # 每位员工随机分配 2~4 项技能
        skill_count = min(random.randint(2, 4), len(dept_skills))
        chosen = random.sample(dept_skills, skill_count)

        for skill_data in chosen:
            # 随机调整熟练程度（与模板有差异）
            level = skill_data["proficiency_level"]
            level_idx = PROFICIENCY_LEVELS.index(level)
            level_idx = max(0, min(len(PROFICIENCY_LEVELS) - 1, level_idx + random.randint(-1, 1)))
            proficiency = PROFICIENCY_LEVELS[level_idx]

            # 随机生成年限
            years = round(random.uniform(0.5, 10.0), 1)
            if proficiency == "beginner":
                years = round(random.uniform(0.5, 2.0), 1)
            elif proficiency == "expert":
                years = round(random.uniform(5.0, 15.0), 1)

            # 保留模板中的认证，或随机清除
            cert = skill_data["certification"]
            if cert and random.random() < 0.4:
                cert = None

            skill_name = skill_data["skill_name"]
            record = EmployeeSkill(
                employee_id=emp["id"],
                skill_name=skill_name,
                skill_id=catalog_ids.get(skill_name),
                proficiency_level=proficiency,
                years_of_experience=years,
                certification=cert,
                created_at=datetime.now() - timedelta(days=random.randint(30, 365)),
            )
            session.add(record)


def seed_skill_catalog(session) -> dict[str, int]:
    """创建技能目录，返回 {技能名称: id}"""
    catalog_ids = {}
    # 收集所有唯一技能
    all_skills = {}
    for dept_skills in DEPT_SKILLS.values():
        for s in dept_skills:
            name = s["skill_name"]
            if name not in all_skills:
                all_skills[name] = SKILL_CATEGORIES.get(name)

    for name, category in all_skills.items():
        record = SkillCatalog(
            name=name,
            category=category,
            created_at=datetime.now() - timedelta(days=random.randint(60, 365)),
        )
        session.add(record)

    session.flush()
    for sc in session.query(SkillCatalog).all():
        catalog_ids[sc.name] = sc.id
    return catalog_ids


def seed_projects(session, employees: list[dict], catalog_ids: dict[str, int]):
    """创建项目、技能需求、成员和工时记录"""
    project_ids = []
    for pd in PROJECTS_DATA:
        project = Project(
            **pd,
            created_at=datetime.now() - timedelta(days=random.randint(30, 90)),
        )
        session.add(project)

    session.flush()
    for p in session.query(Project).all():
        project_ids.append(p.id)

    # 项目1: 智能质检系统 - 需要Python、嵌入式开发、IPC-A-610检验
    req_data_1 = [
        {"skill_id": catalog_ids["Python"], "required_proficiency": "advanced", "person_days": 30.0, "headcount": 2},
        {"skill_id": catalog_ids["嵌入式开发"], "required_proficiency": "advanced", "person_days": 25.0, "headcount": 2},
        {"skill_id": catalog_ids["IPC-A-610检验"], "required_proficiency": "intermediate", "person_days": 15.0, "headcount": 1},
    ]
    req_ids_1 = []
    for rd in req_data_1:
        req = ProjectSkillRequirement(
            project_id=project_ids[0], **rd,
            created_at=datetime.now() - timedelta(days=random.randint(20, 60)),
        )
        session.add(req)
    session.flush()
    for r in session.query(ProjectSkillRequirement).filter_by(project_id=project_ids[0]).all():
        req_ids_1.append(r.id)

    # 项目1成员: 选研发部和品质部员工
    dev_employees = [e for e in employees if e["dept_name"] == "研发部"][:4]
    qa_employees = [e for e in employees if e["dept_name"] == "品质部"][:2]
    member_roles = ["算法工程师", "嵌入式工程师", "测试工程师", "前端开发", "品质顾问", "品质验证"]
    member_list = dev_employees + qa_employees
    member_ids_1 = []
    for i, emp in enumerate(member_list):
        member = ProjectMember(
            project_id=project_ids[0],
            employee_id=emp["id"],
            role=member_roles[i] if i < len(member_roles) else "成员",
            assigned_date=date(2026, 3, 1),
            created_at=datetime.now() - timedelta(days=random.randint(20, 50)),
        )
        session.add(member)
    session.flush()
    for m in session.query(ProjectMember).filter_by(project_id=project_ids[0]).all():
        member_ids_1.append(m.id)

    # 项目1工时记录
    for req_idx, req_id in enumerate(req_ids_1):
        for member_idx, emp in enumerate(member_list[:3]):
            for day_offset in range(0, random.randint(10, 30)):
                work_date = date(2026, 4, 1) + timedelta(days=day_offset)
                if work_date.weekday() >= 5:
                    continue
                if work_date > date.today():
                    continue
                ts = ProjectTimesheet(
                    project_id=project_ids[0],
                    requirement_id=req_id,
                    employee_id=emp["id"],
                    date=work_date,
                    hours=round(random.uniform(4, 8), 1),
                    description=f"项目开发工作",
                    created_at=datetime.now() - timedelta(days=random.randint(1, 30)),
                )
                session.add(ts)

    # 项目2: MES系统集成 - 需要C/C++、PLC编程、ERP系统操作
    req_data_2 = [
        {"skill_id": catalog_ids["C/C++"], "required_proficiency": "advanced", "person_days": 20.0, "headcount": 2},
        {"skill_id": catalog_ids["PLC编程"], "required_proficiency": "advanced", "person_days": 25.0, "headcount": 1},
        {"skill_id": catalog_ids["ERP系统操作"], "required_proficiency": "intermediate", "person_days": 10.0, "headcount": 1},
    ]
    for rd in req_data_2:
        req = ProjectSkillRequirement(
            project_id=project_ids[1], **rd,
            created_at=datetime.now() - timedelta(days=random.randint(10, 30)),
        )
        session.add(req)

    # 项目2成员
    eng_employees = [e for e in employees if e["dept_name"] == "工程部"][:2]
    wh_employees = [e for e in employees if e["dept_name"] == "仓储物流部"][:1]
    dev2_employees = [e for e in employees if e["dept_name"] == "研发部"][4:6]
    mes_roles = ["软件工程师", "PLC工程师", "ERP顾问", "C++开发"]
    mes_members = eng_employees + wh_employees + dev2_employees
    for i, emp in enumerate(mes_members):
        member = ProjectMember(
            project_id=project_ids[1],
            employee_id=emp["id"],
            role=mes_roles[i] if i < len(mes_roles) else "成员",
            assigned_date=date(2026, 4, 15),
            created_at=datetime.now() - timedelta(days=random.randint(5, 20)),
        )
        session.add(member)

    # 项目3: 新产品NPI - 暂无成员和工时（planning状态）
    req_data_3 = [
        {"skill_id": catalog_ids["SMT贴片操作"], "required_proficiency": "advanced", "person_days": 20.0, "headcount": 3},
        {"skill_id": catalog_ids["波峰焊操作"], "required_proficiency": "intermediate", "person_days": 10.0, "headcount": 2},
        {"skill_id": catalog_ids["功能测试"], "required_proficiency": "advanced", "person_days": 15.0, "headcount": 2},
    ]
    for rd in req_data_3:
        req = ProjectSkillRequirement(
            project_id=project_ids[2], **rd,
            created_at=datetime.now() - timedelta(days=random.randint(1, 10)),
        )
        session.add(req)


def main():
    random.seed(42)  # 固定种子保证可复现

    # 确保所有表存在
    Base.metadata.create_all(bind=engine)
    migrate_schema()

    with SessionLocal() as session:
        # 清空所有表
        for table in reversed(Base.metadata.sorted_tables):
            session.execute(table.delete())

        print("正在创建部门...")
        dept_ids = seed_departments(session)

        print("正在创建员工...")
        employees = seed_employees(session, dept_ids)
        print(f"  共创建 {len(employees)} 名员工")

        print("正在创建技能目录...")
        catalog_ids = seed_skill_catalog(session)
        print(f"  共创建 {len(catalog_ids)} 项技能")

        print("正在生成考勤记录...")
        seed_attendance(session, employees)

        print("正在生成请假记录...")
        seed_leaves(session, employees)

        print("正在生成薪资记录...")
        seed_payrolls(session, employees)

        print("正在生成绩效考核记录...")
        seed_performance(session, employees)

        print("正在生成员工技能记录...")
        seed_skills(session, employees, catalog_ids)

        print("正在生成项目数据...")
        seed_projects(session, employees, catalog_ids)

        session.commit()

    # 统计
    with SessionLocal() as session:
        counts = {
            "部门": session.query(Department).count(),
            "员工": session.query(Employee).count(),
            "技能目录": session.query(SkillCatalog).count(),
            "考勤": session.query(Attendance).count(),
            "请假": session.query(Leave).count(),
            "薪资": session.query(Payroll).count(),
            "考核周期": session.query(PerformanceCycle).count(),
            "绩效评分": session.query(PerformanceReview).count(),
            "员工技能": session.query(EmployeeSkill).count(),
            "项目": session.query(Project).count(),
            "技能需求": session.query(ProjectSkillRequirement).count(),
            "项目成员": session.query(ProjectMember).count(),
            "工时记录": session.query(ProjectTimesheet).count(),
        }
        print("\n模拟数据创建完成！")
        for k, v in counts.items():
            print(f"  {k}: {v} 条")


if __name__ == "__main__":
    main()
