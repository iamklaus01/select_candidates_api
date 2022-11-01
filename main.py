from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import database
from routers import admin, auth, candidatesFile, selectionFile, feature, intConstraint, enumConstraint

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

app.include_router(auth.router,prefix="/auth", tags=["Authentification"])
app.include_router(candidatesFile.router,prefix="/candidates/files", tags=["Fichier de candidatures"])
app.include_router(selectionFile.router,prefix="/candidates/selection", tags=["Candidatures sélectionnées"])
app.include_router(feature.router,prefix="/candidates", tags=["Caractéristiques des candidatures"])
app.include_router(intConstraint.router,prefix="/candidates/constraints", tags=["Contraintes sur des entiers"])
app.include_router(enumConstraint.router,prefix="/candidates/constraints", tags=["Contraintes sur des énumérations"])
app.include_router(admin.router, prefix="/admin", tags=["Administration"])
