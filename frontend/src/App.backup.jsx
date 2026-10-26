import { useEffect, useState } from 'react'
import './App.css'

function App() {
  const [showMealForm, setShowMealForm] = useState(false)

  const [foodImage, setFoodImage] = useState(null)
  const [foodPredictions, setFoodPredictions] = useState([])
  const [selectedFood, setSelectedFood] = useState(null)
  const [identifyingFood, setIdentifyingFood] = useState(false)

  const [foods, setFoods] = useState([])
  const [foodId, setFoodId] = useState('')
  const [quantity, setQuantity] = useState('')
  const [saving, setSaving] = useState(false)

  const [showGlucoseForm, setShowGlucoseForm] = useState(false)
  const [glucoseValue, setGlucoseValue] = useState('')
  const [glucoseContext, setGlucoseContext] = useState('before_meal')

  const [analysis, setAnalysis] = useState([])
  const [showInsights, setShowInsights] = useState(false)

  // Load foods from backend
  useEffect(() => {
    fetch('http://127.0.0.1:8000/foods')
      .then((response) => response.json())
      .then((data) => {
        

        // Convert PostgreSQL array rows into objects
        const foodRows = data.foods || data || []

const formattedFoods = foodRows.map((food) => {
  if (Array.isArray(food)) {
    return {
      id: food[0],
      name: food[1],
      carbohydrates: food[2],
      protein: food[3],
      fiber: food[4],
      calories: food[5],
    }
  }

  return {
    id: food.id,
    name: food.name,
    carbohydrates: food.carbohydrates,
    protein: food.protein,
    fiber: food.fiber,
    calories: food.calories,
  }
})

setFoods(formattedFoods)
        
      })
      .catch((error) => {
        console.error('Error loading foods:', error)
      })
  }, [])

  // Identify food using AI
  const identifyFood = async () => {
    if (!foodImage) {
      alert('Please select a food image first.')
      return
    }

    setIdentifyingFood(true)
    setFoodPredictions([])
    setSelectedFood(null)

    const formData = new FormData()
    formData.append('file', foodImage)

    try {
      const response = await fetch(
        'http://127.0.0.1:8000/identify-food',
        {
          method: 'POST',
          body: formData,
        }
      )

      const data = await response.json()

      if (response.ok) {
        setFoodPredictions(data.predictions || [])
      } else {
        alert('Food identification failed.')
      }
    } catch (error) {
      console.error('Food identification error:', error)
      alert('Could not connect to the food AI.')
    } finally {
      setIdentifyingFood(false)
    }

  }

  // Select food predicted by AI
  const selectFood = (prediction) => {
    const matchedFood = foods.find(
      (food) =>
        food.name?.trim().toLowerCase() ===
        prediction.food?.trim().toLowerCase()
)

    if (matchedFood) {
      setSelectedFood(matchedFood)
      setFoodId(String(matchedFood.id))
      setShowMealForm(true)
    } else {
      alert(`Nutrition data not found for ${prediction.food}`)
    }
  }

  // Record meal
  const recordMeal = async (event) => {
    event.preventDefault()

    if (saving) return

    setSaving(true)

    try {
      const response = await fetch(
        'http://127.0.0.1:8000/meals',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            user_id: 1,
            food_id: Number(foodId),
            quantity: Number(quantity),
          }),
        }
      )

      const data = await response.json()

      if (response.ok) {
        alert('Meal recorded successfully!')
        setFoodId('')
        setQuantity('')
        setSelectedFood(null)
        setShowMealForm(false)
      } else {
        alert('Something went wrong: ' + JSON.stringify(data))
      }
    } catch (error) {
      console.error('Meal recording error:', error)
      alert('Could not connect to the backend.')
    } finally {
      setSaving(false)
    }
  }

  // Record glucose
  const recordGlucose = async (event) => {
    event.preventDefault()

    try {
      const response = await fetch(
        'http://127.0.0.1:8000/glucose',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            user_id: 1,
            glucose_value: Number(glucoseValue),
            context: glucoseContext,
          }),
        }
      )

      const data = await response.json()

      if (response.ok) {
        alert('Glucose recorded successfully!')
        setGlucoseValue('')
        setGlucoseContext('before_meal')
        setShowGlucoseForm(false)
      } else {
        alert('Something went wrong: ' + JSON.stringify(data))
      }
    } catch (error) {
      console.error('Glucose recording error:', error)
      alert('Could not connect to the backend.')
    }
  }

  // Load insights
  const loadAnalysis = async () => {
    try {
      const response = await fetch(
        'http://127.0.0.1:8000/analysis/1'
      )

      const data = await response.json()

      if (response.ok) {
        setAnalysis(data.analysis_data || [])
        setShowInsights(true)
      } else {
        alert('Could not load insights')
      }
    } catch (error) {
      console.error('Analysis error:', error)
      alert('Could not connect to the backend.')
    }
  }

  return (
    <div className="app">

      {/* Header */}
      <header className="navbar">
        <h1>GlucoBuddy</h1>
        <p>Personal Food & Blood Glucose Insights</p>
      </header>

      <main className="dashboard">

        {/* Welcome */}
        <section className="welcome">
          <h2>Welcome to GlucoBuddy 👋</h2>

          <p>
            Track your meals, record your glucose, and understand your
            personal food-response patterns.
          </p>
        </section>

        <section className="cards">

          {/* ========================= */}
          {/* IDENTIFY FOOD */}
          {/* ========================= */}

          <div className="card">

            <h3>📸 Identify Food</h3>

            <p>
              Upload a photo of your food to identify it.
            </p>

            <input
              type="file"
              accept="image/*"
              onChange={(event) => {
                setFoodImage(event.target.files[0])
                setFoodPredictions([])
                setSelectedFood(null)
              }}
            />

            <button
              onClick={identifyFood}
              disabled={!foodImage || identifyingFood}
            >
              {identifyingFood
                ? 'Identifying...'
                : 'Identify Food'}
            </button>

            {/* Image preview */}
            {foodImage && (
              <div>
                <p>
                  Selected:{' '}
                  <strong>{foodImage.name}</strong>
                </p>

                <img
                  src={URL.createObjectURL(foodImage)}
                  alt="Selected food"
                  style={{
                    width: '100%',
                    maxHeight: '200px',
                    objectFit: 'cover',
                    borderRadius: '10px',
                    marginTop: '10px',
                  }}
                />
              </div>
            )}

            {/* AI predictions */}
            {foodPredictions.length > 0 && (
              <div>
                <h4>AI Food Predictions</h4>

                {foodPredictions.map((prediction, index) => (
                  <div key={index} style={{ marginBottom: '12px' }}>

                    <p>
                      <strong>{prediction.food}</strong>
                      {' — '}
                      {prediction.confidence}%
                    </p>

                    <button
                      onClick={() => selectFood(prediction)}
                    >
                      Use this food
                    </button>

                  </div>
                ))}
              </div>
            )}

            {/* Selected food nutrition */}
            {selectedFood && (
              <div>
                <h4>Selected Food</h4>

                <p>
                  <strong>{selectedFood.name}</strong>
                </p>

                <p>
                  Carbohydrates:{' '}
                  {selectedFood.carbohydrates} g
                </p>

                <p>
                  Protein:{' '}
                  {selectedFood.protein} g
                </p>

                <p>
                  Fiber:{' '}
                  {selectedFood.fiber} g
                </p>

                <p>
                  Calories:{' '}
                  {selectedFood.calories} kcal
                </p>
              </div>
            )}

          </div>


          {/* ========================= */}
          {/* RECORD MEAL */}
          {/* ========================= */}

          <div className="card">

            <h3>🍽️ Record Meal</h3>

            <p>
              Add the food you ate and its quantity.
            </p>

            <button
              onClick={() => setShowMealForm(true)}
            >
              Record Meal
            </button>

            {showMealForm && (
              <form onSubmit={recordMeal}>

                <label>Food</label>

                <select
                  value={foodId}
                  onChange={(event) =>
                    setFoodId(event.target.value)
                  }
                  required
                >

                  <option value="">
                    Select a food
                  </option>

                  {foods.map((food) => (
                    <option
                      key={food.id}
                      value={food.id}
                    >
                      {food.name}
                    </option>
                  ))}

                </select>


                <label>Quantity</label>

                <input
                  type="number"
                  step="0.1"
                  min="0.1"
                  value={quantity}
                  onChange={(event) =>
                    setQuantity(event.target.value)
                  }
                  placeholder="Example: 2"
                  required
                />

                <button
                  type="submit"
                  disabled={saving}
                >
                  {saving
                    ? 'Saving...'
                    : 'Save Meal'}
                </button>

              </form>
            )}

          </div>


          {/* ========================= */}
          {/* RECORD GLUCOSE */}
          {/* ========================= */}

          <div className="card">

            <h3>🩸 Record Glucose</h3>

            <p>
              Enter a blood glucose reading.
            </p>

            <button
              onClick={() => setShowGlucoseForm(true)}
            >
              Record Glucose
            </button>

            {showGlucoseForm && (
              <form onSubmit={recordGlucose}>

                <label>Glucose Value</label>

                <input
                  type="number"
                  step="0.1"
                  value={glucoseValue}
                  onChange={(event) =>
                    setGlucoseValue(event.target.value)
                  }
                  placeholder="Example: 120"
                  required
                />

                <label>Context</label>

                <select
                  value={glucoseContext}
                  onChange={(event) =>
                    setGlucoseContext(event.target.value)
                  }
                  required
                >

                  <option value="before_meal">
                    Before Meal
                  </option>

                  <option value="after_meal">
                    After Meal
                  </option>

                </select>

                <button type="submit">
                  Save Glucose
                </button>

              </form>
            )}

          </div>


          {/* ========================= */}
          {/* VIEW INSIGHTS */}
          {/* ========================= */}

          <div className="card">

            <h3>📊 View Insights</h3>

            <p>
              Explore your meal and glucose patterns.
            </p>

            <button onClick={loadAnalysis}>
              View Insights
            </button>

            {showInsights && (
              <div>

                <h4>Recent Meal Analysis</h4>

                {analysis.length === 0 ? (
                  <p>
                    No analysis data available yet.
                  </p>
                ) : (
                  analysis
                    .slice(0, 5)
                    .map((item) => (
                      <div key={item.meal_id}>

                        <p>
                          <strong>
                            {item.food}
                          </strong>{' '}
                          × {item.quantity}
                        </p>

                        <p>
                          Carbohydrates:{' '}
                          {item.carbohydrates} g
                        </p>

                        <p>
                          Before glucose:{' '}
                          {item.before_glucose ??
                            'Not available'}
                        </p>

                        <p>
                          After glucose:{' '}
                          {item.after_glucose ??
                            'Not available'}
                        </p>

                        <p>
                          Glucose change:{' '}
                          {item.glucose_change !== null
                            ? item.glucose_change
                            : 'Not available'}
                        </p>

                        <hr />

                      </div>
                    ))
                )}

              </div>
            )}

          </div>

        </section>

      </main>

    </div>
  )
}

export default App