import numpy as np
from sklearn.linear_model import LinearRegression

def generate_ai_task():
    """
    Generate a new AI task by creating a random dataset and target values,
    and returning the task with data, target, and coefficients.
    """
    X = np.random.rand(10, 2)  # 10 samples, 2 features
    coefficients = np.random.rand(2)
    y = X @ coefficients + np.random.normal(scale=0.1, size=10)  # Add noise

    return {'data': X.tolist(), 'target': y.tolist(), 'coefficients': coefficients.tolist()}

def perform_ai_work(ai_task):
    """
    Perform AI work to solve the AI task by fitting a linear regression model.
    """
    model = LinearRegression()
    X, y = np.array(ai_task['data']), np.array(ai_task['target'])
    model.fit(X, y)

    # Return the coefficients from the linear regression model
    return {'coefficients': model.coef_.tolist()}

def verify_ai_work(ai_task, ai_solution):
    """
    Verifies if the provided AI solution is correct by comparing the coefficients.
    Returns a tuple of (bool, dict) containing success status and debug info.
    """
    # Compare directly with the original coefficients from the task
    original_coeffs = np.array(ai_task['coefficients'])
    solution_coeffs = np.array(ai_solution['coefficients'])
    
    # Use a stricter tolerance for comparison
    is_valid = np.allclose(original_coeffs, solution_coeffs, atol=1e-3, rtol=1e-3)
    
    debug_info = {
        'original': original_coeffs.tolist(),
        'solution': solution_coeffs.tolist(),
        'difference': np.abs(original_coeffs - solution_coeffs).tolist()
    }
    
    return is_valid, debug_info

