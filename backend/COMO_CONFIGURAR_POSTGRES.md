# Como Configurar e Executar com PostgreSQL

Esta é a cópia do projeto configurada para integrar diretamente com um banco de dados **PostgreSQL** em vez de ler/escrever em arquivos JSON.

---

## 1. Pré-requisitos e Dependências

Para rodar este projeto, você precisa instalar o driver do PostgreSQL para Python (`psycopg2-binary`). Instale rodando o comando:

```bash
pip install -r requirements.txt
```

---

## 2. Configurando o Banco de Dados

A API está programada para se conectar a um banco de dados chamado `holtech_db`. 
Certifique-se de que o seu servidor PostgreSQL esteja em execução.

Você pode configurar a conexão definindo variáveis de ambiente (ou deixando os valores padrão):

* `DB_HOST` (Padrão: `localhost`)
* `DB_PORT` (Padrão: `5432`)
* `DB_NAME` (Padrão: `holtech_db`)
* `DB_USER` (Padrão: `postgres`)
* `DB_PASSWORD` (Padrão: `postgres`)

### Como a API lida com tabelas e dados:
A API possui um mecanismo automático de inicialização (`init_db()`). Ao iniciar a API pela primeira vez:
1. Ela tentará se conectar ao banco configurado.
2. Criará automaticamente a tabela `usuarios` se ela ainda não existir.
3. Se a tabela estiver vazia, ela irá inserir os usuários padrão (Administrador e Usuário Comum) para você testar imediatamente.

---

## 3. Executando a API e o Streamlit

Navegue até a pasta `backend` e execute os comandos:

1. **Rodar a API (Porta 8000):**
   ```bash
   python main.py
   ```

2. **Rodar o Streamlit (Porta 8501):**
   ```bash
   python -m streamlit run app.py
   ```

Toda a interação de login, listagem, inclusão, edição e exclusão de usuários na interface passará a ler e gravar em tempo real no seu banco de dados PostgreSQL!
