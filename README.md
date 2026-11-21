# Duelo de Veyrion

RPG de batalhas por turnos desenvolvido em Python com Pygame. Escolha um
personagem, enfrente a inteligência artificial ou jogue contra outra pessoa e
vença a melhor de 1, 3 ou 5 rodadas.

## Recursos

- Guerreiro, Mago e Arqueiro.
- Modo contra a CPU e modo para dois jogadores.
- Batalhas por turnos com ataques, cura e habilidades especiais.
- Níveis de dificuldade, configurações de janela e atalhos personalizáveis.
- Animações, efeitos visuais e retratos dos personagens.
- Salvamento local das opções do jogo.

## Como jogar

Na batalha, use as teclas `1` a `5` para escolher uma ação. Também é possível
clicar nos botões da tela. Use `Esc` para pausar e siga as instruções exibidas
nos menus para escolher nomes, personagens e configurações.

## Baixar e jogar sem instalar Python

Os executáveis são publicados nas Releases do GitHub. O download inclui o
jogo e todos os assets necessários.

### Linux

Abra um terminal e execute:

```bash
curl -fsSL https://raw.githubusercontent.com/SoloLF17/first-RPG-test/main/scripts/baixar_jogar.sh | bash
```

O jogo será instalado em `~/.local/share/duelo-veyrion` e iniciado
automaticamente. É necessário ter `curl` e `tar` disponíveis.

### Windows PowerShell

Abra o PowerShell e execute:

```powershell
irm https://raw.githubusercontent.com/SoloLF17/first-RPG-test/main/scripts/baixar_jogar.ps1 | iex
```

O jogo será instalado em `%LOCALAPPDATA%\DueloDeVeyrion` e iniciado
automaticamente. Não é necessário instalar Python.

### Download manual

Também é possível baixar os arquivos diretamente na página de [Releases](https://github.com/SoloLF17/first-RPG-test/releases):

- `duelo-veyrion-linux-x64.tar.gz` para Linux 64-bit.
- `duelo-veyrion-windows-x64.zip` para Windows 64-bit.

Extraia o arquivo e execute `DueloDeVeyrion` no Linux ou
`DueloDeVeyrion.exe` no Windows.

## Executar a partir do código-fonte

Para desenvolvimento, é necessário Python 3.10 ou superior:

```bash
python -m venv .venv
source .venv/bin/activate       # Linux/macOS
.venv\Scripts\activate         # Windows CMD
python -m pip install -r requirements.txt
python -m jogo
```

No Windows, a ativação correta é:

```powershell
.venv\Scripts\Activate.ps1
```

Para executar os testes:

```bash
python -m unittest discover -s testes -p "test_*.py"
```

## Gerar executáveis

Os pacotes portáteis são gerados com PyInstaller. O build deve ser feito no
mesmo sistema operacional do executável:

```bash
./scripts/build_linux.sh
```

No Windows:

```bat
scripts\build_windows.bat
```

Os detalhes de publicação estão em [DISTRIBUICAO.md](DISTRIBUICAO.md). Uma
tag no formato `v1.0.0` aciona automaticamente o workflow de Release do
GitHub.

## Estrutura principal

```text
jogo/                  Código do jogo
jogo/assets/           Imagens dos personagens
testes/                Testes automatizados
scripts/               Builds e download dos pacotes
.github/workflows/     Automação das Releases
```

## Licença

Consulte o arquivo [LICENSE](LICENSE).
