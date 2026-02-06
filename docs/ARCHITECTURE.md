# Architecture Documentation

## Overview

The Meta Ads Quality Control system is a hybrid architecture combining:
- **Python scripts** for automated Meta API interactions and analysis
- **Google Apps Script** for Google Sheets integration and automation
- **Google Sheets** for data storage, reporting, and dashboards
- **External integrations** (Email alerts, Meta Business Manager)

---

## System Architecture

```mermaid
graph TB
    subgraph "Meta Platform"
        MetaAds[Meta Ads Manager]
        MetaAPI[Meta Marketing API]
        BusinessManager[Meta Business Manager]
        Pixel[Meta Pixel]
    end

    subgraph "Python Scripts"
        QualityCheck[comprehensive_quality_check.py]
        DailyHealth[daily_health_check.py]
        MetaClient[_meta_api_client.py]
        SheetsWriter[_sheets_writer.py]
        EmailAlerts[_email_alerts.py]
        Utilities[_shared_utilities.py]
        Config[_config.py]
    end

    subgraph "Data Layer"
        Sheets[Google Sheets]
        LocalCache[Local Data Cache]
    end

    subgraph "Google Apps Script"
        GAS[MetaQualityControl.gs]
        SheetsTriggers[Time-based Triggers]
    end

    subgraph "Notifications"
        Email[Email Alerts]
        SheetUpdates[Sheet Updates]
    end

    subgraph "User Interfaces"
        CLI[Command Line]
        SheetsUI[Google Sheets UI]
        EmailClient[Email Client]
        MetaBusiness[Meta Business Suite]
    end

    %% Connections
    MetaClient -->|OAuth 2.0| MetaAPI
    MetaAPI -->|Fetch data| MetaAds
    MetaAPI -->|Event data| Pixel
    MetaClient -->|Process| QualityCheck
    MetaClient -->|Process| DailyHealth

    QualityCheck -->|Write| SheetsWriter
    DailyHealth -->|Write| SheetsWriter
    SheetsWriter -->|Batch update| Sheets

    EmailAlerts -->|SMTP/TLS| Email
    QualityCheck -->|Trigger| EmailAlerts
    DailyHealth -->|Trigger| EmailAlerts

    GAS -->|Read/Write| Sheets
    SheetsTriggers -->|Schedule| GAS
    GAS -->|Webhook| MetaClient

    CLI -->|Execute| QualityCheck
    CLI -->|Execute| DailyHealth
    SheetsUI -->|View/Edit| Sheets

    Utilities -->|Support| QualityCheck
    Utilities -->|Support| DailyHealth
    Config -->|Settings| MetaClient

    style MetaAds fill:#1877f2,color:#fff
    style MetaAPI fill:#0668e1,color:#fff
    style Python fill:#fbbc04,color:#000
    style Sheets fill:#0f9d58,color:#fff
    style Email fill:#ea4335,color:#fff
```

---

## Script Execution Flow

```mermaid
sequenceDiagram
    participant User
    participant Script
    participant MetaAPI as Meta Marketing API
    participant Sheets as Google Sheets
    participant Email
    participant Pixel as Meta Pixel

    User->>Script: Schedule/Trigger execution
    Script->>Script: Load .env configuration
    Script->>Script: Validate credentials

    Script->>MetaAPI: Authenticate (OAuth 2.0)
    MetaAPI-->>Script: Access token

    loop For each campaign
        Script->>MetaAPI: Fetch campaign data
        MetaAPI-->>Script: Campaign metrics
        Script->>MetaAPI: Fetch ad set data
        MetaAPI-->>Script: Ad set metrics
        Script->>MetaAPI: Fetch ad creative data
        MetaAPI-->>Script: Creative performance
        Script->>MetaAPI: Fetch audience data
        MetaAPI-->>Script: Audience insights
    end

    Script->>MetaAPI: Fetch conversion events
    MetaAPI-->>Pixel: Check pixel status
    Pixel-->>MetaAPI: Event data
    MetaAPI-->>Script: Conversion tracking data

    Script->>Script: Calculate health score
    Script->>Script: Detect anomalies
    Script->>Script: Identify issues
    Script->>Script: Generate recommendations

    Script->>Sheets: Batch write results
    Sheets-->>Script: Confirmation

    alt Critical issues found
        Script->>Email: Send priority alert
        Email-->>User: Immediate notification
    else Warning issues found
        Script->>Email: Send daily digest
        Email-->>User: Summary notification
    else No issues
        Script->>Sheets: Update dashboard only
    end

    Script-->>User: Execution complete with summary
```

---

## Data Flow Diagram

```mermaid
flowchart TB
    subgraph Sources["Data Sources"]
        A1[Campaigns]
        A2[Ad Sets]
        A3[Ad Creatives]
        A4[Audiences]
        A5[Conversion Events]
        A6[Meta Pixel]
    end

    subgraph Collection["Data Collection"]
        B1[Meta API Client]
        B2[Rate Limiting]
        B3[Error Handling]
        B4[Data Validation]
    end

    subgraph Processing["Data Processing"]
        C1[Metric Calculation]
        C2[Budget Pacing Analysis]
        C3[Anomaly Detection]
        C4[Creative Fatigue Check]
        C5[Audience Quality Score]
        C6[Health Score Calculation]
    end

    subgraph Analysis["Quality Analysis"]
        D1[Campaign Structure]
        D2[Targeting Quality]
        D3[Creative Performance]
        D4[Conversion Tracking]
        D5[Budget Efficiency]
    end

    subgraph Storage["Data Storage"]
        E1[Google Sheets Dashboard]
        E2[Historical Data]
        E3[Issues Log]
    end

    subgraph Actions["Actions & Alerts"]
        F1[Email Notifications]
        F2[Sheet Formatting]
        F3[Trend Visualization]
    end

    A1 --> B1
    A2 --> B1
    A3 --> B1
    A4 --> B1
    A5 --> B1
    A6 --> B1

    B1 --> B2
    B2 --> B3
    B3 --> B4

    B4 --> C1
    B4 --> C2
    B4 --> C3
    B4 --> C4
    B4 --> C5

    C1 --> C6
    C2 --> C6
    C3 --> C6
    C4 --> C6
    C5 --> C6

    C6 --> D1
    C6 --> D2
    C6 --> D3
    C6 --> D4
    C6 --> D5

    D1 --> E1
    D2 --> E1
    D3 --> E1
    D4 --> E1
    D5 --> E1

    E1 --> E2
    E1 --> E3

    E1 --> F1
    E1 --> F2
    E2 --> F3

    style B1 fill:#1877f2,color:#fff
    style C6 fill:#fbbc04,color:#000
    style E1 fill:#0f9d58,color:#fff
    style F1 fill:#ea4335,color:#fff
```

---

## Component Architecture

```mermaid
graph TD
    subgraph "Core Components"
        Config[_config.py<br/>Configuration Manager]
        Utilities[_shared_utilities.py<br/>Common Functions]
        MetaClient[_meta_api_client.py<br/>API Interface]
    end

    subgraph "Quality Control Scripts"
        DailyHealth[daily_health_check.py<br/>Daily Monitoring]
        Comprehensive[comprehensive_quality_check.py<br/>Full Audit]
    end

    subgraph "Output Components"
        SheetsWriter[_sheets_writer.py<br/>Sheet Export]
        EmailAlerts[_email_alerts.py<br/>Email System]
    end

    subgraph "External APIs"
        MetaAPI[Meta Marketing API<br/>v19.0+]
        SheetsAPI[Google Sheets API<br/>v4]
        SMTPAPI[SMTP Server<br/>Email Delivery]
    end

    subgraph "Data Storage"
        GoogleSheets[Google Sheets<br/>Reports & Dashboards]
        Logs[Log Files<br/>Execution History]
    end

    subgraph "Utility Functions"
        CalcCPA[calculate_cpa]
        CalcROAS[calculate_roas]
        BudgetPacing[calculate_budget_pacing]
        AnomalyDetect[detect_anomaly]
        ExtractMetrics[extract_metric_from_actions]
    end

    %% Dependencies
    Config -.loads.-> DailyHealth
    Config -.loads.-> Comprehensive

    Utilities -.uses.-> DailyHealth
    Utilities -.uses.-> Comprehensive

    MetaClient -.uses.-> DailyHealth
    MetaClient -.uses.-> Comprehensive

    DailyHealth -->|writes| SheetsWriter
    DailyHealth -->|alerts| EmailAlerts
    Comprehensive -->|writes| SheetsWriter
    Comprehensive -->|alerts| EmailAlerts

    MetaClient -->|calls| MetaAPI
    SheetsWriter -->|calls| SheetsAPI
    EmailAlerts -->|calls| SMTPAPI

    SheetsWriter -->|updates| GoogleSheets
    DailyHealth -->|logs| Logs
    Comprehensive -->|logs| Logs

    Utilities -->|contains| CalcCPA
    Utilities -->|contains| CalcROAS
    Utilities -->|contains| BudgetPacing
    Utilities -->|contains| AnomalyDetect
    Utilities -->|contains| ExtractMetrics

    style Config fill:#4285f4,color:#fff
    style MetaClient fill:#1877f2,color:#fff
    style Utilities fill:#fbbc04,color:#000
    style SheetsWriter fill:#0f9d58,color:#fff
    style EmailAlerts fill:#ea4335,color:#fff
```

---

## Health Scoring System

```mermaid
flowchart TD
    Start([Meta Account Data]) --> Fetch[Fetch Complete Data]

    Fetch --> AccountSetup[Account Setup<br/>Weight: 15%]
    Fetch --> CampaignStruct[Campaign Structure<br/>Weight: 20%]
    Fetch --> CreativeHealth[Creative Health<br/>Weight: 25%]
    Fetch --> AudienceQual[Audience Quality<br/>Weight: 15%]
    Fetch --> ConvTrack[Conversion Tracking<br/>Weight: 15%]
    Fetch --> Performance[Performance<br/>Weight: 10%]

    AccountSetup --> Check1{Pixel Installed?}
    Check1 -->|Yes +5| Score1[5 points]
    Check1 -->|No| Score1b[0 points]

    AccountSetup --> Check2{Domain Verified?}
    Check2 -->|Yes +5| Score2[5 points]
    Check2 -->|No| Score2b[0 points]

    AccountSetup --> Check3{iOS14 Setup?}
    Check3 -->|Yes +5| Score3[5 points]
    Check3 -->|No| Score3b[0 points]

    Score1 --> Norm1[Normalize to 15]
    Score1b --> Norm1
    Score2 --> Norm1
    Score2b --> Norm1
    Score3 --> Norm1
    Score3b --> Norm1

    CampaignStruct --> Check4{Naming Convention?}
    CampaignStruct --> Check5{Budget Setup?}
    CampaignStruct --> Check6{Objectives Clear?}
    Check4 --> Norm2[Normalize to 20]
    Check5 --> Norm2
    Check6 --> Norm2

    CreativeHealth --> Check7{Frequency < 2.5?}
    CreativeHealth --> Check8{CTR Above Avg?}
    CreativeHealth --> Check9{Creative Variety?}
    CreativeHealth --> Check10{Format Mix?}
    Check7 --> Norm3[Normalize to 25]
    Check8 --> Norm3
    Check9 --> Norm3
    Check10 --> Norm3

    AudienceQual --> Check11{Audience Size OK?}
    AudienceQual --> Check12{No Overlap?}
    AudienceQual --> Check13{Not Exhausted?}
    Check11 --> Norm4[Normalize to 15]
    Check12 --> Norm4
    Check13 --> Norm4

    ConvTrack --> Check14{Events Firing?}
    ConvTrack --> Check15{Match Quality > 7?}
    ConvTrack --> Check16{CAPI Connected?}
    Check14 --> Norm5[Normalize to 15]
    Check15 --> Norm5
    Check16 --> Norm5

    Performance --> Check17{Meeting CPA Target?}
    Performance --> Check18{ROAS Above 2?}
    Check17 --> Norm6[Normalize to 10]
    Check18 --> Norm6

    Norm1 --> Sum[Sum All Components]
    Norm2 --> Sum
    Norm3 --> Sum
    Norm4 --> Sum
    Norm5 --> Sum
    Norm6 --> Sum

    Sum --> FinalScore[Final Health Score<br/>0-100]

    FinalScore --> Grade{Assign Grade}
    Grade -->|90-100| A[Grade A: Optimal<br/>Account health excellent]
    Grade -->|80-89| B[Grade B: Good<br/>Minor issues only]
    Grade -->|70-79| C[Grade C: Fair<br/>Several items need attention]
    Grade -->|60-69| D[Grade D: Poor<br/>Multiple problems]
    Grade -->|0-59| F[Grade F: Critical<br/>Immediate action required]

    style FinalScore fill:#fbbc04,color:#000
    style A fill:#0f9d58,color:#fff
    style B fill:#8bc34a,color:#000
    style C fill:#ffc107,color:#000
    style D fill:#ff9800,color:#000
    style F fill:#ea4335,color:#fff
```

---

## Alert Priority System

```mermaid
graph TD
    Issue[Issue Detected] --> Classify{Classify<br/>Severity}

    Classify -->|Pixel not firing| Critical
    Classify -->|Campaign paused| Critical
    Classify -->|Zero spend| Critical
    Classify -->|Budget exhausted| Critical
    Classify -->|Conversion tracking broken| Critical

    Classify -->|High frequency >3.5| High
    Classify -->|CPA 50% over target| High
    Classify -->|Creative fatigue| High
    Classify -->|Audience exhaustion| High
    Classify -->|Low match quality <6| High

    Classify -->|Frequency 2.5-3.5| Medium
    Classify -->|CPA 25% over target| Medium
    Classify -->|Audience overlap| Medium
    Classify -->|CTR decline 30%| Medium
    Classify -->|Budget pacing off| Medium

    Classify -->|Naming convention| Low
    Classify -->|Optimization opportunity| Low
    Classify -->|Missing UTM tags| Low
    Classify -->|Creative refresh suggested| Low

    Critical[Critical Priority<br/>Immediate Action] --> Email1[🔴 Immediate Email<br/>Subject: URGENT]
    Critical --> Slack1[🔴 Slack Alert<br/>@channel mention]
    Critical --> Dashboard1[🔴 Dashboard: Red Banner]
    Critical --> SMS1[📱 SMS Alert<br/>If configured]

    High[High Priority<br/>Same Day Action] --> Email2[🟠 Priority Email<br/>Subject: HIGH PRIORITY]
    High --> Dashboard2[🟠 Dashboard: Orange Alert]
    High --> Digest2[📊 Include in digest]

    Medium[Medium Priority<br/>This Week Action] --> Email3[🟡 Weekly Summary<br/>Consolidated report]
    Medium --> Dashboard3[🟡 Dashboard: Yellow Warning]
    Medium --> Tracking3[📈 Trend tracking]

    Low[Low Priority<br/>FYI / Nice to Have] --> Dashboard4[🟢 Dashboard Only<br/>No alerts]
    Low --> Report4[📄 Monthly report mention]

    style Critical fill:#ea4335,color:#fff
    style High fill:#ff6600,color:#fff
    style Medium fill:#fbbc04,color:#000
    style Low fill:#0f9d58,color:#fff
```

---

## Deployment Architecture

```mermaid
graph TB
    subgraph "Development Environment"
        Dev[Local Development<br/>VS Code/PyCharm]
        Git[GitHub Repository<br/>Version Control]
        Tests[Pytest Suite<br/>28 Unit Tests]
    end

    subgraph "Deployment Options"
        Local[Local Machine<br/>Windows/Mac/Linux]
        Cloud[Cloud Server<br/>AWS/GCP/Azure]
        Docker[Docker Container<br/>Containerized]
        Serverless[Serverless Functions<br/>Lambda/Cloud Functions]
    end

    subgraph "Scheduling"
        Cron[Cron Jobs<br/>Unix/Linux]
        TaskScheduler[Task Scheduler<br/>Windows]
        CloudScheduler[Cloud Scheduler<br/>GCP/AWS EventBridge]
        Airflow[Apache Airflow<br/>Workflow Orchestration]
    end

    subgraph "Python Execution"
        Venv[Virtual Environment<br/>Python 3.8+]
        PythonScripts[Python Scripts]
        Dependencies[Requirements.txt<br/>13 packages]
    end

    subgraph "Data Destinations"
        Sheets[Google Sheets<br/>Live Dashboard]
        EmailSMTP[Email via SMTP<br/>Gmail/SendGrid]
        Logs[Log Files<br/>Rotated daily]
    end

    subgraph "External Services"
        MetaAPI[Meta Marketing API<br/>OAuth 2.0]
        SheetsAPI[Google Sheets API<br/>Service Account]
        MetaBusiness[Meta Business Manager<br/>System User]
    end

    Dev -->|git push| Git
    Tests -->|validate| Dev

    Git -->|deploy| Local
    Git -->|deploy| Cloud
    Git -->|build| Docker
    Git -->|package| Serverless

    Local --> Cron
    Local --> TaskScheduler
    Cloud --> Cron
    Cloud --> CloudScheduler
    Docker --> CloudScheduler
    Serverless --> CloudScheduler
    Cloud --> Airflow

    Cron -->|execute| Venv
    TaskScheduler -->|execute| Venv
    CloudScheduler -->|execute| Venv
    Airflow -->|orchestrate| Venv

    Venv --> Dependencies
    Dependencies --> PythonScripts

    PythonScripts -->|OAuth| MetaAPI
    PythonScripts -->|Service Account| SheetsAPI
    MetaAPI --> MetaBusiness

    PythonScripts -->|write| Sheets
    PythonScripts -->|send| EmailSMTP
    PythonScripts -->|append| Logs

    style Git fill:#f05032,color:#fff
    style Docker fill:#2496ed,color:#fff
    style Cloud fill:#4285f4,color:#fff
    style Sheets fill:#0f9d58,color:#fff
```

---

## Security Architecture

```mermaid
flowchart TD
    subgraph "Authentication Layer"
        OAuth[OAuth 2.0<br/>Meta Authentication]
        ServiceAccount[Service Account<br/>Google Sheets]
        SMTP[SMTP Credentials<br/>Email Alerts]
    end

    subgraph "Secrets Management"
        EnvFile[.env File<br/>Local Development]
        EnvVars[Environment Variables<br/>Production]
        SecretsManager[Secrets Manager<br/>AWS/GCP Optional]
    end

    subgraph "Application Layer"
        ConfigModule[_config.py<br/>Credential Loader]
        ValidationModule[Validation Layer<br/>Input Sanitization]
        Scripts[Python Scripts<br/>Read-Only Access]
    end

    subgraph "Network Security"
        HTTPS[HTTPS/TLS<br/>All API Calls]
        RateLimiting[Rate Limiting<br/>200 calls/hour]
        RetryLogic[Retry with Backoff<br/>Exponential]
    end

    subgraph "Data Protection"
        NoLocalStorage[No Persistent Local Storage<br/>In-memory only]
        SecureSheets[Google Sheets Access Control<br/>Service account only]
        LogSanitization[Log Sanitization<br/>No tokens in logs]
        DataMinimization[Data Minimization<br/>Fetch only required fields]
    end

    subgraph "Access Control"
        SystemUser[Meta System User<br/>ads_read permission]
        SheetPermissions[Sheet Permissions<br/>Editor access only]
        EmailRestricted[Email Recipients<br/>Whitelist only]
    end

    OAuth -->|Stored in| EnvFile
    OAuth -->|Or stored in| EnvVars
    OAuth -->|Or stored in| SecretsManager

    ServiceAccount -->|Stored in| EnvFile
    ServiceAccount -->|Or stored in| EnvVars
    ServiceAccount -->|Or stored in| SecretsManager

    SMTP -->|Stored in| EnvFile
    SMTP -->|Or stored in| EnvVars

    EnvFile -->|Loaded by| ConfigModule
    EnvVars -->|Loaded by| ConfigModule
    SecretsManager -->|Fetched by| ConfigModule

    ConfigModule -->|Provides credentials| Scripts
    ValidationModule -->|Sanitizes inputs| Scripts

    Scripts -->|Calls via| HTTPS
    HTTPS -->|Respects| RateLimiting
    HTTPS -->|Uses| RetryLogic

    Scripts -->|Implements| NoLocalStorage
    Scripts -->|Writes to| SecureSheets
    Scripts -->|Applies| LogSanitization
    Scripts -->|Follows| DataMinimization

    Scripts -->|Authenticates as| SystemUser
    Scripts -->|Uses| SheetPermissions
    Scripts -->|Sends to| EmailRestricted

    style OAuth fill:#34a853,color:#fff
    style HTTPS fill:#4285f4,color:#fff
    style NoLocalStorage fill:#0f9d58,color:#fff
    style SystemUser fill:#1877f2,color:#fff
```

---

## Performance Considerations

### API Limits

| Resource | Limit | Optimization Strategy |
|----------|-------|----------------------|
| **Meta API Calls** | 200/hour (standard tier) | Batch requests, cache data 1 hour |
| **Meta API Response Size** | 100 records/call | Use pagination, fetch in chunks |
| **Google Sheets API** | 500 requests/100sec/project | Batch writes (100+ rows), use append |
| **Email SMTP** | Varies by provider | Consolidate alerts, use digest mode |
| **Script Execution Time** | 15 min (Lambda timeout) | Split large accounts, parallel processing |

### Optimization Strategies

```mermaid
graph LR
    subgraph "Data Fetching"
        A1[Selective Fields<br/>fields=id,name,status]
        A2[Batch Requests<br/>Multiple IDs per call]
        A3[Parallel Calls<br/>async/await]
    end

    subgraph "Data Processing"
        B1[In-Memory Cache<br/>1 hour TTL]
        B2[Pandas Optimization<br/>Vectorized operations]
        B3[Early Exit<br/>Skip disabled campaigns]
    end

    subgraph "Data Writing"
        C1[Batch Sheet Writes<br/>100+ rows at once]
        C2[Conditional Updates<br/>Only changed data]
        C3[Async Writes<br/>Non-blocking operations]
    end

    A1 --> B1
    A2 --> B2
    A3 --> B3

    B1 --> C1
    B2 --> C2
    B3 --> C3

    style A1 fill:#1877f2,color:#fff
    style B1 fill:#fbbc04,color:#000
    style C1 fill:#0f9d58,color:#fff
```

---

## Monitoring & Observability

```mermaid
flowchart TD
    subgraph "Execution Monitoring"
        StartTime[Script Start Time]
        Duration[Execution Duration]
        Success[Success/Failure Status]
        ErrorCount[Error Count]
    end

    subgraph "API Monitoring"
        APICalls[API Calls Made]
        APIErrors[API Error Rate]
        RateLimit[Rate Limit Status]
        ResponseTime[API Response Time]
    end

    subgraph "Data Quality"
        RecordsProcessed[Records Processed]
        DataCompleteness[Data Completeness %]
        ValidationErrors[Validation Errors]
        AnomaliesDetected[Anomalies Found]
    end

    subgraph "Output Tracking"
        SheetsUpdated[Sheets Updated]
        EmailsSent[Emails Sent]
        IssuesLogged[Issues Logged]
    end

    subgraph "Logging Destinations"
        LocalLogs[Local Log Files<br/>logs/*.log]
        CloudWatch[CloudWatch Logs<br/>AWS]
        StackDriver[Cloud Logging<br/>GCP]
        Sentry[Sentry<br/>Error Tracking]
    end

    StartTime --> LocalLogs
    Duration --> LocalLogs
    Success --> LocalLogs
    ErrorCount --> LocalLogs

    APICalls --> LocalLogs
    APIErrors --> Sentry
    RateLimit --> LocalLogs
    ResponseTime --> LocalLogs

    RecordsProcessed --> LocalLogs
    DataCompleteness --> LocalLogs
    ValidationErrors --> Sentry
    AnomaliesDetected --> LocalLogs

    SheetsUpdated --> LocalLogs
    EmailsSent --> LocalLogs
    IssuesLogged --> LocalLogs

    LocalLogs -->|Stream| CloudWatch
    LocalLogs -->|Stream| StackDriver

    style LocalLogs fill:#fbbc04,color:#000
    style Sentry fill:#ea4335,color:#fff
    style CloudWatch fill:#ff9900,color:#000
```

---

## Technology Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Language** | Python | 3.9+ | Core scripting language |
| **Meta API** | facebook-business SDK | Latest | Meta Marketing API client |
| **Google Sheets** | gspread + google-auth | Latest | Sheets API integration |
| **Data Processing** | pandas | 2.0+ | Data manipulation |
| **HTTP Client** | requests | 2.31+ | API calls |
| **Configuration** | python-dotenv | 1.0+ | Environment management |
| **Logging** | loguru | 0.7+ | Structured logging |
| **Testing** | pytest | 9.0+ | Unit testing framework |
| **Email** | smtplib | Built-in | Email delivery |
| **Scheduling** | cron / Task Scheduler / CloudScheduler | - | Automation |
| **Version Control** | Git/GitHub | - | Source control |
| **Container** | Docker (optional) | 24+ | Containerization |

---

## N8N Workflow Sync Pipeline

This repo automatically syncs quality check logic to the [N8N-meta-ads-quality-control](https://github.com/Empire-Amplify/N8N-meta-ads-quality-control) repo for use as an importable n8n workflow.

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant Source as meta-ads-quality-control
    participant GHA as GitHub Actions
    participant N8N as N8N-meta-ads-quality-control

    Dev->>Source: Push to master
    Source->>GHA: lint.yml triggers
    GHA->>GHA: Run lint + test jobs
    GHA->>N8N: repository_dispatch (source-updated)
    Note over GHA,N8N: Uses N8N_SYNC_TOKEN secret

    N8N->>GHA: sync-workflows.yml triggers
    GHA->>Source: Checkout source repo
    GHA->>N8N: Checkout N8N repo
    GHA->>GHA: Run sync_from_source.py
    Note over GHA: Extract config from _config.py<br/>Inject JS logic into workflow JSON

    GHA->>GHA: Run validate_n8n_workflows.py
    Note over GHA: Validate JSON structure<br/>Check node connections<br/>Verify $('NodeName') refs

    GHA->>N8N: Commit & push changes
```

### Sync Components

| Component | Location | Purpose |
|-----------|----------|---------|
| `lint.yml` (notify-n8n job) | `.github/workflows/lint.yml` | Triggers dispatch after CI passes |
| `sync-workflows.yml` | N8N repo `.github/workflows/` | Orchestrates the sync process |
| `sync_from_source.py` | N8N repo root | Extracts config, injects JS logic |
| `validate_n8n_workflows.py` | N8N repo root | Validates workflow JSON integrity |
| `meta_quality_analysis.js` | N8N repo `logic/` | JS quality engine (injected into workflow) |

### Config Extraction

The sync script uses regex to extract 22 configuration values from `scripts/_config.py` and injects them as a `SOURCE_CONFIG` object into the n8n Code node. This ensures threshold values (frequency alerts, CPA limits, ROAS minimums, audience sizes) stay in sync.

---

## Future Architecture Enhancements

```mermaid
graph LR
    Current[Current Architecture<br/>v1.0] --> Phase1[Phase 1: Advanced Analytics<br/>Q2 2026]
    Phase1 --> Phase2[Phase 2: Auto-Remediation<br/>Q3 2026]
    Phase2 --> Phase3[Phase 3: ML Integration<br/>Q4 2026]
    Phase3 --> Phase4[Phase 4: Multi-Platform<br/>2027]

    Phase1 --> F1[Creative Fatigue Prediction<br/>ML model]
    Phase1 --> F2[Performance Forecasting<br/>Time series analysis]
    Phase1 --> F3[Looker Studio Integration<br/>Live dashboards]

    Phase2 --> F4[Auto Budget Shifting<br/>Based on performance]
    Phase2 --> F5[Auto Pause/Enable<br/>Rule-based actions]
    Phase2 --> F6[Smart Bidding Adjustments<br/>Real-time optimization]

    Phase3 --> F7[Anomaly Detection AI<br/>Neural networks]
    Phase3 --> F8[Audience Recommendations<br/>Lookalike optimization]
    Phase3 --> F9[Creative Optimization AI<br/>Image/text analysis]

    Phase4 --> F10[Google Ads Support<br/>Unified platform]
    Phase4 --> F11[TikTok Ads Support<br/>Cross-platform]
    Phase4 --> F12[LinkedIn Ads Support<br/>B2B integration]

    style Current fill:#0f9d58,color:#fff
    style Phase1 fill:#fbbc04,color:#000
    style Phase2 fill:#ff9800,color:#000
    style Phase3 fill:#ea4335,color:#fff
    style Phase4 fill:#9c27b0,color:#fff
```

### Planned Features Roadmap

**Q2 2026 - Advanced Analytics**
- [ ] Creative fatigue prediction using ML
- [ ] Performance forecasting (30-day projections)
- [ ] Looker Studio dashboard templates
- [ ] Advanced audience overlap analysis
- [ ] Competitor spend tracking (via partner data)

**Q3 2026 - Auto-Remediation**
- [ ] Automatic budget reallocation (preview mode)
- [ ] Auto-pause underperforming ads (configurable thresholds)
- [ ] Smart bidding recommendations
- [ ] Automated creative refresh suggestions
- [ ] Budget pacing auto-adjustments

**Q4 2026 - Machine Learning**
- [ ] Neural network-based anomaly detection
- [ ] Lookalike audience recommendations
- [ ] Creative optimization AI (image + text analysis)
- [ ] Conversion prediction models
- [ ] Churn risk prediction

**2027 - Multi-Platform Expansion**
- [ ] Google Ads quality control integration
- [ ] TikTok Ads support
- [ ] LinkedIn Ads support
- [ ] Unified cross-platform dashboard
- [ ] Cross-platform budget optimization
- [ ] Mobile app for alerts and monitoring

---

## Testing Architecture

```mermaid
graph TD
    subgraph "Unit Tests"
        UT1[test_shared_utilities.py<br/>28 tests]
        UT2[Future: test_meta_api_client.py]
        UT3[Future: test_sheets_writer.py]
    end

    subgraph "Integration Tests"
        IT1[Future: Meta API integration]
        IT2[Future: Sheets API integration]
        IT3[Future: Email delivery tests]
    end

    subgraph "End-to-End Tests"
        E2E1[Future: Full daily health check]
        E2E2[Future: Full quality audit]
    end

    subgraph "Test Coverage"
        COV1[Current: Core utilities<br/>100% coverage]
        COV2[Target: 80%+ overall]
    end

    subgraph "CI/CD"
        CI1[GitHub Actions<br/>On push/PR]
        CI2[pytest execution]
        CI3[Coverage reporting]
    end

    UT1 --> COV1
    UT2 --> COV2
    UT3 --> COV2

    IT1 --> COV2
    IT2 --> COV2
    IT3 --> COV2

    E2E1 --> COV2
    E2E2 --> COV2

    COV1 --> CI1
    COV2 --> CI1
    CI1 --> CI2
    CI2 --> CI3

    style UT1 fill:#0f9d58,color:#fff
    style COV1 fill:#4285f4,color:#fff
    style CI1 fill:#fbbc04,color:#000
```

**Current Test Status:**
- ✅ 28/28 unit tests passing (100%)
- ✅ Core utility functions tested
- ⚠️ Integration tests needed
- ⚠️ E2E tests needed

---

## Documentation

For implementation details and guides:
- [README.md](../README.md) - Getting started and overview
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Detailed setup instructions (coming soon)
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution guidelines
- [SECURITY.md](../SECURITY.md) - Security policy and best practices
- [CHANGELOG.md](../CHANGELOG.md) - Version history

---

**Last Updated:** February 6, 2026
**Version:** 1.0.0
**Maintained By:** Gordon Geraghty | Empire Amplify
