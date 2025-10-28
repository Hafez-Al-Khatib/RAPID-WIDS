"""Test if main.py loads correctly with improved schemas"""

print("Testing FastAPI application...")
print("="*60)

try:
    from main import app
    
    print("✓ FastAPI app loaded successfully")
    print(f"✓ App title: {app.title}")
    print(f"✓ Total routes: {len(app.routes)}")
    
    # List some key routes
    print("\nKey API endpoints:")
    for route in app.routes:
        if hasattr(route, 'path') and hasattr(route, 'methods'):
            methods = ','.join(route.methods) if route.methods else 'N/A'
            if '/api/' in route.path:
                print(f"  {methods:10} {route.path}")
    
    print("\n" + "="*60)
    print("🎉 MAIN.PY INTEGRATION SUCCESSFUL!")
    print("="*60)
    print("\nReady to start server with: uvicorn main:app --reload")
    
except Exception as e:
    print(f"\n✗ ERROR loading main.py: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
