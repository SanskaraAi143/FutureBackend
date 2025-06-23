# Tools Implementation Status and Guide

## Tool Implementation Best Practices

### 1. Tool Structure
Each tool should follow these guidelines:
- Clear, single responsibility
- Comprehensive error handling
- Input validation
- Proper typing
- Detailed documentation
- Return standardized response format

### 3. Tool Context
When defining a tool function, include the `context: ToolContext = None` parameter. The ADK agent will automatically assign the appropriate `ToolContext` value when the tool is called. You do not need to manually set or pass this value in your code.
- Detailed documentation
- Return standardized response format

### 2. Implementation Pattern
```python
async def tool_name(
    parameters: Dict[str, Any],
    context: ToolContext,
) -> dict:
    """
    Tool description.

    Args:
        parameters: Dict containing tool parameters

    Returns:
        ToolResult with success status and relevant data

    Raises:
        Error: For specific error conditions
    """
    try:
        # Input validation
        validate_input(parameters)

        # Core logic
        result = await execute_logic(parameters)

        # Return standardized format
        return {
            "status": "success",
            "data": result
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
```

## Tools Categorization and Status

### Core Tools (8/8 Complete)
1. ✓ User Management
   - `get_user_id`
   - `get_user_data` 
   - `update_user_data`
2. ✓ Vendor Management
   - `list_vendors`
   - `get_vendor_details`
3. ✓ Budget Management
   - `add_budget_item`
   - `get_budget_items`
   - `update_budget_item`
4. ✓ Base Agent Tools
   - `decompose_task`
   - `dispatch_agent`

### Database Tools (2/6 Complete)
1. ✓ User Data Operations
2. ✓ Vendor Data Operations
3. ⊘ Timeline Management
4. ⊘ Chat History
5. ⊘ Preferences Storage
6. ⊘ Analytics Storage

### Integration Tools (0/6 Complete)
1. ⊘ WhatsApp Integration
2. ⊘ Email Service
3. ⊘ Calendar Integration
4. ⊘ Maps Integration
5. ⊘ Payment Gateway
6. ⊘ Cloud Storage

### Multi-modal Tools (0/7 Complete)
1. ⊘ Image Processing
   - Style analysis
   - Color extraction
   - Object detection
2. ⊘ Audio Processing
   - Speech-to-text
   - Sentiment analysis
3. ⊘ Video Processing
   - Frame extraction
   - Scene analysis

### Communication Tools (0/4 Complete)
1. ⊘ Notification System
2. ⊘ Template Management
3. ⊘ Channel Routing
4. ⊘ Message Tracking

### Workflow Tools (0/5 Complete)
1. ⊘ Event Scheduling
2. ⊘ Resource Allocation
3. ⊘ Timeline Management
4. ⊘ Dependency Tracking
5. ⊘ Progress Monitoring

### Emergency Tools (0/6 Complete)
1. ⊘ Issue Detection
2. ⊘ Alternative Search
3. ⊘ Emergency Communication
4. ⊘ Escalation Management
5. ⊘ Resolution Tracking
6. ⊘ Recovery Planning

## Implementation Priority Queue

### High Priority (Next 2 Weeks)

### Medium Priority (2-4 Weeks)
1. Multi-modal Processing Core
   - Image analysis
   - Text extraction
   - Basic video processing
2. Communication Foundation
   - Notification system
   - Template engine
   - Channel management

### Completed
1. Timeline Management Tools
   - `create_timeline_event`
   - `update_timeline_event`
   - `get_timeline_events`

## Testing Requirements

Each tool implementation must include:
1. Unit tests for core functionality
2. Integration tests with dependent systems
3. Error handling tests
4. Performance benchmarks
5. Documentation with examples

## Documentation Template

```markdown
# Tool Name

## Purpose
Brief description of the tool's purpose.

## Security Considerations
Any security considerations for this tool.

## Parameters

## Parameters
- param1: type - description
- param2: type - description

## Returns
Description of return value format

## Example Usage
```python
result = await tool_name(params)
```

## Error Handling
List of possible errors and how they're handled

## Dependencies
- External services
- Internal systems
- Required permissions

## Notes
Additional implementation details or considerations
```

# get_timeline_events

## Purpose
Retrieves all timeline events for a given user.

## Security Considerations
TBD

## Parameters
- user_id (str): The UUID of the user.

## Returns
List[dict]: A list of dictionaries, where each dictionary represents a timeline event. Each dictionary should have the following keys: `event_id`, `user_id`, `event_name`, `event_date_time`, `location`, `description`, `created_at`, `updated_at`.
If no events are found, return an empty list `[]`.
If an error occurs, return a dictionary with the following structure:
  - "status": "error"
  - "error": A description of the error.

## Example Usage
```python
events = await get_timeline_events(user_id="some_user_id")
if isinstance(events, list):
    for event in events:
        print(f"Event: {event['event_name']} on {event['event_date_time']}")
else:
    print(f"Error: {events['error']}")
```

## Error Handling
The tool handles the following errors:
- Missing User ID: Returns {"status": "error", "error": "User ID is required."}
- Other exceptions: Returns {"status": "error", "error": str(e)}

## Dependencies
- Supabase

## Notes
- This tool relies on the `execute_supabase_sql` function to interact with the Supabase database.
- It retrieves data from the `timeline_events` table.
```

# create_timeline_event

## Purpose
Creates a timeline event for a user.

## Security Considerations
TBD

## Parameters
- user_id (str): The user's UUID.
- event (dict): A dictionary containing the event details:
    - event_name (str): The name of the event.
    - event_date_time (str): The date and time of the event (ISO format).
    - description (str): A description of the event.
    - location (str): The location of the event.

## Returns
dict: A dictionary with the following structure:
  - "status": "success" or "error"
  - If "status" is "success":
    - "data": A dictionary containing the inserted event data.
  - If "status" is "error":
    - "error": A description of the error.

## Example Usage
```python
event_data = {
    "event_name": "Sangeet",
    "event_date_time": "2024-08-03T18:00:00",
    "description": "Pre-wedding musical night",
    "location": "Grand Ballroom"
}
result = await create_timeline_event(user_id="some_user_id", event=event_data)
if result["status"] == "success":
    event_data = result["data"]
    print(f"Timeline event created: {event_data}")
else:
    print(f"Error: {result['error']}")
```

## Error Handling
The tool handles the following errors:
- Missing User ID: Returns {"status": "error", "error": "User ID is required."}
- Event data must be a dictionary: Returns {"status": "error", "error": "Event data must be a dictionary."}
- Missing required fields: Returns {"status": "error", "error": "Missing required fields for timeline event."}
- Other exceptions: Returns {"status": "error", "error": str(e)}

## Dependencies
- Supabase

## Notes
- This tool relies on the `execute_supabase_sql` function to interact with the Supabase database.
- It inserts data into the `timeline_events` table.

# get_user_data

## Purpose
Retrieves all user data for a given user_id from the users table.

## Parameters
- user_id (str): The user's UUID.
- context (ToolContext): The tool execution context.

## Returns
dict: A dictionary with the following structure:
  - "status": "success" or "error"
  - If "status" is "success":
    - "user_data": A dictionary containing the user's data.
  - If "status" is "error":
    - "error": A description of the error.

## Example Usage
```python
result = await get_user_data(user_id="some_user_id", context=tool_context)
if result["status"] == "success":
    user_data = result["user_data"]
    print(f"User data: {user_data}")
else:
    print(f"Error: {result['error']}")
```

## Error Handling
The tool handles the following errors:
- Missing user_id: Returns {"status": "error", "error": "User ID is required."}
- User not found: Returns {"status": "error", "error": "User not found."}
- Other exceptions: Returns {"status": "error", "error": <exception_message>}

## Dependencies
- Supabase

## Notes
- This tool relies on the `execute_supabase_sql` function to interact with the Supabase database.
- It assumes that the `users` table has a column named `user_id`.

# get_user_activities

## Purpose
Get all user activities for a user.

## Parameters
- user_id (str): The user's UUID.
- context (ToolContext): Tool execution context.

## Returns
dict:  with success status and list of activity dicts, or error status.

## Example Usage
```python
result = await get_user_activities(user_id="some_user_id", context=tool_context)
if result["status"] == "success":
    activities = result["data"]
    print(f"User activities: {activities}")
else:
    print(f"Error: {result['error']}")
```

## Error Handling
The tool handles the following errors:
- Missing user_id: Returns {"status": "error", "error": "User ID is required."}
- Other exceptions: Returns {"status": "error", "error": str(e)}

## Dependencies
- Supabase

## Notes
- This tool relies on the `execute_supabase_sql` function to interact with the Supabase database.
- It retrieves activities from the `chat_messages` table, filtering by `session_id` from `chat_sessions` for the given `user_id`.

## Monitoring and Maintenance

Each tool should include:
1. Performance metrics
2. Error tracking
3. Usage statistics
4. Health checks
5. Version tracking

## Version History
- v1.0: Initial implementation of core tools
- v1.1: Added user management tools
- v1.2: Added vendor and budget tools
- Current: v1.2
