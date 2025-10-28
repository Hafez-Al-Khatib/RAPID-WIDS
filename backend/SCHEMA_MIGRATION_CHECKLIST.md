# ✅ Schema Migration Checklist

## Decision: Adopt Improved Schemas?

### Quick Comparison

| Feature | Current (schemas.py) | Improved (schemas_improved.py) |
|---------|---------------------|-------------------------------|
| Type Safety | ❌ Strings only | ✅ Enums + validation |
| IDE Support | ⚠️ Limited | ✅ Full autocomplete |
| Validation | ⚠️ Basic | ✅ Comprehensive |
| Documentation | ⚠️ Minimal | ✅ Examples + descriptions |
| Geometry Support | ❌ Excluded | ✅ WKT + GeoJSON |
| BoundingBox | ❌ Generic dict | ✅ Typed model |
| Units | ❌ Unclear | ✅ Documented |
| Provenance | ❌ Missing | ✅ reporter_id, updated_at |

**Recommendation: ✅ Migrate** (Major quality improvement)

---

## 🚀 Migration Path

### Option A: Full Migration (Recommended for Hackathon)

**Steps:**

1. **Backup current schemas**
   ```powershell
   cd backend
   copy schemas.py schemas_old_backup.py
   ```

2. **Replace with improved**
   ```powershell
   copy schemas_improved.py schemas.py
   ```

3. **Update imports in main.py** (if needed)
   ```python
   # Add enum imports
   from schemas import (
       # Existing
       DamageReportCreate,
       DamageReportResponse,
       # ... others ...
       
       # New enums
       SourceType,
       RoadStatusType,
       SupplyPointType,
       DamageClass
   )
   ```

4. **Update database.py** (optional - add updated_at, reporter_id columns)

5. **Test API**
   ```powershell
   python main.py
   # Visit http://localhost:8000/docs
   ```

6. **Update frontend** (use enum values)

**Time: ~15 minutes**

---

### Option B: Gradual Migration

Keep both files, migrate endpoints one by one.

**Steps:**

1. **Keep both files**
   - `schemas.py` (old)
   - `schemas_improved.py` (new)

2. **Update one endpoint at a time**
   ```python
   # main.py
   from schemas import DamageReportCreate as OldCreate  # Old
   from schemas_improved import DamageReportCreate as NewCreate  # New
   
   @app.post("/api/upload")  # Use new schema
   async def upload(...) -> DamageReportResponse:
       ...
   ```

3. **Once all migrated, delete old file**

**Time: ~1 hour**

---

### Option C: Cherry-Pick Improvements

Copy specific improvements to existing schemas.py.

**Priority improvements to copy:**

1. **Enums** (highest impact)
2. **BoundingBox model**
3. **Validation (ge, le, max_length)**
4. **Documentation (descriptions, examples)**

**Time: ~30 minutes**

---

## 🧪 Testing Checklist

After migration, test these:

### 1. API Endpoints Still Work

```powershell
# Test upload
curl -X POST http://localhost:8000/api/upload \
  -F "file=@test.jpg" \
  -F "latitude=0.01" \
  -F "longitude=0.02"

# Test stats
curl http://localhost:8000/api/stats

# Test supply optimization
curl -X POST http://localhost:8000/api/optimize-route \
  -H "Content-Type: application/json" \
  -d '{"warehouse_id": 1, "delivery_points": [3, 5], "num_vehicles": 2}'
```

### 2. Validation Works

```python
# Test invalid latitude (should fail)
from schemas import DamageReportCreate

try:
    report = DamageReportCreate(
        latitude=999,  # Invalid!
        longitude=0.0
    )
except ValidationError:
    print("✓ Validation working")

# Test invalid enum (should fail)
try:
    report = DamageReportCreate(
        latitude=0.0,
        longitude=0.0,
        source="invalid_source"  # Invalid!
    )
except ValidationError:
    print("✓ Enum validation working")
```

### 3. OpenAPI Docs Updated

1. Visit http://localhost:8000/docs
2. Check POST endpoints show enum dropdowns
3. Verify examples appear
4. Test "Try it out" functionality

### 4. Frontend Compatible

If you have frontend code:

```javascript
// Update to use enum values
const source = "user_upload";  // Still works
// Or
const source = SourceType.USER_UPLOAD;  // If using TypeScript

// New fields available
const {
  damage_class,  // NEW!
  reporter_id,   // NEW!
  updated_at,    // NEW!
  location       // NEW! (WKT geometry)
} = damageReport;
```

---

## 🔄 Rollback Plan

If something breaks:

```powershell
# Restore old schemas
copy schemas_old_backup.py schemas.py

# Restart server
python main.py
```

No database changes needed (backward compatible).

---

## 📝 Code Changes Needed

### main.py Updates

#### 1. Add Enum Imports

```python
from schemas import (
    # ... existing imports ...
    SourceType,
    RoadStatusType,
    SupplyPointType,
    DamageClass
)
```

#### 2. Use Enums in Default Values (optional)

```python
# Before
@app.post("/api/upload")
async def upload(
    source: str = "user_upload"
):
    ...

# After (more type-safe)
@app.post("/api/upload")
async def upload(
    source: SourceType = SourceType.USER_UPLOAD
):
    ...
```

#### 3. Update Response Models

```python
# If returning DamageReportResponse, add new fields:
return DamageReportResponse(
    # ... existing fields ...
    location=str(report.location),  # Convert WKTElement to string
    damage_class=DamageClass.MAJOR_DAMAGE,  # Or derive from severity
    reporter_id=reporter_id  # From request
)
```

### database.py Updates (Optional)

Add new columns if you want full provenance:

```python
class DamageReport(Base):
    # ... existing columns ...
    
    # NEW columns (optional)
    reporter_id = Column(String(100), nullable=True)
    updated_at = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
```

Then recreate database:

```powershell
python database.py
python seed_data.py
```

---

## ⚡ Quick Start (Fastest Path)

For hackathon demo, minimal changes:

```powershell
# 1. Backup
copy schemas.py schemas_old_backup.py

# 2. Replace
copy schemas_improved.py schemas.py

# 3. Test
python main.py
# Visit http://localhost:8000/docs

# 4. If it works - you're done!
# 5. If errors - restore backup and fix issues
```

**Most endpoints should work without changes!**

---

## 🎯 Benefits You Get Immediately

After migration:

1. **Better API Docs** - `/docs` shows enums, examples, descriptions
2. **Type Safety** - Typos caught at validation time
3. **IDE Support** - Autocomplete for enum values
4. **Validation** - Coordinates, ranges, lengths auto-checked
5. **Professional** - Production-grade schema structure

**Time invested:** 15 minutes  
**Quality improvement:** Massive ⭐⭐⭐⭐⭐

---

## 🆘 Common Issues & Fixes

### Issue 1: "ValidationError: source invalid"

**Cause:** Using string where enum expected

**Fix:**
```python
# Before
source="user_upload"

# After
source=SourceType.USER_UPLOAD
```

### Issue 2: "ImportError: cannot import SourceType"

**Cause:** Forgot to update imports

**Fix:**
```python
from schemas import SourceType, RoadStatusType, SupplyPointType
```

### Issue 3: "AttributeError: 'DamageReport' object has no attribute 'reporter_id'"

**Cause:** Database doesn't have new columns

**Fix (Option 1):** Don't use new fields yet  
**Fix (Option 2):** Add columns to database.py and recreate DB

### Issue 4: Frontend breaks

**Cause:** Frontend expects old field names

**Fix:** New schemas are backward compatible. Old fields still present.

---

## ✅ Final Checklist

Before considering migration complete:

- [ ] Backup created
- [ ] New schemas in place
- [ ] Imports updated in main.py
- [ ] Server starts without errors
- [ ] `/docs` loads correctly
- [ ] Test upload works
- [ ] Test optimization works
- [ ] Test stats endpoint works
- [ ] Enums show as dropdowns in /docs
- [ ] Validation catches invalid data
- [ ] Frontend still works (if applicable)

---

## 🎉 Success Criteria

You'll know it worked when:

1. ✅ Visit `/docs` - see enum dropdowns instead of text fields
2. ✅ Examples show up in "Try it out"
3. ✅ Invalid data gets rejected with clear error messages
4. ✅ IDE autocompletes `SourceType.` with options
5. ✅ No runtime errors from schemas

---

## 💡 Recommendation

**For hackathon (this week):**
- ✅ Do **Option A** (Full Migration)
- ⏱️ Takes 15 minutes
- 🎯 Massive quality boost for demo
- 📚 Better API docs to show judges

**For production (post-hackathon):**
- Add `reporter_id` and `updated_at` to database
- Add audit logging
- Fine-tune validation rules

**Start with full migration - you can always rollback!**
