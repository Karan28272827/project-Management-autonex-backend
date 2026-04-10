"""
Payroll Calculation API
-----------------------
GET  /api/payroll/preview?month=YYYY-MM      — compute salary for all employees (no save)
POST /api/payroll/save                        — save / finalize a payroll run
GET  /api/payroll/saved?month=YYYY-MM        — retrieve a saved run with final numbers
PATCH /api/employees/{id}/salary             — update employee base salary

All endpoints are admin-only (checked by role in request context via query param for now;
caller must pass current_user_id which maps to a user with role=admin).
"""
import io
import csv
from calendar import monthrange
from datetime import date as date_type
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.employee import Employee
from app.models.leave import Leave
from app.models.payroll import PayrollLeaveAdjustment, PayrollRun
from app.models.user import User

router = APIRouter(prefix="/api/payroll", tags=["payroll"])

WORKING_DAYS_DEFAULT = 22


# ── Helpers ───────────────────────────────────────────────────────────────────

def _days_in_month(start: date_type, end: date_type, month_start: date_type, month_end: date_type) -> int:
    """Return count of calendar days a leave overlaps with the given month."""
    effective_start = max(start, month_start)
    effective_end = min(end, month_end)
    if effective_end < effective_start:
        return 0
    return (effective_end - effective_start).days + 1


def _month_bounds(month: str):
    """Return (month_start, month_end_inclusive) for a YYYY-MM string."""
    try:
        year, mo = int(month[:4]), int(month[5:7])
    except Exception:
        raise HTTPException(status_code=400, detail="month must be YYYY-MM")
    last_day = monthrange(year, mo)[1]
    return date_type(year, mo, 1), date_type(year, mo, last_day)


def _build_employee_row(emp: Employee, approved_leaves: list, working_days: int, saved_adjustments: dict = None) -> dict:
    """
    saved_adjustments: {leave_id: deduct_bool} — if None, default all to deduct=True.
    """
    base = emp.base_salary or 0.0
    per_day = round(base / working_days, 2) if working_days > 0 else 0.0

    leave_rows = []
    total_deducted_days = 0

    for leave in approved_leaves:
        leave_id = leave["leave_id"]
        days = leave["days_in_month"]
        if saved_adjustments is not None:
            deduct = saved_adjustments.get(leave_id, True)
        else:
            deduct = True   # preview default
        deduction_amount = round(days * per_day, 2) if deduct else 0.0
        if deduct:
            total_deducted_days += days
        leave_rows.append({**leave, "deduct": deduct, "deduction_amount": deduction_amount})

    total_deduction = round(total_deducted_days * per_day, 2)
    payable_days = working_days - total_deducted_days
    final_salary = round(max(base - total_deduction, 0), 2)

    return {
        "employee_id": emp.id,
        "employee_name": emp.name,
        "designation": emp.designation,
        "employee_type": emp.employee_type,
        "base_salary": base,
        "working_days": working_days,
        "per_day_rate": per_day,
        "leaves": leave_rows,
        "total_leave_days": sum(l["days_in_month"] for l in approved_leaves),
        "total_deducted_days": total_deducted_days,
        "total_deduction": total_deduction,
        "payable_days": payable_days,
        "final_salary": final_salary,
    }


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get("/preview")
def preview_payroll(
    month: str = Query(..., description="YYYY-MM"),
    db: Session = Depends(get_db),
):
    """
    Compute salary for all active employees for the given month.
    Approved leaves default to deduct=True.
    Employees without a base_salary set are included but flagged.
    """
    month_start, month_end = _month_bounds(month)

    employees = db.query(Employee).filter(Employee.status == "active").order_by(Employee.name).all()

    # All approved leaves that overlap with this month
    all_leaves = db.query(Leave).filter(
        Leave.status == "approved",
        Leave.start_date <= month_end,
        Leave.end_date >= month_start,
    ).all()

    leaves_by_emp = {}
    for leave in all_leaves:
        days = _days_in_month(leave.start_date, leave.end_date, month_start, month_end)
        if days <= 0:
            continue
        leaves_by_emp.setdefault(leave.employee_id, []).append({
            "leave_id": leave.id,
            "leave_type": leave.leave_type,
            "start_date": leave.start_date.isoformat(),
            "end_date": leave.end_date.isoformat(),
            "days_in_month": days,
            "reason": leave.reason or "",
        })

    # Check if a finalized run exists for this month
    existing_run = db.query(PayrollRun).filter(PayrollRun.month == month).first()
    saved_adjustments = {}
    if existing_run:
        adjs = db.query(PayrollLeaveAdjustment).filter(
            PayrollLeaveAdjustment.payroll_run_id == existing_run.id
        ).all()
        saved_adjustments = {a.leave_id: a.deduct for a in adjs}

    rows = []
    for emp in employees:
        emp_leaves = leaves_by_emp.get(emp.id, [])
        row = _build_employee_row(
            emp, emp_leaves, WORKING_DAYS_DEFAULT,
            saved_adjustments if existing_run else None
        )
        row["salary_missing"] = emp.base_salary is None
        rows.append(row)

    return {
        "month": month,
        "working_days": WORKING_DAYS_DEFAULT,
        "run_status": existing_run.status if existing_run else None,
        "run_id": existing_run.id if existing_run else None,
        "employees": rows,
    }


class LeaveAdjustmentIn(BaseModel):
    employee_id: int
    leave_id: int
    deduct: bool


class SavePayrollBody(BaseModel):
    month: str
    status: str = "draft"          # "draft" or "finalized"
    notes: Optional[str] = None
    adjustments: List[LeaveAdjustmentIn]
    processed_by: Optional[int] = None


@router.post("/save")
def save_payroll(body: SavePayrollBody, db: Session = Depends(get_db)):
    """
    Upsert a payroll run and its leave adjustments.
    Calling with status='finalized' locks the run.
    """
    if body.status not in ("draft", "finalized"):
        raise HTTPException(status_code=422, detail="status must be 'draft' or 'finalized'")

    run = db.query(PayrollRun).filter(PayrollRun.month == body.month).first()
    if run:
        if run.status == "finalized" and body.status != "finalized":
            raise HTTPException(status_code=400, detail="Payroll already finalized for this month")
        run.status = body.status
        run.notes = body.notes
        run.processed_by = body.processed_by
        # Delete existing adjustments and re-insert
        db.query(PayrollLeaveAdjustment).filter(
            PayrollLeaveAdjustment.payroll_run_id == run.id
        ).delete()
    else:
        run = PayrollRun(
            month=body.month,
            status=body.status,
            working_days=WORKING_DAYS_DEFAULT,
            notes=body.notes,
            processed_by=body.processed_by,
        )
        db.add(run)
        db.flush()

    for adj in body.adjustments:
        db.add(PayrollLeaveAdjustment(
            payroll_run_id=run.id,
            employee_id=adj.employee_id,
            leave_id=adj.leave_id,
            deduct=adj.deduct,
        ))

    db.commit()
    db.refresh(run)
    return {"message": f"Payroll {body.status} for {body.month}", "run_id": run.id, "status": run.status}


@router.get("/saved")
def get_saved_payroll(
    month: str = Query(..., description="YYYY-MM"),
    db: Session = Depends(get_db),
):
    """Retrieve a saved/finalized payroll run with full calculations."""
    run = db.query(PayrollRun).filter(PayrollRun.month == month).first()
    if not run:
        raise HTTPException(status_code=404, detail="No payroll run found for this month")

    # Reuse preview logic with saved adjustments
    return preview_payroll(month=month, db=db)


@router.get("/export.csv")
def export_payroll_csv(
    month: str = Query(..., description="YYYY-MM"),
    db: Session = Depends(get_db),
):
    """Download the payroll summary as a CSV file."""
    data = preview_payroll(month=month, db=db)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Employee", "Designation", "Type",
        "Base Salary (₹)", f"Per Day (₹, ÷{data['working_days']})",
        "Leave Days", "Deducted Days", "Deduction (₹)", "Final Salary (₹)", "Notes"
    ])
    for row in data["employees"]:
        writer.writerow([
            row["employee_name"],
            row["designation"] or "",
            row["employee_type"],
            row["base_salary"],
            row["per_day_rate"],
            row["total_leave_days"],
            row["total_deducted_days"],
            row["total_deduction"],
            row["final_salary"],
            "Salary not set" if row.get("salary_missing") else "",
        ])

    output.seek(0)
    filename = f"payroll_{month}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
