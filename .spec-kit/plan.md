# QME - Technical Implementation Plan

## Technology Stack

### Core Language
- **Python 3.11+**: Primary language for cross-platform compatibility
- **Type Hints**: Used throughout for code clarity and IDE support

### Networking Libraries
- **httpx**: Async HTTP client for API calls
  - Chosen over requests for native async support
  - Better timeout handling and connection pooling
  - Supports HTTP/2 and modern features
- **dnspython**: DNS resolution library
  - Programmatic DNS queries (replaces dig command)
  - Support for custom DNS servers
  - Comprehensive DNS record type support
- **socket**: Standard library for OS-level DNS fallback

### User Interface
- **Textual**: Modern TUI framework for Python
  - AWS Console-style tabbed interface
  - Built-in widgets (DataTable, TabbedContent, Input)
  - Async event loop integration
  - Cross-platform terminal support

### Build & Distribution
- **PyInstaller**: Python application packaging
  - Single-file executable generation
  - Cross-platform binary creation
  - Hidden imports configuration for Textual
- **GitHub Actions**: CI/CD pipeline
  - Multi-platform builds (Windows, Linux, macOS)
  - Automated releases on git tags
  - Artifact management

## Architecture

### Module Structure

```
qme.py (single-file architecture for simplicity)
├── DNS Resolution Layer
│   ├── ValidateTarget(): Input validation
│   └── ResolveDNSChain(): CNAME tracking with fallbacks
├── Geolocation Layer
│   └── GetIp(): Multi-API querying with retry logic
├── Data Aggregation
│   └── fetch_target_metadata(): Orchestrates DNS + Geolocation
└── UI Layer
    └── NetMonitorApp: Textual TUI implementation
```

### Data Flow

```
User Input
    ↓
ValidateTarget (regex validation)
    ↓
┌─────────────┬──────────────┐
│   Domain    │     IP       │
└─────────────┴──────────────┘
      ↓              ↓
ResolveDNSChain   GetIp (direct)
      ↓              ↓
   Final IP    Geolocation APIs
      ↓              ↓
      └──────┬───────┘
             ↓
    fetch_target_metadata
             ↓
        UI Display
```

### DNS Resolution Strategy

1. **Primary**: System DNS resolver
2. **Fallback 1**: Google DNS (8.8.8.8)
3. **Fallback 2**: Google DNS Secondary (8.8.4.4)
4. **Fallback 3**: Cloudflare DNS (1.1.1.1)
5. **Fallback 4**: Cloudflare DNS Secondary (1.0.0.1)
6. **Fallback 5**: OpenDNS (208.67.222.222)
7. **Fallback 6**: Quad9 (9.9.9.9)
8. **Final**: OS socket.gethostbyname()

Each attempt has 1 second timeout. Chain stops on first successful resolution.

### API Query Strategy

1. **Primary**: ipinfo.io
   - HTTPS endpoint
   - JSON response
   - Comprehensive geolocation data

2. **Fallback 1**: ipapi.co
   - HTTPS endpoint
   - JSON response
   - Alternative data source

3. **Fallback 2**: ip-api.com
   - HTTP endpoint (no HTTPS)
   - JSON response
   - Last resort

Each API gets 2 retry attempts with 2 second timeout per attempt.

### UI Architecture

```
NetMonitorApp (Textual App)
├── Header (clock, title)
├── Stats Panel (status bar)
├── Search Input (target entry)
├── Upper Section
│   └── DataTable (target list)
└── AWS Panel (TabbedContent)
    ├── Tab: IPInfo / Geolocation
    ├── Tab: DNS Chain
    ├── Tab: Nmap Scanner
    └── Tab: Network Diagnostics
```

## Implementation Details

### DNS Resolution Implementation

```python
# Key components:
- dns.resolver.Resolver() with custom nameservers
- Timeout configuration: 1.0s
- CNAME recursion with loop detection
- Exception handling for NXDOMAIN, NoAnswer, timeouts
```

### API Query Implementation

```python
# Key components:
- httpx.AsyncClient with timeout limits
- User-Agent header to avoid blocking
- Follow redirects enabled
- Rate limit handling (429 status)
- Exponential backoff on retry
```

### UI Implementation

```python
# Key components:
- Textual App with async event loop
- Worker threads for network operations
- Reactive data updates
- Keyboard bindings (F, Q)
- Tab navigation
- Status formatting with color codes
```

### Error Handling Strategy

1. **DNS Failures**: Try next DNS server, log failure, continue chain
2. **API Failures**: Try next API, log which API failed, continue chain
3. **Timeouts**: Abort current attempt, move to next fallback
4. **UI Errors**: Display error message in Diagnostics tab, don't crash
5. **Invalid Input**: Show error in status bar, don't process

### Performance Optimizations

1. **Async Operations**: All network calls are async to prevent UI blocking
2. **Timeouts**: Strict timeouts prevent hanging on slow networks
3. **Early Exit**: Stop fallback chains on first success
4. **Minimal Dependencies**: Only essential libraries included
5. **Single Binary**: PyInstaller creates optimized single-file executable

## Security Considerations

1. **No Hardcoded Secrets**: All APIs are public, no keys required
2. **Input Validation**: Regex patterns prevent injection attacks
3. **Timeout Protection**: Prevents DoS via slow responses
4. **No Data Collection**: No telemetry or user tracking
5. **HTTPS Preferred**: Use HTTPS when available (ipinfo.io, ipapi.co)

## Testing Strategy

### Unit Tests
- Target validation regex patterns
- DNS resolver configuration
- API response parsing
- Timeout handling

### Integration Tests
- DNS resolution with mock servers
- API calls with mock responses
- UI component interactions
- Error scenario handling

### Manual Testing
- VPN scenarios (WireGuard active/disconnected)
- Different network configurations
- Cross-platform testing (Windows, Linux, macOS)
- Edge cases (invalid inputs, network failures)

## Deployment Strategy

### Development
- Virtual environment with requirements.txt
- Direct Python execution: `python qme.py`

### Production
- PyInstaller single-file binaries
- GitHub Actions automated builds
- GitHub Releases for distribution
- Platform-specific executables

### Version Management
- Semantic versioning (vX.Y.Z)
- Git tags trigger automated builds
- CHANGELOG tracking
- Backward compatibility considerations

## Future Extensibility

### Planned Enhancements
- Actual Nmap integration
- DNS-over-HTTPS support
- Batch scanning
- Result export (CSV/JSON)
- Custom DNS server configuration

### Extension Points
- Modular API integration (easy to add new providers)
- Pluggable DNS resolvers
- UI theme customization
- Plugin architecture for additional features

## Dependencies Rationale

| Dependency | Purpose | Alternative Considered | Reason for Choice |
|------------|---------|----------------------|-------------------|
| httpx | HTTP client | requests, aiohttp | Native async, better timeout handling |
| dnspython | DNS resolution | dnslib, built-in socket | More features, better API |
| textual | TUI framework | rich, curses, npyscreen | Modern, async, widget-rich |
| pyinstaller | Packaging | cx_Freeze, nuitka | Better cross-platform support |

## Risk Mitigation

1. **API Availability**: Multiple fallback APIs ensure service continuity
2. **DNS Reliability**: 6 fallback DNS servers prevent resolution failures
3. **VPN Interference**: Direct DNS queries bypass VPN routing
4. **UI Freezing**: Async operations prevent blocking
5. **Binary Size**: UPX compression reduces executable size
6. **Platform Issues**: Test on all platforms before release
