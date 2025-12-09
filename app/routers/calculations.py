from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Calculation, User
from app.schemas import CalculationCreate, CalculationRead, CalculationUpdate
from app.utils import CalculationFactory
from app.utils.auth import get_current_user

router = APIRouter(
    prefix="/calculations",
    tags=["Calculations"]
)

@router.get("/", response_model=List[CalculationRead])
def read_calculations(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Browse: Retrieve all calculations belonging to the logged-in user.
    """
    calculations = db.query(Calculation).filter(
        Calculation.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    return calculations

@router.get("/{calculation_id}", response_model=CalculationRead)
def read_calculation(
    calculation_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Read: Retrieve a specific calculation by ID belonging to the logged-in user.
    """
    calculation = db.query(Calculation).filter(
        Calculation.id == calculation_id,
        Calculation.user_id == current_user.id
    ).first()
    if calculation is None:
        raise HTTPException(status_code=404, detail="Calculation not found")
    return calculation

@router.post("/", response_model=CalculationRead, status_code=status.HTTP_201_CREATED)
def create_calculation(
    calculation: CalculationCreate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add: Create a new calculation for the logged-in user.
    """
    # Calculate result
    try:
        result = CalculationFactory.calculate(calculation.type, calculation.a, calculation.b)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    db_calculation = Calculation(
        a=calculation.a,
        b=calculation.b,
        type=calculation.type,
        result=result,
        user_id=current_user.id
    )
    db.add(db_calculation)
    db.commit()
    db.refresh(db_calculation)
    return db_calculation

@router.put("/{calculation_id}", response_model=CalculationRead)
def update_calculation(
    calculation_id: int, 
    calculation: CalculationUpdate, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Edit: Update a calculation belonging to the logged-in user.
    """
    db_calculation = db.query(Calculation).filter(
        Calculation.id == calculation_id,
        Calculation.user_id == current_user.id
    ).first()
    if db_calculation is None:
        raise HTTPException(status_code=404, detail="Calculation not found")
    
    # Update fields
    update_data = calculation.model_dump(exclude_unset=True)
    
    # If a, b, or type changed, recalculate result
    a = update_data.get("a", db_calculation.a)
    b = update_data.get("b", db_calculation.b)
    calc_type = update_data.get("type", db_calculation.type)
    
    try:
        result = CalculationFactory.calculate(calc_type, a, b)
        db_calculation.result = result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    for key, value in update_data.items():
        setattr(db_calculation, key, value)
    
    db.commit()
    db.refresh(db_calculation)
    return db_calculation

@router.patch("/{calculation_id}", response_model=CalculationRead)
def partial_update_calculation(
    calculation_id: int,
    calculation: CalculationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Edit (Partial): Partially update a calculation belonging to the logged-in user.
    """
    db_calculation = db.query(Calculation).filter(
        Calculation.id == calculation_id,
        Calculation.user_id == current_user.id
    ).first()
    if db_calculation is None:
        raise HTTPException(status_code=404, detail="Calculation not found")
    
    # Update fields
    update_data = calculation.model_dump(exclude_unset=True)
    
    # If a, b, or type changed, recalculate result
    a = update_data.get("a", db_calculation.a)
    b = update_data.get("b", db_calculation.b)
    calc_type = update_data.get("type", db_calculation.type)
    
    try:
        result = CalculationFactory.calculate(calc_type, a, b)
        db_calculation.result = result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        
    for key, value in update_data.items():
        setattr(db_calculation, key, value)
    
    db.commit()
    db.refresh(db_calculation)
    return db_calculation

@router.delete("/{calculation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_calculation(
    calculation_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete: Remove a calculation belonging to the logged-in user.
    """
    db_calculation = db.query(Calculation).filter(
        Calculation.id == calculation_id,
        Calculation.user_id == current_user.id
    ).first()
    if db_calculation is None:
        raise HTTPException(status_code=404, detail="Calculation not found")
    
    db.delete(db_calculation)
    db.commit()
    return None
