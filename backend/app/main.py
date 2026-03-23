from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routes import auth, users, products, cart, orders
from app.models import user, product, cart as cart_model, order

app = FastAPI(
    title="Market API",
    description="Backend API for the Market mobile application",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables
Base.metadata.create_all(bind=engine)

# Seed data
from app.seed import seed_all
seed_all()

# Register routes
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(orders.router)


@app.get("/")
def root():
    return {"message": "Market API is running", "docs": "/docs"}
