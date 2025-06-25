# Vendor Management & Recommendation Agent - Detailed Implementation Plan

## 1. Overview

The Vendor Management & Recommendation Agent serves as an intelligent assistant for vendor discovery, matching, and management. It leverages both SQL and vector search capabilities for semantic matching of vendor attributes with user preferences.

## 2. Core Components

### 2.1 Agent Class Structure
```python
class VendorManagementAgent(BaseAgent):
    """
    Intelligent agent for vendor management and recommendations.
    Handles vendor search, recommendations, and initial contact management.
    """
    def __init__(self, 
                 tools: List[BaseTool],
                 memory: Optional[BaseMemory] = None,
                 llm: Optional[BaseLLM] = None):
        super().__init__(name="VendorManagementAgent")
        self.tools = tools
        self.memory = memory or ConversationBufferMemory()
        self.llm = llm or ChatOpenAI(model="gpt-4")
        self.chain = self._create_chain()

    async def _create_chain(self) -> Chain:
        """Creates the main decision-making chain for vendor-related tasks"""
        return create_structured_output_chain(
            output_schema={
                "action": str,  # search/recommend/contact/analyze
                "parameters": dict,
                "reasoning": str
            },
            llm=self.llm,
            prompt=VENDOR_AGENT_PROMPT
        )
```

### 2.2 Required Tools Implementation

#### 2.2.1 Vendor Search Tool
```python
@tool("vendor_search")
async def search_vendors(
    category: Optional[str] = None,
    location: Optional[str] = None,
    budget_range: Optional[Dict[str, float]] = None,
    keywords: Optional[List[str]] = None,
    rating_min: Optional[float] = None
) -> List[Dict]:
    """
    Searches vendors based on given criteria.
    Returns a list of matching vendors with basic details.
    """
    query = _build_vendor_search_query(
        category=category,
        location=location,
        budget_range=budget_range,
        keywords=keywords,
        rating_min=rating_min
    )
    return await execute_supabase_sql(query)
```

#### 2.2.2 Vendor Vector Search Tool
```python
@tool("vendor_semantic_search")
async def search_vendors_semantic(
    description: str,
    vendor_category: Optional[str] = None,
    top_k: int = 5
) -> List[Dict]:
    """
    Performs semantic search on vendor descriptions and portfolios.
    Uses AstraDB for vector search capabilities.
    """
    # Implementation will use AstraDB for vector search
    pass
```

#### 2.2.3 Portfolio Analysis Tool
```python
@tool("analyze_portfolio")
async def analyze_vendor_portfolio(
    vendor_id: str,
    style_description: Optional[str] = None,
    reference_image_url: Optional[str] = None
) -> Dict:
    """
    Analyzes a vendor's portfolio for style matching.
    Can compare against a reference image or style description.
    """
    pass
```

#### 2.2.4 Availability Check Tool
```python
@tool("check_vendor_availability")
async def check_vendor_availability(
    vendor_id: str,
    date: str,
    service_ids: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Checks vendor and specific service availability for a given date.
    """
    query = _build_availability_check_query(
        vendor_id=vendor_id,
        date=date,
        service_ids=service_ids
    )
    return await execute_supabase_sql(query)
```

### 2.3 Database Schema Extensions

#### 2.3.1 Vendor Services Vector Table (AstraDB)
```sql
CREATE TABLE vendor_services_vectors (
    service_id uuid,
    description_embedding vector<float, 1536>,  -- For OpenAI embeddings
    portfolio_style_embedding vector<float, 1536>,
    PRIMARY KEY (service_id)
);
```

#### 2.3.2 Additional Supabase Indexes
```sql
-- Add to existing vendors table
CREATE INDEX idx_vendor_price_range ON vendors USING GIN (pricing_range);
CREATE INDEX idx_vendor_portfolio ON vendors USING GIN (portfolio_image_urls);
```

## 3. Implementation Phases

### Phase 1: Core Search & Match (Week 1-2)

1. **Basic Vendor Search**
   - Implement SQL query builder
   - Add filtering by category, location, budget
   - Create basic search function tests

2. **Vector Search Integration**
   - Setup AstraDB connection
   - Implement embedding generation
   - Create vector search function
   - Add semantic search tests

### Phase 2: Portfolio & Availability (Week 3)

1. **Portfolio Management**
   - Implement portfolio upload
   - Add image analysis
   - Create style matching logic
   - Add portfolio tests

2. **Availability System**
   - Create availability calendar
   - Implement booking checks
   - Add availability tests

### Phase 3: Recommendation Engine (Week 4)

1. **Smart Matching**
   - Implement preference matching
   - Add budget optimization
   - Create recommendation algorithms
   - Add recommendation tests

2. **Contact Management**
   - Setup notification system
   - Implement contact workflow
   - Add contact management tests

## 4. Integration Tests

### 4.1 Test Scenarios
```python
async def test_vendor_search_flow():
    """Tests complete vendor search and recommendation flow"""
    agent = VendorManagementAgent()
    
    # Test basic search
    result = await agent.execute(
        "Find me a photographer in Bangalore with a budget of 50000-100000"
    )
    assert result.vendors is not None
    assert len(result.vendors) > 0
    
    # Test style matching
    result = await agent.execute(
        "I want someone who shoots in a candid style",
        context={"reference_images": ["url1", "url2"]}
    )
    assert result.style_match_score > 0.7
```

## 5. Error Handling & Edge Cases

### 5.1 Error Scenarios
1. No vendors matching criteria
2. Vendor availability conflicts
3. Budget range mismatches
4. Invalid location/category
5. Failed image analysis

### 5.2 Error Handling Implementation
```python
class VendorSearchError(Exception):
    """Base class for vendor search errors"""
    pass

class NoMatchingVendorsError(VendorSearchError):
    """Raised when no vendors match the search criteria"""
    pass

class VendorUnavailableError(VendorSearchError):
    """Raised when vendor is not available for specified date"""
    pass
```

## 6. Monitoring & Logging

### 6.1 Key Metrics
1. Search response time
2. Recommendation accuracy
3. Vendor availability accuracy
4. User satisfaction rate
5. Contact success rate

### 6.2 Logging Implementation
```python
class VendorAgentLogger:
    """Handles logging for vendor agent actions"""
    async def log_search(self, criteria: Dict, results: List[Dict]):
        """Log search operation and results"""
        pass

    async def log_recommendation(self, user_id: str, vendors: List[Dict]):
        """Log recommendation and user interaction"""
        pass
```

## 7. Documentation Requirements

### 7.1 Code Documentation
- Complete docstrings for all classes and methods
- Type hints for all functions
- Example usage in docstrings
- Error handling documentation

### 7.2 User Documentation
- API usage guides
- Search criteria options
- Recommendation system explanation
- Error troubleshooting guide

## 8. Dependencies

### 8.1 External Services
- Supabase for structured data
- AstraDB for vector search
- OpenAI for embeddings
- Google Maps API for location services

### 8.2 Required Python Packages
```python
# requirements.txt additions
cassandra-driver==3.25.0  # For AstraDB
openai==1.0.0
googlemaps==4.10.0
langchain==0.0.200
