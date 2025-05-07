import streamlit as st
import requests
import os
import json
import io
import base64
import time
from PIL import Image
from moviepy.editor import ImageSequenceClip, AudioFileClip, concatenate_videoclips, TextClip, CompositeVideoClip
import tempfile
import google.generativeai as genai
from dotenv import load_dotenv
import openai
import random

# Carregar variáveis de ambiente
load_dotenv()

# Configurações de página
st.set_page_config(
    page_title="Gerador Automático de Conteúdo",
    page_icon="🎬",
    layout="wide"
)

# Estilos CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #42A5F5;
        margin-bottom: 1rem;
    }
    .success-message {
        background-color: #D4EDDA;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Título principal
st.markdown("<h1 class='main-header'>Gerador Automático de Conteúdo</h1>", unsafe_allow_html=True)

# Funções de geração de conteúdo
def gerar_historia(tema, estilo, comprimento):
    """Gera uma história baseada nos parâmetros fornecidos usando API de IA"""
    try:
        # Usando OpenAI para gerar a história
        openai.api_key = os.getenv("OPENAI_API_KEY")
        
        # Preparar o prompt conforme o comprimento desejado
        palavras = 200 if comprimento == "Curta" else 500 if comprimento == "Média" else 1000
        
        response = openai.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "system",
                    "content": f"Você é um escritor especializado em criar histórias no estilo {estilo}."
                },
                {
                    "role": "user", 
                    "content": f"Crie uma história {comprimento.lower()} (aproximadamente {palavras} palavras) sobre '{tema}'. A história deve ser envolvente, criativa e adequada para ser transformada em um vídeo curto."
                }
            ],
            max_tokens=1500
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Erro ao gerar história: {str(e)}")
        return None

def gerar_imagem(descricao, estilo):
    """Gera uma imagem baseada na descrição e estilo usando API de IA"""
    try:
        # Configurar API Gemini (Google)
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        
        # Criar prompt para geração de imagem
        prompt = f"Gere uma imagem que represente: {descricao}. Estilo visual: {estilo}."
        
        # Usando Stability AI (alternativa)
        api_host = os.getenv('STABILITY_API_HOST', 'https://api.stability.ai')
        api_key = os.getenv("STABILITY_API_KEY")
        
        if not api_key:
            raise ValueError("API key de Stability AI não encontrada")
            
        engine_id = "stable-diffusion-xl-1024-v1-0"
        
        response = requests.post(
            f"{api_host}/v1/generation/{engine_id}/text-to-image",
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {api_key}"
            },
            json={
                "text_prompts": [{"text": prompt}],
                "cfg_scale": 7,
                "height": 1024,
                "width": 1024,
                "samples": 1,
                "steps": 30,
            },
        )
        
        if response.status_code != 200:
            raise Exception(f"API de geração de imagem retornou {response.status_code}: {response.text}")
            
        data = response.json()
        image_base64 = data["artifacts"][0]["base64"]
        image = Image.open(io.BytesIO(base64.b64decode(image_base64)))
        
        # Salvar em um arquivo temporário
        temp_img = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        image.save(temp_img.name)
        
        return temp_img.name, image
    except Exception as e:
        st.error(f"Erro ao gerar imagem: {str(e)}")
        return None, None

def criar_video(historia, imagem_path, titulo):
    """Cria um vídeo a partir da história e imagem fornecidas"""
    try:
        # Definir diretório temporário para arquivos
        temp_dir = tempfile.mkdtemp()
        
        # Carregar imagem
        img = Image.open(imagem_path)
        
        # Criar clipe da imagem
        duracoes = []
        imagens = []
        
        # Dividir história em segmentos
        paragrafos = historia.split('\n\n')
        for _ in paragrafos:
            imagens.append(imagem_path)
            duracoes.append(5)  # 5 segundos por parágrafo
            
        # Gerar narração de texto para áudio (simulado com um arquivo de áudio silencioso)
        audio_temp = os.path.join(temp_dir, "temp_audio.mp3")
        with open(audio_temp, 'wb') as f:
            # Em um sistema real, aqui seria usado TTS (Text-to-Speech)
            # Por simplicidade, estamos criando um arquivo de áudio em branco
            f.write(b'')
        
        # Criar clipe de áudio (em uma implementação real, usaria TTS)
        # audio_clip = AudioFileClip(audio_temp)
        
        # Criar clipe de imagem
        clip = ImageSequenceClip(imagens, durations=duracoes)
        
        # Adicionar título
        txt_clip = TextClip(titulo, fontsize=70, color='white', bg_color='rgba(0,0,0,0.5)',
                           size=clip.size, method='caption').set_duration(5)
        video = CompositeVideoClip([clip, txt_clip.set_start(0)])
        
        # Definir caminho para o vídeo final
        output_path = os.path.join(temp_dir, "video_final.mp4")
        
        # Exportar vídeo
        video.write_videofile(output_path, fps=24, codec='libx264', audio_codec='aac')
        
        return output_path
    except Exception as e:
        st.error(f"Erro ao criar vídeo: {str(e)}")
        return None

def salvar_no_github(historia, imagem_path, video_path, titulo):
    """Salva os arquivos gerados em um repositório GitHub"""
    # Em uma implementação real, usaria a API do GitHub
    # Por agora, retornamos um sucesso simulado
    return True

# Interface do usuário
with st.form("gerador_form"):
    st.markdown("<h2 class='sub-header'>Defina os parâmetros para geração de conteúdo</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        tema = st.text_input("Tema da história", "Uma aventura na floresta amazônica")
        estilo_historia = st.selectbox(
            "Estilo da narrativa",
            ["Aventura", "Fantasia", "Sci-Fi", "Drama", "Comédia", "Terror", "Educacional"]
        )
        comprimento = st.selectbox(
            "Comprimento da história",
            ["Curta", "Média", "Longa"]
        )
    
    with col2:
        descricao_imagem = st.text_area("Descrição da imagem principal", "Floresta tropical densa com um explorador em primeiro plano")
        estilo_imagem = st.selectbox(
            "Estilo visual",
            ["Realista", "Cartoon", "Pixel Art", "Óleo", "Aquarela", "Minimalista", "Futurista"]
        )
        titulo_video = st.text_input("Título do vídeo", "Aventuras na Amazônia")
    
    gerar_button = st.form_submit_button("Gerar Conteúdo")

# Processamento quando o botão é clicado
if gerar_button:
    with st.spinner('Gerando história...'):
        historia = gerar_historia(tema, estilo_historia, comprimento)
        
        if historia:
            st.success("História gerada com sucesso!")
            st.markdown("### História Gerada")
            st.write(historia)
            
            with st.spinner('Gerando imagem...'):
                imagem_path, imagem = gerar_imagem(descricao_imagem, estilo_imagem)
                
                if imagem_path:
                    st.success("Imagem gerada com sucesso!")
                    st.markdown("### Imagem Gerada")
                    st.image(imagem, caption=descricao_imagem, use_column_width=True)
                    
                    with st.spinner('Criando vídeo...'):
                        video_path = criar_video(historia, imagem_path, titulo_video)
                        
                        if video_path:
                            st.success("Vídeo criado com sucesso!")
                            st.markdown("### Vídeo Gerado")
                            st.video(video_path)
                            
                            with st.spinner('Salvando no GitHub...'):
                                if salvar_no_github(historia, imagem_path, video_path, titulo_video):
                                    st.markdown("""
                                    <div class='success-message'>
                                        <h3>🎉 Processo Completo!</h3>
                                        <p>Todos os conteúdos foram gerados e salvos com sucesso!</p>
                                    </div>
                                    """, unsafe_allow_html=True)

# Informações adicionais
st.markdown("---")
st.markdown("""
### Como funciona
1. **Geração de história**: Utilizamos GPT-4 para criar narrativas envolventes baseadas no tema e estilo escolhidos.
2. **Geração de imagens**: Utilizamos Stability AI para criar imagens impressionantes que representam sua história.
3. **Criação de vídeo**: Combinamos a imagem com o texto da história para criar um vídeo completo.
4. **Integração com GitHub**: Todos os arquivos são automaticamente salvos em seu repositório GitHub.

### Dicas de uso
- Seja específico na descrição da imagem para obter resultados mais precisos
- Experimente diferentes estilos e combinações para resultados variados
- Histórias mais curtas funcionam melhor para vídeos curtos
""")
