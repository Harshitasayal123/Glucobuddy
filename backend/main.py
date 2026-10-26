import psycopg2
import joblib
from dotenv import load_dotenv
import os
import open_clip
import torch
import pandas as pd
from fastapi import FastAPI, UploadFile, File, HTTPException , Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pwdlib import PasswordHash

load_dotenv()
password_hash = PasswordHash.recommended()
print("Loading food recognition model...")

food_model, _, food_preprocess = open_clip.create_model_and_transforms(
    "ViT-B-32",
    pretrained="laion2b_s34b_b79k"
)

food_tokenizer = open_clip.get_tokenizer("ViT-B-32")

food_labels = [
    "rice",
    "roti",
    "naan",
    "dal",
    "rajma",
    "chole",
    "paratha",
    "biryani",
    "chicken curry",
    "vegetable curry"
]

print("Food recognition model loaded!")
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
model = joblib.load("../ml/glucobuddy_glucose_model.pkl")


@app.get("/")
def home():
    return {"message": "Welcome to GlucoBuddy!"}


connection = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    port=os.getenv("DB_PORT")
)

print("Database connected successfully!")

@app.get("/users")
def get_users():
    cursor = connection.cursor()
    cursor.execute("SELECT id, name, email FROM users;")
    users = cursor.fetchall()
    cursor.close()

    return {"users": users}



class UserCreate(BaseModel):
    name: str
    email: str
    password: str



@app.post("/users")
def create_user(user: UserCreate):
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO users (name, email, password_hash)
            VALUES (%s, %s, %s)
            RETURNING id, name, email;
            """,
            (
                user.name,
                user.email,
                password_hash.hash(user.password)
            )
        )

        new_user = cursor.fetchone()
        connection.commit()

        return {
            "message": "User created successfully",
            "user": new_user
        }

    except psycopg2.errors.UniqueViolation:
        connection.rollback()
        raise HTTPException(
            status_code=409,
            detail="This email address is already registered."
        )

    except Exception:
        connection.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to create user due to a server error."
        )

    finally:
        cursor.close()




@app.get("/foods")
def get_foods():
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT id, name, carbohydrates, protein, fiber, calories
            FROM foods;
            """
        )

        foods = cursor.fetchall()
        return {"foods": foods}

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve food list."
        )

    finally:
        cursor.close()





class MealCreate(BaseModel):
    user_id: int = Field(gt=0)
    food_id: int = Field(gt=0)
    quantity: float = Field(gt=0, le=100)



@app.post("/meals")
def create_meal(meal: MealCreate):
    cursor = connection.cursor()

    try:
        # Check whether the user exists
        cursor.execute(
            "SELECT id FROM users WHERE id = %s;",
            (meal.user_id,)
        )
        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail="User not found."
            )

        # Check whether the food exists
        cursor.execute(
            "SELECT id FROM foods WHERE id = %s;",
            (meal.food_id,)
        )
        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail="Food not found."
            )

        # Record the meal
        cursor.execute(
            """
            INSERT INTO meals (user_id, food_id, quantity)
            VALUES (%s, %s, %s)
            RETURNING id, user_id, food_id, quantity, meal_time;
            """,
            (meal.user_id, meal.food_id, meal.quantity)
        )

        new_meal = cursor.fetchone()
        connection.commit()

        return {
            "message": "Meal recorded successfully",
            "meal": new_meal
        }

    except HTTPException:
        connection.rollback()
        raise

    except Exception:
        connection.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to record meal due to a server error."
        )

    finally:
        cursor.close()


@app.get("/meals")
def get_meals(user_id: int = Query(gt=0)):
    cursor = connection.cursor()

    try:
        cursor.execute(
    """
            SELECT
            m.id,
            m.user_id,
            m.food_id,
            f.name,
            m.quantity,
            m.meal_time
        FROM meals m
        JOIN foods f ON m.food_id = f.id
        WHERE m.user_id = %s
        ORDER BY m.meal_time DESC;
    """,
            (user_id,)
)


        meals = cursor.fetchall()
        return {"meals": meals}

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve meal history."
        )

    finally:
        cursor.close()


class GlucoseCreate(BaseModel):
    user_id: int = Field(gt=0)
    glucose_value: float = Field(gt=0, le=1000)
    context: str = Field(pattern="^(before_meal|after_meal)$")



@app.post("/glucose")
def create_glucose(glucose: GlucoseCreate):
    cursor = connection.cursor()

    try:
        # Check whether the user exists
        cursor.execute(
            "SELECT id FROM users WHERE id = %s;",
            (glucose.user_id,)
        )

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail="User not found."
            )

        # Record the glucose reading
        cursor.execute(
            """
            INSERT INTO glucose_readings
            (user_id, glucose_value, context)
            VALUES (%s, %s, %s)
            RETURNING id, user_id, glucose_value, reading_time, context;
            """,
            (glucose.user_id, glucose.glucose_value, glucose.context)
        )

        new_reading = cursor.fetchone()
        connection.commit()

        return {
            "message": "Glucose reading recorded successfully",
            "reading": new_reading
        }

    except HTTPException:
        connection.rollback()
        raise

    except Exception:
        connection.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to record glucose reading due to a server error."
        )

    finally:
        cursor.close()




@app.get("/glucose")
def get_glucose():
    cursor = connection.cursor()

    try:
        cursor.execute(
    """
    SELECT id, user_id, glucose_value, reading_time, context
    FROM glucose_readings
    WHERE user_id = %s
    ORDER BY reading_time DESC;
    """,
    (1,)
)

        readings = cursor.fetchall()
        return {"readings": readings}

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve glucose readings."
        )

    finally:
        cursor.close()


class GlucosePredictionInput(BaseModel):
    bg: float
    insulin: float
    heart_rate: float
    calories: float


@app.post("/predict-glucose")
def predict_glucose(data: GlucosePredictionInput):

    input_data = pd.DataFrame([{
        "bg-0:00": data.bg,
        "insulin-0:00": data.insulin,
        "hr-0:00": data.heart_rate,
        "cals-0:00": data.calories
    }])

    prediction = model.predict(input_data)

    return {
        "predicted_glucose": float(prediction[0])
    }

@app.post("/identify-food")
async def identify_food(file: UploadFile = File(...)):
    image_bytes = await file.read()

    from PIL import Image
    from io import BytesIO

    image = Image.open(BytesIO(image_bytes)).convert("RGB")

    image_input = food_preprocess(image).unsqueeze(0)
    text_input = food_tokenizer(food_labels)

    with torch.no_grad():
        image_features = food_model.encode_image(image_input)
        text_features = food_model.encode_text(text_input)

        image_features /= image_features.norm(dim=-1, keepdim=True)
        text_features /= text_features.norm(dim=-1, keepdim=True)

        similarity = (
            100.0 * image_features @ text_features.T
        ).softmax(dim=-1)

    results = similarity[0]

    predictions = []

    for index in results.argsort(descending=True)[:5]:
        predictions.append({
            "food": food_labels[index],
            "confidence": round(
                results[index].item() * 100,
                2
            )
        })

    return {
        "predictions": predictions
    }


@app.get("/analysis/{user_id}")
def analyze_user(user_id: int):
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            m.id,
            f.name,
            m.quantity,
            m.meal_time,
            f.carbohydrates,
            f.protein,
            f.fiber,
            f.calories,

            (
                SELECT g.glucose_value
                FROM glucose_readings g
                WHERE g.user_id = m.user_id
                  AND g.context = 'before_meal'
                  AND g.reading_time <= m.meal_time
                ORDER BY g.reading_time DESC
                LIMIT 1
            ) AS before_glucose,

            (
                SELECT g.glucose_value
                FROM glucose_readings g
                WHERE g.user_id = m.user_id
                  AND g.context = 'after_meal'
                  AND g.reading_time > m.meal_time
                  AND g.reading_time <= m.meal_time + INTERVAL '2 hours'
                  AND NOT EXISTS (
                      SELECT 1
                      FROM meals m2
                      WHERE m2.user_id = m.user_id
                        AND m2.meal_time > m.meal_time
                        AND m2.meal_time < g.reading_time
                  )
                ORDER BY g.reading_time ASC
                LIMIT 1
            ) AS after_glucose

        FROM meals m
        JOIN foods f ON m.food_id = f.id
        WHERE m.user_id = %s
        ORDER BY m.meal_time DESC;
        """,
        (user_id,)
    )

    data = cursor.fetchall()
    cursor.close()

    analysis_results = []

    for row in data:
        meal_id = row[0]
        food_name = row[1]
        quantity = row[2]
        meal_time = row[3]

        carbohydrates = row[4]
        protein = row[5]
        fiber = row[6]
        calories = row[7]

        before_glucose = row[8]
        after_glucose = row[9]

        total_carbohydrates = float(carbohydrates) * float(quantity)
        total_protein = float(protein) * float(quantity)
        total_fiber = float(fiber) * float(quantity)
        total_calories = float(calories) * float(quantity)

        if before_glucose is not None and after_glucose is not None:
            glucose_change = float(after_glucose) - float(before_glucose)
        else:
            glucose_change = None

        analysis_results.append({
            "meal_id": meal_id,
            "food": food_name,
            "quantity": float(quantity),
            "meal_time": meal_time,
            "carbohydrates": total_carbohydrates,
            "protein": total_protein,
            "fiber": total_fiber,
            "calories": total_calories,
            "before_glucose": before_glucose,
            "after_glucose": after_glucose,
            "glucose_change": glucose_change
        })

    insights = []

    for item in analysis_results:
        if item["glucose_change"] is not None:
            if item["glucose_change"] > 30:
                insights.append(
                    f"Your recorded glucose increased by "
                    f"{item['glucose_change']:.0f} after "
                    f"{item['food']} × {item['quantity']}."
                )
            else:
                insights.append(
                    f"Your recorded glucose changed by "
                    f"{item['glucose_change']:.0f} after "
                    f"{item['food']} × {item['quantity']}."
                )

    return {
        "analysis_data": analysis_results,
        "insights": insights
    }