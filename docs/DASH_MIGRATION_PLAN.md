# Dash Migration Plan: ART Call Center Solution
## Comprehensive Phase-by-Phase Migration Strategy

---

## Executive Summary

**Current State:** Streamlit-based dashboard with 3 main components:
- Agent Dashboard (Live Call Assist)
- Analytics Dashboard  
- Supervisor Dashboard

**Target State:** Dash-based application with improved reactivity control, better state management, and no HTML corruption issues.

**Estimated Timeline:** 6-8 weeks (with testing)

**Risk Level:** Medium-High (significant refactoring required)

---

## Phase 0: Preparation & Setup (Week 1)

### Objectives
- Set up Dash development environment
- Create parallel codebase structure
- Establish testing framework
- Map Streamlit → Dash component equivalents

### Tasks

#### 0.1 Environment Setup
- [ ] Install Dash and dependencies (`dash`, `dash-bootstrap-components`, `dash-core-components`)
- [ ] Create new directory structure: `app_dash/`
- [ ] Set up virtual environment for Dash development
- [ ] Create `requirements_dash.txt` with Dash dependencies

#### 0.2 Component Mapping Document
- [ ] Document Streamlit → Dash equivalents:
  - `st.columns()` → `dbc.Row()` + `dbc.Col()`
  - `st.sidebar` → `dbc.Offcanvas()` or separate layout
  - `st.tabs()` → `dbc.Tabs()`
  - `st.button()` → `dbc.Button()` with `n_clicks` callback
  - `st.text_input()` → `dcc.Input()` with `value` callback
  - `st.selectbox()` → `dcc.Dropdown()`
  - `st.radio()` → `dbc.RadioItems()`
  - `st.markdown()` → `html.Div()` with `dangerously_allow_html=True`
  - `st.empty()` → `html.Div()` with `id` for callbacks
  - `st.cache_data()` → `@lru_cache` or manual caching
  - `st.session_state` → `dash.callback_context` + `dcc.Store()`

#### 0.3 Testing Framework
- [ ] Set up pytest for Dash app testing
- [ ] Create test fixtures for mock Databricks clients
- [ ] Create test data fixtures (sample transcripts, KB articles)
- [ ] Set up integration test structure

#### 0.4 Architecture Design
- [ ] Design callback structure (minimize callback chains)
- [ ] Plan state management strategy (`dcc.Store` components)
- [ ] Design component hierarchy
- [ ] Plan caching strategy (client-side vs server-side)

### Deliverables
- ✅ Dash development environment ready
- ✅ Component mapping document
- ✅ Test framework setup
- ✅ Architecture design document

### Testing
- [ ] Verify Dash app can run on `localhost:8050`
- [ ] Test basic callback functionality
- [ ] Verify Databricks SDK integration works

---

## Phase 1: Core Infrastructure (Week 2)

### Objectives
- Build base Dash app structure
- Implement authentication/connection handling
- Create reusable components
- Set up state management

### Tasks

#### 1.1 Base App Structure
- [ ] Create `app_dash/app.py` with Dash app initialization
- [ ] Set up Bootstrap theme (ART branding colors)
- [ ] Create layout skeleton (header, sidebar, main content)
- [ ] Implement navigation structure

#### 1.2 Databricks Integration Layer
- [ ] Create `app_dash/utils/databricks_client.py`:
  - Wrap WorkspaceClient initialization
  - Create cached connection functions
  - Error handling wrapper
- [ ] Create `app_dash/utils/sql_executor.py`:
  - SQL query execution with caching
  - Result formatting
  - Error handling

#### 1.3 State Management
- [ ] Create `app_dash/components/stores.py`:
  - `dcc.Store` components for:
    - `selected_call_id`
    - `transcript_data`
    - `kb_results`
    - `suggestion_data`
    - `compliance_alerts`
    - `member_context`
- [ ] Create state update utilities

#### 1.4 Reusable Components
- [ ] Create `app_dash/components/common.py`:
  - `CallCard()` - Call selection component
  - `StatusIndicator()` - Online/offline status
  - `LoadingSpinner()` - Loading states
  - `ErrorAlert()` - Error display
- [ ] Create `app_dash/components/transcript.py`:
  - `TranscriptBubble()` - Individual message bubble
  - `TranscriptContainer()` - Full transcript display

### Deliverables
- ✅ Base Dash app running
- ✅ Databricks integration working
- ✅ State management structure
- ✅ Reusable component library

### Testing
- [ ] Unit tests for Databricks client wrapper
- [ ] Unit tests for SQL executor
- [ ] Integration test: App loads and connects to Databricks
- [ ] Test state management (Store components)

---

## Phase 2: Sidebar & Call Selection (Week 2-3)

### Objectives
- Migrate sidebar functionality
- Implement call selection dropdown
- Add call info display

### Tasks

#### 2.1 Sidebar Component
- [ ] Create `app_dash/components/sidebar.py`:
  - Call selection dropdown
  - Call info display (Member, Scenario, Utterances)
  - Status indicator
  - System online/offline status
- [ ] Implement `dbc.Offcanvas` for mobile responsiveness

#### 2.2 Call Selection Logic
- [ ] Create callback: `update_active_calls()`
  - Input: `interval` component (auto-refresh)
  - Output: `dropdown options` + `call_info display`
  - Cache: 10 second TTL
- [ ] Create callback: `on_call_selection()`
  - Input: `dropdown value`
  - Output: Update `selected_call_id` Store
  - Trigger: Transcript fetch, context fetch

#### 2.3 Call Info Display
- [ ] Display selected call metadata
- [ ] Format member name, scenario, utterance count
- [ ] Add visual indicators

### Deliverables
- ✅ Sidebar component functional
- ✅ Call selection working
- ✅ Call info displays correctly

### Testing
- [ ] Test call dropdown populates with active calls
- [ ] Test call selection updates state
- [ ] Test auto-refresh (interval component)
- [ ] Test error handling (no calls available)
- [ ] Visual regression test: Sidebar matches Streamlit version

---

## Phase 3: Live Transcript Display (Week 3)

### Objectives
- Migrate live transcript display
- Implement real-time updates
- Add sentiment indicators
- Preserve formatting and styling

### Tasks

#### 3.1 Transcript Fetching
- [ ] Create callback: `fetch_transcript()`
  - Input: `selected_call_id` Store
  - Output: `transcript_data` Store
  - Cache: 5 second TTL
  - Prevent: Only fetch when `call_id` changes

#### 3.2 Transcript Display Component
- [ ] Create `app_dash/components/transcript_display.py`:
  - `TranscriptBubble()` for each message
  - Speaker icons (customer/agent)
  - Sentiment emojis
  - Timestamp formatting
  - CSS styling (match Streamlit version)

#### 3.3 Real-time Updates
- [ ] Add `dcc.Interval` component (5 second refresh)
- [ ] Create callback: `update_transcript()`
  - Input: `interval` + `selected_call_id`
  - Output: `transcript_display` children
  - Prevent: Only update if call_id hasn't changed

#### 3.4 Conditional Rendering
- [ ] Implement smart caching:
  - Use cached transcript during KB interactions
  - Fetch fresh when call_id changes
  - Prevent unnecessary rerenders

### Deliverables
- ✅ Transcript displays correctly
- ✅ Real-time updates working
- ✅ Styling matches Streamlit version
- ✅ No unnecessary rerenders

### Testing
- [ ] Test transcript fetches on call selection
- [ ] Test transcript updates on interval
- [ ] Test caching prevents unnecessary fetches
- [ ] Test transcript formatting (HTML rendering)
- [ ] Test empty state (no transcript)
- [ ] Performance test: Multiple rapid call switches
- [ ] Visual regression test: Transcript matches Streamlit

---

## Phase 4: AI Assistant - Suggestions Tab (Week 4)

### Objectives
- Migrate AI suggestion functionality
- Implement async LLM calls
- Fix HTML formatting issues
- Add response time display

### Tasks

#### 4.1 Suggestion Button & State
- [ ] Create `app_dash/components/ai_suggestions.py`:
  - "Get AI Suggestion" button
  - Loading indicator
  - Error display
  - Suggestion display area
- [ ] Create `suggestion_state` Store:
  - `loading`, `error`, `suggestion_text`, `response_time`

#### 4.2 Heuristic Suggestion (Instant)
- [ ] Create callback: `get_heuristic_suggestion()`
  - Input: Button `n_clicks` + `selected_call_id`
  - Output: Display heuristic immediately
  - No LLM call (fast)

#### 4.3 LLM Suggestion (Async)
- [ ] Create callback: `get_llm_suggestion()`
  - Input: `suggestion_trigger` Store
  - Output: Update `suggestion_state` Store
  - Background: Use `dash.callback_context` to prevent blocking
  - Cache: Store formatted HTML separately

#### 4.4 HTML Formatting
- [ ] Create `app_dash/utils/html_formatter.py`:
  - Port `format_suggestion_text()` function
  - Fix HTML structure issues
  - Cache formatted versions
  - Validate HTML before rendering

#### 4.5 Display Component
- [ ] Create callback: `render_suggestion()`
  - Input: `suggestion_state` Store
  - Output: `suggestion_display` children
  - Format: Use `dangerously_allow_html=True`
  - Cache: Store formatted HTML in Store

### Deliverables
- ✅ AI suggestions working
- ✅ HTML formatting correct
- ✅ Response time displayed
- ✅ No HTML corruption on tab switches

### Testing
- [ ] Test heuristic suggestion displays instantly
- [ ] Test LLM suggestion fetches correctly
- [ ] Test HTML formatting (all sections render correctly)
- [ ] Test tab switching doesn't corrupt HTML
- [ ] Test error handling (LLM failure)
- [ ] Test response time calculation
- [ ] Visual regression test: Suggestions match Streamlit

---

## Phase 5: AI Assistant - Member Info Tab (Week 4)

### Objectives
- Migrate member context display
- Show member details, balance, transcript summary
- Add interaction history

### Tasks

#### 5.1 Member Context Fetching
- [ ] Create callback: `fetch_member_context()`
  - Input: `selected_call_id` Store
  - Output: `member_context` Store
  - Cache: 10 second TTL
  - SQL: Use `FUNCTION_GET_CALL_CONTEXT()`

#### 5.2 Member Info Display
- [ ] Create `app_dash/components/member_info.py`:
  - Member name metric
  - Balance display (formatted)
  - Recent transcript summary
  - Interaction history
- [ ] Format: Use `dbc.Card` components

#### 5.3 Member History
- [ ] Create callback: `fetch_member_history()`
  - Input: `selected_call_id` Store
  - Output: `member_history` Store
  - SQL: Use `FUNCTION_GET_MEMBER_HISTORY()`

#### 5.4 Display Component
- [ ] Create callback: `render_member_info()`
  - Input: `member_context` + `member_history` Stores
  - Output: `member_info_display` children
  - Format: Clean, professional layout

### Deliverables
- ✅ Member info displays correctly
- ✅ Balance formatting correct
- ✅ History displays properly

### Testing
- [ ] Test member context fetches on call selection
- [ ] Test balance formatting (currency)
- [ ] Test transcript summary display
- [ ] Test member history display
- [ ] Test empty states
- [ ] Visual regression test: Member info matches Streamlit

---

## Phase 6: AI Assistant - Knowledge Base Tab (Week 5)

### Objectives
- Migrate KB search functionality
- Implement vector search integration
- Add suggested questions
- Simplify interaction (radio buttons)

### Tasks

#### 6.1 KB Search Component
- [ ] Create `app_dash/components/kb_search.py`:
  - Radio buttons for suggested questions
  - Text input for manual search
  - Results display area
- [ ] Use `dbc.RadioItems` (already simplified)

#### 6.2 Suggested Questions
- [ ] Create callback: `get_suggested_questions()`
  - Input: `selected_call_id` Store
  - Output: Radio button options
  - Cache: 30 second TTL

#### 6.3 KB Search Logic
- [ ] Create callback: `search_kb()`
  - Input: Radio selection OR text input
  - Output: `kb_results` Store
  - Vector search: Use existing `search_kb_vector_search()`
  - Prevent: Only search when query changes

#### 6.4 Results Display
- [ ] Create callback: `render_kb_results()`
  - Input: `kb_results` Store
  - Output: `kb_results_display` children
  - Format: Article cards with title, category, content preview

#### 6.5 State Isolation
- [ ] Ensure KB interactions don't trigger transcript refresh
- [ ] Use separate Store for KB state
- [ ] Prevent callback chains

### Deliverables
- ✅ KB search working
- ✅ Radio buttons functional
- ✅ Results display correctly
- ✅ No interference with other tabs

### Testing
- [ ] Test suggested questions load
- [ ] Test radio button selection triggers search
- [ ] Test manual text search
- [ ] Test vector search returns results
- [ ] Test results formatting
- [ ] Test KB interactions don't refresh transcript
- [ ] Visual regression test: KB tab matches Streamlit

---

## Phase 7: Compliance Alerts (Week 5)

### Objectives
- Migrate compliance alert display
- Show severity levels
- Add visual indicators

### Tasks

#### 7.1 Compliance Fetching
- [ ] Create callback: `fetch_compliance_alerts()`
  - Input: `selected_call_id` Store
  - Output: `compliance_alerts` Store
  - Cache: 10 second TTL
  - SQL: Use `FUNCTION_CHECK_COMPLIANCE()`

#### 7.2 Compliance Display Component
- [ ] Create `app_dash/components/compliance.py`:
  - Severity badges (Critical, High, Medium)
  - Alert cards
  - Summary metrics
- [ ] Format: Use `dbc.Alert` components

#### 7.3 Display Callback
- [ ] Create callback: `render_compliance_alerts()`
  - Input: `compliance_alerts` Store
  - Output: `compliance_display` children
  - Format: Color-coded by severity

### Deliverables
- ✅ Compliance alerts display correctly
- ✅ Severity indicators working
- ✅ Summary metrics accurate

### Testing
- [ ] Test compliance alerts fetch on call selection
- [ ] Test severity classification
- [ ] Test alert formatting
- [ ] Test empty state (no alerts)
- [ ] Visual regression test: Compliance matches Streamlit

---

## Phase 8: Tab Navigation & Integration (Week 6)

### Objectives
- Integrate all tabs into single component
- Implement tab switching
- Ensure state isolation
- Fix any remaining HTML issues

### Tasks

#### 8.1 Tab Component
- [ ] Create `app_dash/components/ai_assistant_tabs.py`:
  - `dbc.Tabs` with 3 tabs:
    - Suggestions
    - Member Info
    - Knowledge Base
  - Each tab uses separate Store for state

#### 8.2 Tab Switching Logic
- [ ] Create callback: `on_tab_change()`
  - Input: Tab `active_tab` prop
  - Output: Update active tab state
  - Prevent: Don't trigger other callbacks

#### 8.3 State Isolation
- [ ] Ensure each tab has isolated state
- [ ] Prevent cross-tab interference
- [ ] Cache tab-specific data separately

#### 8.4 HTML Protection
- [ ] Ensure suggestion HTML doesn't corrupt on tab switch
- [ ] Store formatted HTML in separate Store
- [ ] Validate HTML before rendering

### Deliverables
- ✅ All tabs integrated
- ✅ Tab switching smooth
- ✅ No state interference
- ✅ HTML stays intact

### Testing
- [ ] Test tab switching doesn't refresh other components
- [ ] Test suggestion HTML survives tab switches
- [ ] Test KB search doesn't affect transcript
- [ ] Test member info doesn't affect suggestions
- [ ] Performance test: Rapid tab switching
- [ ] Visual regression test: All tabs match Streamlit

---

## Phase 9: Analytics Dashboard Migration (Week 6-7)

### Objectives
- Migrate analytics dashboard
- Preserve charts and visualizations
- Maintain data refresh logic

### Tasks

#### 9.1 Analytics Layout
- [ ] Create `app_dash/pages/analytics.py`
- [ ] Port layout structure
- [ ] Set up routing (if using multi-page)

#### 9.2 Charts Migration
- [ ] Convert Plotly charts (already compatible)
- [ ] Use `dcc.Graph` components
- [ ] Preserve chart configurations

#### 9.3 Data Fetching
- [ ] Create callbacks for each metric
- [ ] Implement caching
- [ ] Add refresh intervals

#### 9.4 Filters & Controls
- [ ] Migrate date range selectors
- [ ] Migrate filter dropdowns
- [ ] Connect to data callbacks

### Deliverables
- ✅ Analytics dashboard functional
- ✅ Charts display correctly
- ✅ Filters working

### Testing
- [ ] Test all charts render
- [ ] Test filters update charts
- [ ] Test data refresh
- [ ] Visual regression test: Analytics matches Streamlit

---

## Phase 10: Supervisor Dashboard Migration (Week 7)

### Objectives
- Migrate supervisor dashboard
- Preserve escalation scoring
- Maintain real-time updates

### Tasks

#### 10.1 Supervisor Layout
- [ ] Create `app_dash/pages/supervisor.py`
- [ ] Port layout structure
- [ ] Set up routing

#### 10.2 Escalation Display
- [ ] Create escalation score components
- [ ] Add risk indicators
- [ ] Display agent performance metrics

#### 10.3 Real-time Updates
- [ ] Add interval components
- [ ] Create update callbacks
- [ ] Implement caching

### Deliverables
- ✅ Supervisor dashboard functional
- ✅ Escalation scores display
- ✅ Real-time updates working

### Testing
- [ ] Test escalation scores calculate
- [ ] Test real-time updates
- [ ] Test agent metrics display
- [ ] Visual regression test: Supervisor matches Streamlit

---

## Phase 11: Integration & Routing (Week 7-8)

### Objectives
- Integrate all dashboards
- Set up multi-page routing
- Create navigation
- Handle authentication

### Tasks

#### 11.1 Multi-Page Setup
- [ ] Use `dash.page_registry` or `dash_multi_page`
- [ ] Create routes:
  - `/` - Agent Dashboard
  - `/analytics` - Analytics Dashboard
  - `/supervisor` - Supervisor Dashboard

#### 11.2 Navigation Component
- [ ] Create `app_dash/components/navigation.py`
- [ ] Add navigation bar/header
- [ ] Link to all pages

#### 11.3 Shared Components
- [ ] Extract common components
- [ ] Create shared utilities
- [ ] Set up shared state management

#### 11.4 Authentication (if needed)
- [ ] Implement auth check
- [ ] Redirect if not authenticated
- [ ] Store auth state

### Deliverables
- ✅ All dashboards integrated
- ✅ Navigation working
- ✅ Routing functional

### Testing
- [ ] Test navigation between pages
- [ ] Test routing works correctly
- [ ] Test shared state persists
- [ ] Test authentication (if applicable)

---

## Phase 12: Performance Optimization (Week 8)

### Objectives
- Optimize callback performance
- Reduce unnecessary rerenders
- Improve caching strategy
- Optimize data fetching

### Tasks

#### 12.1 Callback Optimization
- [ ] Review all callbacks for efficiency
- [ ] Minimize callback chains
- [ ] Use `prevent_initial_call` where appropriate
- [ ] Add `suppress_callback_exceptions` for development

#### 12.2 Caching Strategy
- [ ] Implement server-side caching (Redis/Memcached)
- [ ] Optimize client-side Store usage
- [ ] Add cache invalidation logic

#### 12.3 Data Fetching Optimization
- [ ] Batch SQL queries where possible
- [ ] Use connection pooling
- [ ] Implement query result caching

#### 12.4 Frontend Optimization
- [ ] Minimize re-renders
- [ ] Use `dash.callback_context` to prevent unnecessary updates
- [ ] Optimize HTML rendering

### Deliverables
- ✅ Optimized callbacks
- ✅ Improved caching
- ✅ Faster data fetching
- ✅ Reduced rerenders

### Testing
- [ ] Performance benchmarks
- [ ] Load testing
- [ ] Response time measurements
- [ ] Memory usage profiling

---

## Phase 13: Testing & QA (Week 8)

### Objectives
- Comprehensive testing
- Bug fixes
- Performance validation
- User acceptance testing

### Tasks

#### 13.1 Unit Testing
- [ ] Test all utility functions
- [ ] Test component rendering
- [ ] Test callback logic
- [ ] Achieve >80% code coverage

#### 13.2 Integration Testing
- [ ] Test Databricks integration
- [ ] Test SQL execution
- [ ] Test vector search
- [ ] Test LLM calls

#### 13.3 End-to-End Testing
- [ ] Test complete user workflows
- [ ] Test all dashboard pages
- [ ] Test error scenarios
- [ ] Test edge cases

#### 13.4 Visual Regression Testing
- [ ] Compare Dash vs Streamlit screenshots
- [ ] Verify styling matches
- [ ] Check responsive design
- [ ] Validate branding

#### 13.5 Performance Testing
- [ ] Load testing (multiple concurrent users)
- [ ] Stress testing (high data volumes)
- [ ] Response time testing
- [ ] Memory leak testing

#### 13.6 User Acceptance Testing
- [ ] Create UAT test plan
- [ ] Conduct user testing sessions
- [ ] Gather feedback
- [ ] Document issues

### Deliverables
- ✅ Comprehensive test suite
- ✅ Bug fixes completed
- ✅ Performance validated
- ✅ UAT completed

### Testing
- [ ] All tests passing
- [ ] No critical bugs
- [ ] Performance targets met
- [ ] User approval

---

## Phase 14: Deployment & Migration (Week 8)

### Objectives
- Deploy Dash app
- Set up monitoring
- Create migration guide
- Train users

### Tasks

#### 14.1 Deployment Setup
- [ ] Create deployment configuration
- [ ] Set up production environment
- [ ] Configure reverse proxy (if needed)
- [ ] Set up SSL certificates

#### 14.2 Monitoring & Logging
- [ ] Set up application monitoring
- [ ] Configure error logging
- [ ] Set up performance monitoring
- [ ] Create alerting rules

#### 14.3 Migration Guide
- [ ] Document migration steps
- [ ] Create user guide
- [ ] Document differences from Streamlit
- [ ] Create troubleshooting guide

#### 14.4 User Training
- [ ] Create training materials
- [ ] Conduct training sessions
- [ ] Create video tutorials
- [ ] Set up support channels

#### 14.5 Rollout Plan
- [ ] Plan phased rollout
- [ ] Set up feature flags
- [ ] Create rollback plan
- [ ] Schedule migration window

### Deliverables
- ✅ Dash app deployed
- ✅ Monitoring configured
- ✅ Migration guide complete
- ✅ Users trained

### Testing
- [ ] Deployment successful
- [ ] Monitoring working
- [ ] Users can access app
- [ ] Support channels ready

---

## Risk Mitigation

### High-Risk Areas

1. **HTML Formatting Issues**
   - **Risk:** HTML corruption during tab switches
   - **Mitigation:** Store formatted HTML in separate Store, validate before rendering
   - **Contingency:** Fallback to plain text if HTML validation fails

2. **Callback Complexity**
   - **Risk:** Callback chains causing performance issues
   - **Mitigation:** Minimize callback dependencies, use Stores for state
   - **Contingency:** Refactor callbacks if performance degrades

3. **State Management**
   - **Risk:** State not persisting correctly
   - **Mitigation:** Use `dcc.Store` components, test state management thoroughly
   - **Contingency:** Implement session-based state storage

4. **Data Fetching Performance**
   - **Risk:** Slow SQL queries affecting UX
   - **Mitigation:** Aggressive caching, query optimization
   - **Contingency:** Add loading states, optimize queries

5. **User Adoption**
   - **Risk:** Users prefer Streamlit version
   - **Mitigation:** Maintain feature parity, provide training
   - **Contingency:** Keep Streamlit version as backup

---

## Success Criteria

### Functional Requirements
- ✅ All features from Streamlit version working
- ✅ No HTML corruption issues
- ✅ Smooth tab switching
- ✅ Real-time updates working
- ✅ All dashboards functional

### Performance Requirements
- ✅ Page load time < 2 seconds
- ✅ Callback response time < 500ms
- ✅ No unnecessary rerenders
- ✅ Memory usage < 500MB

### Quality Requirements
- ✅ >80% code coverage
- ✅ No critical bugs
- ✅ Visual parity with Streamlit version
- ✅ Responsive design working

### User Requirements
- ✅ User acceptance testing passed
- ✅ Training completed
- ✅ Support documentation available
- ✅ Migration successful

---

## Timeline Summary

| Phase | Duration | Key Deliverables |
|-------|----------|------------------|
| Phase 0: Preparation | Week 1 | Environment setup, component mapping |
| Phase 1: Core Infrastructure | Week 2 | Base app, Databricks integration |
| Phase 2: Sidebar | Week 2-3 | Call selection, sidebar |
| Phase 3: Transcript | Week 3 | Live transcript display |
| Phase 4: AI Suggestions | Week 4 | AI suggestion tab |
| Phase 5: Member Info | Week 4 | Member info tab |
| Phase 6: Knowledge Base | Week 5 | KB search tab |
| Phase 7: Compliance | Week 5 | Compliance alerts |
| Phase 8: Tab Integration | Week 6 | Tab navigation |
| Phase 9: Analytics | Week 6-7 | Analytics dashboard |
| Phase 10: Supervisor | Week 7 | Supervisor dashboard |
| Phase 11: Integration | Week 7-8 | Multi-page routing |
| Phase 12: Optimization | Week 8 | Performance optimization |
| Phase 13: Testing | Week 8 | Comprehensive testing |
| Phase 14: Deployment | Week 8 | Production deployment |

**Total Duration: 6-8 weeks**

---

## Next Steps

1. **Review this plan** with stakeholders
2. **Approve timeline** and resource allocation
3. **Set up development environment** (Phase 0)
4. **Begin Phase 1** implementation
5. **Schedule weekly reviews** to track progress

---

## Appendix

### A. Component Mapping Reference
See `docs/DASH_COMPONENT_MAPPING.md` (to be created)

### B. Testing Strategy
See `docs/DASH_TESTING_STRATEGY.md` (to be created)

### C. Architecture Diagrams
See `docs/DASH_ARCHITECTURE.md` (to be created)

### D. Rollback Plan
- Keep Streamlit version running in parallel
- Feature flag to switch between versions
- Database schema remains unchanged
- Can rollback within 1 hour if critical issues

---

**Document Version:** 1.0  
**Last Updated:** [Current Date]  
**Owner:** Development Team  
**Status:** Draft - Pending Approval

