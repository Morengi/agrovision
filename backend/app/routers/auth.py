from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.dependencies import get_current_user
from app.core.email import send_email
from app.core.rate_limit import limiter
from app.core.security import create_access_token, verify_password
from app.crud import token as token_crud
from app.crud import user as user_crud
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    AccessTokenResponse,
    AuthResponse,
    ForgotPasswordRequest,
    LoginRequest,
    RegisterRequest,
    ResetPasswordRequest,
)
from app.schemas.user import UserRead

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()

REFRESH_COOKIE_NAME = "refresh_token"


def _set_refresh_cookie(response: Response, raw_token: str) -> None:
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=raw_token,
        httponly=True,
        samesite="lax",
        secure=not settings.debug,
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
        path="/",
    )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(key=REFRESH_COOKIE_NAME, path="/")


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register(
    request: Request, payload: RegisterRequest, response: Response, db: AsyncSession = Depends(get_db)
):
    if not payload.personal_data_consent:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Для регистрации необходимо согласие на обработку персональных данных",
        )

    existing = await user_crud.get_by_email(db, payload.email)
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Пользователь с таким email уже существует"
        )

    user = await user_crud.create_user(
        db,
        email=payload.email,
        password=payload.password,
        full_name=payload.full_name,
        personal_data_consent=payload.personal_data_consent,
    )

    access_token = create_access_token(subject=str(user.id), role=user.role.value)
    refresh_token = await token_crud.issue_refresh_token(db, user.id)
    _set_refresh_cookie(response, refresh_token)

    return AuthResponse(access_token=access_token, user=UserRead.model_validate(user))


@router.post("/login", response_model=AuthResponse)
@limiter.limit("10/minute")
async def login(request: Request, payload: LoginRequest, response: Response, db: AsyncSession = Depends(get_db)):
    user = await user_crud.get_by_email(db, payload.email)
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный email или пароль")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Аккаунт деактивирован")

    access_token = create_access_token(subject=str(user.id), role=user.role.value)
    refresh_token = await token_crud.issue_refresh_token(db, user.id)
    _set_refresh_cookie(response, refresh_token)

    return AuthResponse(access_token=access_token, user=UserRead.model_validate(user))


@router.post("/refresh", response_model=AccessTokenResponse)
async def refresh(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    unauthorized = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Сессия истекла")

    raw_token = request.cookies.get(REFRESH_COOKIE_NAME)
    if raw_token is None:
        raise unauthorized

    token = await token_crud.get_valid_refresh_token(db, raw_token)
    if token is None:
        _clear_refresh_cookie(response)
        raise unauthorized

    user = await user_crud.get_by_id(db, token.user_id)
    if user is None or not user.is_active:
        raise unauthorized

    # Rotate: revoke the presented refresh token and issue a fresh one.
    await token_crud.revoke_refresh_token(db, token)
    new_refresh_token = await token_crud.issue_refresh_token(db, user.id)
    _set_refresh_cookie(response, new_refresh_token)

    access_token = create_access_token(subject=str(user.id), role=user.role.value)
    return AccessTokenResponse(access_token=access_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    raw_token = request.cookies.get(REFRESH_COOKIE_NAME)
    if raw_token is not None:
        token = await token_crud.get_valid_refresh_token(db, raw_token)
        if token is not None:
            await token_crud.revoke_refresh_token(db, token)
    _clear_refresh_cookie(response)


@router.get("/me", response_model=UserRead)
async def me(current_user: User = Depends(get_current_user)):
    return UserRead.model_validate(current_user)


@router.post("/forgot-password", status_code=status.HTTP_202_ACCEPTED)
@limiter.limit("3/minute")
async def forgot_password(request: Request, payload: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    user = await user_crud.get_by_email(db, payload.email)
    # Always respond 202 regardless of whether the email exists, to avoid user enumeration.
    if user is not None:
        raw_token = await token_crud.issue_password_reset_token(db, user.id)
        reset_link = f"{settings.frontend_url}/reset-password?token={raw_token}"
        await send_email(
            to=user.email,
            subject="Восстановление пароля — АгроВзгляд",
            body=(
                f"Здравствуйте, {user.full_name}!\n\n"
                f"Для восстановления пароля перейдите по ссылке:\n{reset_link}\n\n"
                "Если вы не запрашивали восстановление пароля, просто проигнорируйте это письмо."
            ),
        )


@router.post("/reset-password", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("10/minute")
async def reset_password(request: Request, payload: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    token = await token_crud.get_valid_reset_token(db, payload.token)
    if token is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ссылка недействительна или устарела")

    user = await user_crud.get_by_id(db, token.user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ссылка недействительна или устарела")

    await user_crud.set_password(db, user, payload.new_password)
    await token_crud.consume_reset_token(db, token)
