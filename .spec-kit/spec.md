# QME - Functional Specification

## Overview

QME is a network monitoring tool that provides comprehensive IP and domain analysis through a terminal user interface (TUI). The tool is specifically designed to work reliably even when VPN connections (particularly WireGuard) are active, which typically break standard DNS resolution and API calls.

## Problem Statement

Network administrators and security professionals need to quickly analyze IP addresses and domains to understand:
- Geolocation and ownership information
- DNS resolution chains (CNAME tracking)
- Network connectivity status
- Potential routing issues caused by VPNs

Existing tools often fail when VPNs are active because:
- DNS queries are routed through the VPN tunnel
- External APIs may block VPN IP addresses
- DNS servers in the tunnel may be unreliable or misconfigured

## Solution

QME provides a resilient network analysis tool that:
- Uses multiple DNS fallback servers to bypass VPN routing issues
- Queries multiple geolocation APIs with automatic failover
- Provides clear diagnostic information when network issues occur
- Offers an intuitive TUI interface inspired by AWS Console

## Functional Requirements

### Core Features

#### 1. Target Validation
- Accept IPv4 addresses as input
- Accept IPv6 addresses as input
- Accept domain names as input
- Validate input format using regex patterns
- Return clear error messages for invalid targets

#### 2. DNS Resolution with Fallbacks
- Resolve domain names to IP addresses
- Track complete CNAME chains
- Use system DNS as primary resolver
- Automatically fallback to 6 public DNS servers:
  - Google DNS (8.8.8.8, 8.8.4.4)
  - Cloudflare DNS (1.1.1.1, 1.0.0.1)
  - OpenDNS (208.67.222.222)
  - Quad9 (9.9.9.9)
- Implement strict timeouts (1 second per DNS server)
- Fall back to OS socket resolution if all DNS servers fail

#### 3. Geolocation API Integration
- Query IP geolocation information from multiple APIs:
  - Primary: ipinfo.io
  - Fallback 1: ipapi.co
  - Fallback 2: ip-api.com
- Extract and display: country, city, region, organization, timezone, postal code
- Implement retry logic (2 attempts per API)
- Use strict timeouts (2 seconds per API attempt)
- Handle rate limits with exponential backoff
- Display which API successfully provided data

#### 4. Terminal User Interface
- AWS Console-style tabbed interface
- Upper panel: Table of scanned targets with status
- Lower panel: Tabbed views for detailed information
- Tabs:
  - IPInfo / Geolocation
  - DNS Chain (CNAME tracking)
  - Nmap Scanner (placeholder for future integration)
  - Network Diagnostics
- Keyboard navigation (F for search, Q to quit, arrows for navigation)
- Real-time status indicators (connected, blocked, error)
- Responsive async operations to prevent UI freezing

#### 5. Network Diagnostics
- Display connection status for each target
- Show which API was used for successful queries
- Identify when VPN is likely causing issues
- Provide troubleshooting suggestions:
  - Disconnect VPN temporarily
  - Configure split-tunneling
  - Use direct IP instead of domain
- Show target type (IPv4, IPv6, CNAME)

#### 6. Session Management
- Maintain list of scanned targets in current session
- Allow re-selection of previous targets
- Display scan history in table format
- Support initial target via command-line argument

### Non-Functional Requirements

#### Performance
- DNS resolution must complete within 2 seconds with fallbacks
- API calls must timeout within 2 seconds per attempt
- UI must remain responsive during network operations
- Memory usage should be minimal for a CLI tool

#### Reliability
- Tool must work with WireGuard VPN active
- Multiple fallback strategies for DNS and APIs
- Graceful degradation when services are unavailable
- No data loss during session

#### Compatibility
- Support Windows, Linux, and macOS
- Work with PowerShell, Bash, and Zsh
- Package as standalone binary via PyInstaller
- Support Python 3.11+

#### Security & Privacy
- No telemetry or user data collection
- No hardcoded API keys
- Use only public APIs
- Respect user's network configuration
- No data sent to third parties beyond required API calls

## User Stories

### As a network administrator
I want to quickly check the geolocation of an IP address so that I can identify the origin of suspicious traffic.

### As a security analyst
I want to trace DNS CNAME chains so that I can understand the full resolution path of a domain.

### As a developer
I want to test network connectivity from different network configurations so that I can diagnose VPN-related issues.

### As a system administrator
I want a tool that works reliably with VPNs active so that I don't have to disconnect my VPN to perform basic network checks.

## Success Criteria

1. Tool successfully resolves domains and IPs with WireGuard VPN active
2. Multiple DNS fallbacks prevent resolution failures
3. API failover ensures geolocation data is always retrieved
4. Clear diagnostic information helps users troubleshoot network issues
5. Interface is intuitive and responsive
6. Standalone binaries work on Windows, Linux, and macOS

## Out of Scope (Future Enhancements)

- Actual Nmap integration (currently placeholder)
- DNS-over-HTTPS support
- Historical scan data persistence
- Batch scanning of multiple targets
- Export results to CSV/JSON
- Custom DNS server configuration
- API key support for premium geolocation services
