"""模拟数据填充脚本 - 电子车间员工管理系统"""

import random
from datetime import date, datetime, time, timedelta

from app.database import SessionLocal
from app.models.orm import (
    Attendance,
    Department,
    Employee,
    Leave,
    Payroll,
    PerformanceCycle,
    PerformanceReview,
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


def main():
    random.seed(42)  # 固定种子保证可复现

    with SessionLocal() as session:
        # 清空所有表
        for table in reversed(Base.metadata.sorted_tables):
            session.execute(table.delete())

        print("正在创建部门...")
        dept_ids = seed_departments(session)

        print("正在创建员工...")
        employees = seed_employees(session, dept_ids)
        print(f"  共创建 {len(employees)} 名员工")

        print("正在生成考勤记录...")
        seed_attendance(session, employees)

        print("正在生成请假记录...")
        seed_leaves(session, employees)

        print("正在生成薪资记录...")
        seed_payrolls(session, employees)

        print("正在生成绩效考核记录...")
        seed_performance(session, employees)

        session.commit()

    # 统计
    with SessionLocal() as session:
        counts = {
            "部门": session.query(Department).count(),
            "员工": session.query(Employee).count(),
            "考勤": session.query(Attendance).count(),
            "请假": session.query(Leave).count(),
            "薪资": session.query(Payroll).count(),
            "考核周期": session.query(PerformanceCycle).count(),
            "绩效评分": session.query(PerformanceReview).count(),
        }
        print("\n模拟数据创建完成！")
        for k, v in counts.items():
            print(f"  {k}: {v} 条")


if __name__ == "__main__":
    from app.database import Base
    main()
