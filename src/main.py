from fastapi.routing import APIRoute
from fastapi import FastAPI, APIRouter
from database.database import create_all, add_default_roles
# from src.app1 import apps as app1
# from src.app2 import apps as app2
# from src.user import router as user_app
from src.auth import router as auth_app


def custom_generate_unique_id(route: APIRoute):
    return f"{route.tags[0]}_{route.name}"


# Add each router in each app to app.include_routers.
app = FastAPI(generate_unique_id_function=custom_generate_unique_id)
# app.include_router(app1.router)
# app.include_router(app2.router)
# app.include_router(user_app.router)
app.include_router(auth_app.router)


@app.on_event("startup")
async def startup():
    await create_all()
    await add_default_roles()

@app.on_event("shutdown")
async def shutdown():
    pass

