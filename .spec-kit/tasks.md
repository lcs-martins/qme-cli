# QME - Implementation Tasks

## Phase 1: Project Setup

### 1.1 Initialize Project Structure
- [ ] Create project directory structure
- [ ] Set up Python virtual environment
- [ ] Create requirements.txt with dependencies
- [ ] Initialize .gitignore for Python projects
- [ ] Set up version control (git init)

### 1.2 Configure Development Environment
- [ ] Install httpx library
- [ ] Install dnspython library
- [ ] Install textual library
- [ ] Verify Python version (3.11+)
- [ ] Test basic imports

## Phase 2: Core DNS Resolution

### 2.1 Implement Target Validation
- [ ] Create ValidateTarget() function
- [ ] Implement IPv4 regex pattern
- [ ] Implement IPv6 regex pattern
- [ ] Implement domain name regex pattern
- [ ] Add invalid input handling
- [ ] Write unit tests for validation patterns

### 2.2 Implement DNS Resolution with Fallbacks
- [ ] Define FALLBACK_DNS_SERVERS constant (6 servers)
- [ ] Create ResolveDNSChain() function
- [ ] Implement system DNS resolver (primary)
- [ ] Implement fallback DNS server iteration
- [ ] Add CNAME tracking logic
- [ ] Implement 1-second timeout per DNS server
- [ ] Add socket.gethostbyname() final fallback
- [ ] Write unit tests for DNS resolution

### 2.3 Test DNS Resilience
- [ ] Test with system DNS working
- [ ] Test with system DNS failing
- [ ] Test with VPN active (WireGuard)
- [ ] Test CNAME chain tracking
- [ ] Verify timeout behavior
- [ ] Test all 6 fallback DNS servers

## Phase 3: Geolocation API Integration

### 3.1 Implement API Query Infrastructure
- [ ] Create GetIp() async function
- [ ] Define API list (ipinfo.io, ipapi.co, ip-api.com)
- [ ] Implement API-specific parsers
- [ ] Add User-Agent header
- [ ] Configure httpx.AsyncClient with timeouts
- [ ] Implement retry logic (2 attempts per API)

### 3.2 Implement API Fallback Chain
- [ ] Implement ipinfo.io primary query
- [ ] Implement ipapi.co fallback query
- [ ] Implement ip-api.com final fallback
- [ ] Add rate limit handling (429 status)
- [ ] Implement exponential backoff
- [ ] Track which API succeeded
- [ ] Write unit tests for API parsers

### 3.3 Test API Resilience
- [ ] Test with all APIs working
- [ ] Test with primary API failing
- [ ] Test with two APIs failing
- [ ] Test rate limit scenarios
- [ ] Test timeout behavior
- [ ] Verify data parsing for each API

## Phase 4: Data Aggregation Layer

### 4.1 Implement Metadata Fetcher
- [ ] Create fetch_target_metadata() function
- [ ] Integrate DNS resolution with geolocation
- [ ] Handle IPv4/IPv6 direct queries
- [ ] Handle domain name queries
- [ ] Implement error aggregation
- [ ] Create result data structure
- [ ] Write integration tests

### 4.2 Implement Error Handling
- [ ] Add comprehensive exception handling
- [ ] Implement graceful degradation
- [ ] Add error logging without sensitive data
- [ ] Create user-friendly error messages
- [ ] Test error scenarios

## Phase 5: User Interface

### 5.1 Implement Textual App Structure
- [ ] Create NetMonitorApp class
- [ ] Implement compose() method
- [ ] Add Header widget
- [ ] Add Footer widget
- [ ] Create upper section with DataTable
- [ ] Create lower section with TabbedContent

### 5.2 Implement Tabbed Interface
- [ ] Create IPInfo/Geolocation tab
- [ ] Create DNS Chain tab
- [ ] Create Nmap Scanner tab (placeholder)
- [ ] Create Network Diagnostics tab
- [ ] Implement tab navigation
- [ ] Add tab content display logic

### 5.3 Implement Interactive Features
- [ ] Add search input field
- [ ] Implement Enter key handler
- [ ] Add F key binding for search focus
- [ ] Add Q key binding for quit
- [ ] Implement table row selection
- [ ] Add row highlight handler
- [ ] Implement tab data updates

### 5.4 Implement Status Display
- [ ] Add status formatting (green/red colors)
- [ ] Display connection status
- [ ] Show API used indicator
- [ ] Add loading states
- [ ] Implement async worker threads

## Phase 6: Network Diagnostics

### 6.1 Implement Diagnostics Tab
- [ ] Create diagnostics content display
- [ ] Show connection status
- [ ] Display API used
- [ ] Show target type
- [ ] Add VPN detection logic
- [ ] Implement troubleshooting suggestions

### 6.2 Add Diagnostic Information
- [ ] List possible failure causes
- [ ] Add VPN-specific suggestions
- [ ] Include firewall troubleshooting
- [ ] Add DNS troubleshooting tips
- [ ] Provide API rate limit guidance

## Phase 7: Build & Distribution

### 7.1 Configure PyInstaller
- [ ] Create qme.spec file
- [ ] Add hidden imports for Textual
- [ ] Add hidden imports for dnspython
- [ ] Configure single-file build
- [ ] Set executable name
- [ ] Test local build

### 7.2 Set Up GitHub Actions
- [ ] Create .github/workflows/build.yml
- [ ] Configure Windows build job
- [ ] Configure Linux build job
- [ ] Configure macOS build job
- [ ] Add artifact upload steps
- [ ] Configure release automation
- [ ] Test workflow manually

### 7.3 Create Distribution Artifacts
- [ ] Build Windows executable
- [ ] Build Linux executable
- [ ] Build macOS executable
- [ ] Test binaries on respective platforms
- [ ] Verify standalone execution
- [ ] Test with VPN scenarios

## Phase 8: Documentation

### 8.1 Create User Documentation
- [ ] Write README.md
- [ ] Document installation via pip
- [ ] Document installation via binary
- [ ] Add usage examples
- [ ] Document keyboard shortcuts
- [ ] Add troubleshooting section

### 8.2 Create Developer Documentation
- [ ] Document build process
- [ ] Add PyInstaller instructions
- [ ] Document GitHub Actions workflow
- [ ] Add contribution guidelines
- [ ] Document code structure
- [ ] Add API integration notes

## Phase 9: Testing & Quality Assurance

### 9.1 Unit Testing
- [ ] Write tests for ValidateTarget()
- [ ] Write tests for ResolveDNSChain()
- [ ] Write tests for GetIp()
- [ ] Write tests for API parsers
- [ ] Write tests for fetch_target_metadata()
- [ ] Achieve >80% code coverage

### 9.2 Integration Testing
- [ ] Test DNS + API integration
- [ ] Test UI + backend integration
- [ ] Test error handling end-to-end
- [ ] Test with mock servers
- [ ] Test with real APIs

### 9.3 Manual Testing
- [ ] Test on Windows
- [ ] Test on Linux
- [ ] Test on macOS
- [ ] Test with WireGuard VPN active
- [ ] Test with VPN disconnected
- [ ] Test edge cases (invalid inputs, network failures)

## Phase 10: Spec-Kit Integration

### 10.1 Create Spec-Kit Structure
- [ ] Create .spec-kit directory
- [ ] Write constitution.md
- [ ] Write spec.md
- [ ] Write plan.md
- [ ] Write tasks.md

### 10.2 Align with Spec-Kit Standards
- [ ] Verify constitution compliance
- [ ] Ensure spec completeness
- [ ] Validate plan feasibility
- [ ] Check tasks breakdown
- [ ] Update documentation

## Phase 11: Release Preparation

### 11.1 Version Management
- [ ] Implement semantic versioning
- [ ] Create CHANGELOG.md
- [ ] Tag initial release (v1.0.0)
- [ ] Document breaking changes
- [ ] Prepare release notes

### 11.2 Final Verification
- [ ] Test all binaries one last time
- [ ] Verify VPN resilience
- [ ] Check documentation completeness
- [ ] Validate GitHub Actions workflow
- [ ] Test release process

## Phase 12: Maintenance & Future Enhancements

### 12.1 Monitoring Setup
- [ ] Set up issue templates
- [ ] Create contribution guidelines
- [ ] Add bug reporting instructions
- [ ] Set up feature request process

### 12.2 Future Enhancement Planning
- [ ] Plan Nmap integration
- [ ] Research DNS-over-HTTPS
- [ ] Design batch scanning feature
- [ ] Plan export functionality
- [ ] Consider custom DNS configuration

## Task Status Legend

- [ ] Not started
- [x] Completed
- [~] In progress
- [!] Blocked
- [?] Needs investigation

## Estimated Timeline

- Phase 1-2: 2 days (Setup + DNS)
- Phase 3: 2 days (API Integration)
- Phase 4: 1 day (Data Layer)
- Phase 5: 3 days (UI Implementation)
- Phase 6: 1 day (Diagnostics)
- Phase 7: 2 days (Build & Distribution)
- Phase 8: 1 day (Documentation)
- Phase 9: 2 days (Testing)
- Phase 10: 1 day (Spec-Kit)
- Phase 11: 1 day (Release)
- Phase 12: Ongoing (Maintenance)

**Total Estimated Time: 16 days for initial implementation**
