# Database Architecture & Technologies
## AI-Powered iGaming Promotional Engine

**Version:** 1.0  
**Date:** 8 Jan 2026 11:25 AM                             
**Target Scale:** 10,000 Operators, Millions of Users/Games, Real-time Processing

---

## Executive Summary

This document outlines the database architecture and technology stack for an enterprise-grade, multi-tenant promotional engine designed to handle highly dynamic data schemas, support thousands of operators simultaneously, and process millions of events in real-time.

**Core Architectural Principles:**
- **Dynamic Schema First:** No fixed columns - all operator data is schema-flexible
- **Event-Driven Architecture:** Kafka is MANDATORY - operators never write directly to databases
- **Polyglot Persistence:** Right database for the right purpose (PostgreSQL, MongoDB, Redis, etc.)
- **Multi-Tenancy by Design:** Built for 10,000+ operators with complete data isolation
- **Real-time Processing:** Sub-second latency for campaign decisions and insights
- **Local Development Focus:** All services run locally via Docker Compose

---

## 1. Database Architecture Overview

### 1.1 Polyglot Persistence Strategy

Given the requirement for **extremely dynamic data** (no fixed columns per operator) and the scale requirements (10,000 operators, millions of users), we employ a **polyglot persistence** approach. **A single database cannot solve this problem effectively.**

**Key Principle:** Operators do not integrate with our database directly. They integrate with our **event contract**. Schemas evolve, events don't break, databases project.

### 1.2 Three-Layer Data Model

The architecture is built on three distinct layers, each serving a specific purpose:

#### **Layer A: Event Ingestion (100% Schema-Flexible)**
**Purpose:** Raw data ingestion from operators - source of truth for operator data

**Technology:** Apache Kafka / Pulsar (mandatory backbone)

**Characteristics:**
- Operators send events, not direct database writes
- Payload is operator-defined (no enforced columns)
- Schema-on-read, not schema-on-write
- Decouples producers from consumers
- Enables event replay and history

#### **Layer B: Canonical Normalization (Nexora-Owned Schema)**
**Purpose:** Internal platform schema - what we need for our operations

**Technology:** PostgreSQL

**Characteristics:**
- Fixed relational schema for platform operations
- ACID guarantees for financial/critical data
- Operators never see this schema
- Used for: transactions, wallets, bets, campaigns, users (core identity)

#### **Layer C: Operator-Specific Dynamic Attributes**
**Purpose:** Flexible, operator-configurable data for promotions, AI, personalization

**Technology:** MongoDB / DynamoDB

**Characteristics:**
- Fully dynamic schemas per operator
- Custom VIP logic, risk flags, segments
- Used for: user attributes, preferences, operator-specific metadata
- Not source of truth for money/financial data

### 1.3 Technology Stack by Purpose

| Purpose | Technology | Why |
|---------|-----------|-----|
| **Money, Bets, Wallets** | PostgreSQL | ACID guarantees, correctness, regulatory compliance |
| **Event Streaming Backbone** | Apache Kafka | Decouples producers/consumers, infinite replay, scales infinitely |
| **Raw Event Storage** | Cassandra (optional) | High-volume append-only events, time-series access |
| **User Profiles & Dynamic Attributes** | MongoDB | Schema-flexible, per-operator differences, fast reads |
| **Promo Execution** | Redis | Sub-200ms real-time eligibility, rate limiting, counters |
| **Segmentation & Search** | Elasticsearch | Fast filtering, operator-defined queries, analytics |
| **Analytics** | ClickHouse | Fast aggregations, no impact on production traffic |

---

## 2. Core Database Design

### 2.1 PostgreSQL Schema (Canonical Normalization Layer)

PostgreSQL serves as the **system of record** for:
- **Financial/Transactional Data:** Wallets, bets, settlements, bonus issuance (ledger-style)
- **Multi-tenant Infrastructure:** Operators, users (core identity), authentication
- **Campaign Definitions:** Campaigns, segments (core structure)
- **System Configuration:** Platform-level settings
- **Audit Logs:** Regulatory compliance, audit trails

**Critical Rule:** PostgreSQL is NOT used for operator-specific dynamic schemas. It maintains our canonical, fixed schema for correctness and ACID guarantees.

#### 2.1.1 Multi-Tenancy Tables

```sql
-- Operators (Tenants)
CREATE TABLE operators (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    domain_url VARCHAR(255) UNIQUE NOT NULL,
    subdomain VARCHAR(100) UNIQUE,
    contact_email VARCHAR(255),
    status VARCHAR(50) DEFAULT 'active', -- active, suspended, deleted
    plan_tier VARCHAR(50) DEFAULT 'standard', -- free, standard, enterprise
    resource_limits JSONB DEFAULT '{}', -- quotas, limits
    config JSONB DEFAULT '{}', -- operator-specific config
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX idx_operators_domain ON operators(domain_url);
CREATE INDEX idx_operators_status ON operators(status);

-- Row-Level Security Policy
ALTER TABLE operators ENABLE ROW LEVEL SECURITY;

CREATE POLICY operator_isolation ON operators
    USING (id = current_setting('app.current_operator_id', true)::INTEGER);
```

#### 2.1.2 Authentication & Authorization

```sql
-- Operator Users (Staff/Team Members)
CREATE TABLE operator_users (
    id SERIAL PRIMARY KEY,
    operator_id INTEGER NOT NULL REFERENCES operators(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role VARCHAR(50) NOT NULL, -- owner, admin, manager, analyst, viewer
    permissions JSONB DEFAULT '{}', -- granular permissions
    mfa_enabled BOOLEAN DEFAULT false,
    mfa_secret VARCHAR(255),
    last_login_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    UNIQUE(operator_id, email)
);

CREATE INDEX idx_operator_users_email ON operator_users(email);
CREATE INDEX idx_operator_users_operator ON operator_users(operator_id);

-- Sessions
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER NOT NULL REFERENCES operator_users(id) ON DELETE CASCADE,
    operator_id INTEGER NOT NULL REFERENCES operators(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) NOT NULL,
    refresh_token_hash VARCHAR(255),
    ip_address INET,
    user_agent TEXT,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_sessions_user ON user_sessions(user_id);
CREATE INDEX idx_sessions_token ON user_sessions(token_hash);
CREATE INDEX idx_sessions_expires ON user_sessions(expires_at);
```

#### 2.1.3 Schema Registry (Dynamic Schema Management)

```sql
-- Entity Schema Definitions (Critical for Dynamic Data)
CREATE TABLE operator_schemas (
    id SERIAL PRIMARY KEY,
    operator_id INTEGER NOT NULL REFERENCES operators(id) ON DELETE CASCADE,
    entity_type VARCHAR(100) NOT NULL, -- 'game', 'player', 'payment_gateway', 'transaction', etc.
    schema_name VARCHAR(255) NOT NULL, -- e.g., 'player_v1', 'game_v2'
    schema_definition JSONB NOT NULL, -- Field definitions, types, constraints
    version INTEGER NOT NULL DEFAULT 1,
    is_active BOOLEAN DEFAULT true,
    is_default BOOLEAN DEFAULT false, -- Default schema for entity type
    created_by INTEGER REFERENCES operator_users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(operator_id, entity_type, schema_name)
);

CREATE INDEX idx_schemas_operator_entity ON operator_schemas(operator_id, entity_type);
CREATE INDEX idx_schemas_active ON operator_schemas(operator_id, entity_type, is_active) WHERE is_active = true;

-- Example schema_definition JSONB structure:
-- {
--   "fields": {
--     "player_id": {"type": "string", "required": true, "indexed": true},
--     "email": {"type": "string", "required": true, "indexed": true},
--     "total_deposits": {"type": "number", "required": false},
--     "preferences": {"type": "object", "required": false},
--     "custom_fields": {"type": "object", "required": false}
--   },
--   "indexes": ["player_id", "email", "total_deposits"],
--   "validation_rules": {...}
-- }
```

#### 2.1.4 Campaign Management

```sql
-- Campaigns
CREATE TABLE campaigns (
    id BIGSERIAL PRIMARY KEY,
    operator_id INTEGER NOT NULL REFERENCES operators(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    campaign_type VARCHAR(50) NOT NULL, -- email, sms, push, in_app, whatsapp
    status VARCHAR(50) DEFAULT 'draft', -- draft, scheduled, active, paused, completed, archived
    trigger_type VARCHAR(50) NOT NULL, -- manual, event_based, scheduled, ai_optimized
    target_segment_id BIGINT, -- Reference to segment
    config JSONB NOT NULL DEFAULT '{}', -- Campaign configuration (dynamic)
    schedule_config JSONB DEFAULT '{}',
    personalization_config JSONB DEFAULT '{}',
    ai_config JSONB DEFAULT '{}', -- AI optimization settings
    performance_metrics JSONB DEFAULT '{}', -- Cached metrics
    created_by INTEGER REFERENCES operator_users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    scheduled_at TIMESTAMPTZ,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);

CREATE INDEX idx_campaigns_operator_status ON campaigns(operator_id, status);
CREATE INDEX idx_campaigns_scheduled ON campaigns(operator_id, scheduled_at) WHERE status = 'scheduled';
CREATE INDEX idx_campaigns_active ON campaigns(operator_id, status) WHERE status = 'active';

-- Campaign Executions (Individual message sends)
CREATE TABLE campaign_executions (
    id BIGSERIAL PRIMARY KEY,
    campaign_id BIGINT NOT NULL REFERENCES campaigns(id) ON DELETE CASCADE,
    operator_id INTEGER NOT NULL REFERENCES operators(id) ON DELETE CASCADE,
    player_id VARCHAR(255) NOT NULL, -- External player ID
    channel VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending', -- pending, sent, delivered, opened, clicked, failed
    message_data JSONB NOT NULL, -- Personalized message content
    delivery_metadata JSONB DEFAULT '{}', -- Provider response, timestamps
    sent_at TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ,
    opened_at TIMESTAMPTZ,
    clicked_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_executions_campaign ON campaign_executions(campaign_id, status);
CREATE INDEX idx_executions_player ON campaign_executions(operator_id, player_id);
CREATE INDEX idx_executions_sent ON campaign_executions(sent_at) WHERE status = 'sent';
```

#### 2.1.5 Segments

```sql
-- Segments
CREATE TABLE segments (
    id BIGSERIAL PRIMARY KEY,
    operator_id INTEGER NOT NULL REFERENCES operators(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    segment_type VARCHAR(50) NOT NULL, -- rfm, behavioral, predictive, custom, ai_generated
    criteria JSONB NOT NULL, -- Dynamic segment criteria
    player_count INTEGER DEFAULT 0,
    last_calculated_at TIMESTAMPTZ,
    calculation_status VARCHAR(50) DEFAULT 'pending', -- pending, calculating, completed, failed
    performance_metrics JSONB DEFAULT '{}',
    created_by INTEGER REFERENCES operator_users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_segments_operator ON segments(operator_id);
CREATE INDEX idx_segments_type ON segments(operator_id, segment_type);

-- Segment Membership (Many-to-Many)
CREATE TABLE segment_memberships (
    segment_id BIGINT NOT NULL REFERENCES segments(id) ON DELETE CASCADE,
    operator_id INTEGER NOT NULL REFERENCES operators(id) ON DELETE CASCADE,
    player_id VARCHAR(255) NOT NULL, -- External player ID
    added_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (segment_id, operator_id, player_id)
);

CREATE INDEX idx_memberships_segment ON segment_memberships(segment_id);
CREATE INDEX idx_memberships_player ON segment_memberships(operator_id, player_id);
```

#### 2.1.6 ML Models & Predictions

```sql
-- ML Models Registry
CREATE TABLE ml_models (
    id SERIAL PRIMARY KEY,
    operator_id INTEGER REFERENCES operators(id) ON DELETE CASCADE, -- NULL for global models
    model_type VARCHAR(100) NOT NULL, -- churn, ltv, propensity, recommendation
    model_name VARCHAR(255) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    model_metadata JSONB NOT NULL, -- Training config, features, performance
    model_path TEXT, -- S3 path or model registry path
    status VARCHAR(50) DEFAULT 'training', -- training, active, deprecated
    performance_metrics JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    activated_at TIMESTAMPTZ
);

CREATE INDEX idx_models_operator_type ON ml_models(operator_id, model_type, status);

-- Predictions Cache
CREATE TABLE predictions (
    id BIGSERIAL PRIMARY KEY,
    operator_id INTEGER NOT NULL REFERENCES operators(id) ON DELETE CASCADE,
    player_id VARCHAR(255) NOT NULL,
    model_type VARCHAR(100) NOT NULL,
    prediction_value JSONB NOT NULL, -- Prediction results (dynamic)
    confidence_score NUMERIC(5,4),
    model_version VARCHAR(50),
    calculated_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    UNIQUE(operator_id, player_id, model_type)
);

CREATE INDEX idx_predictions_operator_player ON predictions(operator_id, player_id);
CREATE INDEX idx_predictions_type ON predictions(operator_id, model_type);
CREATE INDEX idx_predictions_expires ON predictions(expires_at) WHERE expires_at IS NOT NULL;
```

#### 2.1.7 Import/Export Jobs

```sql
-- Data Import Jobs
CREATE TABLE import_jobs (
    id BIGSERIAL PRIMARY KEY,
    operator_id INTEGER NOT NULL REFERENCES operators(id) ON DELETE CASCADE,
    entity_type VARCHAR(100) NOT NULL, -- game, player, payment_gateway, etc.
    file_name VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL, -- S3 path
    file_format VARCHAR(50) NOT NULL, -- csv, json, excel, xml
    schema_id INTEGER REFERENCES operator_schemas(id),
    status VARCHAR(50) DEFAULT 'pending', -- pending, processing, completed, failed
    total_records INTEGER,
    processed_records INTEGER DEFAULT 0,
    failed_records INTEGER DEFAULT 0,
    error_log JSONB DEFAULT '[]',
    config JSONB DEFAULT '{}', -- Import configuration
    created_by INTEGER REFERENCES operator_users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);

CREATE INDEX idx_imports_operator_status ON import_jobs(operator_id, status);

-- Data Export Jobs
CREATE TABLE export_jobs (
    id BIGSERIAL PRIMARY KEY,
    operator_id INTEGER NOT NULL REFERENCES operators(id) ON DELETE CASCADE,
    entity_type VARCHAR(100) NOT NULL,
    export_format VARCHAR(50) NOT NULL, -- csv, json, excel
    filters JSONB DEFAULT '{}', -- Export filters
    file_path TEXT, -- S3 path (after completion)
    status VARCHAR(50) DEFAULT 'pending',
    total_records INTEGER,
    file_size_bytes BIGINT,
    expires_at TIMESTAMPTZ, -- File retention
    created_by INTEGER REFERENCES operator_users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);
```

---

### 2.2 MongoDB Schema (Operator-Specific Dynamic Attributes)

MongoDB stores **operator-specific dynamic attributes** where schemas vary per operator. This is Layer C of our architecture.

**Important:** MongoDB is NOT the source of truth for financial data. It stores:
- Dynamic user attributes (VIP tiers, preferences, custom flags)
- Operator-specific metadata
- Custom segments and attributes
- Promotional targeting data

#### 2.2.1 Database Structure

```
Database: nexora_attributes
├── Collections (shared, filtered by operator_id)
│   ├── user_attributes
│   ├── game_metadata
│   ├── operator_configs
│   └── custom_entities
```

**Note:** We use `operator_id` as a filter field, not separate databases per operator (for operational simplicity in local development).

#### 2.2.2 Collection Examples

**Games Collection:**
```javascript
{
  _id: ObjectId("..."),
  operator_id: 123,
  external_id: "game_abc123",
  schema_version: 1,
  data: {
    // Fully dynamic - no fixed schema
    name: "Starburst",
    provider: "NetEnt",
    category: "slots",
    rtp: 96.1,
    volatility: "medium",
    min_bet: 0.10,
    max_bet: 100,
    // Operator-specific fields
    custom_field_1: "...",
    custom_field_2: {...}
  },
  metadata: {
    imported_at: ISODate("..."),
    last_updated: ISODate("..."),
    source: "import_job_456"
  },
  indexes: {
    external_id: 1,
    "data.provider": 1,
    "data.category": 1
  }
}
```

**Players Collection:**
```javascript
{
  _id: ObjectId("..."),
  operator_id: 123,
  external_player_id: "player_xyz789",
  schema_version: 2,
  data: {
    // Dynamic player data
    email: "player@example.com",
    first_name: "John",
    last_name: "Doe",
    registration_date: ISODate("..."),
    total_deposits: 5000.00,
    total_withdrawals: 3000.00,
    favorite_games: ["game_abc123", "game_def456"],
    preferences: {
      language: "en",
      currency: "USD",
      notifications: true
    },
    // Operator-specific fields
    vip_tier: "gold",
    custom_attributes: {...}
  },
  computed_fields: {
    ltv_prediction: 15000.00,
    churn_risk_score: 0.15,
    last_segment_update: ISODate("...")
  },
  metadata: {
    created_at: ISODate("..."),
    updated_at: ISODate("..."),
    last_activity: ISODate("...")
  }
}
```

#### 2.2.3 MongoDB Indexing Strategy

```javascript
// Compound indexes for common queries
db.players.createIndex({ operator_id: 1, external_player_id: 1 }, { unique: true });
db.players.createIndex({ operator_id: 1, "data.email": 1 });
db.players.createIndex({ operator_id: 1, "computed_fields.churn_risk_score": 1 });
db.players.createIndex({ operator_id: 1, "metadata.last_activity": -1 });

db.games.createIndex({ operator_id: 1, external_id: 1 }, { unique: true });
db.games.createIndex({ operator_id: 1, "data.provider": 1, "data.category": 1 });

// Text indexes for search
db.players.createIndex({ "data.email": "text", "data.first_name": "text", "data.last_name": "text" });
```

#### 2.2.4 MongoDB Sharding Strategy

For scale (10,000 operators, millions of documents):

```javascript
// Shard key: operator_id (ensures operator data co-location)
sh.enableSharding("nexora_data");
sh.shardCollection("nexora_data.players", { operator_id: 1, external_player_id: 1 });
sh.shardCollection("nexora_data.games", { operator_id: 1, external_id: 1 });
```

---

### 2.3 Cassandra (Optional - High-Volume Event Storage)

**Cassandra is OPTIONAL** - only add if event volume exceeds 500k/sec or you need cheap long-term event storage.

**Use Cases:**
- Raw event storage (append-only)
- User activity events
- Promotion impressions
- Bonus consumption logs
- Session tracking (TTL-based)

**When NOT to use:**
- Promo eligibility logic
- User profiles
- Financial state
- Complex queries

**Schema Pattern:**
```sql
PRIMARY KEY ((operator_id), event_date, event_time)
-- payload stored as blob/map
```

### 2.4 Elasticsearch (Segmentation & Search)

**Elasticsearch is a SEARCH INDEX, not a primary database.**

**Use Cases:**
- User segmentation (fast filtering)
- Promo targeting ("Users with X AND Y AND NOT Z")
- Operator dashboards (aggregations)
- User lookup and search
- Real-time analytics visibility

**Critical Rule:** Elasticsearch is a **projection** fed from Kafka, not source of truth.

**Example Query:**
```
country = "DE"
AND vip_level >= 3
AND deposits_30d > 5
AND NOT bonus_abuse_flag
```

### 2.5 ClickHouse (Analytics & Time-Series)

For high-volume analytics and aggregations without impacting production traffic.

#### 2.5.1 Events Table (ClickHouse)

```sql
CREATE TABLE events (
    operator_id UInt32,
    player_id String,
    event_type String,
    event_timestamp DateTime64(3),
    event_data String, -- JSON string
    campaign_id Nullable(UInt64),
    segment_id Nullable(UInt64),
    source_utm String,
    medium_utm String,
    campaign_utm String,
    -- Materialized columns for common fields
    revenue Nullable(Decimal64(2)) MATERIALIZED JSONExtractFloat(event_data, 'revenue'),
    game_id Nullable(String) MATERIALIZED JSONExtractString(event_data, 'game_id')
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_timestamp)
ORDER BY (operator_id, event_timestamp, event_type)
TTL event_timestamp + INTERVAL 2 YEAR;

-- Aggregating views for real-time analytics
CREATE MATERIALIZED VIEW events_hourly_mv
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(hour)
ORDER BY (operator_id, hour, event_type)
AS SELECT
    operator_id,
    toStartOfHour(event_timestamp) AS hour,
    event_type,
    count() AS event_count,
    sum(revenue) AS total_revenue
FROM events
GROUP BY operator_id, hour, event_type;
```

#### 2.3.2 Campaign Analytics (TimescaleDB)

```sql
-- Hypertable for campaign metrics
CREATE TABLE campaign_metrics (
    time TIMESTAMPTZ NOT NULL,
    operator_id INTEGER NOT NULL,
    campaign_id BIGINT NOT NULL,
    metric_type VARCHAR(50) NOT NULL, -- sent, delivered, opened, clicked, converted
    metric_value NUMERIC(15,2) DEFAULT 0,
    metadata JSONB DEFAULT '{}'
);

SELECT create_hypertable('campaign_metrics', 'time');

CREATE INDEX idx_campaign_metrics_lookup ON campaign_metrics(operator_id, campaign_id, time DESC);
```

---

### 2.4 Redis Schema (Cache & Real-time)

Redis serves multiple purposes:

#### 2.4.1 Key Naming Conventions

```
# Sessions
session:{session_id} -> {user_data}
session:refresh:{refresh_token_hash} -> {session_id}

# Feature Store (Real-time ML features)
features:{operator_id}:{player_id}:{feature_set} -> {features_json}
features:ttl:{operator_id}:{player_id} -> {expiry_timestamp}

# Campaign State
campaign:state:{operator_id}:{campaign_id} -> {state_json}
campaign:queue:{operator_id} -> [campaign_ids]

# Segment Cache
segment:members:{operator_id}:{segment_id} -> Set{player_ids}
segment:count:{operator_id}:{segment_id} -> {count}

# Rate Limiting
ratelimit:{operator_id}:{user_id}:{endpoint} -> {count}
ratelimit:api:{operator_id} -> {count}

# Real-time Insights
insights:{operator_id}:{insight_type} -> {insight_json}
insights:cache:{operator_id}:{player_id} -> {insights_json}
```

#### 2.4.2 Redis Data Structures

```python
# Sessions (Hash)
HSET session:{session_id} user_id {user_id} operator_id {operator_id} expires_at {timestamp}

# Feature Store (Hash with TTL)
HSET features:{operator_id}:{player_id}:churn churn_score 0.75 ltv_prediction 15000.00
EXPIRE features:{operator_id}:{player_id}:churn 3600

# Segment Membership (Set)
SADD segment:members:{operator_id}:{segment_id} {player_id_1} {player_id_2} ...

# Campaign Queue (List)
LPUSH campaign:queue:{operator_id} {campaign_id}

# Rate Limiting (String with INCR)
INCR ratelimit:{operator_id}:{user_id}:api
EXPIRE ratelimit:{operator_id}:{user_id}:api 60
```

---

### 2.5 Apache Kafka Topics (Event Streaming Backbone)

**Kafka is the MANDATORY backbone** - all operator data flows through Kafka first, never directly to databases.

```
# Layer A: Raw Event Ingestion (Schema-Flexible)
nexora.events.raw.{operator_id}      # Raw events from operators (operator-defined payload)
nexora.events.raw.all                # All raw events (for monitoring)

# Layer B: Canonical Events (Normalized)
nexora.events.canonical              # Normalized events (Nexora schema)
nexora.events.enriched               # Events with ML features

# Campaign Events
nexora.campaigns.triggered           # Campaign trigger events
nexora.campaigns.executed            # Campaign execution events
nexora.campaigns.delivered           # Message delivery events
nexora.campaigns.interactions        # Opens, clicks, conversions

# Data Import/Export
nexora.imports.started               # Import job started
nexora.imports.progress              # Import progress updates
nexora.imports.completed             # Import completed
nexora.exports.requested             # Export requested
nexora.exports.completed             # Export completed

# ML Pipeline
nexora.ml.predictions                # ML predictions
nexora.ml.model_updates              # Model retraining events
nexora.ml.insights                   # Generated insights

# System Events
nexora.system.operator.created       # New operator onboarded
nexora.system.schema.updated         # Schema changes
```

**Event Contract Example (Layer A - Raw):**
```json
{
  "operator_id": "op_123",
  "event_type": "BET_PLACED",
  "timestamp": "2024-01-08T10:15:00Z",
  "payload": {
    "stake": 10,
    "game_code": "JILI_79",
    "custom_field_x": "VIP_FAST",
    "operator_specific_data": {...}
  }
}
```

**Canonical Event Example (Layer B - Normalized):**
```json
{
  "nexora_user_id": "uuid",
  "operator_id": "op_123",
  "event_type": "BET",
  "amount": 10,
  "currency": "INR",
  "timestamp": "2024-01-08T10:15:00Z"
}
```

---

## 3. Technology Stack & Justifications

### 3.1 PostgreSQL 15+ (Canonical Normalization Layer)

**Why PostgreSQL:**
- **ACID Compliance:** Critical for financial data (wallets, bets, balances)
- **Strong Consistency:** Regulatory-friendly, auditable
- **Row-Level Security:** Built-in multi-tenancy support
- **Mature Ecosystem:** Extensive tooling and community
- **Correctness > Flexibility:** Financial operations require correctness

**Use Cases:**
- **Financial/Transactional:** Wallets, bets, settlements, bonus issuance
- **Core Identity:** Users (core fields), operators, authentication
- **Campaign Definitions:** Campaigns, segments (core structure)
- **System Configuration:** Platform-level settings
- **Audit Logs:** Regulatory compliance

**What PostgreSQL Does NOT Store:**
- Operator-specific dynamic schemas (use MongoDB)
- Raw event payloads (use Kafka/Cassandra)
- High-frequency event streams (use Kafka)

**Local Development Setup:**
- Single PostgreSQL instance
- Connection pooling via SQLAlchemy
- No read replicas needed initially

---

### 3.2 MongoDB 7+ (Operator-Specific Dynamic Attributes)

**Why MongoDB:**
- **Schema-less:** Perfect for operator-specific dynamic attributes
- **Flexible Queries:** Rich query language for dynamic schemas
- **Fast Reads:** Optimized for promo eligibility checks
- **Per-Operator Differences:** Each operator can have different fields

**Use Cases:**
- **Dynamic User Attributes:** VIP tiers, preferences, custom flags
- **Operator-Specific Metadata:** Custom fields per operator
- **Promotional Targeting Data:** Segments, attributes for campaigns
- **Custom Entities:** Operator-defined data structures

**What MongoDB Does NOT Store:**
- Financial balances (use PostgreSQL)
- Raw event streams (use Kafka)
- Source of truth for money (use PostgreSQL)

**Local Development Setup:**
- Single MongoDB instance
- Collections filtered by `operator_id` field
- Indexes on `operator_id` for performance

---

### 3.3 Time-Series Database: ClickHouse / TimescaleDB

**Why ClickHouse:**
- **Extreme Performance:** Handles billions of events
- **Columnar Storage:** Optimized for analytics
- **Real-time Aggregations:** Materialized views
- **Compression:** Efficient storage for time-series data
- **SQL Interface:** Familiar query language

**Why TimescaleDB (Alternative):**
- **PostgreSQL Extension:** Seamless integration
- **Hypertables:** Automatic partitioning
- **Continuous Aggregates:** Pre-computed views
- **PostgreSQL Ecosystem:** Use existing tools

**Use Cases:**
- Event streams (player actions, campaign events)
- Real-time analytics
- Time-series aggregations
- Historical data analysis

**Scaling Strategy:**
- Partitioning by time (monthly/quarterly)
- Distributed ClickHouse cluster
- Data retention policies (TTL)

---

### 3.4 Cache & Real-time: Redis 7+

**Why Redis:**
- **Sub-millisecond Latency:** Critical for real-time features
- **Rich Data Structures:** Sets, Hashes, Sorted Sets
- **Pub/Sub:** Real-time notifications
- **Persistence Options:** RDB + AOF for durability
- **Cluster Mode:** Horizontal scaling

**Use Cases:**
- Session management
- Real-time ML feature store
- Campaign state cache
- Segment membership cache
- Rate limiting
- Real-time insights

**Scaling Strategy:**
- Redis Cluster for horizontal scaling
- Read replicas for read-heavy workloads
- Memory optimization (compression)
- TTL management for cache eviction

---

### 3.5 Apache Kafka (Event Streaming Backbone - MANDATORY)

**Why Kafka (MANDATORY):**
- **Decouples Producers from Consumers:** Operators send events, databases consume
- **Schema Flexibility:** Operators define their own event payloads
- **Event Replay:** Complete event history for reprocessing
- **Scalability:** Handles millions of events per second
- **No Direct DB Writes:** Operators never write directly to databases

**Critical Architecture Rule:**
```
Operators → Kafka → Databases (PostgreSQL, MongoDB, etc.)
NOT: Operators → Databases directly
```

**Use Cases:**
- **Event Ingestion:** All operator data flows through Kafka first
- **Event Sourcing:** Complete event history
- **Real-time Processing:** Stream processing for campaigns
- **Data Pipeline:** Orchestrates data flow to multiple databases
- **Schema Evolution:** Events evolve, databases project

**Local Development Setup:**
- Single Kafka broker (sufficient for development)
- Zookeeper or KRaft mode
- Topic partitioning for parallelism
- Consumer groups for parallel processing

---

### 3.6 Message Queue: RabbitMQ / Celery

**Why RabbitMQ:**
- **Reliability:** Message persistence and acknowledgments
- **Flexible Routing:** Exchanges and queues
- **Management UI:** Easy monitoring
- **Celery Integration:** Python async task processing

**Use Cases:**
- Async task processing (imports, exports)
- Campaign execution queue
- Email/SMS delivery queue
- Scheduled jobs

---

### 3.7 Object Storage: MinIO (Local Development)

**Why MinIO:**
- **S3-Compatible:** Same API as AWS S3
- **Local Development:** Runs on local machine
- **Cost-effective:** Free for development
- **API Access:** Programmatic access

**Use Cases:**
- Import/export file storage
- ML model artifacts
- Campaign templates and assets
- File uploads from operators

**Local Development Setup:**
- Single MinIO instance
- Local filesystem storage
- S3-compatible API

---

## 4. Data Flow Architecture

### 4.1 Data Import Flow (Event-Driven)

```
1. Operator uploads file → API endpoint
2. File stored in MinIO (local)
3. Import job created in PostgreSQL
4. Celery task processes file:
   a. Detect schema (or use operator schema)
   b. Parse file (CSV/JSON/Excel)
   c. Validate data against schema
   d. Transform to canonical format
   e. Publish events to Kafka (nexora.events.raw.{operator_id})
5. Kafka consumers:
   a. Write canonical data to PostgreSQL (financial/core)
   b. Write dynamic attributes to MongoDB (operator-specific)
   c. Update Redis cache (real-time features)
   d. Index in Elasticsearch (for segmentation)
6. Kafka event: nexora.imports.completed
7. Trigger data processing pipeline
8. Update ML features
9. Recalculate segments
```

**Key Principle:** Data flows through Kafka first, then to appropriate databases.

### 4.2 Real-time Event Processing (Event-Driven)

```
1. Operator sends event → API endpoint
   - Event payload is operator-defined (schema-flexible)
   - No validation of operator-specific fields
2. Publish to Kafka: nexora.events.raw.{operator_id}
   - Raw event stored as-is
   - Schema-on-read approach
3. Event Normalization Service (Kafka Consumer):
   a. Extract canonical fields (user_id, amount, timestamp)
   b. Validate canonical fields
   c. Publish to Kafka: nexora.events.canonical
4. Multiple Kafka Consumers (parallel processing):
   a. PostgreSQL Consumer: Write financial/transactional data
   b. MongoDB Consumer: Write dynamic attributes
   c. Redis Consumer: Update real-time features
   d. Elasticsearch Consumer: Index for segmentation
   e. ClickHouse Consumer: Store for analytics
5. Campaign Trigger Service (Kafka Consumer):
   a. Check campaign triggers
   b. Evaluate eligibility (Redis)
   c. If triggered → Publish to Kafka: nexora.campaigns.triggered
6. Campaign Execution Service:
   a. Consume campaign triggers
   b. Execute campaign
   c. Publish delivery events
```

**Key Principle:** Event-driven architecture - all processing happens via Kafka consumers, not direct database writes.

### 4.3 Campaign Execution Flow

```
1. Campaign trigger (event/schedule)
2. Load campaign config from PostgreSQL
3. Load target segment from Redis (or compute)
4. For each player in segment:
   a. Load player data from MongoDB
   b. Load ML features from Redis
   c. Personalize message
   d. Queue message delivery (RabbitMQ)
5. Message delivery workers:
   a. Send via channel (Email/SMS/Push)
   b. Update execution status in PostgreSQL
   c. Publish delivery event to Kafka
6. Track interactions (opens, clicks)
7. Update campaign metrics
```

### 4.4 ML Prediction Flow

```
1. Request prediction → API endpoint
2. Check Redis cache (features:{operator_id}:{player_id})
3. If not cached:
   a. Load player data from MongoDB
   b. Extract features
   c. Store in Redis (TTL 1 hour)
4. Load ML model (from model registry)
5. Generate prediction
6. Cache prediction in PostgreSQL
7. Return prediction
```

---

## 5. Multi-Tenancy Implementation

### 5.1 Database-Level Isolation

**PostgreSQL Row-Level Security:**
```sql
-- Set tenant context
SET app.current_operator_id = '123';

-- All queries automatically filtered
SELECT * FROM campaigns; -- Only returns operator 123's campaigns
```

**MongoDB:**
- All queries include `operator_id` filter
- Application-level enforcement
- Indexes on `operator_id` for performance

### 5.2 Application-Level Isolation

**FastAPI Middleware:**
```python
@app.middleware("http")
async def tenant_context_middleware(request: Request, call_next):
    # Extract operator_id from JWT or subdomain
    operator_id = get_operator_id_from_request(request)
    
    # Set in request state
    request.state.operator_id = operator_id
    
    # Set PostgreSQL session variable
    if db := request.state.db:
        db.execute(f"SET app.current_operator_id = {operator_id}")
    
    response = await call_next(request)
    return response
```

### 5.3 Resource Isolation

- **Connection Pooling:** Per-operator connection limits
- **Rate Limiting:** Per-operator API rate limits
- **Storage Quotas:** Per-operator data limits
- **Compute Limits:** Per-operator processing quotas

---

## 6. Local Development Strategy

### 6.1 Single-Instance Setup

**For Local Development:**
- **PostgreSQL:** Single instance, no replicas
- **MongoDB:** Single instance, no sharding
- **Redis:** Single instance, no cluster
- **Kafka:** Single broker, local Zookeeper/KRaft
- **Elasticsearch:** Single node
- **ClickHouse:** Single instance
- **MinIO:** Single instance, local storage

**Rationale:**
- Simpler setup for development
- Easier debugging
- Lower resource requirements
- Can run on single machine

### 6.2 Docker Compose Setup

All services run via Docker Compose for easy local development:
- One container per service
- Local networking between services
- Volume mounts for data persistence
- Environment variables for configuration

### 6.3 Caching Strategy

**Multi-Layer Caching:**
1. **Application Cache:** In-memory (Python dicts)
2. **Redis Cache:** Local Redis instance
3. **Database Query Cache:** PostgreSQL query cache

**Cache Invalidation:**
- Event-driven invalidation via Kafka
- TTL-based expiration
- Manual invalidation API

---

## 7. Data Consistency & Reliability

### 7.1 Consistency Models

- **Strong Consistency:** PostgreSQL for critical financial data (ACID)
- **Eventual Consistency:** MongoDB for dynamic attributes (acceptable)
- **Causal Consistency:** Event ordering via Kafka (guaranteed per partition)

### 7.2 Local Development Data Persistence

- **PostgreSQL:** Data directory mounted as volume
- **MongoDB:** Data directory mounted as volume
- **Redis:** RDB snapshots (optional)
- **Kafka:** Log directories mounted as volumes
- **Elasticsearch:** Data directory mounted as volume
- **ClickHouse:** Data directory mounted as volume

### 7.3 Backup Strategy (Local Development)

- **PostgreSQL:** Manual pg_dump or automated daily dumps
- **MongoDB:** Manual mongodump or automated daily dumps
- **Kafka:** Log retention (7 days default)
- **All Data:** Volume backups (Docker volumes)

**Note:** For production, implement proper backup strategies. For local development, volume persistence is sufficient.

---

## 8. Security & Compliance

### 8.1 Data Encryption

- **At Rest:** Database encryption (TDE)
- **In Transit:** TLS 1.3 for all connections
- **Application:** Encrypted sensitive fields

### 8.2 Access Control

- **Database:** Row-level security (PostgreSQL)
- **Application:** JWT-based authentication
- **API:** Rate limiting, API keys
- **Audit:** Complete audit trail

### 8.3 Compliance

- **GDPR:** Right to deletion, data portability
- **CCPA:** Data access, deletion
- **SOC 2:** Security controls
- **PCI DSS:** If handling payments

---

## 9. Monitoring & Observability (Local Development)

### 9.1 Database Monitoring

- **PostgreSQL:** pg_stat_statements, slow query log, pgAdmin
- **MongoDB:** MongoDB Compass, mongostat
- **Redis:** redis-cli INFO, RedisInsight
- **Kafka:** Kafka Manager / kafka-console-consumer
- **ClickHouse:** System tables, query log

### 9.2 Application Monitoring

- **Logging:** Structured logging (JSON) to stdout/files
- **Metrics:** Prometheus (optional, for advanced monitoring)
- **Tracing:** OpenTelemetry (optional, for distributed tracing)

### 9.3 Development Tools

- **Database GUIs:** pgAdmin, MongoDB Compass, RedisInsight
- **Kafka Tools:** Kafka Manager, kafkacat, Conduktor
- **API Testing:** Postman, Insomnia, FastAPI docs
- **Log Viewing:** Docker logs, local log files

---

## 10. Schema Evolution & Versioning

### 10.1 Event Schema Versioning

- **Event Contract Versioning:** Version events in Kafka topics
- **Backward Compatibility:** Support multiple event versions
- **Schema Registry:** Track operator event schemas
- **Data Transformation:** Transform during normalization (Kafka consumers)

### 10.2 Database Schema Migrations

- **PostgreSQL:** Alembic migrations for canonical schema
- **MongoDB:** No migrations needed (schema-less)
- **Elasticsearch:** Index versioning and reindexing

### 10.3 Operator Schema Evolution

- **Schema Registry:** Track operator-specific schemas
- **Version Support:** Support multiple schema versions per operator
- **Migration Tools:** Transform data during import/processing

---

## Conclusion

This polyglot persistence architecture provides:

1. **Schema Flexibility:** Operators define their own event schemas, no fixed columns
2. **Event-Driven:** Kafka as mandatory backbone - operators never write directly to databases
3. **Correctness:** PostgreSQL for financial/transactional data (ACID guarantees)
4. **Flexibility:** MongoDB for operator-specific dynamic attributes
5. **Real-time:** Redis for sub-200ms campaign decisions
6. **Search:** Elasticsearch for segmentation and filtering
7. **Analytics:** ClickHouse for high-volume aggregations

**Key Architectural Principle:**
> **Operators do not integrate with our database. They integrate with our event contract.**

Schemas evolve, events don't break, databases project. This architecture supports 10,000+ operators with millions of users while maintaining performance, correctness, and flexibility.

**Local Development Focus:**
- All services run locally via Docker Compose
- Single instances of each database (no clustering)
- Volume persistence for data
- Easy setup and teardown
