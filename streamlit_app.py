import streamlit as st
import requests
import os
import io
import base64
import tempfile
from PIL import Image
import numpy as np
from moviepy.editor import ImageSequenceClip, TextClip, CompositeVideoClip
from dotenv import load_dotenv
import time
import random

# Carregar variáveis de ambiente do arquivo .env (para desenvolvimento local)
load_dotenv()

# Configuração da página
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

# Função para obter chaves de API (primeiro de Streamlit secrets, depois de .env)
def get_api_key(key_name):
    try:
        # Primeiro tenta obter do Streamlit secrets
        return st.secrets[key_name]
    except:
        # Se não encontrar, tenta do arquivo .env
        return os.getenv(key_name)

# Função para gerar história
def gerar_historia(tema, estilo, comprimento):
    try:
        # Verificar se temos a chave da OpenAI
        api_key = get_api_key("OPENAI_API_KEY")
        
        if api_key:
            # Usar método antigo e compatível para evitar erros de proxies
            import openai
            openai.api_key = api_key
            
            # Preparar o prompt conforme o comprimento desejado
            palavras = 200 if comprimento == "Curta" else 500 if comprimento == "Média" else 1000
            
            # Fazer a requisição para a API usando o método antigo
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
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
            
            # Extrair e retornar o conteúdo da resposta (método antigo)
            return response.choices[0].message.content
        else:
            # Se não tiver a chave, usa método alternativo
            st.warning("API OpenAI não configurada. Usando gerador alternativo.")
            return gerar_historia_offline(tema, estilo, comprimento)
            
    except Exception as e:
        st.error(f"Erro ao gerar história: {str(e)}")
        return gerar_historia_offline(tema, estilo, comprimento)

# Função alternativa para gerar história sem API
def gerar_historia_offline(tema, estilo, comprimento):
    # Estilo da história
    estilos = {
        "Aventura": "com muita ação e exploração",
        "Fantasia": "com elementos mágicos e criaturas fantásticas",
        "Sci-Fi": "com tecnologia futurista e conceitos científicos",
        "Drama": "com intensidade emocional e conflitos internos",
        "Comédia": "com situações engraçadas e diálogos divertidos",
        "Terror": "com elementos assustadores e suspense",
        "Educacional": "com fatos interessantes e lições importantes"
    }
    
    estilo_desc = estilos.get(estilo, "interessante")
    
    # Comprimento da história
    if comprimento == "Curta":
        paragrafos = 3
        intro = f"Uma breve história {estilo_desc} sobre {tema}."
    elif comprimento == "Média":
        paragrafos = 5
        intro = f"Uma história {estilo_desc} de tamanho médio sobre {tema}."
    else:
        paragrafos = 7
        intro = f"Uma história mais longa {estilo_desc} sobre {tema}."
        
    # Gerar a história
    historia = f"# {tema.title()}\n\n"
    historia += intro + "\n\n"
    
    # Adicionar alguns parágrafos genéricos mas temáticos
    for i in range(paragrafos):
        if i == 0:
            historia += f"Em um mundo onde {tema.lower()} era parte do cotidiano, nossos protagonistas descobriram algo extraordinário. "
            historia += f"Era uma manhã comum quando tudo começou a mudar de maneira inesperada.\n\n"
        elif i == 1:
            historia += f"O primeiro desafio apareceu quando eles menos esperavam. "
            historia += f"Como verdadeiros heróis de uma história {estilo.lower()}, eles enfrentaram o problema com determinação.\n\n"
        elif i == 2:
            historia += f"À medida que a jornada continuava, segredos sobre {tema.lower()} começavam a se revelar. "
            historia += f"Cada descoberta trazia mais perguntas do que respostas.\n\n"
        elif i == 3:
            historia += f"Os personagens precisavam tomar decisões difíceis. "
            historia += f"O caminho não era fácil, mas as lições aprendidas valiam cada passo.\n\n"
        elif i == 4:
            historia += f"Quando tudo parecia perdido, uma reviravolta surpreendente mudou o curso da história. "
            historia += f"Era como se o próprio {tema.lower()} estivesse conspirando a favor deles.\n\n"
        elif i == 5:
            historia += f"O confronto final estava próximo. Todos os caminhos levavam a este momento decisivo. "
            historia += f"A tensão crescia a cada segundo, típico de uma grande história {estilo.lower()}.\n\n"
        else:
            historia += f"No fim, quando a poeira baixou, o mundo nunca mais seria o mesmo. "
            historia += f"O {tema.lower()} havia transformado a vida de todos para sempre, deixando um legado inesquecível.\n\n"
    
    return historia

# Função para gerar imagem
def gerar_imagem(descricao, estilo):
    try:
        # Verificar se temos a chave da Stability AI
        api_key = get_api_key("STABILITY_API_KEY")
        
        if api_key:
            # Criar prompt para geração de imagem
            prompt = f"Gere uma imagem que represente: {descricao}. Estilo visual: {estilo}."
            
            # Configurar API Stability AI
            url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
            
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            payload = {
                "text_prompts": [{"text": prompt}],
                "cfg_scale": 7,
                "height": 1024,
                "width": 1024,
                "samples": 1,
                "steps": 30,
            }
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code != 200:
                st.error(f"Erro na API de imagem: {response.status_code}")
                return gerar_imagem_offline(descricao, estilo)
                
            data = response.json()
            image_base64 = data["artifacts"][0]["base64"]
            image = Image.open(io.BytesIO(base64.b64decode(image_base64)))
            
            # Salvar em um arquivo temporário
            temp_img = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            image.save(temp_img.name)
            
            return temp_img.name, image
        else:
            # Se não tiver a chave, usa método alternativo
            st.warning("API Stability AI não configurada. Usando gerador alternativo.")
            return gerar_imagem_offline(descricao, estilo)
            
    except Exception as e:
        st.error(f"Erro ao gerar imagem: {str(e)}")
        return gerar_imagem_offline(descricao, estilo)

# Função alternativa para gerar imagem sem API
def gerar_imagem_offline(descricao, estilo):
    # Definir dimensões e cores
    largura, altura = 1024, 1024
    
    # Escolher cores de fundo baseadas no estilo
    cores_estilo = {
        "Realista": (50, 50, 50),
        "Cartoon": (80, 150, 200),
        "Pixel Art": (40, 40, 40),
        "Óleo": (120, 90, 60),
        "Aquarela": (230, 220, 210),
        "Minimalista": (250, 250, 250),
        "Futurista": (20, 30, 80)
    }
    
    cor_fundo = cores_estilo.get(estilo, (30, 30, 30))
    
    # Criar uma imagem em branco
    img = Image.new('RGB', (largura, altura), cor_fundo)
    
    # Adicionar texto descritivo
    import PIL.ImageDraw as ImageDraw
    import PIL.ImageFont as ImageFont
    
    try:
        # Tentar carregar uma fonte
        fonte = ImageFont.truetype("Arial.ttf", 40)
    except:
        # Se não encontrar, usar fonte padrão
        fonte = ImageFont.load_default()
        
    draw = ImageDraw.Draw(img)
    
    # Adicionar título
    titulo = "Visualização Imaginária"
    titulo_fonte = fonte
    
    # Centralizar título
    titulo_largura = draw.textlength(titulo, font=titulo_fonte)
    draw.text(((largura - titulo_largura) // 2, 100), titulo, font=titulo_fonte, fill=(255, 255, 255))
    
    # Quebrar a descrição em linhas
    linhas = []
    palavras = descricao.split()
    linha_atual = ""
    
    for palavra in palavras:
        if len(linha_atual + palavra) < 30:
            linha_atual += palavra + " "
        else:
            linhas.append(linha_atual)
            linha_atual = palavra + " "
    
    if linha_atual:
        linhas.append(linha_atual)
        
    # Adicionar informações sobre estilo
    linhas.append("")
    linhas.append(f"Estilo: {estilo}")
    
    # Desenhar descrição centralizada
    y_pos = altura // 3
    for linha in linhas:
        largura_texto = draw.textlength(linha, font=fonte)
        x_pos = (largura - largura_texto) // 2
        draw.text((x_pos, y_pos), linha, font=fonte, fill=(255, 255, 255))
        y_pos += 60
        
    # Adicionar elementos visuais baseados no estilo
    if estilo == "Cartoon":
        # Adicionar um sol simples
        draw.ellipse([(700, 200), (850, 350)], fill=(255, 220, 0))
    elif estilo == "Pixel Art":
        # Adicionar grade de pixels
        pixel_size = 32
        for x in range(0, largura, pixel_size):
            for y in range(0, altura, pixel_size):
                if (x + y) % (pixel_size * 2) == 0:
                    draw.rectangle([(x, y), (x + pixel_size, y + pixel_size)], fill=(60, 60, 80))
    elif estilo == "Futurista":
        # Adicionar linhas de grade
        for i in range(0, largura, 50):
            draw.line([(i, 0), (i, altura)], fill=(0, 100, 200, 128), width=1)
            draw.line([(0, i), (largura, i)], fill=(0, 150, 200, 128), width=1)
            
    # Adicionar uma borda decorativa
    for i in range(10):
        draw.rectangle(
            [(0 + i, 0 + i), (largura - 1 - i, altura - 1 - i)],
            outline=(100 + i * 15, 100 + i * 5, 200 - i * 10)
        )
        
    # Texto informativo na parte inferior
    info_text = "Imagem gerada localmente. Configure APIs para imagens reais."
    info_largura = draw.textlength(info_text, font=fonte)
    draw.text(
        ((largura - info_largura) // 2, altura - 100),
        info_text,
        font=fonte,
        fill=(200, 200, 200)
    )
        
    # Salvar em um arquivo temporário
    temp_img = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    img.save(temp_img.name)
    
    return temp_img.name, img

# Função para criar um vídeo muito simples (sem ImageMagick)
def criar_video(historia, imagem_path, titulo):
    try:
        # Criar um diretório temporário
        temp_dir = tempfile.mkdtemp()
        
        # Carregar a imagem
        img = Image.open(imagem_path)
        img_array = np.array(img)
        
        # Criar um clipe simples com a imagem como fundo
        clip = ImageSequenceClip([img_array], durations=[10])
        
        # Criar um texto simples para o vídeo
        # O parâmetro method='label' é crucial para evitar dependência do ImageMagick
        texto = TextClip(titulo, fontsize=70, font='Arial', color='white', 
                        bg_color='black', method='label', size=(img.width - 100, None))
        texto = texto.set_position('center').set_duration(10)
        
        # Combinar a imagem e o texto
        video = CompositeVideoClip([clip, texto])
        
        # Salvar o vídeo
        output_path = os.path.join(temp_dir, "video_final.mp4")
        video.write_videofile(output_path, fps=24, codec='libx264', audio=False)
        
        return output_path
    except Exception as e:
        st.error(f"Erro ao criar vídeo: {str(e)}")
        # Se falhar, retornar pelo menos a história como texto
        try:
            output_path = os.path.join(temp_dir, "historia.txt")
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(f"# {titulo}\n\n{historia}")
            return output_path
        except:
            return None

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
                        
                        if video_path and video_path.endswith('.mp4'):
                            st.success("Vídeo criado com sucesso!")
                            st.markdown("### Vídeo Gerado")
                            st.video(video_path)
                        elif video_path:
                            st.warning("Vídeo não pôde ser criado, mas a história foi salva.")
                            with open(video_path, 'r', encoding='utf-8') as f:
                                conteudo = f.read()
                            st.download_button("Baixar História", conteudo, "historia.txt")
                        
                        st.markdown("""
                        <div class='success-message'>
                            <h3>🎉 Processo Completo!</h3>
                            <p>Todos os conteúdos foram gerados com sucesso!</p>
                        </div>
                        """, unsafe_allow_html=True)

# Informações adicionais
st.markdown("---")
st.markdown("""
### Como funciona
1. **Geração de história**: Utilizamos IA para criar narrativas envolventes baseadas no tema e estilo escolhidos.
2. **Geração de imagens**: Utilizamos IA para criar imagens impressionantes que representam sua história.
3. **Criação de vídeo**: Combinamos a imagem com o texto da história para criar um vídeo completo.

### Dicas de uso
- Seja específico na descrição da imagem para obter resultados mais precisos
- Experimente diferentes estilos e combinações para resultados variados
- Histórias mais curtas funcionam melhor para vídeos curtos
""")
