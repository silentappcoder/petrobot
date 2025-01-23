import os
import streamlit as st
from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate
from langchain_community.document_loaders import PyPDFLoader

# Configuração da API
api_key = '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'
os.environ['GROQ_API_KEY'] = api_key
chat = ChatGroq(model='llama-3.3-70b-versatile')

# Pasta para armazenar uploads
upload_folder = os.path.join(os.getcwd(), 'uploaded_document')

# Cria a pasta se ela não existir
if not os.path.exists(upload_folder):
    os.mkdir(upload_folder)

# Cabeçalho do app
st.header("PetroBot App")
uploaded_file = st.file_uploader("Selecione os arquivos necessários")
documentos = ""

# Processamento do arquivo carregado
if uploaded_file is not None:
    file_name = uploaded_file.name
    saved_path = os.path.join(upload_folder, file_name)

    with open(saved_path, 'wb') as f:
        f.write(uploaded_file.getbuffer())
    st.success(f'Documento salvo: {file_name}')

    # Verifica se o arquivo é um PDF
    if uploaded_file.type == "application/pdf":
        try:
            loader = PyPDFLoader(saved_path)
            lista_documentos = loader.load()
            documentos = "".join(
                [doc.page_content for doc in lista_documentos])
            st.success("Documento processado com sucesso.")
        except Exception as e:
            st.error(f"Erro ao carregar o documento: {e}")
            documentos = ""
    else:
        st.error("Por favor, envie um arquivo PDF válido.")
        documentos = ""

# Função para processar a pergunta e retornar a resposta


def resposta_petrobot(pergunta):
    try:
        if not documentos.strip():
            return "Nenhum documento foi carregado para consulta."
        if not pergunta or not pergunta.strip():
            return "Por favor, insira uma pergunta válida."

        mensagens_modelo = [
            ('system',
             'Você se chama PetroBot. Você tem os seguintes documentos para se basear nas respostas: {documentos_informados}'),
            ('user', pergunta)
        ]
        template = ChatPromptTemplate.from_messages(mensagens_modelo)
        chain = template | chat
        return chain.invoke({'documentos_informados': documentos}).content
    except Exception as e:
        return f"Erro ao processar a resposta: {e}"


# Controle de estado das mensagens
if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

# Exibe as mensagens na interface
for mensagem in st.session_state.mensagens:
    with st.chat_message(mensagem["role"]):
        st.markdown(mensagem['content'])

# Entrada do usuário
prompt = st.chat_input("Pergunte ao PetroBot")

# Processa a pergunta
if prompt:
    st.chat_message("user").markdown(prompt)
    st.session_state.mensagens.append({"role": "user", "content": prompt})

    # Obtém a resposta
    resposta = resposta_petrobot(prompt)
    with st.chat_message("assistant"):
        st.markdown(resposta)

    st.session_state.mensagens.append(
        {"role": "assistant", "content": resposta})
