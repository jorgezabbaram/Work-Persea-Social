#!/usr/bin/env python3
"""
Script de verificación completa del sistema de procesamiento de órdenes
Prueba todos los casos de uso y la comunicación entre servicios
"""
import requests
import json
import time
from uuid import uuid4

BASE_URLS = {
    'order': 'http://localhost:8001',
    'inventory': 'http://localhost:8002',
    'payment': 'http://localhost:8003',
    'notification': 'http://localhost:8004'
}

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def print_success(text):
    print(f"✅ {text}")

def print_error(text):
    print(f"❌ {text}")

def print_info(text):
    print(f"ℹ️  {text}")

def test_health_checks():
    print_header("TEST 1: HEALTH CHECKS")
    
    all_healthy = True
    for service, url in BASE_URLS.items():
        try:
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print_success(f"{service.capitalize()}: {data}")
            else:
                print_error(f"{service.capitalize()}: {response.status_code}")
                all_healthy = False
        except Exception as e:
            print_error(f"{service.capitalize()}: {str(e)}")
            all_healthy = False
    
    return all_healthy

def test_create_order():
    print_header("TEST 2: CREATE ORDER")
    
    customer_id = str(uuid4())
    product_id = "e9e9e9e9-e9e9-e9e9-e9e9-e9e9e9e9e9e9"
    
    order_data = {
        "customer_id": customer_id,
        "items": [
            {
                "product_id": product_id,
                "quantity": 1,
                "price": 50.0
            }
        ]
    }
    
    try:
        response = requests.post(f"{BASE_URLS['order']}/orders", json=order_data, timeout=10)
        if response.status_code == 201:
            order = response.json()
            print_success("Order created!")
            return order, customer_id
        else:
            print_error(f"Error: {response.text}")
            return None, customer_id
    except Exception as e:
        print_error(f"Exception: {str(e)}")
        return None, customer_id

def test_get_order(order_id):
    print_header("TEST 3: GET ORDER")
    try:
        response = requests.get(f"{BASE_URLS['order']}/orders/{order_id}", timeout=5)
        if response.status_code == 200:
            print_success("Order retrieved!")
            return response.json()
        return None
    except Exception:
        return None

def test_event_processing(order_id):
    print_header("TEST 4: EVENT PROCESSING")
    time.sleep(3)
    try:
        response = requests.get(f"{BASE_URLS['order']}/orders/{order_id}", timeout=5)
        if response.status_code == 200:
            order = response.json()
            print_info(f"Status: {order.get('status')}")
            return True
        return False
    except Exception:
        return False

def test_notifications():
    print_header("TEST 5: NOTIFICATIONS")
    try:
        response = requests.get(f"{BASE_URLS['notification']}/notifications", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"Notifications found: {len(data.get('notifications', []))}")
            return True
        return False
    except Exception:
        return False

def main():
    print_header("SYSTEM VERIFICATION")
    
    if not test_health_checks(): return
    
    order, customer_id = test_create_order()
    if order:
        order_id = order['id']
        test_get_order(order_id)
        test_event_processing(order_id)
        test_notifications()

    print("\nVerification complete.")

