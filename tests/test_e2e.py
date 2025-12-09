import pytest
from playwright.sync_api import Page, expect
import time
import subprocess
import sys
import os

# We need to run the server for E2E tests
# In a real CI environment, the server would be started separately
# For local testing, we can assume it's running or start it
# Here we'll assume the user or CI starts it, but we can add a check

BASE_URL = "http://localhost:8000"

@pytest.fixture(scope="session", autouse=True)
def ensure_server_running():
    """
    Ensure the server is running before tests.
    In CI, this is handled by the workflow.
    Locally, you should run `uvicorn app.main:app --reload`
    """
    # Simple check if server is reachable
    import requests
    try:
        requests.get(f"{BASE_URL}/health")
    except requests.exceptions.ConnectionError:
        pytest.fail(f"Server is not running at {BASE_URL}. Please start it before running E2E tests.")

def test_register_success(page: Page):
    """Test successful user registration."""
    page.goto(f"{BASE_URL}/static/register.html")
    
    # Generate unique user
    timestamp = int(time.time())
    username = f"user_{timestamp}"
    email = f"user_{timestamp}@example.com"
    password = "securepassword123"
    
    page.fill("#username", username)
    page.fill("#email", email)
    page.fill("#password", password)
    page.fill("#confirmPassword", password)
    
    page.click("button[type='submit']")
    
    # Check for success message
    success_message = page.locator(".alert-success")
    expect(success_message).to_be_visible()
    expect(success_message).to_contain_text("Registration successful")

def test_register_password_mismatch(page: Page):
    """Test registration with password mismatch."""
    page.goto(f"{BASE_URL}/static/register.html")
    
    page.fill("#username", "testuser")
    page.fill("#email", "test@example.com")
    page.fill("#password", "password123")
    page.fill("#confirmPassword", "password456")
    
    page.click("button[type='submit']")
    
    error_message = page.locator(".alert-danger")
    expect(error_message).to_be_visible()
    expect(error_message).to_contain_text("Passwords do not match")

def test_register_short_password(page: Page):
    """Test registration with short password."""
    page.goto(f"{BASE_URL}/static/register.html")
    
    page.fill("#username", "testuser")
    page.fill("#email", "test@example.com")
    page.fill("#password", "short")
    page.fill("#confirmPassword", "short")
    
    page.click("button[type='submit']")
    
    error_message = page.locator(".alert-danger")
    expect(error_message).to_be_visible()
    expect(error_message).to_contain_text("Password must be at least 8 characters")

def test_login_success(page: Page):
    """Test successful login."""
    # First register a user
    timestamp = int(time.time())
    username = f"login_user_{timestamp}"
    email = f"login_{timestamp}@example.com"
    password = "securepassword123"
    
    # Register via API to speed up
    import requests
    requests.post(f"{BASE_URL}/users/register", json={
        "username": username,
        "email": email,
        "password": password
    })
    
    page.goto(f"{BASE_URL}/static/login.html")
    
    page.fill("#username", username)
    page.fill("#password", password)
    
    page.click("button[type='submit']")
    
    success_message = page.locator(".alert-success")
    expect(success_message).to_be_visible()
    expect(success_message).to_contain_text("Login successful")

def test_login_failure(page: Page):
    """Test login with invalid credentials."""
    page.goto(f"{BASE_URL}/static/login.html")
    
    page.fill("#username", "nonexistentuser")
    page.fill("#password", "wrongpassword")
    
    page.click("button[type='submit']")
    
    error_message = page.locator(".alert-danger")
    expect(error_message).to_be_visible()
    expect(error_message).to_contain_text("Invalid credentials")


# BREAD Operations Tests for Calculations

def test_add_calculation_success(page: Page):
    """Test adding a new calculation (CREATE operation)."""
    # First register and login a user
    timestamp = int(time.time())
    username = f"calc_user_{timestamp}"
    email = f"calc_{timestamp}@example.com"
    password = "securepassword123"
    
    import requests
    requests.post(f"{BASE_URL}/users/register", json={
        "username": username,
        "email": email,
        "password": password
    })
    
    # Login and get token
    login_response = requests.post(f"{BASE_URL}/users/login", json={
        "username": username,
        "password": password
    })
    token = login_response.json()["access_token"]
    
    # Navigate to calculations page
    # Use login page first to set localStorage safely without redirect race condition
    page.goto(f"{BASE_URL}/static/login.html")
    
    # Set token in localStorage
    page.evaluate(f"localStorage.setItem('token', '{token}')")
    page.evaluate(f"localStorage.setItem('username', '{username}')")
    
    # Now navigate to calculations page
    page.goto(f"{BASE_URL}/static/calculations.html")
    
    # Fill in calculation form
    page.fill("#operandA", "10")
    page.fill("#operandB", "5")
    page.select_option("#operationType", "Add")
    
    page.click("button[type='submit']")
    
    # Check for success message
    success_message = page.locator(".alert-success")
    expect(success_message).to_be_visible()
    expect(success_message).to_contain_text("Calculation created successfully")
    expect(success_message).to_contain_text("Result: 15")

def test_browse_calculations(page: Page):
    """Test browsing all calculations (READ ALL operation)."""
    # Create user and login
    timestamp = int(time.time())
    username = f"browse_user_{timestamp}"
    email = f"browse_{timestamp}@example.com"
    password = "securepassword123"
    
    import requests
    requests.post(f"{BASE_URL}/users/register", json={
        "username": username,
        "email": email,
        "password": password
    })
    
    login_response = requests.post(f"{BASE_URL}/users/login", json={
        "username": username,
        "password": password
    })
    token = login_response.json()["access_token"]
    
    # Create some calculations via API
    headers = {"Authorization": f"Bearer {token}"}
    requests.post(f"{BASE_URL}/calculations/", json={"a": 10, "b": 5, "type": "Add"}, headers=headers)
    requests.post(f"{BASE_URL}/calculations/", json={"a": 20, "b": 4, "type": "Divide"}, headers=headers)
    
    # Navigate to calculations page
    # Use login page first to set localStorage safely without redirect race condition
    page.goto(f"{BASE_URL}/static/login.html")
    
    # Set token in localStorage
    page.evaluate(f"localStorage.setItem('token', '{token}')")
    page.evaluate(f"localStorage.setItem('username', '{username}')")
    
    # Now navigate to calculations page
    page.goto(f"{BASE_URL}/static/calculations.html")
    
    # Wait for table to load
    page.wait_for_timeout(1000)
    
    # Check that calculations are displayed
    table_rows = page.locator("#calculationsTableBody tr")
    expect(table_rows).to_have_count(2, timeout=5000)

def test_read_specific_calculation(page: Page):
    """Test reading a specific calculation (READ ONE operation)."""
    # Create user and login
    timestamp = int(time.time())
    username = f"read_user_{timestamp}"
    email = f"read_{timestamp}@example.com"
    password = "securepassword123"
    
    import requests
    requests.post(f"{BASE_URL}/users/register", json={
        "username": username,
        "email": email,
        "password": password
    })
    
    login_response = requests.post(f"{BASE_URL}/users/login", json={
        "username": username,
        "password": password
    })
    token = login_response.json()["access_token"]
    
    # Create a calculation
    headers = {"Authorization": f"Bearer {token}"}
    calc_response = requests.post(f"{BASE_URL}/calculations/", json={"a": 15, "b": 3, "type": "Multiply"}, headers=headers)
    calc_id = calc_response.json()["id"]
    
    # Navigate to calculations page
    # Use login page first to set localStorage safely without redirect race condition
    page.goto(f"{BASE_URL}/static/login.html")
    
    # Set token in localStorage
    page.evaluate(f"localStorage.setItem('token', '{token}')")
    page.evaluate(f"localStorage.setItem('username', '{username}')")
    
    # Now navigate to calculations page
    page.goto(f"{BASE_URL}/static/calculations.html")
    
    # Wait for table to load
    page.wait_for_timeout(1000)
    
    # Verify calculation details in table
    table_body = page.locator("#calculationsTableBody")
    expect(table_body).to_contain_text("15")
    expect(table_body).to_contain_text("3")
    expect(table_body).to_contain_text("45")

def test_edit_calculation_success(page: Page):
    """Test editing a calculation (UPDATE operation)."""
    # Create user and login
    timestamp = int(time.time())
    username = f"edit_user_{timestamp}"
    email = f"edit_{timestamp}@example.com"
    password = "securepassword123"
    
    import requests
    requests.post(f"{BASE_URL}/users/register", json={
        "username": username,
        "email": email,
        "password": password
    })
    
    login_response = requests.post(f"{BASE_URL}/users/login", json={
        "username": username,
        "password": password
    })
    token = login_response.json()["access_token"]
    
    # Create a calculation
    headers = {"Authorization": f"Bearer {token}"}
    requests.post(f"{BASE_URL}/calculations/", json={"a": 10, "b": 2, "type": "Add"}, headers=headers)
    
    # Navigate to calculations page
    # Use login page first to set localStorage safely without redirect race condition
    page.goto(f"{BASE_URL}/static/login.html")
    
    # Set token in localStorage
    page.evaluate(f"localStorage.setItem('token', '{token}')")
    page.evaluate(f"localStorage.setItem('username', '{username}')")
    
    # Now navigate to calculations page
    page.goto(f"{BASE_URL}/static/calculations.html")
    
    # Wait for table to load
    page.wait_for_timeout(1000)
    
    # Click edit button
    page.click("button.btn-outline-primary")
    
    # Wait for modal
    page.wait_for_selector("#editModal.show", timeout=5000)
    
    # Update calculation values
    page.fill("#editOperandA", "20")
    page.fill("#editOperandB", "5")
    page.select_option("#editOperationType", "Multiply")
    
    # Submit edit form
    page.click("#editCalculationForm button[type='submit']")
    
    # Check for success message
    success_message = page.locator(".alert-success")
    expect(success_message).to_be_visible(timeout=5000)
    expect(success_message).to_contain_text("updated successfully")
    expect(success_message).to_contain_text("100")

def test_delete_calculation_success(page: Page):
    """Test deleting a calculation (DELETE operation)."""
    # Create user and login
    timestamp = int(time.time())
    username = f"delete_user_{timestamp}"
    email = f"delete_{timestamp}@example.com"
    password = "securepassword123"
    
    import requests
    requests.post(f"{BASE_URL}/users/register", json={
        "username": username,
        "email": email,
        "password": password
    })
    
    login_response = requests.post(f"{BASE_URL}/users/login", json={
        "username": username,
        "password": password
    })
    token = login_response.json()["access_token"]
    
    # Create a calculation
    headers = {"Authorization": f"Bearer {token}"}
    requests.post(f"{BASE_URL}/calculations/", json={"a": 30, "b": 6, "type": "Divide"}, headers=headers)
    
    # Navigate to calculations page
    # Use login page first to set localStorage safely without redirect race condition
    page.goto(f"{BASE_URL}/static/login.html")
    
    # Set token in localStorage
    page.evaluate(f"localStorage.setItem('token', '{token}')")
    page.evaluate(f"localStorage.setItem('username', '{username}')")
    
    # Now navigate to calculations page
    page.goto(f"{BASE_URL}/static/calculations.html")
    
    # Wait for table to load
    page.wait_for_timeout(1000)
    
    # Setup dialog handler for confirmation
    page.on("dialog", lambda dialog: dialog.accept())
    
    # Click delete button
    page.click("button.btn-outline-danger")
    
    # Check for success message
    success_message = page.locator(".alert-success")
    expect(success_message).to_be_visible(timeout=5000)
    expect(success_message).to_contain_text("deleted successfully")
    
    # Verify calculation is removed from table
    page.wait_for_timeout(1000)
    table_body = page.locator("#calculationsTableBody")
    expect(table_body).to_contain_text("No calculations yet")

def test_add_calculation_division_by_zero(page: Page):
    """Test negative scenario: division by zero validation."""
    # Create user and login
    timestamp = int(time.time())
    username = f"divzero_user_{timestamp}"
    email = f"divzero_{timestamp}@example.com"
    password = "securepassword123"
    
    import requests
    requests.post(f"{BASE_URL}/users/register", json={
        "username": username,
        "email": email,
        "password": password
    })
    
    login_response = requests.post(f"{BASE_URL}/users/login", json={
        "username": username,
        "password": password
    })
    token = login_response.json()["access_token"]
    
    # Navigate to calculations page
    # Use login page first to set localStorage safely without redirect race condition
    page.goto(f"{BASE_URL}/static/login.html")
    
    # Set token in localStorage
    page.evaluate(f"localStorage.setItem('token', '{token}')")
    page.evaluate(f"localStorage.setItem('username', '{username}')")
    
    # Now navigate to calculations page
    page.goto(f"{BASE_URL}/static/calculations.html")
    
    # Try to create division by zero
    page.fill("#operandA", "10")
    page.fill("#operandB", "0")
    page.select_option("#operationType", "Divide")
    
    page.click("button[type='submit']")
    
    # Check for error message
    error_message = page.locator(".alert-danger")
    expect(error_message).to_be_visible()
    expect(error_message).to_contain_text("Division by zero")

def test_unauthorized_access_calculations(page: Page):
    """Test negative scenario: accessing calculations without authentication."""
    # Navigate to calculations page without token
    page.goto(f"{BASE_URL}/static/calculations.html")
    
    # Should redirect to login page
    page.wait_for_timeout(1000)
    expect(page).to_have_url(f"{BASE_URL}/static/login.html")

def test_edit_calculation_invalid_data(page: Page):
    """Test negative scenario: editing with invalid data."""
    # Create user and login
    timestamp = int(time.time())
    username = f"invalid_user_{timestamp}"
    email = f"invalid_{timestamp}@example.com"
    password = "securepassword123"
    
    import requests
    requests.post(f"{BASE_URL}/users/register", json={
        "username": username,
        "email": email,
        "password": password
    })
    
    login_response = requests.post(f"{BASE_URL}/users/login", json={
        "username": username,
        "password": password
    })
    token = login_response.json()["access_token"]
    
    # Create a calculation
    headers = {"Authorization": f"Bearer {token}"}
    requests.post(f"{BASE_URL}/calculations/", json={"a": 10, "b": 2, "type": "Add"}, headers=headers)
    
    # Navigate to calculations page
    # Use login page first to set localStorage safely without redirect race condition
    page.goto(f"{BASE_URL}/static/login.html")
    
    # Set token in localStorage
    page.evaluate(f"localStorage.setItem('token', '{token}')")
    page.evaluate(f"localStorage.setItem('username', '{username}')")
    
    # Now navigate to calculations page
    page.goto(f"{BASE_URL}/static/calculations.html")
    
    # Wait for table to load
    page.wait_for_timeout(1000)
    
    # Click edit button
    page.click("button.btn-outline-primary")
    
    # Wait for modal
    page.wait_for_selector("#editModal.show", timeout=5000)
    
    # Try to set division by zero
    page.fill("#editOperandA", "10")
    page.fill("#editOperandB", "0")
    page.select_option("#editOperationType", "Divide")
    
    # Submit edit form
    page.click("#editCalculationForm button[type='submit']")
    
    # Check for error message
    error_message = page.locator(".alert-danger")
    expect(error_message).to_be_visible(timeout=5000)
    expect(error_message).to_contain_text("Division by zero")
