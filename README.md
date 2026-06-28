# QME - Network Monitor

Ferramenta de monitoramento de rede com interface TUI (Textual) resiliente a VPN WireGuard. Suporta resolução DNS, geolocalização IP e diagnóstico de rede.

## Funcionalidades

- **Resolução DNS com múltiplos fallbacks**: Google DNS, Cloudflare, OpenDNS, Quad9
- **Múltiplas APIs de geolocalização**: ipinfo.io, ipapi.co, ip-api.com
- **Interface TUI moderna**: Painel estilo AWS Console com abas funcionais
- **Diagnóstico de rede**: Identifica problemas causados por VPN
- **Cadeia DNS completa**: Rastreia CNAMEs até o IP final
- **Resiliente a WireGuard**: Funciona mesmo com VPN ativa

## Requisitos

- Python 3.11+
- Dependências listadas em `requirements.txt`

## Instalação

### Via pip (Recomendado para Desenvolvedores)

```bash
# Clone o repositório
git clone <repository-url>
cd projects

# Crie ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instale dependências
pip install -r requirements.txt
```

### Via Binário (Recomendado para Usuários Finais)

Baixe o binário correspondente ao seu sistema na seção [Releases](https://github.com/seu-usuario/qme/releases):

- `qme-windows.exe` - Windows
- `qme-linux` - Linux
- `qme-macos` - macOS

## Uso

### Via Python (Desenvolvimento)

```bash
# Execução direta
python qme.py

# Com alvo initial
python qme.py google.com
python qme.py 8.8.8.8
```

### Via Binário (Produção)

```bash
# Linux/Mac
./qme-linux google.com
./qme-macos google.com

# Windows
qme-windows.exe google.com
```

### Controles da Interface

- `F` - Focar campo de busca
- `Q` - Sair
- `Setas` - Navegar na tabela
- `Enter` - Buscar novo alvo
- `Tab` - Alternar entre abas

## Build Local com PyInstaller

```bash
# Instale PyInstaller
pip install pyinstaller

# Build usando o arquivo .spec
pyinstaller qme.spec

# Ou build direto (one-file)
pyinstaller --onefile --name qme qme.py
```

O binário será gerado na pasta `dist/`.

## Build Automatizado (GitHub Actions)

O projeto inclui workflow do GitHub Actions para build multi-plataforma.

### Disparar Build

**Via tag (automático):**
```bash
git tag v1.0.0
git push origin v1.0.0
```

**Manualmente:**
1. Vá para Actions no GitHub
2. Selecione "Build Multi-Platform Binaries"
3. Clique em "Run workflow"

### Artefatos Gerados

O workflow gera 3 binários:
- `qme-windows.exe` - Windows
- `qme-linux` - Linux
- `qme-macos` - macOS

Os binários são anexados ao Release quando disparado via tag.

## Estrutura do Projeto

```
.
├── qme.py                 # Código principal
├── qme.spec               # Configuração PyInstaller
├── requirements.txt        # Dependências Python
├── .github/
│   └── workflows/
│       └── build.yml      # Workflow GitHub Actions
└── README.md              # Este arquivo
```

## Solução de Problemas

### VPN WireGuard Bloqueando Resoluções

Se a ferramenta não funcionar com VPN ativa:

1. **Aba Diagnóstico**: Verifique qual API foi usada
2. **Desconecte VPN**: Teste sem VPN para confirmar
3. **Split-tunneling**: Configure WireGuard para não rotear DNS
4. **Use IP direto**: Em vez de domínio, use o IP

### Erro de DNS

- O sistema tenta 6 servidores DNS públicos automaticamente
- Se todos falharem, verifique sua conexão de rede

### APIs Bloqueadas

- O sistema tenta 3 APIs em sequência
- Se todas falharem, pode ser bloqueio geográfico ou rate limit

## Dependências

- `httpx` - Cliente HTTP assíncrono
- `dnspython` - Resolução DNS
- `textual` - Framework TUI

## Licença

[Adicione sua licença aqui]
