# Phase 1: Product Requirements Document (PRD)
## AI-Powered iGaming Promotional Engine - Foundation & Core Platform

**Version:** 1.0  
**Date:** January 2025  
**Status:** Draft  
**Target Timeline:** Months 1-4

---

## Executive Summary

Phase 1 establishes the foundational platform for the AI-Powered iGaming Promotional Engine. This phase focuses on building core infrastructure that enables operators to authenticate, import/export their dynamic data, receive AI-powered insights, and manage campaigns. The system is designed from day one to support multi-tenancy, handle highly dynamic schemas, and scale to thousands of operators.

**Key Deliverables:**
1. Operator Authentication & Multi-Tenancy Infrastructure
2. Dynamic Data Import/Export System
3. AI/ML Insights & Recommendations Engine
4. Campaign Management System

---

## 1. Operator Authentication & Multi-Tenancy Infrastructure

### 1.1 Overview

Build a secure, multi-tenant authentication system that allows operators to register, login, and manage their accounts with complete data isolation.

### 1.2 User Stories

**As an Operator Owner:**
- I want to register my operator account so that I can access the platform
- I want to login securely so that I can manage my promotional campaigns
- I want to invite team members with different roles so that I can delegate work
- I want to reset my password if I forget it
- I want to enable two-factor authentication for additional security

**As an Operator Admin:**
- I want to manage team member permissions so that I can control access
- I want to view audit logs so that I can track system usage
- I want to configure operator settings so that I can customize the platform

**As a System:**
- I must ensure complete data isolation between operators
- I must enforce authentication on all API requests
- I must track all user actions for audit purposes

### 1.3 Functional Requirements

#### 1.3.1 Operator Registration
- **FR-1.1.1:** System shall allow operators to register with:
  - Company name
  - Domain URL (unique identifier)
  - Contact email
  - Password (min 8 chars, complexity requirements)
- **FR-1.1.2:** System shall send email verification upon registration
- **FR-1.1.3:** System shall prevent duplicate domain URLs
- **FR-1.1.4:** System shall create default operator configuration upon registration

#### 1.3.2 Authentication
- **FR-1.2.1:** System shall support JWT-based authentication
- **FR-1.2.2:** System shall provide access tokens (30 min expiry) and refresh tokens (7 days expiry)
- **FR-1.2.3:** System shall store sessions in Redis for fast validation
- **FR-1.2.4:** System shall support password reset via email
- **FR-1.2.5:** System shall support multi-factor authentication (MFA) with TOTP
- **FR-1.2.6:** System shall log all authentication attempts

#### 1.3.3 Role-Based Access Control (RBAC)
- **FR-1.3.1:** System shall support the following roles:
  - **Owner:** Full access, can manage team, billing
  - **Admin:** Full access except billing
  - **Manager:** Can create/edit campaigns, view analytics
  - **Analyst:** Read-only access to analytics and reports
- **FR-1.3.2:** System shall enforce role-based permissions on all API endpoints
- **FR-1.3.3:** System shall allow owners/admins to invite team members
- **FR-1.3.4:** System shall allow owners/admins to manage team member roles

#### 1.3.4 Multi-Tenancy
- **FR-1.4.1:** System shall enforce tenant isolation at database level using PostgreSQL Row-Level Security (RLS)
- **FR-1.4.2:** System shall include tenant context in all API requests via middleware
- **FR-1.4.3:** System shall prevent cross-tenant data access (100% isolation)
- **FR-1.4.4:** System shall support tenant-specific configuration
- **FR-1.4.5:** System shall enforce resource quotas per tenant (configurable)

### 1.4 Technical Requirements

- **TR-1.1:** Use FastAPI with JWT authentication (python-jose)
- **TR-1.2:** Use PostgreSQL Row-Level Security for tenant isolation
- **TR-1.3:** Use Redis for session storage and caching
- **TR-1.4:** Implement tenant context middleware for all routes
- **TR-1.5:** Use passlib with bcrypt for password hashing
- **TR-1.6:** Implement rate limiting per tenant (1000 requests/hour)

### 1.5 Success Criteria

- ✅ Support 100+ concurrent operator logins
- ✅ Authentication response time <100ms (p95)
- ✅ 100% tenant data isolation (zero cross-tenant leakage)
- ✅ Password reset email delivery <5 seconds
- ✅ MFA setup completion rate >80%

---

## 2. Dynamic Data Import/Export System

### 2.1 Overview

Build a flexible data import/export system that allows operators to upload their data (games, players, payment gateways, etc.) with completely dynamic schemas. The system must support schema detection, validation, and transformation.

### 2.2 User Stories

**As an Operator:**
- I want to import my game catalog so that I can run campaigns on games
- I want to import player data so that I can segment and target players
- I want to import payment gateway configurations so that I can track transactions
- I want to export my data in various formats so that I can use it elsewhere
- I want to see import progress and errors so that I can fix issues
- I want to schedule automatic exports so that I can get regular data dumps

**As a System:**
- I must accept data with any schema structure (no fixed columns)
- I must detect and validate data types automatically
- I must handle large files (1M+ records) efficiently
- I must preserve all operator-specific fields

### 2.3 Functional Requirements

#### 2.3.1 Data Import
- **FR-2.1.1:** System shall support import from:
  - CSV files
  - JSON files
  - Excel files (.xlsx, .xls)
  - XML files
- **FR-2.1.2:** System shall support bulk import via API (async processing)
- **FR-2.1.3:** System shall auto-detect schema from first 100 rows
- **FR-2.1.4:** System shall allow operators to define custom schemas
- **FR-2.1.5:** System shall validate data against schema (type checking, required fields)
- **FR-2.1.6:** System shall report import errors with row numbers and error messages
- **FR-2.1.7:** System shall support incremental imports (update existing records)
- **FR-2.1.8:** System shall track import history and status

#### 2.3.2 Supported Entity Types
- **FR-2.2.1:** System shall support import of:
  - **Games:** Game metadata, categories, providers, RTP, volatility, custom fields
  - **Players/Users:** Demographics, preferences, behavior data, custom attributes
  - **Payment Gateways:** Gateway configs, fees, currencies, custom settings
  - **Transactions:** Deposits, withdrawals, bets, wins (historical data)
  - **Custom Entities:** Operator-defined data structures
- **FR-2.2.2:** System shall store all data in MongoDB (dynamic schema) or PostgreSQL JSONB
- **FR-2.2.3:** System shall maintain schema registry per operator per entity type

#### 2.3.3 Schema Management
- **FR-2.3.1:** System shall maintain schema registry in PostgreSQL
- **FR-2.3.2:** System shall support schema versioning
- **FR-2.3.3:** System shall allow schema migration between versions
- **FR-2.3.4:** System shall infer field types (string, number, date, boolean, object)
- **FR-2.3.5:** System shall allow operators to define custom field validations

#### 2.3.4 Data Export
- **FR-2.4.1:** System shall support export in formats:
  - CSV
  - JSON
  - Excel
- **FR-2.4.2:** System shall allow filtered exports (custom queries)
- **FR-2.4.3:** System shall support scheduled exports (daily, weekly, monthly)
- **FR-2.4.4:** System shall provide API-based exports for integrations
- **FR-2.4.5:** System shall allow export templates and presets
- **FR-2.4.6:** System shall generate export files asynchronously for large datasets

### 2.4 Technical Requirements

- **TR-2.1:** Use Celery for async import/export processing
- **TR-2.2:** Store files in MinIO (local S3-compatible storage)
- **TR-2.3:** Use pandas for CSV/Excel parsing
- **TR-2.4:** Publish import events to Kafka for downstream processing
- **TR-2.5:** Store dynamic data in MongoDB with operator_id filtering
- **TR-2.6:** Maintain schema registry in PostgreSQL

### 2.5 Success Criteria

- ✅ Import 1M+ records in <10 minutes
- ✅ Support 50+ different data schemas per operator
- ✅ 99.9% import success rate
- ✅ Export 100K records in <30 seconds
- ✅ Zero data loss during import/export
- ✅ Schema detection accuracy >95%

---

## 3. AI/ML Insights & Recommendations Engine

### 3.1 Overview

Build an AI-powered insights engine that processes operator data and provides actionable recommendations for campaigns, player segmentation, and business intelligence.

### 3.2 User Stories

**As an Operator:**
- I want to see which players are at risk of churning so that I can target them
- I want to know the predicted lifetime value of my players so that I can prioritize
- I want to get campaign recommendations so that I can improve engagement
- I want to see insights in plain English so that I can understand them easily
- I want to receive weekly automated reports so that I can stay informed

**As a System:**
- I must process data from dynamic schemas
- I must generate insights in real-time (<200ms for API)
- I must learn from operator data patterns
- I must provide explainable recommendations

### 3.3 Functional Requirements

#### 3.3.1 Data Processing Pipeline
- **FR-3.1.1:** System shall ingest data from imports in real-time
- **FR-3.1.2:** System shall normalize and enrich data from dynamic schemas
- **FR-3.1.3:** System shall extract features from JSONB/dynamic data
- **FR-3.1.4:** System shall calculate data quality scores
- **FR-3.1.5:** System shall detect anomalies in data patterns

#### 3.3.2 Player Insights
- **FR-3.2.1:** System shall calculate churn risk scores (7-day, 30-day predictions)
- **FR-3.2.2:** System shall predict player lifetime value (LTV)
- **FR-3.2.3:** System shall identify engagement patterns and trends
- **FR-3.2.4:** System shall recommend player segments
- **FR-3.2.5:** System shall suggest next best actions per player

#### 3.3.3 Campaign Insights
- **FR-3.3.1:** System shall recommend optimal campaign timing
- **FR-3.3.2:** System shall suggest target segments for campaigns
- **FR-3.3.3:** System shall provide content personalization ideas
- **FR-3.3.4:** System shall analyze channel effectiveness
- **FR-3.3.5:** System shall recommend budget allocation

#### 3.3.4 Business Intelligence
- **FR-3.4.1:** System shall forecast revenue
- **FR-3.4.2:** System shall analyze player acquisition costs by channel
- **FR-3.4.3:** System shall track retention rate trends
- **FR-3.4.4:** System shall provide game performance insights
- **FR-3.4.5:** System shall analyze payment gateway efficiency

#### 3.3.5 Natural Language Insights
- **FR-3.5.1:** System shall generate insights in plain English using AI
- **FR-3.5.2:** System shall create automated weekly/monthly reports
- **FR-3.5.3:** System shall send anomaly alerts and notifications
- **FR-3.5.4:** System shall explain trends and patterns

### 3.4 Technical Requirements

- **TR-3.1:** Use scikit-learn and XGBoost for ML models
- **TR-3.2:** Use OpenAI GPT-4 for natural language insights
- **TR-3.3:** Use MLflow for model versioning and tracking
- **TR-3.4:** Use Redis for real-time feature caching
- **TR-3.5:** Use Celery for batch insight generation
- **TR-3.6:** Process events from Kafka for real-time updates

### 3.5 ML Models (Phase 1)

- **Churn Prediction:** XGBoost classifier (7-day, 30-day risk scores)
- **LTV Prediction:** Gradient Boosting Regressor
- **Segment Clustering:** K-means with dynamic K
- **Propensity Scoring:** Logistic Regression ensemble

### 3.6 Success Criteria

- ✅ Generate insights for 1M+ players in <1 hour
- ✅ Churn prediction accuracy >70% (Phase 1 target)
- ✅ LTV prediction within 20% error margin
- ✅ Real-time insight API <200ms response time
- ✅ 100+ actionable insights per operator per week
- ✅ Natural language insights readability score >4.0/5.0

---

## 4. Campaign Management System

### 4.1 Overview

Build a comprehensive campaign management system that allows operators to create, configure, execute, and analyze marketing campaigns across multiple channels.

### 4.2 User Stories

**As an Operator:**
- I want to create campaigns so that I can engage my players
- I want to target specific player segments so that I can personalize messages
- I want to schedule campaigns so that they run automatically
- I want to see campaign performance in real-time so that I can optimize
- I want to A/B test campaigns so that I can improve results
- I want to clone successful campaigns so that I can reuse them

**As a System:**
- I must execute campaigns in real-time
- I must track all campaign interactions
- I must support multiple channels (Email, SMS, Push, In-app)
- I must handle high volume (100K+ messages per hour)

### 4.3 Functional Requirements

#### 4.3.1 Campaign Creation
- **FR-4.1.1:** System shall provide visual campaign builder (drag-and-drop UI)
- **FR-4.1.2:** System shall offer campaign templates library
- **FR-4.1.3:** System shall support multi-channel campaigns:
  - Email
  - SMS
  - Push notifications
  - In-app messages
- **FR-4.1.4:** System shall allow campaign scheduling:
  - One-time campaigns
  - Recurring campaigns (daily, weekly, monthly)
  - Event-triggered campaigns
- **FR-4.1.5:** System shall support basic A/B testing (2 variants)

#### 4.3.2 Campaign Execution
- **FR-4.2.1:** System shall trigger campaigns in real-time (<5 second latency)
- **FR-4.2.2:** System shall process campaigns asynchronously (batch processing)
- **FR-4.2.3:** System shall personalize messages (basic personalization)
- **FR-4.2.4:** System shall track delivery status (sent, delivered, opened, clicked)
- **FR-4.2.5:** System shall retry failed deliveries (3 retries with exponential backoff)
- **FR-4.2.6:** System shall handle rate limiting per channel

#### 4.3.3 Campaign Analytics
- **FR-4.3.1:** System shall display real-time performance metrics
- **FR-4.3.2:** System shall track:
  - Delivery rates (sent, delivered, opened, clicked)
  - Conversion tracking
  - Revenue attribution
  - ROI calculations
- **FR-4.3.3:** System shall provide A/B test comparison
- **FR-4.3.4:** System shall generate campaign performance reports
- **FR-4.3.5:** System shall update dashboard in real-time

#### 4.3.4 Campaign Management
- **FR-4.4.1:** System shall support campaign statuses:
  - Draft
  - Scheduled
  - Active
  - Paused
  - Completed
  - Archived
- **FR-4.4.2:** System shall allow campaign cloning
- **FR-4.4.3:** System shall send performance alerts (email notifications)
- **FR-4.4.4:** System shall allow campaign export (reports)

### 4.4 Technical Requirements

- **TR-4.1:** Use Kafka for campaign trigger events
- **TR-4.2:** Use Celery/RabbitMQ for async message delivery
- **TR-4.3:** Use Jinja2 for message templating and personalization
- **TR-4.4:** Integrate with SendGrid (email) and Twilio (SMS)
- **TR-4.5:** Use ClickHouse for campaign analytics (time-series)
- **TR-4.6:** Implement webhook system for delivery events

### 4.5 Success Criteria

- ✅ Execute 10K+ campaigns simultaneously
- ✅ Process 100K+ messages per hour
- ✅ Campaign trigger latency <5 seconds
- ✅ 99.5% message delivery rate
- ✅ Real-time analytics dashboard updates (<2 second refresh)
- ✅ A/B test statistical significance calculation

---

## 5. Non-Functional Requirements

### 5.1 Performance
- API response time <200ms (p95)
- Real-time campaign triggers <5 seconds
- Dashboard load time <2 seconds
- Import processing: 1M records in <10 minutes

### 5.2 Scalability
- Support 100+ concurrent operator logins
- Handle 10K+ active campaigns
- Process 100K+ messages per hour
- Support 1M+ players per operator

### 5.3 Security
- 100% tenant data isolation
- JWT-based authentication with refresh tokens
- MFA support
- Rate limiting per tenant
- Audit logging for all actions

### 5.4 Reliability
- 99.9% uptime target
- Zero data loss during imports
- Automatic retry for failed operations
- Graceful error handling

### 5.5 Usability
- Intuitive UI/UX
- Mobile-responsive design
- Clear error messages
- Comprehensive documentation

---

## 6. Out of Scope (Phase 1)

The following features are explicitly **NOT** included in Phase 1:

- Advanced segmentation engine (Phase 2)
- Real-time personalization engine (Phase 2)
- Journey builder (Phase 2)
- Multi-channel orchestration (Phase 3)
- Advanced attribution models (Phase 3)
- Autonomous AI campaign manager (Phase 4)
- Deep learning models (Phase 4)
- Integrations marketplace (Phase 5)

---

## 7. Dependencies

### 7.1 External Services
- **SendGrid:** Email delivery (API key required)
- **Twilio:** SMS delivery (Account SID and Auth Token required)
- **OpenAI:** Natural language insights (API key required)

### 7.2 Infrastructure
- **PostgreSQL 15+:** Primary database
- **MongoDB 7+:** Dynamic data storage
- **Redis 7+:** Caching and sessions
- **Apache Kafka:** Event streaming (mandatory)
- **MinIO:** File storage (local)
- **Celery:** Async task processing

### 7.3 Development Tools
- Docker & Docker Compose (local development)
- Python 3.11+
- Node.js 18+ (for frontend)

---

## 8. Success Metrics

### 8.1 Business Metrics
- Operator registration completion rate >80%
- Data import success rate >99.9%
- Campaign execution success rate >99.5%
- Operator satisfaction score >4.0/5.0

### 8.2 Technical Metrics
- API uptime >99.9%
- Authentication latency <100ms (p95)
- Import processing time: 1M records <10 minutes
- Campaign trigger latency <5 seconds

### 8.3 ML Model Metrics
- Churn prediction accuracy >70%
- LTV prediction error <20%
- Insight generation: 1M players <1 hour
- Real-time insight API <200ms

---

## 9. Risks & Mitigation

### 9.1 Technical Risks
- **Dynamic Schema Complexity:** Mitigated by MongoDB + schema registry approach
- **Scale Challenges:** Mitigated by Kafka event streaming, async processing
- **Data Import Failures:** Mitigated by validation, error reporting, retry logic

### 9.2 Business Risks
- **Operator Onboarding:** Mitigated by self-service registration, clear documentation
- **Data Migration:** Mitigated by flexible import/export, migration tools

---

## 10. Timeline & Milestones

### Month 1
- ✅ Multi-tenancy infrastructure
- ✅ Operator authentication system
- ✅ Basic data import (CSV, JSON)

### Month 2
- ✅ Dynamic schema management
- ✅ Data export system
- ✅ Data processing pipeline

### Month 3
- ✅ ML models (churn, LTV)
- ✅ Insights dashboard
- ✅ Campaign creation system

### Month 4
- ✅ Campaign execution engine
- ✅ Analytics dashboard
- ✅ End-to-end testing
- ✅ Beta operator onboarding

---

## Appendix

### A. API Endpoints (High-Level)

**Authentication:**
- `POST /api/v1/auth/register` - Operator registration
- `POST /api/v1/auth/login` - Operator login
- `POST /api/v1/auth/refresh` - Refresh token
- `POST /api/v1/auth/password-reset` - Password reset

**Data Import/Export:**
- `POST /api/v1/imports` - Create import job
- `GET /api/v1/imports/{job_id}` - Get import status
- `POST /api/v1/exports` - Create export job
- `GET /api/v1/exports/{job_id}` - Get export status

**Insights:**
- `GET /api/v1/insights/players/{player_id}` - Get player insights
- `GET /api/v1/insights/campaigns/recommendations` - Get campaign recommendations
- `GET /api/v1/insights/business` - Get business intelligence

**Campaigns:**
- `POST /api/v1/campaigns` - Create campaign
- `GET /api/v1/campaigns` - List campaigns
- `POST /api/v1/campaigns/{id}/execute` - Execute campaign
- `GET /api/v1/campaigns/{id}/analytics` - Get campaign analytics

---

**Document Status:** Ready for Review  
**Next Steps:** Create detailed implementation document and begin development
