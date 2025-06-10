# Processador de Resultados CSV

Uma aplicação web criada com Streamlit e Python para automatizar o processo de limpeza, transformação e enriquecimento de dados a partir de um arquivo CSV.

## Funcionalidades

- Upload de arquivos CSV.
- Limpeza de cabeçalhos e dados indesejados.
- Transformação de valores com base em regras de negócio.
- Interface interativa para mapear dados (Placa e Teste).
- Geração de um arquivo Excel (.xlsx) final com os dados pivotados e prontos para análise.

## Como Executar

1.  Clone este repositório:
    ```bash
    git clone [https://github.com/SEU-USUARIO/NOME-DO-REPOSITORIO.git](https://github.com/SEU-USUARIO/NOME-DO-REPOSITORIO.git)
    ```
2.  Navegue até a pasta do projeto:
    ```bash
    cd NOME-DO-REPOSITORIO
    ```
3.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```
4.  Execute a aplicação Streamlit:
    ```bash
    streamlit run app.py
    ```

#### **5. Inicie o Repositório Git Local e Faça seu Primeiro Commit**

Agora, vamos usar o Git. Abra seu terminal **dentro da pasta do projeto**.

```bash
# 1. Inicia um repositório Git na pasta atual
git init

# 2. Adiciona todos os arquivos para serem monitorados pelo Git
git add .

# 3. Salva uma "fotografia" do estado atual dos arquivos (commit)
git commit -m "Commit inicial: Adiciona a primeira versão da aplicação e arquivos de configuração"