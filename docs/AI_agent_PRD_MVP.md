# Sanskara AI - Hindu Wedding Planning Platform
## Product Requirements Document (PRD)

### Version: 1.0 (MVP)
### Date: June 2025

---

## 1. Executive Summary

Sanskara AI is an intelligent Hindu wedding planning platform that leverages AI agents to provide personalized, culturally-aware wedding planning assistance. The platform connects couples with vendors, manages rituals according to Hindu traditions, handles budget allocation, and orchestrates the entire wedding planning journey through intelligent automation.

### 1.1 Vision
To become the most trusted AI-powered platform for Hindu wedding planning, preserving cultural authenticity while simplifying the complex process of organizing traditional marriages.

### 1.2 Mission
Empower couples to plan their dream Hindu wedding by providing intelligent guidance on rituals, vendor matching, budget management, and cultural compliance while maintaining the sanctity of traditional practices.

---

## 2. Product Overview

### 2.1 Core Value Proposition
- **Cultural Intelligence**: Deep understanding of Hindu wedding traditions, rituals, and regional variations
- **Intelligent Matching**: AI-powered vendor discovery and matching based on preferences, budget, and location
- **Ritual Guidance**: Comprehensive guidance on traditional ceremonies, timing, and required materials (Samagri)
- **Budget Optimization**: Smart budget allocation and expense tracking across multiple events
- **Seamless Communication**: WhatsApp integration for vendor-client communication
- **End-to-End Orchestration**: Complete wedding planning workflow from onboarding to execution

### 2.2 Target Users
- **Primary**: Engaged couples planning Hindu weddings (25-35 years, urban/semi-urban, tech-savvy)
- **Secondary**: Wedding vendors (venues, photographers, caterers, decorators, priests)
- **Tertiary**: Family members involved in wedding planning

---

## 3. Technical Architecture

### 3.1 Core Technology Stack
- **Database**: Supabase (PostgreSQL with real-time features)
- **Agent Framework**: Google Agent Development Kit (ADK)
- **Vector Database**: Astra DB (ritual and cultural knowledge)
- **LLM Provider**: Google AI (Gemini models)
- **Web Search**: Tavily API
- **Communication**: WhatsApp Business API
- **Authentication**: Supabase Auth
- **Storage**: Supabase Storage (images, documents)

### 3.2 Agent Architecture Framework
```
Google ADK Orchestration Layer
├── Multi-Agent System Coordinator
├── Workflow State Management
├── Agent Communication Bus
└── Error Handling & Recovery
```

---

## 4. Agent System Design

### 4.1 Master Orchestrator Agent
**Role**: Central coordinator managing the entire wedding planning workflow

**Capabilities**:
- User journey orchestration from onboarding to wedding completion
- Sub-agent delegation and coordination
- Workflow state management across multiple events
- Cross-agent communication and data synchronization
- Failure detection and recovery mechanisms

**Tools & Integrations**:
- Google ADK Workflow Engine
- Supabase state management
- Agent communication bus
- Error logging and alerting

**Key Workflows**:
- `InitiateWeddingPlanningWorkflow`
- `CoordinateMultiEventPlanningWorkflow`
- `VendorBookingOrchestrationWorkflow`
- `EmergencyHandlingWorkflow`

### 4.2 Cultural Intelligence & Ritual Agent
**Role**: Expert advisor on Hindu wedding traditions, rituals, and cultural practices

**Capabilities**:
- Ritual recommendation based on region, caste, and family traditions
- Auspicious timing calculations (Muhurat)
- Samagri (materials) checklist generation
- Cultural compliance validation
- Regional variation awareness
- Integration with Pandit/Priest recommendations

**Tools & Integrations**:
- Astra DB vector search (ritual knowledge base)
- Google AI for cultural context understanding
- Pandit directory and availability checking
- Cultural calendar integration

**Knowledge Base Categories**:
- Pre-wedding ceremonies (Haldi, Mehendi, Sangeet)
- Main wedding rituals (Saptapadi, Mangalsutra, etc.)
- Post-wedding ceremonies (Griha Pravesh, Reception)
- Regional variations (North Indian, South Indian, Bengali, etc.)
- Caste-specific traditions
- Auspicious timing calculations

### 4.3 User Onboarding & Preferences Agent
**Role**: Intelligent onboarding specialist collecting comprehensive user preferences

**Capabilities**:
- Interactive questionnaire management
- Preference extraction from natural language
- Cultural background assessment
- Budget range establishment
- Guest count estimation
- Date preference analysis
- Style and theme preference identification

**Tools & Integrations**:
- Supabase user profile management
- Google AI for conversation understanding
- WhatsApp API for mobile onboarding
- Form validation and completion tracking

**Data Collection Areas**:
- Personal details (couple information)
- Cultural background (region, caste, traditions)
- Budget expectations (overall and category-wise)
- Event preferences (number of functions, scale)
- Style preferences (traditional vs contemporary)
- Location preferences (hometown vs destination)
- Guest list estimates
- Dietary requirements and restrictions

### 4.4 Intelligent Vendor Matching Agent
**Role**: Advanced vendor discovery and matching specialist

**Capabilities**:
- Multi-criteria vendor search and ranking
- Availability verification across dates
- Budget compatibility assessment
- Portfolio analysis and recommendation
- Vendor reputation and review analysis
- Negotiation assistance and price optimization
- Vendor communication facilitation

**Tools & Integrations**:
- Supabase vendor database queries
- Google AI for preference matching
- WhatsApp API for vendor communication
- Tavily web search for vendor discovery
- Google Maps integration for location-based search
- Review and rating analysis algorithms

**Vendor Categories**:
- Venues (marriage halls, banquet halls, outdoor venues)
- Catering services
- Photography & videography
- Decoration & flowers
- Music & entertainment
- Transportation
- Priests & religious services
- Makeup & beauty services
- Wedding planners & coordinators

### 4.5 Budget Management & Optimization Agent
**Role**: Financial planning and optimization expert

**Capabilities**:
- Intelligent budget allocation across categories
- Real-time expense tracking
- Cost optimization suggestions
- Vendor price comparison
- Payment schedule management
- Emergency fund recommendations
- ROI analysis for different spending options

**Tools & Integrations**:
- Supabase budget tracking
- Google AI for spending pattern analysis
- Vendor pricing comparison algorithms
- Payment gateway integration preparation
- Financial reporting and analytics

**Budget Categories**:
- Venue & accommodation (30-40%)
- Catering & food (25-35%)
- Photography & videography (8-12%)
- Decoration & flowers (10-15%)
- Clothing & jewelry (10-15%)
- Music & entertainment (5-8%)
- Transportation (3-5%)
- Miscellaneous & contingency (5-10%)

### 4.6 Communication & Notification Agent
**Role**: Multi-channel communication orchestrator

**Capabilities**:
- WhatsApp message automation
- Vendor-client communication facilitation
- Appointment scheduling and reminders
- Status update notifications
- Emergency alert system
- Multi-language support (Hindi, English, regional languages)

**Tools & Integrations**:
- WhatsApp Business API
- Supabase notification system
- Google AI for message personalization
- Scheduling and calendar integration
- SMS fallback system

**Communication Scenarios**:
- Vendor introduction and contact facilitation
- Appointment confirmations and reminders
- Budget updates and alerts
- Ritual timing notifications
- Emergency vendor replacement
- Progress milestone celebrations
- Post-wedding follow-up

### 4.7 Task Management & Timeline Agent
**Role**: Project management specialist for wedding planning

**Capabilities**:
- Intelligent task creation and prioritization
- Timeline optimization based on wedding date
- Dependency management between tasks
- Progress tracking and bottleneck identification
- Automated reminder system
- Milestone celebration triggers

**Tools & Integrations**:
- Supabase task management
- Google ADK workflow orchestration
- Calendar integration
- WhatsApp reminder system
- Progress analytics and reporting

**Task Categories**:
- Venue booking and confirmation
- Vendor finalization and contracts
- Invitation design and distribution
- Ritual preparation and scheduling
- Shopping and procurement
- Guest coordination
- Final preparations and coordination

---

## 5. User Journey & Workflows

### 5.1 Primary User Journey

#### Phase 1: Discovery & Onboarding (Days 1-7)
1. **Initial Interaction**
   - User accesses platform via web/mobile
   - Master Orchestrator initiates `InitiateWeddingPlanningWorkflow`
   - User Onboarding Agent engages with welcome sequence

2. **Comprehensive Preference Collection**
   - Cultural background assessment
   - Budget range establishment
   - Event preferences and scale determination
   - Style and theme preference identification
   - Guest list and dietary requirement collection

3. **Initial Recommendations**
   - Cultural Intelligence Agent provides ritual overview
   - Budget Agent suggests initial allocation framework
   - Vendor Matching Agent provides sample vendor categories

#### Phase 2: Planning & Exploration (Days 8-30)
1. **Ritual Planning Deep Dive**
   - Cultural Intelligence Agent provides detailed ritual timeline
   - Muhurat calculation and auspicious timing recommendations
   - Samagri checklist generation for each ceremony
   - Pandit recommendation and availability checking

2. **Vendor Discovery & Matching**
   - Vendor Matching Agent initiates comprehensive search
   - Multi-criteria filtering and ranking
   - Initial vendor shortlist with portfolio review
   - Availability verification for wedding dates

3. **Budget Refinement**
   - Budget Agent provides detailed category-wise allocation
   - Cost optimization suggestions based on vendor quotes
   - Payment timeline and milestone planning

#### Phase 3: Vendor Engagement & Booking (Days 31-60)
1. **Vendor Communication Facilitation**
   - Communication Agent facilitates WhatsApp introductions
   - Appointment scheduling for vendor meetings
   - Quote collection and comparison assistance
   - Negotiation support and guidance

2. **Booking Coordination**
   - Master Orchestrator manages multi-vendor booking workflow
   - Contract review and finalization support
   - Payment schedule coordination
   - Booking confirmation and documentation

#### Phase 4: Execution & Coordination (Days 61-Wedding Day)
1. **Task Management & Timeline Execution**
   - Task Management Agent creates detailed action items
   - Progress tracking and bottleneck identification
   - Automated reminders and status updates
   - Emergency handling and vendor replacement if needed

2. **Final Preparations**
   - Cultural Intelligence Agent provides final ritual guidelines
   - Communication Agent coordinates with all stakeholders
   - Last-minute troubleshooting and support

#### Phase 5: Post-Wedding (Days After Wedding)
1. **Completion & Feedback**
   - Final payment coordination
   - Vendor performance evaluation
   - User feedback collection and analysis
   - Photo/video delivery coordination

### 5.2 Vendor Journey

#### Vendor Onboarding
1. Registration and profile setup
2. Service catalog creation
3. Portfolio upload and optimization
4. Availability calendar setup
5. Pricing and package definition

#### Client Engagement
1. AI-powered client matching
2. WhatsApp introduction facilitation
3. Quote request and response management
4. Booking confirmation and contract processing
5. Project execution and communication

---

## 6. Data Architecture & Schema

### 6.1 Core Entities (Based on Provided Schema)

#### User Management
- `users`: Customer profiles and preferences
- `chat_sessions` & `chat_messages`: Conversation history
- `notifications`: User communication tracking

#### Vendor Management
- `vendors`: Vendor profiles and capabilities
- `vendor_staff`: Team member management
- `vendor_services`: Detailed service offerings
- `vendor_availability`: Date-wise availability tracking

#### Booking & Transaction Management
- `bookings`: Formal vendor-client agreements
- `booking_services`: Specific services within bookings
- `payments`: Financial transaction tracking
- `reviews`: Post-service feedback

#### Planning & Organization
- `tasks` & `vendor_tasks`: Action item management
- `budget_items`: Financial tracking
- `timeline_events`: Wedding schedule management
- `guest_list`: Guest coordination
- `mood_boards`: Visual inspiration tracking

### 6.2 AI-Specific Data Extensions

#### Cultural Knowledge Base (Astra DB)
- Ritual descriptions and requirements
- Regional variation documentation
- Auspicious timing calculations
- Samagri and material requirements
- Traditional practices and customs

#### Agent State Management
- Workflow state tracking
- Agent communication logs
- Decision trees and reasoning trails
- Performance metrics and analytics

---

## 7. API Design & Integration Points

### 7.1 Core APIs

#### User Management APIs
```
POST /api/users/onboard - User onboarding initiation
GET /api/users/{id}/preferences - Retrieve user preferences
PUT /api/users/{id}/preferences - Update user preferences
GET /api/users/{id}/journey-status - Current planning phase
```

#### Agent Interaction APIs
```
POST /api/agents/chat - Chat with AI agents
GET /api/agents/recommendations - Get AI recommendations
POST /api/agents/trigger-workflow - Initiate specific workflows
GET /api/agents/workflow-status - Check workflow progress
```

#### Vendor APIs
```
GET /api/vendors/search - Search vendors with filters
GET /api/vendors/{id}/availability - Check vendor availability
POST /api/vendors/{id}/contact - Facilitate vendor communication
POST /api/bookings - Create vendor booking
```

#### Cultural Intelligence APIs
```
GET /api/rituals/recommendations - Get ritual recommendations
GET /api/rituals/timeline - Generate ritual timeline
GET /api/rituals/samagri - Get material requirements
GET /api/rituals/muhurat - Calculate auspicious timings
```

### 7.2 External Integrations

#### WhatsApp Business API
- Message sending and receiving
- Media sharing (images, documents)
- Template message management
- Contact synchronization

#### Google AI Integration
- Natural language processing
- Conversation understanding
- Preference extraction
- Cultural context analysis

#### Tavily Web Search
- Real-time vendor discovery
- Market price research
- Trend analysis and insights
- Competitive intelligence

---

## 8. Success Metrics & KPIs

### 8.1 User Engagement Metrics
- User onboarding completion rate (target: >85%)
- Average session duration (target: >15 minutes)
- Feature adoption rate across different agents
- User retention at key milestones (30, 60, 90 days)

### 8.2 Wedding Planning Efficiency
- Time from onboarding to first vendor contact (target: <3 days)
- Average number of vendors contacted per category (target: 3-5)
- Booking success rate (target: >70% of engaged users)
- Budget adherence rate (target: within 10% of planned budget)

### 8.3 Cultural Accuracy & Satisfaction
- Cultural recommendation accuracy (user validation: >90%)
- Ritual compliance satisfaction score (target: >4.5/5)
- Pandit/priest recommendation success rate (target: >80%)
- Overall wedding planning satisfaction (target: >4.5/5)

### 8.4 Vendor Performance
- Vendor response rate to client inquiries (target: >75% within 24 hours)
- Average time to booking confirmation (target: <7 days)
- Vendor satisfaction with platform (target: >4.0/5)
- Revenue per successfully matched vendor

---

## 9. Implementation Roadmap

### 9.1 MVP Phase (Months 1-3)
**Core Agent Development**:
- Master Orchestrator Agent setup with Google ADK
- User Onboarding & Preferences Agent
- Basic Cultural Intelligence Agent (ritual recommendations)
- Simple Vendor Matching Agent
- Basic Budget Management Agent

**Infrastructure Setup**:
- Supabase database deployment and schema implementation
- Astra DB vector search integration
- Google AI API integration
- WhatsApp Business API setup
- Basic web application frontend

**Key Features**:
- User onboarding and preference collection
- Basic ritual recommendations
- Vendor search and matching
- WhatsApp communication facilitation
- Simple budget allocation

### 9.2 Enhanced Features Phase (Months 4-6)
**Advanced Agent Capabilities**:
- Enhanced Cultural Intelligence with regional variations
- Advanced Vendor Matching with ML-based recommendations
- Comprehensive Task Management Agent
- Communication Agent with multi-language support
- Advanced Budget Optimization

**Platform Enhancements**:
- Mobile application development
- Advanced analytics and reporting
- Vendor portal development
- Payment gateway integration
- Enhanced security and compliance

### 9.3 Scale & Optimization Phase (Months 7-12)
**AI/ML Enhancements**:
- Machine learning model training on user behavior
- Predictive analytics for vendor recommendations
- Automated price optimization
- Intelligent timeline adjustments
- Personalized cultural recommendations

**Business Growth**:
- Multi-city expansion
- Vendor partner program
- Enterprise/family plan features
- Integration with wedding service marketplaces
- Revenue optimization and monetization strategies

---

## 10. Risk Assessment & Mitigation

### 10.1 Technical Risks
**Risk**: Agent coordination failures
**Mitigation**: Robust error handling, fallback mechanisms, manual override capabilities

**Risk**: Cultural accuracy concerns
**Mitigation**: Expert validation, community feedback integration, continuous knowledge base updates

**Risk**: Vendor availability and reliability
**Mitigation**: Vendor verification process, backup vendor recommendations, performance monitoring

### 10.2 Business Risks
**Risk**: User adoption challenges
**Mitigation**: Extensive user testing, cultural sensitivity training, localized marketing

**Risk**: Vendor partnership difficulties
**Mitigation**: Clear value proposition, fair revenue sharing, dedicated vendor support

**Risk**: Competition from established players
**Mitigation**: Focus on AI differentiation, cultural expertise, superior user experience

---

## 11. Conclusion

Sanskara AI represents a significant opportunity to revolutionize Hindu wedding planning through intelligent automation while preserving cultural authenticity. The comprehensive agent-based architecture ensures scalable, personalized, and culturally-aware wedding planning assistance.

The MVP focuses on core functionalities that provide immediate value to users while establishing the foundation for advanced features. The use of Google ADK for agent orchestration, combined with Supabase for data management and Astra DB for cultural knowledge, creates a robust and scalable platform.

Success will be measured not just by user engagement and booking conversions, but by the platform's ability to preserve and celebrate Hindu wedding traditions while making the planning process more accessible and enjoyable for modern couples.

---

*This PRD serves as the foundational document for the development of Sanskara AI. It should be regularly updated based on user feedback, market research, and technical discoveries during the development process.*