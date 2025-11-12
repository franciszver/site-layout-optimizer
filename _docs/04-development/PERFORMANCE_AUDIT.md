# Performance & Cost Optimization Audit

## Critical Issues Found

### 🔴 HIGH PRIORITY - Cost Risks

#### 1. **Expensive AI API Calls Without Caching**
- **Location**: `backend/src/handlers/optimize.py` line 90-105
- **Issue**: GPT-4o via OpenRouter called on EVERY optimization request
- **Cost Impact**: ~$0.01-0.03 per request (GPT-4o pricing)
- **Risk**: If user clicks "Optimize" multiple times = $$$
- **Fix**: Add caching layer, request deduplication, rate limiting

#### 2. **Regulatory API Calls Without Caching**
- **Location**: `backend/src/handlers/optimize.py` line 60-67
- **Issue**: FEMA, EPA, USGS APIs called on every optimization
- **Cost Impact**: Free APIs but slow (10-15s per request)
- **Risk**: Timeouts, poor UX, unnecessary load
- **Fix**: Cache regulatory data by bounds (same location = cached result)

#### 3. **Large Data Serialization**
- **Location**: `backend/src/services/terrain_analyzer.py` line 217
- **Issue**: DEM arrays (potentially 1000x1000+) converted to lists for JSON
- **Cost Impact**: Large response payloads, slow network, memory issues
- **Risk**: Timeouts, high bandwidth costs, poor performance
- **Fix**: Store large arrays in S3, return references only

#### 4. **No Request Deduplication**
- **Location**: All handlers
- **Issue**: Same request processed multiple times if user clicks rapidly
- **Cost Impact**: Duplicate AI calls, duplicate processing
- **Fix**: Add request deduplication with request hashing

### 🟡 MEDIUM PRIORITY - Performance Issues

#### 5. **Frontend Re-render Loops**
- **Location**: `frontend/src/components/MapViewer.tsx`
- **Issue**: Object references in dependencies can cause loops
- **Fix**: Deep comparison or stable references

#### 6. **Missing Rate Limiting**
- **Location**: All API endpoints
- **Issue**: No protection against abuse or accidental loops
- **Fix**: Add rate limiting middleware

#### 7. **Terrain Analysis Not Cached**
- **Location**: `backend/src/handlers/analyze.py`
- **Issue**: Same terrain analyzed multiple times
- **Fix**: Cache by file_id + resolution

### 🟢 LOW PRIORITY - Optimization Opportunities

#### 8. **Inefficient Grid Generation**
- **Location**: `backend/src/services/asset_placer.py` line 64-76
- **Issue**: Nested loops for large properties
- **Fix**: Use spatial indexing (R-tree)

#### 9. **No Connection Pooling**
- **Location**: HTTP clients
- **Issue**: New connections for each request
- **Fix**: Reuse HTTP clients

## Implemented Fixes

### ✅ 1. Caching Layer (`backend/src/utils/cache.py`)
- In-memory cache with TTL support
- AI responses cached for 1 hour
- Regulatory data cached for 24 hours
- Terrain analysis cached for 24 hours
- Thread-safe implementation

### ✅ 2. AI Optimizer Caching (`backend/src/services/ai_optimizer.py`)
- Checks cache before calling OpenRouter API
- Caches results by prompt hash
- Prevents duplicate expensive AI calls
- **Cost Savings**: ~$0.01-0.03 per duplicate request avoided

### ✅ 3. Regulatory Data Caching (`backend/src/services/regulatory_fetcher.py`)
- Caches FEMA/EPA/USGS API responses by bounds
- Same location = cached result (no API call)
- **Time Savings**: 10-15s per duplicate request avoided

### ✅ 4. Request Deduplication (`backend/src/handlers/optimize.py`)
- Prevents duplicate processing of identical requests
- Returns cached result if same request made within 5 minutes
- Returns 202 if request already processing
- **Cost Savings**: Prevents accidental duplicate AI calls

### ✅ 5. Rate Limiting (`backend/src/middleware/rate_limit.py`)
- `/optimize`: 10 requests/minute
- `/analyze`: 20 requests/minute
- `/generate-roads`: 20 requests/minute
- `/upload`: 5 requests/minute
- Returns 429 if limit exceeded
- **Cost Protection**: Prevents runaway costs from loops/abuse

### ✅ 6. Optimized Data Serialization (`backend/src/services/terrain_analyzer.py`)
- Large arrays (>100x100) not serialized to JSON
- Returns stats only, full data stored in S3
- **Performance**: Reduces response size by 90%+ for large properties

### ✅ 7. Frontend Dependency Fixes (`frontend/src/components/MapViewer.tsx`)
- Uses JSON.stringify for stable dependency comparison
- Prevents infinite re-render loops
- **Performance**: Eliminates constant map refreshes

## Cost Estimates (Before vs After)

### Before Fixes:
- **AI Calls**: $0.01-0.03 per optimization (no caching)
- **Regulatory Calls**: 10-15s per optimization (no caching)
- **Data Transfer**: Large payloads (DEM arrays in JSON)
- **Risk**: User clicks 10x = $0.10-0.30 just in AI costs

### After Fixes:
- **AI Calls**: $0.01-0.03 per UNIQUE optimization (cached)
- **Regulatory Calls**: 10-15s per UNIQUE location (cached)
- **Data Transfer**: References only (arrays in S3)
- **Risk**: Cached results = $0.00 for duplicates

## Monitoring Recommendations

1. Track AI API call counts and costs
2. Monitor cache hit rates
3. Alert on unusual request patterns
4. Set budget alerts for OpenRouter API

