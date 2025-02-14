def service_create_user(user_create: UserCreate) -> User:
    try:
        hashed_password = pwd_context.hash(
            user_create.password_hash)  # Hash password

        db_user = User(
            username=user_create.username,
            email=user_create.email,
            password_hash=hashed_password,
            is_active=user_create.is_active,
            is_disabled=user_create.is_disabled
        )

        with get_session() as session:
            session.add(db_user)
            session.commit()
            session.refresh(db_user)
            return db_user
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409,
                            detail="Username or email already exists")