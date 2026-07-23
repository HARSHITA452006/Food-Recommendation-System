from fastapi import FastAPI
from recommendation_model import recommend_food
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.staticfiles import StaticFiles

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


@app.get("/recommend")
def get_recommendations(
    cuisine: str,
    diet: str,
    spice_level: str,
    meal_type: str
):
    recommendations = recommend_food(
        cuisine,
        diet,
        spice_level,
        meal_type
    )

    return {
        "recommendations": recommendations
    }