# FlashCards — Sistema de Flashcards com Repetição Espaçada

Um app desktop para Windows, no estilo Anki, para criar decks e cards e
revisá-los usando repetição espaçada (algoritmo SM-2 — o mesmo em que o
Anki se baseia).

## O que tem aqui

- `main.py` — interface gráfica (Tkinter)
- `database.py` — banco de dados local (SQLite)
- `srs.py` — algoritmo de repetição espaçada
- `build.bat` — script que gera o `.exe` no Windows
- `requirements.txt` — dependência necessária só para compilar (PyInstaller)

## Opção A — Compilar automaticamente com GitHub Actions (recomendado)

Não precisa instalar nada no seu computador — o GitHub compila o `.exe`
para você em um servidor Windows na nuvem.

1. Crie um repositório novo no GitHub (pode ser privado ou público).
2. Suba todo o conteúdo desta pasta `app/` para a raiz do repositório
   (incluindo a pasta `.github/workflows/build.yml` — ela já vem pronta
   aqui dentro). Pelo site do GitHub: botão **"Add file" → "Upload
   files"**, arraste tudo e clique em **Commit**. Ou pelo terminal:
   ```
   git init
   git add .
   git commit -m "primeiro commit"
   git branch -M main
   git remote add origin https://github.com/SEU_USUARIO/SEU_REPO.git
   git push -u origin main
   ```
3. Vá na aba **Actions** do seu repositório no GitHub. O workflow
   "Build Windows EXE" vai rodar automaticamente após o push (leva
   1-3 minutos).
4. Quando terminar (bolinha verde ✅), clique no build concluído e
   baixe o arquivo `.exe` em **Artifacts → FlashCards-windows**.
   Ele também cria uma **Release** automática na aba "Releases" do
   repositório, já com o `FlashCards.exe` anexado para download direto.

Depois disso, toda vez que você alterar o código e der `git push`, um
novo `.exe` é gerado sozinho.

## Opção B — Compilar localmente no Windows

1. **Instale o Python no Windows** (se ainda não tiver):
   https://www.python.org/downloads/
   Durante a instalação, marque a caixa **"Add Python to PATH"**.

2. **Copie a pasta inteira** (`app/`, com todos os arquivos `.py`, o
   `build.bat` e o `requirements.txt`) para o seu computador Windows.

3. **Dê dois cliques em `build.bat`** (ou abra o Prompt de Comando dentro
   da pasta e rode `build.bat`).

4. Aguarde — ele vai instalar o PyInstaller e compilar o programa.

5. Quando terminar, o executável estará em:
   ```
   dist\FlashCards.exe
   ```
   Você pode mover esse arquivo `.exe` para qualquer lugar (área de
   trabalho, pasta de programas, pendrive) e ele funciona sozinho, sem
   precisar do Python instalado depois de pronto.

## Como usar o app

- **Tela inicial**: lista seus decks (baralhos de cards), com total de
  cards e quantos estão "para revisar hoje".
- **Novo Deck**: cria um novo baralho.
- **Gerenciar**: abre a tela para adicionar, editar e excluir cards
  (frente = pergunta, verso = resposta).
- **Revisar**: mostra os cards que estão devidos para hoje, um de cada
  vez. Você vê a pergunta, clica em "Mostrar resposta", e depois avalia
  quão bem lembrou: **Errei / Difícil / Bom / Fácil**. Isso ajusta
  automaticamente quando aquele card vai aparecer de novo (o coração do
  sistema de repetição espaçada).

## Onde ficam os seus dados

O banco de dados fica salvo em:
```
%APPDATA%\FlashCardsApp\flashcards.db
```
Isso normalmente é algo como
`C:\Users\SeuUsuario\AppData\Roaming\FlashCardsApp\flashcards.db`.
Você pode fazer backup copiando esse arquivo.

## Extensões possíveis (me avise se quiser que eu adicione)

- Tags e busca de cards
- Importar/exportar decks (CSV ou formato compatível com Anki)
- Suporte a imagens nos cards
- Estatísticas e gráficos de progresso
- Atalhos de teclado na revisão (espaço = mostrar resposta, 1-4 = avaliar)
- Modo escuro
