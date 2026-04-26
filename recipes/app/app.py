from flask import Flask, render_template, jsonify, request
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "recipes-secret-key")

RECIPES = [
    {
        "id": 1,
        "title": "Spaghetti Carbonara",
        "category": "Pasta",
        "time": 25,
        "servings": 4,
        "difficulty": "Medium",
        "image_emoji": "🍝",
        "description": "Classic Roman pasta with eggs, cheese, pancetta and black pepper.",
        "ingredients": [
            "400g spaghetti",
            "200g pancetta or guanciale",
            "4 large eggs",
            "100g Pecorino Romano, grated",
            "100g Parmesan, grated",
            "2 cloves garlic",
            "Black pepper to taste",
            "Salt for pasta water"
        ],
        "steps": [
            "Bring a large pot of salted water to boil and cook spaghetti until al dente.",
            "Fry pancetta with garlic in a pan over medium heat until crispy. Remove garlic.",
            "Whisk eggs with grated Pecorino and Parmesan in a bowl. Season with black pepper.",
            "Reserve 1 cup pasta water before draining.",
            "Remove pan from heat, add drained pasta to pancetta, toss well.",
            "Pour egg mixture over pasta, toss quickly adding pasta water to create creamy sauce.",
            "Serve immediately with extra cheese and black pepper."
        ],
        "tags": ["Italian", "Quick", "Comfort Food"]
    },
    {
        "id": 2,
        "title": "Chicken Tikka Masala",
        "category": "Curry",
        "time": 45,
        "servings": 4,
        "difficulty": "Medium",
        "image_emoji": "🍛",
        "description": "Tender chicken in a rich, creamy tomato-based spiced sauce.",
        "ingredients": [
            "700g chicken breast, cubed",
            "400ml coconut cream",
            "400g crushed tomatoes",
            "2 tbsp tikka masala paste",
            "1 onion, diced",
            "3 cloves garlic, minced",
            "1 tbsp ginger, grated",
            "2 tbsp vegetable oil",
            "Fresh cilantro to serve"
        ],
        "steps": [
            "Marinate chicken in tikka paste for at least 30 minutes.",
            "Heat oil in a large pan, cook onion until softened, about 5 minutes.",
            "Add garlic and ginger, cook for 1 minute until fragrant.",
            "Add marinated chicken, cook until browned on all sides.",
            "Pour in crushed tomatoes, simmer for 10 minutes.",
            "Stir in coconut cream, simmer for another 10 minutes.",
            "Garnish with fresh cilantro and serve with naan or rice."
        ],
        "tags": ["Indian", "Spicy", "Popular"]
    },
    {
        "id": 3,
        "title": "Avocado Toast",
        "category": "Breakfast",
        "time": 10,
        "servings": 2,
        "difficulty": "Easy",
        "image_emoji": "🥑",
        "description": "Creamy avocado on crispy sourdough with a perfect poached egg.",
        "ingredients": [
            "2 slices sourdough bread",
            "2 ripe avocados",
            "2 eggs",
            "1 lemon, juiced",
            "Red pepper flakes",
            "Salt and black pepper",
            "Extra virgin olive oil",
            "Microgreens to garnish"
        ],
        "steps": [
            "Toast sourdough slices until golden and crispy.",
            "Halve and pit avocados, scoop flesh into a bowl.",
            "Mash avocado with lemon juice, salt and pepper.",
            "Bring a pot of water to gentle simmer, add a splash of vinegar.",
            "Crack eggs into small bowls, swirl water and slide eggs in.",
            "Poach for 3 minutes for a runny yolk.",
            "Spread avocado on toast, top with poached egg, chili flakes and microgreens."
        ],
        "tags": ["Breakfast", "Healthy", "Quick"]
    },
    {
        "id": 4,
        "title": "Beef Tacos",
        "category": "Mexican",
        "time": 30,
        "servings": 4,
        "difficulty": "Easy",
        "image_emoji": "🌮",
        "description": "Spiced ground beef tacos with all the classic toppings.",
        "ingredients": [
            "500g ground beef",
            "8 taco shells",
            "1 packet taco seasoning",
            "1 onion, diced",
            "2 cloves garlic",
            "Shredded cheese",
            "Sour cream",
            "Salsa",
            "Shredded lettuce",
            "Lime wedges"
        ],
        "steps": [
            "Brown ground beef in a skillet over medium-high heat, drain excess fat.",
            "Add diced onion and garlic, cook until softened.",
            "Stir in taco seasoning with 1/4 cup water, simmer 5 minutes.",
            "Warm taco shells in oven at 180°C for 3 minutes.",
            "Fill shells with beef mixture.",
            "Top with cheese, lettuce, sour cream and salsa.",
            "Serve with lime wedges."
        ],
        "tags": ["Mexican", "Family Friendly", "Quick"]
    },
    {
        "id": 5,
        "title": "Mushroom Risotto",
        "category": "Rice",
        "time": 40,
        "servings": 4,
        "difficulty": "Hard",
        "image_emoji": "🍄",
        "description": "Creamy Italian risotto with mixed wild mushrooms and Parmesan.",
        "ingredients": [
            "300g Arborio rice",
            "400g mixed mushrooms",
            "1L vegetable stock, warm",
            "1 onion, finely diced",
            "3 cloves garlic",
            "150ml white wine",
            "80g Parmesan, grated",
            "2 tbsp butter",
            "Fresh thyme",
            "Olive oil"
        ],
        "steps": [
            "Sauté mushrooms in olive oil until golden, set aside.",
            "In same pan, cook onion and garlic in butter until soft.",
            "Add rice, stir to coat in butter and toast for 2 minutes.",
            "Pour in white wine, stir until absorbed.",
            "Add warm stock one ladle at a time, stirring constantly.",
            "Continue adding stock every few minutes for 20 minutes.",
            "Stir in mushrooms, Parmesan and remaining butter. Season and serve."
        ],
        "tags": ["Italian", "Vegetarian", "Comfort Food"]
    },
    {
        "id": 6,
        "title": "Greek Salad",
        "category": "Salad",
        "time": 15,
        "servings": 4,
        "difficulty": "Easy",
        "image_emoji": "🥗",
        "description": "Fresh Mediterranean salad with feta, olives and a simple dressing.",
        "ingredients": [
            "4 tomatoes, chopped",
            "1 cucumber, sliced",
            "1 red onion, thinly sliced",
            "200g feta cheese",
            "100g kalamata olives",
            "1 green bell pepper",
            "4 tbsp olive oil",
            "2 tbsp red wine vinegar",
            "1 tsp dried oregano",
            "Salt and pepper"
        ],
        "steps": [
            "Chop tomatoes into large chunks and place in a bowl.",
            "Slice cucumber and add to bowl with red onion.",
            "Add sliced bell pepper and olives.",
            "Crumble feta cheese over the top.",
            "Drizzle with olive oil and red wine vinegar.",
            "Season with oregano, salt and pepper.",
            "Toss gently and serve immediately."
        ],
        "tags": ["Greek", "Vegetarian", "Healthy"]
    }
]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/recipes", methods=["GET"])
def get_recipes():
    category = request.args.get("category", "")
    search = request.args.get("search", "").lower()
    result = RECIPES
    if category:
        result = [r for r in result if r["category"] == category]
    if search:
        result = [
            r for r in result
            if search in r["title"].lower()
            or search in r["description"].lower()
            or any(search in t.lower() for t in r["tags"])
        ]
    return jsonify(result)


@app.route("/api/recipes/<int:recipe_id>", methods=["GET"])
def get_recipe(recipe_id):
    recipe = next((r for r in RECIPES if r["id"] == recipe_id), None)
    if not recipe:
        return jsonify({"error": "Recipe not found"}), 404
    return jsonify(recipe)


@app.route("/api/categories", methods=["GET"])
def get_categories():
    cats = sorted(set(r["category"] for r in RECIPES))
    return jsonify(cats)


@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
