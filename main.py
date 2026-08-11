from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware
import bcrypt

from recommendation_model import recommend_food, search_food
from database import engine, Base, SessionLocal

# IMPORTANT:
# Order आणि OrderItem सुद्धा import केले आहेत
from models import User, FavoriteFood, Order, OrderItem


# =========================================================
# DATABASE
# =========================================================

Base.metadata.create_all(bind=engine)


# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI()


# =========================================================
# SESSION
# =========================================================

app.add_middleware(
    SessionMiddleware,
    secret_key="food_recommendation_secret_key"
)


# =========================================================
# TEMPLATES
# =========================================================

templates = Jinja2Templates(
    directory="templates"
)


# =========================================================
# STATIC FILES
# =========================================================

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


# =========================================================
# HOME PAGE
# =========================================================

@app.get("/")
def home(request: Request):

    username = request.session.get("username")

    # Automatically show all foods
    # sorted by rating
    initial_foods = search_food("")

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "username": username,
            "initial_foods": initial_foods
        }
    )


# =========================================================
# REGISTER PAGE
# =========================================================

@app.get("/register")
def register_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={}
    )


# =========================================================
# REGISTER USER
# =========================================================

@app.post("/register")
def register_user(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):

    db: Session = SessionLocal()

    try:

        # Check username
        existing_user = db.query(User).filter(
            User.username == username
        ).first()

        if existing_user:

            return templates.TemplateResponse(
                request=request,
                name="register.html",
                context={
                    "error": "Username already exists!"
                }
            )

        # Check email
        existing_email = db.query(User).filter(
            User.email == email
        ).first()

        if existing_email:

            return templates.TemplateResponse(
                request=request,
                name="register.html",
                context={
                    "error": "Email already registered!"
                }
            )

        # Password
        password_bytes = password.encode("utf-8")

        # bcrypt maximum 72 bytes
        password_bytes = password_bytes[:72]

        # Hash password
        hashed_password = bcrypt.hashpw(
            password_bytes,
            bcrypt.gensalt()
        )

        # Create user
        new_user = User(
            username=username,
            email=email,
            password=hashed_password.decode("utf-8")
        )

        db.add(new_user)
        db.commit()

        return RedirectResponse(
            url="/login",
            status_code=303
        )

    finally:

        db.close()


# =========================================================
# LOGIN PAGE
# =========================================================

@app.get("/login")
def login_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={}
    )


# =========================================================
# LOGIN USER
# =========================================================

@app.post("/login")
def login_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...)
):

    db: Session = SessionLocal()

    try:

        user = db.query(User).filter(
            User.username == username
        ).first()

        if user is None:

            return templates.TemplateResponse(
                request=request,
                name="login.html",
                context={
                    "error": "Invalid username or password!"
                }
            )

        password_bytes = password.encode("utf-8")
        password_bytes = password_bytes[:72]

        stored_password = user.password.encode("utf-8")

        password_correct = bcrypt.checkpw(
            password_bytes,
            stored_password
        )

        if not password_correct:

            return templates.TemplateResponse(
                request=request,
                name="login.html",
                context={
                    "error": "Invalid username or password!"
                }
            )

        # Save username in session
        request.session["username"] = user.username

        # Make sure old temporary order data
        # does not interfere
        request.session.pop("last_order_id", None)

        return RedirectResponse(
            url="/",
            status_code=303
        )

    finally:

        db.close()


# =========================================================
# LOGOUT
# =========================================================

@app.get("/logout")
def logout(request: Request):

    request.session.clear()

    return RedirectResponse(
        url="/login",
        status_code=303
    )


# =========================================================
# FOOD RECOMMENDATION
# =========================================================

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


# =========================================================
# SEARCH FOOD
# =========================================================

@app.get("/search")
def search_food_api(q: str = ""):

    results = search_food(q)

    return {
        "results": results
    }


# =========================================================
# ADD FAVORITE
# =========================================================

@app.post("/add-favorite")
def add_favorite(
    request: Request,
    food_name: str = Form(...)
):

    username = request.session.get("username")

    if not username:

        return RedirectResponse(
            url="/login",
            status_code=303
        )

    db: Session = SessionLocal()

    try:

        user = db.query(User).filter(
            User.username == username
        ).first()

        if user is None:

            return RedirectResponse(
                url="/login",
                status_code=303
            )

        existing_favorite = db.query(
            FavoriteFood
        ).filter(
            FavoriteFood.user_id == user.id,
            FavoriteFood.food_name == food_name
        ).first()

        if existing_favorite is None:

            favorite = FavoriteFood(
                user_id=user.id,
                food_name=food_name
            )

            db.add(favorite)
            db.commit()

        return RedirectResponse(
            url="/",
            status_code=303
        )

    finally:

        db.close()


# =========================================================
# FAVORITES PAGE
# =========================================================

@app.get("/favorites")
def favorites_page(request: Request):

    username = request.session.get("username")

    if not username:

        return RedirectResponse(
            url="/login",
            status_code=303
        )

    db: Session = SessionLocal()

    try:

        user = db.query(User).filter(
            User.username == username
        ).first()

        if user is None:

            return RedirectResponse(
                url="/login",
                status_code=303
            )

        favorites = db.query(
            FavoriteFood
        ).filter(
            FavoriteFood.user_id == user.id
        ).all()

        return templates.TemplateResponse(
            request=request,
            name="favorites.html",
            context={
                "username": username,
                "favorites": favorites
            }
        )

    finally:

        db.close()


# =========================================================
# REMOVE FAVORITE
# =========================================================

@app.post("/remove-favorite")
def remove_favorite(
    request: Request,
    favorite_id: int = Form(...)
):

    username = request.session.get("username")

    if not username:

        return RedirectResponse(
            url="/login",
            status_code=303
        )

    db: Session = SessionLocal()

    try:

        user = db.query(User).filter(
            User.username == username
        ).first()

        if user is None:

            return RedirectResponse(
                url="/login",
                status_code=303
            )

        favorite = db.query(
            FavoriteFood
        ).filter(
            FavoriteFood.id == favorite_id,
            FavoriteFood.user_id == user.id
        ).first()

        if favorite:

            db.delete(favorite)
            db.commit()

        return RedirectResponse(
            url="/favorites",
            status_code=303
        )

    finally:

        db.close()


# =========================================================
# ADD TO CART
# =========================================================

@app.post("/add-to-cart")
def add_to_cart(
    request: Request,
    food_name: str = Form(...),
    price: float = Form(...)
):

    username = request.session.get("username")

    # Login required
    if not username:

        return RedirectResponse(
            url="/login",
            status_code=303
        )

    # Cart stored in session
    cart = request.session.get(
        "cart",
        []
    )

    found = False

    # Check existing item
    for item in cart:

        if item["food_name"] == food_name:

            item["quantity"] += 1

            found = True

            break

    # New item
    if not found:

        cart.append({
            "food_name": food_name,
            "price": float(price),
            "quantity": 1
        })

    request.session["cart"] = cart

    return RedirectResponse(
        url="/cart",
        status_code=303
    )


# =========================================================
# CART PAGE
# =========================================================

@app.get("/cart")
def cart_page(request: Request):

    username = request.session.get("username")

    if not username:

        return RedirectResponse(
            url="/login",
            status_code=303
        )

    cart_items = request.session.get(
        "cart",
        []
    )

    total = 0

    for item in cart_items:

        total += (
            float(item["price"])
            * int(item["quantity"])
        )

    return templates.TemplateResponse(
        request=request,
        name="cart.html",
        context={
            "username": username,
            "cart_items": cart_items,
            "total": total
        }
    )


# =========================================================
# INCREASE CART
# =========================================================

@app.post("/increase-cart")
def increase_cart(
    request: Request,
    food_name: str = Form(...)
):

    if not request.session.get("username"):

        return RedirectResponse(
            url="/login",
            status_code=303
        )

    cart = request.session.get(
        "cart",
        []
    )

    for item in cart:

        if item["food_name"] == food_name:

            item["quantity"] += 1

            break

    request.session["cart"] = cart

    return RedirectResponse(
        url="/cart",
        status_code=303
    )


# =========================================================
# DECREASE CART
# =========================================================

@app.post("/decrease-cart")
def decrease_cart(
    request: Request,
    food_name: str = Form(...)
):

    if not request.session.get("username"):

        return RedirectResponse(
            url="/login",
            status_code=303
        )

    cart = request.session.get(
        "cart",
        []
    )

    for item in cart:

        if item["food_name"] == food_name:

            item["quantity"] -= 1

            if item["quantity"] <= 0:

                cart.remove(item)

            break

    request.session["cart"] = cart

    return RedirectResponse(
        url="/cart",
        status_code=303
    )


# =========================================================
# REMOVE FROM CART
# =========================================================

@app.post("/remove-cart")
def remove_cart(
    request: Request,
    food_name: str = Form(...)
):

    if not request.session.get("username"):

        return RedirectResponse(
            url="/login",
            status_code=303
        )

    cart = request.session.get(
        "cart",
        []
    )

    cart = [
        item
        for item in cart
        if item["food_name"] != food_name
    ]

    request.session["cart"] = cart

    return RedirectResponse(
        url="/cart",
        status_code=303
    )


# =========================================================
# CHECKOUT PAGE
# =========================================================

@app.get("/checkout")
def checkout_page(request: Request):

    username = request.session.get("username")

    if not username:

        return RedirectResponse(
            url="/login",
            status_code=303
        )

    cart_items = request.session.get(
        "cart",
        []
    )

    if not cart_items:

        return RedirectResponse(
            url="/cart",
            status_code=303
        )

    total = 0

    for item in cart_items:

        total += (
            float(item["price"])
            * int(item["quantity"])
        )

    return templates.TemplateResponse(
        request=request,
        name="checkout.html",
        context={
            "username": username,
            "cart_items": cart_items,
            "total": total
        }
    )


# =========================================================
# PLACE ORDER
# =========================================================

@app.post("/place-order")
def place_order(
    request: Request,
    full_name: str = Form(...),
    phone: str = Form(...),
    address: str = Form(...)
):

    username = request.session.get("username")

    if not username:

        return RedirectResponse(
            url="/login",
            status_code=303
        )

    cart_items = request.session.get(
        "cart",
        []
    )

    if not cart_items:

        return RedirectResponse(
            url="/cart",
            status_code=303
        )

    db: Session = SessionLocal()

    try:

        # Find logged-in user
        user = db.query(User).filter(
            User.username == username
        ).first()

        if user is None:

            return RedirectResponse(
                url="/login",
                status_code=303
            )

        # Calculate total
        total = 0

        for item in cart_items:

            total += (
                float(item["price"])
                * int(item["quantity"])
            )

        # Create Order
        new_order = Order(
            user_id=user.id,
            full_name=full_name,
            phone=phone,
            address=address,
            total=total,
            status="Placed"
        )

        db.add(new_order)

        # Get generated order ID
        db.flush()

        # Create Order Items
        for item in cart_items:

            new_order_item = OrderItem(
                order_id=new_order.id,
                food_name=item["food_name"],
                price=float(item["price"]),
                quantity=int(item["quantity"])
            )

            db.add(new_order_item)

        # Save order
        db.commit()

        # Save only order ID in session
        request.session["last_order_id"] = new_order.id

        # Clear cart
        request.session["cart"] = []

        return RedirectResponse(
            url="/order-success",
            status_code=303
        )

    except Exception as e:

        db.rollback()

        print(
            "================================="
        )

        print(
            "ORDER ERROR:",
            str(e)
        )

        print(
            "================================="
        )

        return RedirectResponse(
            url="/checkout",
            status_code=303
        )

    finally:

        db.close()


# =========================================================
# ORDER SUCCESS
# =========================================================

@app.get("/order-success")
def order_success(request: Request):

    username = request.session.get("username")

    if not username:

        return RedirectResponse(
            url="/login",
            status_code=303
        )

    order_id = request.session.get(
        "last_order_id"
    )

    if not order_id:

        return RedirectResponse(
            url="/",
            status_code=303
        )

    db: Session = SessionLocal()

    try:

        # Find user
        user = db.query(User).filter(
            User.username == username
        ).first()

        if user is None:

            return RedirectResponse(
                url="/login",
                status_code=303
            )

        # Find order
        order = db.query(Order).filter(
            Order.id == order_id,
            Order.user_id == user.id
        ).first()

        if order is None:

            return RedirectResponse(
                url="/",
                status_code=303
            )

        # Find order items
        order_items = db.query(
            OrderItem
        ).filter(
            OrderItem.order_id == order.id
        ).all()

        return templates.TemplateResponse(
            request=request,
            name="order_success.html",
            context={
                "username": username,
                "order": order,
                "order_items": order_items
            }
        )

    finally:

        db.close()


# =========================================================
# ORDER HISTORY
# =========================================================

@app.get("/order-history")
def order_history(request: Request):

    username = request.session.get("username")

    if not username:

        return RedirectResponse(
            url="/login",
            status_code=303
        )

    db: Session = SessionLocal()

    try:

        # Find user
        user = db.query(User).filter(
            User.username == username
        ).first()

        if user is None:

            return RedirectResponse(
                url="/login",
                status_code=303
            )

        # Get user's orders
        orders = db.query(
            Order
        ).filter(
            Order.user_id == user.id
        ).order_by(
            Order.order_date.desc()
        ).all()

        return templates.TemplateResponse(
            request=request,
            name="order_history.html",
            context={
                "username": username,
                "orders": orders
            }
        )

    finally:

        db.close()


# =========================================================
# ORDER DETAILS
# =========================================================

@app.get("/order-details/{order_id}")
def order_details(
    request: Request,
    order_id: int
):

    username = request.session.get("username")

    if not username:

        return RedirectResponse(
            url="/login",
            status_code=303
        )

    db: Session = SessionLocal()

    try:

        # Find user
        user = db.query(User).filter(
            User.username == username
        ).first()

        if user is None:

            return RedirectResponse(
                url="/login",
                status_code=303
            )

        # Find order belonging to user
        order = db.query(Order).filter(
            Order.id == order_id,
            Order.user_id == user.id
        ).first()

        if order is None:

            return RedirectResponse(
                url="/order-history",
                status_code=303
            )

        # Find order items
        order_items = db.query(
            OrderItem
        ).filter(
            OrderItem.order_id == order.id
        ).all()

        return templates.TemplateResponse(
            request=request,
            name="order_details.html",
            context={
                "username": username,
                "order": order,
                "order_items": order_items
            }
        )

    finally:

        db.close()