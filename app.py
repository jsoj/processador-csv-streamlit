import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

# --- Configurações da Página (Logo, Favicon e Título) ---
# IMPORTANTE: Substitua os caminhos pelos nomes reais dos seus arquivos de imagem.
# Os arquivos devem estar na mesma pasta da aplicação (/var/www/upload).
st.set_page_config(
    layout="wide", 
    page_title="Processador de Resultados",
    page_icon="/var/www/upload/favicon.png" # Ex: "favicon.png"
)

# Adiciona o logo na barra lateral
st.logo("/var/www/upload/logo.png") # Ex: "logo_agromarkers.png"

# --- Funções Auxiliares ---

@st.cache_data
def to_excel(df):
    """
    Converte um DataFrame do Pandas para um arquivo Excel (.xlsx) em memória.
    """
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Resultados')
    processed_data = output.getvalue()
    return processed_data

# --- Lógica de Inicialização e Processamento do Arquivo ---

def initialize_processing(uploaded_file):
    """
    Executa os passos iniciais de processamento do arquivo CSV.
    """
    try:
        uploaded_file.seek(0)
        lines = [line.decode('utf-8', errors='ignore') for line in uploaded_file.readlines()]
        start_row = 0
        found_data_header = False
        for i, line in enumerate(lines):
            if "Data" in line:
                start_row = i + 1
                found_data_header = True
                break
        
        if not found_data_header:
            st.error("Erro: A linha de cabeçalho contendo 'Data' não foi encontrada. Por favor, verifique o conteúdo do arquivo CSV.")
            st.session_state.clear()
            return

        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file, skiprows=start_row)

        df['Empresa'] = ""
        df['Projeto'] = ""
        df['Placa'] = ""
        df['Teste'] = ""
        
        if 'Call' in df.columns:
            df['Resultado'] = df['Call'].copy()
            replacements = {'X:X': 'POS:POS', 'Y:X': 'NEG:POS', 'Y:Y': 'NEG:NEG', '?': 'FAIL'}
            df['Resultado'] = df['Resultado'].astype(str).replace(replacements)
        else:
            st.error("Erro: A coluna 'Call' não foi encontrada. O processo não pode continuar.")
            st.session_state.clear()
            return
        
        st.session_state.df = df
        st.session_state.step = 'mapping'
        st.success("Arquivo processado. Por favor, preencha o mapeamento abaixo.")

    except Exception as e:
        st.error(f"Ocorreu um erro inesperado durante o processamento do arquivo: {e}")
        st.warning("Por favor, verifique se o arquivo CSV está formatado corretamente e tente novamente.")
        st.session_state.clear()


# --- Interface Principal do Streamlit (em Português) ---

st.title("🔬 Ferramenta de Transformação de CSV para XLSX")
st.markdown("""
Esta aplicação web foi criada para automatizar o processo de limpeza e enriquecimento de dados de placas.
Siga os passos abaixo para carregar seu arquivo, fornecer as informações necessárias e baixar o resultado final.
""")

st.header("Passo 1: Carregue seu arquivo CSV")
uploaded_file = st.file_uploader("Escolha um arquivo .csv", type="csv", key="file_uploader", label_visibility="collapsed")

if uploaded_file is not None:
    file_identifier = f"{uploaded_file.name}-{uploaded_file.size}"
    
    if 'file_id' not in st.session_state or st.session_state.file_id != file_identifier:
        st.session_state.clear()
        st.session_state.file_id = file_identifier
        initialize_processing(uploaded_file)
        st.rerun()

if 'step' in st.session_state and st.session_state.step == 'mapping':
    st.header("Passo 2: Mapeamento de Placas e Testes")
    st.markdown("""
    Para cada `DaughterPlate` única encontrada, forneça os valores para **Placa** e **Teste**.
    - Exemplo: Para `1003_001_004_BT2`, informe **Placa** `001-004` e **Teste** `BT2`.
    """)
    
    df = st.session_state.df
    if 'DaughterPlate' in df.columns:
        unique_daughter_plates = df['DaughterPlate'].unique()
        
        with st.form(key='mapping_form'):
            mapping_data = {}
            for plate in unique_daughter_plates:
                st.write(f"**DaughterPlate:** `{plate}`")
                col1, col2 = st.columns(2)
                placa_val = col1.text_input("Valor para Placa:", key=f"placa_{plate}")
                teste_val = col2.text_input("Valor para Teste:", key=f"teste_{plate}")
                mapping_data[plate] = {'Placa': placa_val, 'Teste': teste_val}
            
            submit_button = st.form_submit_button(label='Aplicar Mapeamento e Continuar')

            if submit_button:
                for daughter_plate, values in mapping_data.items():
                    mask = df['DaughterPlate'] == daughter_plate
                    df.loc[mask, 'Placa'] = values['Placa']
                    df.loc[mask, 'Teste'] = values['Teste']
                
                st.session_state.df = df
                st.session_state.step = 'final_info'
                st.success("Mapeamento aplicado com sucesso!")
                st.rerun()
    else:
        st.error("Erro: A coluna 'DaughterPlate' não foi encontrada no DataFrame.")

if 'step' in st.session_state and st.session_state.step == 'final_info':
    st.header("Passo 3: Informações Finais do Projeto")
    df = st.session_state.df
    
    with st.form(key='final_info_form'):
        empresa = st.text_input("Nome da Empresa:")
        projeto = st.text_input("Nome do Projeto:")
        submit_final = st.form_submit_button("Gerar Arquivo Final")

        if submit_final:
            if empresa and projeto:
                df['Empresa'] = empresa
                df['Projeto'] = projeto
                if 'MasterWell' in df.columns:
                    df['Chave'] = df['Placa'].astype(str) + '-' + df['MasterWell'].astype(str)
                else:
                    st.error("Erro: A coluna 'MasterWell' não foi encontrada. Não é possível criar a coluna 'Chave'.")
                
                st.session_state.df = df
                st.session_state.step = 'download'
                st.rerun()
            else:
                st.warning("Por favor, preencha os campos Empresa e Projeto.")

if 'step' in st.session_state and st.session_state.step == 'download':
    st.header("Passo 4: Revisão Final e Download")
    df = st.session_state.df
    
    if 'SubjectID' in df.columns:
        df = df.drop(columns=['SubjectID','X','Y','DaughterPlate','MasterPlate','Call','SNPID'], errors='ignore')
        st.info("Colunas antigas foram removidas para fazer o pivot dos dados.")

    final_df = df
    try:
        st.write("Realizando o pivot (tabela dinâmica) dos dados...")
        index_cols = [col for col in df.columns if col not in ['Teste', 'Resultado']]
        
        if not index_cols:
             st.warning("Não foi possível identificar colunas para agrupar. O pivot não será realizado.")
        else:
            pivoted_df = df.pivot_table(
                index=index_cols,
                columns='Teste',
                values='Resultado',
                aggfunc='first'
            ).reset_index()
            pivoted_df.columns.name = None
            final_df = pivoted_df
            st.success("Dados pivotados com sucesso!")

    except Exception as e:
        st.error(f"Ocorreu um erro ao tentar pivotar os dados: {e}")
        st.info("O arquivo Excel será gerado com os dados no formato original (não pivotado).")
    
    st.dataframe(final_df)

    empresa = final_df['Empresa'].iloc[0]
    projeto = final_df['Projeto'].iloc[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"Resultados_{empresa}_{projeto}_{timestamp}.xlsx"
    
    excel_data = to_excel(final_df)

    st.download_button(
        label="📥 Baixar Arquivo XLSX Final",
        data=excel_data,
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    if st.button("Processar Novo Arquivo"):
        st.session_state.clear()
        st.rerun()
