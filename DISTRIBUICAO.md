# Distribuição do Duelo de Veyrion

Os jogadores não precisam instalar Python. Cada sistema recebe um pacote
portátil com o executável e os assets do jogo.

## Gerar os pacotes

No Linux:

```bash
chmod +x scripts/build_linux.sh
./scripts/build_linux.sh
```

O arquivo gerado é `dist/duelo-veyrion-linux-x64.tar.gz`.

No Windows, abra o `cmd` na pasta do projeto e execute:

```bat
scripts\build_windows.bat
```

O arquivo gerado é `dist\duelo-veyrion-windows-x64.zip`.

Publique os dois arquivos em uma Release do GitHub com exatamente estes nomes:

- `duelo-veyrion-linux-x64.tar.gz`
- `duelo-veyrion-windows-x64.zip`

## Comando para o jogador

Linux com `curl` e `tar`:

```bash
curl -fsSL https://raw.githubusercontent.com/SoloLF17/first-RPG-test/main/scripts/baixar_jogar.sh | bash
```

Windows PowerShell:

```powershell
irm https://raw.githubusercontent.com/SoloLF17/first-RPG-test/main/scripts/baixar_jogar.ps1 | iex
```

Os comandos baixam o pacote da Release mais recente, extraem em uma pasta do
usuário e iniciam o jogo. Eles dependem apenas de `curl`/`tar` no Linux e do
PowerShell no Windows; Python não é necessário para jogar.
