from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories import manufacturing as repo
from app.schemas import manufacturing as s
from app.services import production_foundation as svc
from app.services.manufacturing_common import line_exists, list_response, workstation_exists

router = APIRouter(tags=["production foundation"])


@router.post("/production-lines", status_code=201)
def create_line(data: s.ProductionLineCreate, db: Session = Depends(get_db)):
    return svc.create_line(data, db)


@router.get("/production-lines", response_model=s.ListResponse)
def list_lines(db: Session = Depends(get_db)):
    return svc.list_lines(db)


@router.get("/production-lines/{line_id}")
def get_line(line_id: int, db: Session = Depends(get_db)):
    return svc.get_line(line_id, db)


@router.patch("/production-lines/{line_id}")
def update_line(line_id: int, data: s.ProductionLineUpdate, db: Session = Depends(get_db)):
    return svc.update_line(line_id, data, db)


@router.get("/production-lines/{line_id}/workstations", response_model=s.ListResponse)
def line_workstations(line_id: int, db: Session = Depends(get_db)):
    line_exists(line_id, db)
    return list_response("workstation", {"line_id": line_id}, db)


@router.post("/production-teams", status_code=201)
def create_team(data: s.ProductionTeamCreate, db: Session = Depends(get_db)):
    return svc.create_team(data, db)


@router.get("/production-teams", response_model=s.ListResponse)
def list_teams(db: Session = Depends(get_db)):
    return list_response("production_team", db=db)


@router.get("/production-teams/{team_id}")
def get_team(team_id: int, db: Session = Depends(get_db)):
    return svc.get_team(team_id, db)


@router.patch("/production-teams/{team_id}")
def update_team(team_id: int, data: s.ProductionTeamUpdate, db: Session = Depends(get_db)):
    return svc.update_team(team_id, data, db)


@router.get("/production-teams/{team_id}/employees", response_model=s.ListResponse)
def team_employees(team_id: int, db: Session = Depends(get_db)):
    svc.get_team(team_id, db)
    return list_response("employee_team_assignment", {"team_id": team_id}, db)


@router.post("/workstations", status_code=201)
def create_workstation(data: s.WorkstationCreate, db: Session = Depends(get_db)):
    return svc.create_workstation(data, db)


@router.get("/workstations", response_model=s.ListResponse)
def list_workstations(db: Session = Depends(get_db)):
    return list_response("workstation", db=db)


@router.get("/workstations/{workstation_id}")
def get_workstation(workstation_id: int, db: Session = Depends(get_db)):
    return svc.get_workstation(workstation_id, db)


@router.patch("/workstations/{workstation_id}")
def update_workstation(workstation_id: int, data: s.WorkstationUpdate, db: Session = Depends(get_db)):
    return svc.update_workstation(workstation_id, data, db)


@router.post("/workstations/{workstation_id}/required-skills", status_code=201)
def add_required_skill(
    workstation_id: int,
    data: s.WorkstationRequiredSkillCreate,
    db: Session = Depends(get_db),
):
    return svc.add_required_skill(workstation_id, data, db)


@router.get("/workstations/{workstation_id}/required-skills", response_model=s.ListResponse)
def list_required_skills(workstation_id: int, db: Session = Depends(get_db)):
    return list_response("workstation_required_skill", {"workstation_id": workstation_id}, db)


@router.delete("/workstations/{workstation_id}/required-skills/{requirement_id}")
def delete_required_skill(workstation_id: int, requirement_id: int, db: Session = Depends(get_db)):
    workstation_exists(workstation_id, db)
    return {"deleted": repo.delete_record("workstation_required_skill", requirement_id, db)}


@router.post("/workstations/{workstation_id}/required-certifications", status_code=201)
def add_required_certification(
    workstation_id: int,
    data: s.WorkstationRequiredCertificationCreate,
    db: Session = Depends(get_db),
):
    return svc.add_required_certification(workstation_id, data, db)


@router.get("/workstations/{workstation_id}/required-certifications", response_model=s.ListResponse)
def list_required_certifications(workstation_id: int, db: Session = Depends(get_db)):
    return list_response("workstation_required_certification", {"workstation_id": workstation_id}, db)


@router.delete("/workstations/{workstation_id}/required-certifications/{requirement_id}")
def delete_required_certification(workstation_id: int, requirement_id: int, db: Session = Depends(get_db)):
    workstation_exists(workstation_id, db)
    return {"deleted": repo.delete_record("workstation_required_certification", requirement_id, db)}


@router.post("/workstations/{workstation_id}/equipment-requirements", status_code=201)
def add_equipment_requirement(
    workstation_id: int,
    data: s.WorkstationEquipmentRequirementCreate,
    db: Session = Depends(get_db),
):
    return svc.add_equipment_requirement(workstation_id, data, db)


@router.get("/workstations/{workstation_id}/equipment-requirements", response_model=s.ListResponse)
def list_equipment_requirements(workstation_id: int, db: Session = Depends(get_db)):
    return list_response("workstation_equipment_requirement", {"workstation_id": workstation_id}, db)


@router.delete("/workstations/{workstation_id}/equipment-requirements/{requirement_id}")
def delete_equipment_requirement(workstation_id: int, requirement_id: int, db: Session = Depends(get_db)):
    workstation_exists(workstation_id, db)
    return {"deleted": repo.delete_record("workstation_equipment_requirement", requirement_id, db)}
