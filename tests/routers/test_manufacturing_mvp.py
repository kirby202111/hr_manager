from fastapi.testclient import TestClient


def _post(client: TestClient, path: str, payload: dict) -> dict:
    response = client.post(path, json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def test_manufacturing_mvp_happy_path(
    client: TestClient,
    sample_department: dict,
    sample_employee: dict,
    sample_skill_catalog: dict,
):
    line = _post(
        client,
        "/production-lines",
        {"name": "Assembly Line A", "department_id": sample_department["id"]},
    )
    team = _post(client, "/production-teams", {"name": "Day Team", "line_id": line["id"]})
    workstation = _post(
        client,
        "/workstations",
        {"line_id": line["id"], "code": "ASM-01", "name": "Assembly", "risk_level": "high"},
    )
    _post(
        client,
        "/employee-team-assignments",
        {
            "employee_id": sample_employee["id"],
            "team_id": team["id"],
            "line_id": line["id"],
            "start_date": "2026-05-01",
            "is_primary": True,
        },
    )
    profile = _post(
        client,
        "/employee-production-profiles",
        {
            "employee_id": sample_employee["id"],
            "worker_type": "operator",
            "production_status": "active",
            "can_support_lines": [line["id"]],
        },
    )
    assert profile["can_support_lines"] == [line["id"]]

    certification = _post(
        client,
        "/certifications",
        {"name": "Assembly Safety", "category": "safety", "required_training_hours": 4},
    )
    _post(
        client,
        f"/workstations/{workstation['id']}/required-skills",
        {"skill_id": sample_skill_catalog["id"], "required_proficiency": "advanced"},
    )
    _post(
        client,
        f"/workstations/{workstation['id']}/required-certifications",
        {"certification_id": certification["id"], "required": True},
    )
    _post(
        client,
        f"/workstations/{workstation['id']}/equipment-requirements",
        {"equipment_code": "PRESS-01", "required_authorization_level": "operator"},
    )
    _post(
        client,
        "/employee-certifications",
        {
            "employee_id": sample_employee["id"],
            "certification_id": certification["id"],
            "issued_at": "2026-01-01",
            "expires_at": "2027-01-01",
        },
    )
    _post(
        client,
        "/equipment-authorizations",
        {
            "employee_id": sample_employee["id"],
            "equipment_code": "PRESS-01",
            "authorization_level": "operator",
            "issued_at": "2026-01-01",
            "expires_at": "2027-01-01",
        },
    )
    training = _post(client, "/safety-trainings", {"title": "High Risk Safety", "category": "hazard"})
    _post(
        client,
        "/employee-safety-records",
        {
            "employee_id": sample_employee["id"],
            "training_id": training["id"],
            "completed_at": "2026-01-01",
            "expires_at": "2027-01-01",
        },
    )
    _post(
        client,
        "/employee-skills/",
        {
            "employee_id": sample_employee["id"],
            "skill_name": sample_skill_catalog["name"],
            "skill_id": sample_skill_catalog["id"],
            "proficiency_level": "advanced",
        },
    )

    order = _post(
        client,
        "/production-orders",
        {"order_no": "PO-001", "product_name": "Controller", "line_id": line["id"], "planned_quantity": 100},
    )
    _post(
        client,
        f"/production-orders/{order['id']}/operations",
        {
            "workstation_id": workstation["id"],
            "process_code": "ASM",
            "sequence": 1,
            "required_headcount": 1,
        },
    )
    shift = _post(
        client,
        "/shifts",
        {"code": "D1", "name": "Day", "start_time": "08:00:00", "end_time": "16:00:00"},
    )
    plan = _post(
        client,
        "/production-shift-plans",
        {
            "order_id": order["id"],
            "line_id": line["id"],
            "shift_id": shift["id"],
            "work_date": "2026-05-20",
            "required_headcount": 1,
        },
    )
    _post(
        client,
        "/shift-assignments",
        {"plan_id": plan["id"], "employee_id": sample_employee["id"], "workstation_id": workstation["id"]},
    )

    validation = client.post(f"/production-shift-plans/{plan['id']}/validate")
    assert validation.status_code == 200
    assert validation.json()["valid"] is True
    publish = client.post(f"/production-shift-plans/{plan['id']}/publish")
    assert publish.status_code == 200
    assert publish.json()["status"] == "published"


def test_shift_plan_validation_generates_risk_signal(
    client: TestClient,
    sample_department: dict,
    sample_employee: dict,
):
    line = _post(client, "/production-lines", {"name": "Line B", "department_id": sample_department["id"]})
    workstation = _post(
        client,
        "/workstations",
        {"line_id": line["id"], "code": "PACK-01", "name": "Packing", "risk_level": "low"},
    )
    shift = _post(
        client,
        "/shifts",
        {"code": "N1", "name": "Night", "start_time": "20:00:00", "end_time": "04:00:00", "shift_type": "night"},
    )
    plan = _post(
        client,
        "/production-shift-plans",
        {"line_id": line["id"], "shift_id": shift["id"], "work_date": "2026-05-21", "required_headcount": 2},
    )
    _post(
        client,
        "/shift-assignments",
        {"plan_id": plan["id"], "employee_id": sample_employee["id"], "workstation_id": workstation["id"]},
    )

    publish = client.post(f"/production-shift-plans/{plan['id']}/publish")
    assert publish.status_code == 400
    risks = client.get("/production-risk-signals")
    assert risks.status_code == 200
    assert any(item["signal_type"] == "insufficient_headcount" for item in risks.json()["items"])
