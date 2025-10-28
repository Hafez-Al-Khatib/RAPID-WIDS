# 🧪 RAPID Unit Testing Guide

## Quick Test Each Component

### Test All Components at Once
```powershell
cd backend
python test_all.py
```

### Test Individual Components

**Damage Detector:**
```powershell
python tests/test_damage_detector.py
```

**Supply Optimizer:**
```powershell
python tests/test_supply_optimizer.py
```

**Graph Navigator:**
```powershell
python tests/test_graph_navigator.py
```

## Using pytest (Optional)

Install pytest:
```powershell
pip install pytest
```

Run all tests:
```powershell
pytest tests/ -v
```

Run specific test file:
```powershell
pytest tests/test_damage_detector.py -v
```

## Expected Output

Each test will show:
- ✓ PASSED - Test succeeded
- ✗ FAILED - Test failed with error details

## Test Coverage

- **Damage Detector**: 12 tests
- **Supply Optimizer**: 10 tests  
- **Graph Navigator**: 3 tests

Total: 25+ unit tests
