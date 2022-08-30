from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import database
from routers import auth, candidatesFile, selectionFile, feature, intConstraint, enumConstraint

app = FastAPI(title="Celect")

origins = [
    "http://localhost:5500",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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

app.include_router(auth.router,prefix="/auth", tags=["Administration"])
app.include_router(candidatesFile.router,prefix="/candidates/files", tags=["Fichier de candidatures"])
app.include_router(selectionFile.router,prefix="/candidates/selection", tags=["Candidatures sélectionnées"])
app.include_router(feature.router,prefix="/candidates", tags=["Caractéristiques des candidatures"])
app.include_router(intConstraint.router,prefix="/candidates/constraints", tags=["Contraintes sur des entiers"])
app.include_router(enumConstraint.router,prefix="/candidates/constraints", tags=["Contraintes sur des énumérations"])
