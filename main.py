from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import database
from routers import user, admin, auth, candidatesFile, selectionFile, feature, intConstraint, enumConstraint

app = FastAPI(title="Celect")

origins = [
    "http://localhost:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

app.include_router(user.router,prefix="/user", tags=["Get In Touch"])
app.include_router(auth.router,prefix="/auth", tags=["Authentication"])
app.include_router(candidatesFile.router,prefix="/candidates/files", tags=["Files of candidacy"])
app.include_router(selectionFile.router,prefix="/candidates/selection", tags=["Selected candidacy"])
app.include_router(feature.router,prefix="/candidates", tags=["Features of candidates"])
app.include_router(intConstraint.router,prefix="/candidates/constraints", tags=["Constraints on integer"])
app.include_router(enumConstraint.router,prefix="/candidates/constraints", tags=["Constraints on enumerations"])
app.include_router(admin.router, prefix="/admin", tags=["Administration"])
