from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate,UserResponse,UserLogin
from app.core.security import hash_password,verify_password,create_access_token
from app.core.dependencies import get_current_user,require_role
router=APIRouter(
    prefix="/auth",
    tags=['Authentication']
)
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register_user(
    user_data:UserCreate,
    db:Session=Depends(get_db)
):
    existing_user=db.query(User).filter(
        User.email==user_data.email
    ).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
        detail="Email is already registered"
        )
    hashed_password=hash_password(user_data.password)

    #create the new user
    new_user=User(
        full_name=user_data.full_name,
        email=user_data.email,
        password_hash=hashed_password,
        role="candidate",
        is_active=True
    )
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Unable to register user.Email may already exists"
        )
    return new_user
@router.post("/login")
def login_user(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):

    # Find user by email
    user = db.query(User).filter(
        User.email == login_data.email
    ).first()

    # Check whether user exists
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Verify password
    password_valid = verify_password(
        login_data.password,
        user.password_hash
    )

    if not password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Check account status
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account is inactive"
        )

    # Generate Access Token
    access_token = create_access_token(
        user_id=user.user_id,
        role=user.role
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
@router.get(
    "/me",
    response_model=UserResponse
)
def get_my_Profile(
    current_user:User=Depends(get_current_user)
):
    return current_user

@router.get("/hr-test")
def hr_test(
    current_user:User=Depends(require_role("hr"))
):
    return{
        "message":"Hr authorization successful",
        "user_id":current_user.user_id,
        "role":current_user.role
    }

@router.get("/candidate-test")
def candidate_test(
    current_user: User = Depends(require_role("candidate"))
):

    return {
        "message": "Candidate authorization successful",
        "user_id": current_user.user_id,
        "role": current_user.role
    }




