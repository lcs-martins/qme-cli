# QME - Project Constitution

## Core Principles

### Code Quality
- **Type Safety**: Use type hints consistently throughout the codebase
- **Error Handling**: Implement comprehensive error handling with clear user feedback
- **Modularity**: Keep functions focused and single-purpose
- **Documentation**: Document complex logic and public APIs with docstrings

### Testing Standards
- **Unit Tests**: Critical network operations must have unit tests
- **Integration Tests**: API integrations should be tested with mocks
- **Edge Cases**: Test VPN scenarios, DNS failures, and API rate limits
- **Coverage**: Maintain >80% code coverage for core networking logic

### User Experience Consistency
- **Interface**: Maintain AWS Console-style UI consistency across all tabs
- **Feedback**: Provide clear status indicators (connected, blocked, error)
- **Performance**: Keep UI responsive with async operations
- **Accessibility**: Ensure keyboard navigation works flawlessly

### Performance Requirements
- **DNS Resolution**: Complete within 2 seconds with fallbacks
- **API Calls**: Each API attempt should timeout within 2 seconds
- **UI Responsiveness**: No blocking operations on main thread
- **Memory Usage**: Keep memory footprint reasonable for CLI tool

### Security & Privacy
- **No Data Collection**: No telemetry or user data collection
- **DNS Privacy**: Support for DNS-over-HTTPS if needed in future
- **API Keys**: No hardcoded API keys; use public APIs only
- **VPN Awareness**: Respect user's network configuration

## Development Guidelines

### Network Operations
- Always implement timeout mechanisms
- Use multiple fallback strategies for DNS and APIs
- Log network failures for debugging without exposing sensitive data
- Handle rate limits gracefully with exponential backoff

### Cross-Platform Compatibility
- Test on Windows, Linux, and macOS before releases
- Handle platform-specific path separators correctly
- Ensure terminal compatibility (PowerShell, Bash, Zsh)
- Package with PyInstaller for standalone binaries

### Dependency Management
- Pin dependency versions in requirements.txt
- Prefer well-maintained libraries with active communities
- Minimize external dependencies where possible
- Document why each dependency is needed

### Release Process
- Tag releases with semantic versioning (vX.Y.Z)
- Build binaries for all platforms via GitHub Actions
- Update CHANGELOG with each release
- Test binaries before publishing to Releases

## Non-Negotiables

1. **VPN Resilience**: The tool MUST work with WireGuard VPN active
2. **DNS Fallbacks**: At least 6 public DNS servers as fallback
3. **API Redundancy**: Minimum 3 geolocation APIs with automatic failover
4. **User Privacy**: No data sent to third parties beyond required API calls
5. **Open Source**: All code remains open source with clear licensing
