# Data Redundancy Removal System

A comprehensive system that identifies and prevents redundant data from being added to cloud databases. This system uses advanced similarity detection algorithms to classify data as redundant or false positive, ensuring database accuracy and efficiency.

## Features

- **Redundancy Detection**: Identifies exact duplicates and similar content using multiple similarity algorithms
- **False Positive Classification**: Intelligent heuristics to distinguish between actual duplicates and false positives
- **Validation Mechanism**: Pre-validation of new data against existing entries before insertion
- **Database Efficiency**: Prevents duplicate data from being added, maintaining clean and efficient databases
- **Comprehensive API**: RESTful API for all operations including validation, insertion, search, and management
- **Statistical Insights**: Detailed statistics on database health and redundancy metrics
- **Flexible Configuration**: Adjustable similarity thresholds and detection parameters

## Architecture

The system consists of several key components:

1. **Redundancy Detector**: Core logic for identifying similar and duplicate content
2. **Database Layer**: SQLAlchemy-based ORM with efficient indexing
3. **API Layer**: FastAPI-based REST API with comprehensive endpoints
4. **Validation Engine**: Pre-insertion validation with detailed feedback
5. **Logging System**: Comprehensive audit trail of all redundancy checks

## Installation

### Prerequisites

- Python 3.8+
- pip (Python package manager)

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Chandanchandu55/codealpha_tasks.git
   cd codealpha_tasks
   cd "Data Redundancy Removal System Task"
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run the application**:
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:8000`

## 🚀 Quick Start: Validate, Run, and Test

### Step 1: Start the Server

```bash
# Navigate to the project directory
cd "Data Redundancy Removal System Task"

# Start the server
python main.py
```

**Server Status:** Running on `http://localhost:8000`

### Step 2: Access Interactive Documentation

Open your browser and go to:
```
http://localhost:8000/docs
```

This provides a beautiful Swagger UI to test all endpoints interactively.

### Step 3: Validate Data Before Adding

**Method 1: Using curl (Command Line)**
```bash
# Validate a new entry
curl -X POST "http://localhost:8000/validate" \
  -H "Content-Type: application/json" \
  -d '{"content": "This is unique content", "data_type": "test", "source": "manual"}'
```

**Expected Response:**
```json
{
  "is_valid": true,
  "can_add": true,
  "message": "No redundancy detected. Safe to add this entry.",
  "redundancy_check": {
    "is_duplicate": false,
    "is_false_positive": false,
    "similarity_score": 0.0,
    "matched_entries": [],
    "recommendation": "No redundancy detected. Safe to add this entry."
  }
}
```

**Method 2: Using Python**
```python
import requests

# Validate content
response = requests.post('http://localhost:8000/validate', json={
    'content': 'Your unique content here',
    'data_type': 'document',
    'source': 'user_input'
})

result = response.json()
print(f"Can add: {result['can_add']}")
print(f"Message: {result['message']}")
```

### Step 4: Add Validated Data

**Method 1: Using curl**
```bash
# Add the validated entry
curl -X POST "http://localhost:8000/add" \
  -H "Content-Type: application/json" \
  -d '{"content": "This is unique content", "data_type": "test", "source": "manual"}'
```

**Method 2: Using Python**
```python
import requests

# Add entry
response = requests.post('http://localhost:8000/add', json={
    'content': 'Your unique content here',
    'data_type': 'document',
    'source': 'user_input'
})

if response.status_code == 200:
    entry = response.json()
    print(f"Successfully added entry ID: {entry['id']}")
else:
    print(f"Error: {response.json()}")
```

### Step 5: Test Redundancy Detection

**Test Exact Duplicate Detection:**
```bash
# Try to add the same content again
curl -X POST "http://localhost:8000/add" \
  -H "Content-Type: application/json" \
  -d '{"content": "This is unique content", "data_type": "test", "source": "manual"}'
```

**Expected Response (400 Bad Request):**
```json
{
  "detail": "Exact duplicate found. Reject this entry."
}
```

**Test Similar Content Detection:**
```bash
# Try to add similar content (with small variation)
curl -X POST "http://localhost:8000/add" \
  -H "Content-Type: application/json" \
  -d '{"content": "This is unique content!", "data_type": "test", "source": "manual"}'
```

**Expected Response (400 Bad Request):**
```json
{
  "detail": "Similar content found. High probability of redundancy. Reject this entry."
}
```

### Step 6: Force Add Override (When Needed)

```bash
# Force add a duplicate entry
curl -X POST "http://localhost:8000/add?force_add=true" \
  -H "Content-Type: application/json" \
  -d '{"content": "This is unique content", "data_type": "test", "source": "manual"}'
```

**Expected Response (200 OK):**
```json
{
  "content": "This is unique content",
  "data_type": "test",
  "source": "manual",
  "id": 2,
  "content_hash": "...",
  "similarity_score": 1.0,
  "is_duplicate": true,
  "is_false_positive": false,
  "created_at": "...",
  "updated_at": "..."
}
```

### Step 7: Search and Manage Data

**Search Entries:**
```bash
# Search for specific content
curl "http://localhost:8000/search?query=unique"
```

**Get Statistics:**
```bash
# View database statistics
curl "http://localhost:8000/statistics"
```

**Expected Statistics Response:**
```json
{
  "total_entries": 2,
  "unique_entries": 1,
  "duplicates_found": 1,
  "false_positives": 0,
  "data_type_distribution": {
    "test": 2
  }
}
```

### Step 8: Run Comprehensive Tests

**Method 1: Automated Test Suite**
```bash
# Run the comprehensive API test
python test_api.py
```

**Expected Output:**
```
🧪 Testing Data Redundancy Removal System API
============================================================
✅ PASSED: Root Endpoint
✅ PASSED: Validate Unique Entry
✅ PASSED: Add Unique Entry
✅ PASSED: Add Exact Duplicate (should fail)
✅ PASSED: Add Similar Entry (should fail)
✅ PASSED: Get All Entries
✅ PASSED: Search Entries
✅ PASSED: Get Statistics
✅ PASSED: Force Add Duplicate
🏁 TEST SUMMARY
Passed: 9/9
Success Rate: 100%
🎉 ALL TESTS PASSED! The system is working correctly.
```

**Method 2: Example Usage Script**
```bash
# Run the example usage demonstration
python example_usage.py
```

## 🔧 Advanced Testing Scenarios

### Scenario 1: Complete Workflow Test

```python
import requests
import json

def complete_workflow_test():
    base_url = "http://localhost:8000"
    
    # Step 1: Validate new content
    print("1️⃣ Validating new content...")
    response = requests.post(f"{base_url}/validate", json={
        'content': 'Complete workflow test entry',
        'data_type': 'workflow_test',
        'source': 'automated_test'
    })
    print(f"Validation: {response.json()['message']}")
    
    # Step 2: Add the content
    print("\n2️⃣ Adding content...")
    response = requests.post(f"{base_url}/add", json={
        'content': 'Complete workflow test entry',
        'data_type': 'workflow_test',
        'source': 'automated_test'
    })
    entry_id = response.json()['id']
    print(f"Added entry ID: {entry_id}")
    
    # Step 3: Try to add duplicate (should fail)
    print("\n3️⃣ Testing duplicate detection...")
    response = requests.post(f"{base_url}/add", json={
        'content': 'Complete workflow test entry',
        'data_type': 'workflow_test',
        'source': 'automated_test'
    })
    print(f"Duplicate detection: {response.json()['detail']}")
    
    # Step 4: Search for the entry
    print("\n4️⃣ Searching for entry...")
    response = requests.get(f"{base_url}/search?query=workflow")
    print(f"Found {len(response.json())} matching entries")
    
    # Step 5: Get final statistics
    print("\n5️⃣ Getting statistics...")
    response = requests.get(f"{base_url}/statistics")
    stats = response.json()
    print(f"Total entries: {stats['total_entries']}")
    print(f"Unique entries: {stats['unique_entries']}")
    print(f"Duplicates found: {stats['duplicates_found']}")
    
    print("\n✅ Complete workflow test finished!")

# Run the test
complete_workflow_test()
```

### Scenario 2: Performance Testing

```python
import requests
import time
import random

def performance_test():
    base_url = "http://localhost:8000"
    
    # Test validation performance
    print("🚀 Performance Testing...")
    
    start_time = time.time()
    
    # Validate 100 entries
    for i in range(100):
        content = f"Performance test entry {i}"
        response = requests.post(f"{base_url}/validate", json={
            'content': content,
            'data_type': 'performance_test',
            'source': 'automated'
        })
        
        if response.json()['can_add']:
            # Add the entry
            requests.post(f"{base_url}/add", json={
                'content': content,
                'data_type': 'performance_test',
                'source': 'automated'
            })
    
    end_time = time.time()
    
    # Get final statistics
    response = requests.get(f"{base_url}/statistics")
    stats = response.json()
    
    print(f"⏱️  Processed 100 entries in {end_time - start_time:.2f} seconds")
    print(f"📊 Final stats: {stats['total_entries']} total, {stats['duplicates_found']} duplicates")

# Run performance test
performance_test()
```

## 🐛 Troubleshooting

### Common Issues and Solutions

**Issue: Server won't start**
```bash
# Check if port 8000 is already in use
netstat -ano | findstr :8000

# Kill the process using the port
taskkill /PID <PID> /F
```

**Issue: Database errors**
```bash
# Delete the database file and restart
rm data_redundancy.db
python main.py
```

**Issue: Import errors**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

**Issue: Validation always returns no redundancy**
- Make sure you're adding entries to the database first
- Validation only checks against existing entries
- Use the `/add` endpoint to populate the database

## 📊 Monitoring and Maintenance

### Check System Health
```bash
# Get current statistics
curl "http://localhost:8000/statistics"

# Get all entries (with pagination)
curl "http://localhost:8000/entries?limit=10"

# Get only unique entries
curl "http://localhost:8000/entries?unique_only=true"
```

### Database Maintenance
```bash
# View database size
ls -lh data_redundancy.db

# Backup database
cp data_redundancy.db data_redundancy_backup_$(date +%Y%m%d).db
```

## 🎯 Best Practices

1. **Always validate before adding** - Use the `/validate` endpoint first
2. **Handle duplicate responses gracefully** - Check for 400 status codes
3. **Use force add sparingly** - Only when you have a specific reason
4. **Monitor statistics regularly** - Keep track of database health
5. **Test with sample data** - Use the provided test scripts
6. **Search before adding** - Use `/search` to check for similar content

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
DATABASE_URL=sqlite:///./data_redundancy.db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
SIMILARITY_THRESHOLD=0.8
```

### Similarity Threshold

The `SIMILARITY_THRESHOLD` determines how similar content must be to be flagged as redundant:
- `0.9-1.0`: Very strict (only near-identical content)
- `0.7-0.9`: Recommended balanced setting
- `0.5-0.7`: More lenient (catches more potential duplicates)

## API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### 1. Validate Entry
Validate if an entry can be added without creating redundancy.

```http
POST /validate
Content-Type: application/json

{
  "content": "Your content here",
  "data_type": "text",
  "source": "optional_source"
}
```

**Response**:
```json
{
  "is_valid": true,
  "can_add": true,
  "message": "No redundancy detected. Safe to add this entry.",
  "redundancy_check": {
    "is_duplicate": false,
    "is_false_positive": false,
    "similarity_score": 0.0,
    "matched_entries": [],
    "recommendation": "No redundancy detected. Safe to add this entry."
  }
}
```

#### 2. Add Entry
Add a new data entry with automatic redundancy checking.

```http
POST /add?force_add=false
Content-Type: application/json

{
  "content": "Your content here",
  "data_type": "text",
  "source": "optional_source"
}
```

**Parameters**:
- `force_add` (optional): Override redundancy detection and force add the entry

#### 3. Get Entries
Retrieve data entries with pagination.

```http
GET /entries?skip=0&limit=100&unique_only=false
```

**Parameters**:
- `skip`: Number of entries to skip (pagination)
- `limit`: Maximum number of entries to return
- `unique_only`: Return only non-duplicate entries

#### 4. Search Entries
Search entries by content.

```http
GET /search?query=search_term&data_type=optional_type
```

#### 5. Get Statistics
Get comprehensive database statistics.

```http
GET /statistics
```

**Response**:
```json
{
  "total_entries": 150,
  "unique_entries": 120,
  "duplicates_found": 25,
  "false_positives": 5,
  "data_type_distribution": {
    "text": 80,
    "document": 45,
    "metadata": 25
  }
}
```

#### 6. Update Entry
Update an existing entry.

```http
PUT /entries/{entry_id}
Content-Type: application/json

{
  "content": "Updated content",
  "data_type": "updated_type"
}
```

#### 7. Delete Entry
Delete an existing entry.

```http
DELETE /entries/{entry_id}
```

#### 8. Mark as Duplicate
Manually mark an entry as duplicate.

```http
POST /entries/{entry_id}/mark-duplicate?original_id=123&similarity_score=0.85
```

#### 9. Mark as False Positive
Mark an entry as false positive.

```http
POST /entries/{entry_id}/mark-false-positive
```

## Usage Examples

### Python Client Example

```python
import requests
import json

# Base URL
BASE_URL = "http://localhost:8000"

# Validate an entry before adding
def validate_entry(content, data_type):
    response = requests.post(f"{BASE_URL}/validate", json={
        "content": content,
        "data_type": data_type
    })
    return response.json()

# Add an entry
def add_entry(content, data_type, source=None):
    response = requests.post(f"{BASE_URL}/add", json={
        "content": content,
        "data_type": data_type,
        "source": source
    })
    return response.json()

# Search entries
def search_entries(query, data_type=None):
    params = {"query": query}
    if data_type:
        params["data_type"] = data_type
    response = requests.get(f"{BASE_URL}/search", params=params)
    return response.json()

# Example usage
if __name__ == "__main__":
    # Validate first
    validation = validate_entry("This is test content", "text")
    print("Validation result:", validation)
    
    if validation["can_add"]:
        # Add the entry
        result = add_entry("This is test content", "text", "example_source")
        print("Added entry:", result)
    
    # Search for entries
    search_results = search_entries("test content")
    print("Search results:", search_results)
```

### JavaScript/Node.js Example

```javascript
const axios = require('axios');

const BASE_URL = 'http://localhost:8000';

// Validate an entry
async function validateEntry(content, dataType) {
    try {
        const response = await axios.post(`${BASE_URL}/validate`, {
            content: content,
            data_type: dataType
        });
        return response.data;
    } catch (error) {
        console.error('Validation error:', error.response.data);
    }
}

// Add an entry
async function addEntry(content, dataType, source = null) {
    try {
        const response = await axios.post(`${BASE_URL}/add`, {
            content: content,
            data_type: dataType,
            source: source
        });
        return response.data;
    } catch (error) {
        console.error('Add entry error:', error.response.data);
    }
}

// Example usage
async function main() {
    const validation = await validateEntry('Sample content', 'text');
    console.log('Validation:', validation);
    
    if (validation.can_add) {
        const result = await addEntry('Sample content', 'text', 'api_source');
        console.log('Added:', result);
    }
}

main();
```

## Testing

### Run Tests

```bash
# Run all tests
pytest test_redundancy_system.py -v

# Run redundancy detector tests
pytest test_redundancy_detector.py -v

# Run with coverage
pytest --cov=. --cov-report=html
```

### Test Coverage

The test suite covers:
- API endpoint functionality
- Redundancy detection algorithms
- Database operations
- Error handling
- Edge cases and validation

## Redundancy Detection Algorithms

The system uses multiple similarity detection methods:

1. **Exact Duplicate Detection**: SHA-256 hashing for identical content
2. **Fuzzy Matching**: 
   - Ratio-based similarity
   - Partial ratio matching
   - Token sort ratio
3. **False Positive Heuristics**:
   - Length difference analysis
   - Word overlap analysis
   - Content pattern analysis

### Similarity Scoring

- **1.0**: Exact duplicate
- **0.8-0.99**: High similarity (likely duplicate)
- **0.6-0.79**: Medium similarity (possible false positive)
- **0.0-0.59**: Low similarity (likely unique)

## Database Schema

### DataEntry Table
- `id`: Primary key
- `content`: The actual data content
- `content_hash`: SHA-256 hash for exact duplicate detection
- `data_type`: Type/category of data
- `source`: Source of the data
- `similarity_score`: Similarity score to matched content
- `is_duplicate`: Boolean flag for duplicates
- `is_false_positive`: Boolean flag for false positives
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### RedundancyLog Table
- `id`: Primary key
- `original_entry_id`: Reference to original entry
- `duplicate_entry_id`: Reference to duplicate entry
- `similarity_score`: Similarity score at detection
- `detection_method`: Method used for detection
- `action_taken`: Action performed
- `created_at`: Log timestamp

## Performance Considerations

### Indexing
- Content hash is indexed for fast exact duplicate detection
- Data type is indexed for efficient filtering
- Created_at is indexed for temporal queries

### Optimization Tips
1. **Batch Processing**: Process multiple entries in batches for better performance
2. **Similarity Threshold**: Adjust threshold based on your specific use case
3. **Database Choice**: Consider PostgreSQL for production environments
4. **Caching**: Implement caching for frequently accessed entries

## Deployment

### Docker Deployment

Create a `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "main.py"]
```

Create a `docker-compose.yml`:

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/redundancy_db
    depends_on:
      - db

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=redundancy_db
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Production Considerations

1. **Database**: Use PostgreSQL or MySQL for production
2. **Security**: Implement authentication and authorization
3. **Monitoring**: Add logging and monitoring
4. **Scaling**: Consider horizontal scaling for high throughput
5. **Backup**: Implement regular database backups

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Create an issue on GitHub
- Check the API documentation at `/docs` endpoint
- Review the test cases for usage examples

## Changelog

### Version 1.0.0
- Initial release
- Core redundancy detection functionality
- REST API implementation
- Comprehensive test suite
- Documentation and examples
