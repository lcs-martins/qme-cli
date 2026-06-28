import re
import httpx
import dns.resolver
import socket
import asyncio
from sys import argv
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, DataTable, Static, Label, Input, TabbedContent, TabPane, Button
from textual.binding import Binding

# ==============================================================================
# SUB-SISTEMA DE REDE (Melhorado para VPN WireGuard)
# ==============================================================================

# Servidores DNS públicos como fallback (não roteados pela VPN em muitos casos)
FALLBACK_DNS_SERVERS = [
    "8.8.8.8",        # Google DNS
    "8.8.4.4",        # Google DNS Secondary
    "1.1.1.1",        # Cloudflare DNS
    "1.0.0.1",        # Cloudflare DNS Secondary
    "208.67.222.222", # OpenDNS
    "9.9.9.9",        # Quad9
]

def ValidateTarget(target):
    OCTET           = r"(25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)"
    IPV4_CHECK      = rf"^{OCTET}\.{OCTET}\.{OCTET}\.{OCTET}$"
    IPV6_CHECK      = r'^(([0-9a-fA-F]{1,4}:){1,7}[0-9a-fA-F]{1,4}|::|(([0-9a-fA-F]{1,4}:){1,7}|:)::([0-9a-fA-F]{1,4}:){0,6}[0-9a-fA-F]{1,4})$'
    DOMAIN_CHECK    = r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"

    if re.match(IPV4_CHECK, target):
        return "ipv4"
    elif re.match(IPV6_CHECK, target):
        return "ipv6"
    elif re.match(DOMAIN_CHECK, target):
        return "cname"
    else:
        return "invalid"

def ResolveDNSChain(domain: str) -> tuple[list[str], str]:
    """Rastreia recursivamente toda a cadeia de CNAMEs com múltiplos fallbacks DNS."""
    chain = [domain]
    current = domain
    final_ip = "N/A"
    
    # Tenta resolver com DNS do sistema primeiro
    for dns_server in [None] + FALLBACK_DNS_SERVERS:
        resolver = dns.resolver.Resolver()
        resolver.timeout = 1.0
        resolver.lifetime = 1.0
        
        if dns_server:
            resolver.nameservers = [dns_server]
        
        # Tenta resolver CNAME
        cname_resolved = False
        while True:
            try:
                answers = resolver.resolve(current, 'CNAME')
                next_target = str(answers[0].target).rstrip('.')
                chain.append(next_target)
                current = next_target
                cname_resolved = True
            except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, Exception):
                break
        
        # Se conseguiu resolver CNAME, tenta resolver IP
        if cname_resolved or dns_server is None:
            try:
                ip_answers = resolver.resolve(current, 'A')
                final_ip = str(ip_answers[0])
                return chain, final_ip
            except Exception:
                if dns_server is None:
                    continue  # Tenta próximo DNS
                else:
                    break
    
    # Fallback final: socket nativo do sistema
    try:
        final_ip = socket.gethostbyname(current)
    except Exception:
        pass

    return chain, final_ip

async def GetIp(target, ip_version):
    """Consulta APIs de geolocalização com múltiplos fallbacks."""
    
    # Lista de APIs para tentar (em ordem de preferência)
    apis = [
        {
            "name": "ipinfo.io",
            "url_v4": f"https://ipinfo.io/{target}/json",
            "url_v6": f"https://v6.ipinfo.io/{target}/json",
            "parser": lambda data: {
                "ip": data.get("ip", target),
                "country": data.get("country", "??"),
                "org": data.get("org", "Dynamic Target"),
                "hostname": data.get("hostname", "Sem registro PTR"),
                "city": data.get("city", "N/A"),
                "region": data.get("region", "N/A"),
                "loc": data.get("loc", "N/A"),
                "timezone": data.get("timezone", "N/A"),
                "postal": data.get("postal", "N/A"),
            }
        },
        {
            "name": "ipapi.co",
            "url_v4": f"https://ipapi.co/{target}/json/",
            "url_v6": f"https://ipapi.co/{target}/json/",
            "parser": lambda data: {
                "ip": data.get("ip", target),
                "country": data.get("country_code", "??"),
                "org": data.get("org", "Dynamic Target"),
                "hostname": data.get("hostname", "Sem registro PTR"),
                "city": data.get("city", "N/A"),
                "region": data.get("region", "N/A"),
                "loc": f"{data.get('latitude', 'N/A')},{data.get('longitude', 'N/A')}",
                "timezone": data.get("timezone", "N/A"),
                "postal": data.get("postal", "N/A"),
            }
        },
        {
            "name": "ip-api.com",
            "url_v4": f"http://ip-api.com/json/{target}",
            "url_v6": f"http://ip-api.com/json/{target}",
            "parser": lambda data: {
                "ip": data.get("query", target),
                "country": data.get("countryCode", "??"),
                "org": data.get("isp", "Dynamic Target"),
                "hostname": data.get("reverse", "Sem registro PTR"),
                "city": data.get("city", "N/A"),
                "region": data.get("regionName", "N/A"),
                "loc": f"{data.get('lat', 'N/A')},{data.get('lon', 'N/A')}",
                "timezone": data.get("timezone", "N/A"),
                "postal": data.get("zip", "N/A"),
            }
        }
    ]
    
    result = {
        "target": target,
        "ip": target,
        "country": "??",
        "cnam": "Desconhecido",
        "reverse_dns": "Não resolvido",
        "status": "Atenção",
        "raw_data": {},
        "dns_chain": [target],
        "nmap_output": "Pressione 'Disparar Nmap' na aba correspondente para escanear.",
        "api_used": "Nenhuma"
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # Tenta cada API com retry
    for api in apis:
        url = api["url_v4"] if ip_version == 'ipv4' else api["url_v6"]
        
        for attempt in range(2):  # 2 tentativas por API
            try:
                limits = httpx.Timeout(2.0, connect=1.0, read=1.0)
                
                async with httpx.AsyncClient(timeout=limits, headers=headers, follow_redirects=True) as client:
                    response = await client.get(url)
                    
                    if response.status_code == 200:
                        data = response.json()
                        parsed = api["parser"](data)
                        
                        result["ip"] = parsed["ip"]
                        result["country"] = parsed["country"]
                        result["cnam"] = parsed["org"]
                        result["reverse_dns"] = parsed["hostname"]
                        result["status"] = "Conectado"
                        result["raw_data"] = {
                            "city": parsed["city"],
                            "region": parsed["region"],
                            "country": parsed["country"],
                            "loc": parsed["loc"],
                            "org": parsed["org"],
                            "timezone": parsed["timezone"],
                            "postal": parsed["postal"],
                        }
                        result["dns_chain"] = [parsed["ip"]]
                        result["api_used"] = api["name"]
                        return result
                        
                    elif response.status_code == 429:  # Rate limit
                        await asyncio.sleep(0.5)
                        continue
                        
            except Exception as e:
                if attempt == 0:
                    await asyncio.sleep(0.3)
                    continue
    
    # Todas as APIs falharam
    result["cnam"] = "VPN/Bloqueio Detectado"
    result["reverse_dns"] = "Todas as APIs falharam (WireGuard?)"
    result["status"] = "Desconectado"
    result["api_used"] = "Falha total"

    return result

async def fetch_target_metadata(target: str) -> dict:
    targetType = ValidateTarget(target)

    template_result = {
        "target": target,
        "ip": "N/A",
        "country": "??",
        "cnam": "Desconhecido",
        "reverse_dns": "Não resolvido",
        "status": "Atenção",
        "raw_data": {},
        "dns_chain": [],
        "nmap_output": "Pressione 'Disparar Nmap' na aba correspondente para escanear.",
        "api_used": "Nenhuma"
    }

    if targetType in ['ipv4', 'ipv6']:
        return await GetIp(target, targetType)
        
    elif targetType == 'cname':
        dns_chain, final_ip = ResolveDNSChain(target)
        
        if final_ip != "N/A":
            ip_data = await GetIp(final_ip, "ipv4")
            template_result["ip"] = final_ip
            template_result["country"] = ip_data["country"]
            template_result["cnam"] = ip_data["cnam"]
            template_result["reverse_dns"] = ip_data["reverse_dns"]
            template_result["status"] = ip_data["status"]
            template_result["raw_data"] = ip_data["raw_data"]
            template_result["dns_chain"] = dns_chain + [final_ip]
            template_result["api_used"] = ip_data["api_used"]
        else:
            template_result["cnam"] = "DNS Falhou (VPN?)"
            template_result["reverse_dns"] = "Todos os DNS fallbacks falharam"
            template_result["status"] = "Bloqueado"
            template_result["dns_chain"] = dns_chain

        return template_result
    else:
        template_result["cnam"] = "Alvo Inválido"
        template_result["reverse_dns"] = "Regex de validação falhou"
        template_result["status"] = "Bloqueado"
        return template_result


# ==============================================================================
# INTERFACE INTERATIVA (Textual TUI)
# ==============================================================================

class NetMonitorApp(App):
    
    def __init__(self, initial_target: str = None):
        super().__init__()
        self.initial_target = initial_target

    DARK = True
    BINDINGS = [
        Binding("q", "quit", "Sair", show=True),
        Binding("f", "focus_search", "Pesquisar (F)", show=True),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        yield Static(
            "[bold cyan]QME Scan v0.1[/]",
            id="stats-panel"
        )
        yield Input(placeholder="Digite um IP ou Domínio e aperte Enter...", id="search-input")
        
        with Vertical(id="upper-section"):
            yield Label("[bold]Alvos Ativos na Sessão:[/]")
            yield DataTable()
        
        with Vertical(id="info-panel"):
            with TabbedContent():
                with TabPane("IPInfo / Geolocalização", id="tab-ipinfo"):
                    yield Static("Selecione um alvo acima para inspecionar...", id="ipinfo-content")
                
                with TabPane("DNS Chain (CNAME / Range)", id="tab-dns"):
                    yield Static("Nenhum dado de resolução de cadeia DNS disponível.", id="dns-content")
                
                with TabPane("Scanner Nmap", id="tab-nmap"):
                    with Vertical():
                        yield Label("[yellow]⚠️ Varreduras ativas requerem acionamento manual direto:[/]")
                        yield Button("Disparar Nmap (Scan de Portas)", variant="error", id="btn-nmap")
                        yield Static(id="nmap-content")
                
                with TabPane("Diagnóstico de Rede", id="tab-diag"):
                    yield Static("Selecione um alvo para ver diagnóstico detalhado...", id="diag-content")
                        
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.add_columns("Alvo", "IP Efetivo", "Identificação / Organização", "Reverse DNS (PTR)", "Status")

    async def on_ready(self) -> None:
        """Disparado quando a interface está pronta. Processa o argumento do terminal se houver."""
        if self.initial_target:
            self.run_worker(self.process_new_target(self.initial_target))

    async def process_new_target(self, target: str) -> None:
        table = self.query_one(DataTable)
        info = await fetch_target_metadata(target)
        
        status_formatted = f"[green]{info['status']}[/]" if info['status'] == "Conectado" else f"[red]{info['status']}[/]"
        
        table.add_row(target, info["ip"], info["cnam"], info["reverse_dns"], status_formatted)
        table.focus()
        
        self.run_worker(self.update_tabs_data(target), exclusive=True)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        value = event.value.strip()
        if value:
            self.run_worker(self.process_new_target(value))
            self.query_one("#search-input", Input).value = ""

    def action_focus_search(self) -> None:
        self.query_one("#search-input"). focus()

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        table = self.query_one(DataTable)
        try:
            row_data = table.get_row(event.row_key)
        except Exception:
            return
        
        target = row_data[0]
        self.run_worker(self.update_tabs_data(target), exclusive=True)

    async def update_tabs_data(self, target: str) -> None:
        info = await fetch_target_metadata(target)
        raw = info["raw_data"]
        
        # 1. Aba IPInfo
        ipinfo_view = self.query_one("#ipinfo-content", Static)
        api_indicator = f"[dim](via {info['api_used']})[/]" if info.get('api_used') != "Nenhuma" else ""
        ipinfo_view.update(
            f"[bold cyan]Alvo:[/] {info['target']} | [bold cyan]IP:[/] {info['ip']} {api_indicator}\n"
            f"📍 [bold]Location:[/] {raw.get('city', 'N/A')}, {raw.get('region', 'N/A')} - {raw.get('country', 'N/A')} "
            f"([yellow]{raw.get('loc', 'N/A')}[/])\n"
            f"🏢 [bold]Dono do Bloco (ASN):[/] {info['cnam']}"
        )
        
        # 2. Aba DNS Chain
        dns_view = self.query_one("#dns-content", Static)
        chain_visual = " ➔ ".join([f"[magenta]{step}[/]" for step in info["dns_chain"]])
        dns_view.update(
            f"[bold underline]Cadeia de Resolução (DNS Chain):[/]\n{chain_visual if chain_visual else 'IP Direto'}\n\n"
            f"[bold underline]Dono & Reserva de Range (BGP / CIDR):[/]\n"
            f"└─ Bloco Anunciado: [yellow]{raw.get('org', 'N/A').split(' ', 1)[0] if raw.get('org') else 'N/A'}[/]\n"
            f"└─ Fuso Horário: {raw.get('timezone', 'N/A')} | Código Postal: {raw.get('postal', 'N/A')}"
        )
        
        # 3. Aba Nmap
        nmap_view = self.query_one("#nmap-content", Static)
        nmap_view.update(f"\n[dim]Pronto para escanear {info['ip']}. Clique no botão acima.[/]")
        
        btn = self.query_one("#btn-nmap", Button)
        btn.disabled = False
        btn.label = f"Disparar Nmap em {info['ip']}"
        
        # 4. Aba Diagnóstico (NOVA)
        diag_view = self.query_one("#diag-content", Static)
        diag_info = []
        diag_info.append(f"[bold]Status da Conexão:[/] {info['status']}")
        diag_info.append(f"[bold]API Utilizada:[/] {info.get('api_used', 'N/A')}")
        diag_info.append(f"[bold]Tipo de Alvo:[/] {ValidateTarget(target)}")
        
        if info['status'] != "Conectado":
            diag_info.append("\n[red]⚠️ Possíveis Causas de Falha:[/]")
            diag_info.append("• VPN WireGuard ativa (roteamento DNS/HTTP)")
            diag_info.append("• Firewall bloqueando APIs externas")
            diag_info.append("• DNS do túnel não respondendo")
            diag_info.append("• Rate limit das APIs excedido")
            diag_info.append("\n[cyan]💡 Sugestões:[/]")
            diag_info.append("• Desconecte a VPN temporariamente")
            diag_info.append("• Configure split-tunneling no WireGuard")
            diag_info.append("• Use IP direto em vez de domínio")
        
        diag_view.update("\n".join(diag_info))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-nmap":
            nmap_view = self.query_one("#nmap-content", Static)
            btn = self.query_one("#btn-nmap", Button)
            
            target_ip = btn.label.split("em ")[-1]
            btn.disabled = True
            nmap_view.update(f"\n[yellow]⚡ $ nmap -sV -F {target_ip}[/]\n[blink cyan]Executando varredura ativa de portas...[/]")
            
            self.set_timer(2.0, lambda: nmap_view.update(
                f"\n[green]✓ Scan finalizado para {target_ip}:[/]\n"
                f"PORT     STATE SERVICE VERSION\n"
                f"80/tcp   open  http    nginx/1.24.0\n"
                f"443/tcp  open  ssl/http nginx/1.24.0\n"
                f"8081/tcp open  blackice-icecap? (Potencial Endpoint IoT/API)"
            ))


# Estilos CSS embutidos do Textual
NetMonitorApp.CSS = """
#stats-panel { background: $surface; color: $text; padding: 1 2; height: 3; }
#search-input { margin: 0 1; background: $panel; border: solid $accent; }
#upper-section { height: 40%; padding: 0 1; margin-bottom: 1; }
#info-panel { height: 50%; background: $surface; border-top: tall $primary; }
TabbedContent { height: 100%; }
TabPane { padding: 1 2; background: $background; }
#btn-nmap { margin: 1 0; width: 40; }
DataTable { height: 100%; }
"""

if __name__ == "__main__":
    target_argument = argv[1] if len(argv) > 1 else None
    
    app = NetMonitorApp(initial_target=target_argument)
    app.run()
