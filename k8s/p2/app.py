import ast
import math
import os

from flask import Flask, jsonify, render_template, request, session

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-me")

MAX_HISTORY_ITEMS = 12
MAX_EXPRESSION_LENGTH = 180


def format_number(value):
    text = f"{float(value):.12g}"
    return text if text else "0"


def safe_factorial(value):
    if value < 0 or not float(value).is_integer():
        raise ValueError("Factorial works only with non-negative integers.")
    if value > 170:
        raise ValueError("Input too large for factorial.")
    return math.factorial(int(value))


def safe_ln(value):
    if value <= 0:
        raise ValueError("ln is defined only for positive numbers.")
    return math.log(value)


def safe_log10(value):
    if value <= 0:
        raise ValueError("log is defined only for positive numbers.")
    return math.log10(value)


def build_functions(angle_mode):
    in_degrees = angle_mode == "deg"

    def to_radians(value):
        return math.radians(value) if in_degrees else value

    def from_radians(value):
        return math.degrees(value) if in_degrees else value

    return {
        "sin": lambda x: math.sin(to_radians(x)),
        "cos": lambda x: math.cos(to_radians(x)),
        "tan": lambda x: math.tan(to_radians(x)),
        "asin": lambda x: from_radians(math.asin(x)),
        "acos": lambda x: from_radians(math.acos(x)),
        "atan": lambda x: from_radians(math.atan(x)),
        "sqrt": math.sqrt,
        "ln": safe_ln,
        "log": safe_log10,
        "abs": abs,
        "factorial": safe_factorial,
    }


class SafeExpressionEvaluator(ast.NodeVisitor):
    def __init__(self, names, functions):
        self.names = names
        self.functions = functions

    def visit_Expression(self, node):
        return self.visit(node.body)

    def visit_BinOp(self, node):
        left = self.visit(node.left)
        right = self.visit(node.right)

        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            return left / right
        if isinstance(node.op, ast.Mod):
            return left % right
        if isinstance(node.op, ast.Pow):
            return left**right

        raise ValueError("Unsupported operator.")

    def visit_UnaryOp(self, node):
        value = self.visit(node.operand)
        if isinstance(node.op, ast.UAdd):
            return +value
        if isinstance(node.op, ast.USub):
            return -value
        raise ValueError("Unsupported unary operator.")

    def visit_Call(self, node):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Invalid function call.")

        function_name = node.func.id
        if function_name not in self.functions:
            raise ValueError(f"Function '{function_name}' is not supported.")
        if node.keywords:
            raise ValueError("Keyword arguments are not supported.")

        args = [self.visit(arg) for arg in node.args]
        try:
            return self.functions[function_name](*args)
        except TypeError as exc:
            raise ValueError("Invalid number of arguments.") from exc

    def visit_Name(self, node):
        if node.id in self.names:
            return self.names[node.id]
        raise ValueError(f"Unknown name '{node.id}'.")

    def visit_Constant(self, node):
        if isinstance(node.value, (int, float)):
            return float(node.value)
        raise ValueError("Only numbers are allowed.")

    def generic_visit(self, node):
        raise ValueError("Unsupported expression.")


def normalize_expression(expression):
    return (
        expression.lower()
        .replace(" ", "")
        .replace("×", "*")
        .replace("÷", "/")
        .replace("^", "**")
        .replace("π", "pi")
    )


def evaluate_expression(expression, ans_value, angle_mode):
    normalized = normalize_expression(expression)

    if not normalized:
        raise ValueError("Enter an expression first.")
    if len(normalized) > MAX_EXPRESSION_LENGTH:
        raise ValueError("Expression is too long.")

    tree = ast.parse(normalized, mode="eval")
    evaluator = SafeExpressionEvaluator(
        names={"pi": math.pi, "e": math.e, "ans": float(ans_value)},
        functions=build_functions(angle_mode),
    )
    result = evaluator.visit(tree)

    if isinstance(result, complex) or not math.isfinite(float(result)):
        raise ValueError("Result is not a finite real number.")

    return float(result)

    if operation == "divide":
        if b == 0:
            raise ZeroDivisionError
        return a / b, "/"

    if operation == "modulus" and b == 0:
        raise ZeroDivisionError

    if operation not in operations:
        raise KeyError

    return operations[operation]


@app.get("/healthz")
def healthz():
    return {"status": "ok"}, 200


@app.get("/")
def index():
    history = session.get("history", [])
    ans = session.get("ans", 0.0)

    return render_template("index.html", history=history, ans=format_number(ans))


@app.post("/api/calculate")
def api_calculate():
    payload = request.get_json(silent=True) or {}
    expression = str(payload.get("expression", "")).strip()
    angle_mode = str(payload.get("angle_mode", "deg")).lower()

    if angle_mode not in {"deg", "rad"}:
        angle_mode = "deg"

    try:
        ans_value = float(session.get("ans", 0.0))
        result = evaluate_expression(expression, ans_value, angle_mode)
        formatted = format_number(result)

        history_item = {
            "expression": expression,
            "result": formatted,
            "mode": angle_mode.upper(),
        }
        history = session.get("history", [])
        history = [history_item, *history][:MAX_HISTORY_ITEMS]

        session["ans"] = result
        session["history"] = history

        return jsonify(
            {
                "ok": True,
                "result": formatted,
                "ans": formatted,
                "history": history,
            }
        )
    except ZeroDivisionError:
        return jsonify({"ok": False, "error": "Cannot divide by zero."}), 400
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    except SyntaxError:
        return jsonify({"ok": False, "error": "Expression syntax is invalid."}), 400


@app.post("/api/clear-history")
def api_clear_history():
    session["history"] = []
    return jsonify({"ok": True, "history": []})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
