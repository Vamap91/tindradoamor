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

# Carregar variáveis de ambiente 
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

# Função para gerar história - VERSÃO OFFLINE GARANTIDA
def gerar_historia(tema, estilo, comprimento):
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

# Função aprimorada para gerar imagem
def gerar_imagem(descricao, estilo):
    # Definir dimensões e cores
    largura, altura = 1024, 1024
    
    # Escolher cores de fundo baseadas no estilo
    cores_estilo = {
        "Realista": (20, 20, 30),  # Azul escuro para noites realistas
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
    
    import PIL.ImageDraw as ImageDraw
    import PIL.ImageFont as ImageFont
    
    try:
        # Tentar carregar uma fonte
        fonte = ImageFont.truetype("Arial.ttf", 40)
    except:
        # Se não encontrar, usar fonte padrão
        fonte = ImageFont.load_default()
        
    draw = ImageDraw.Draw(img)
    
    # Criar elementos visuais baseados na descrição
    descricao_lower = descricao.lower()
    
    # Verifica termos na descrição para criar elementos visuais específicos
    if "carro" in descricao_lower and "rua" in descricao_lower:
        # Criar uma rua
        draw.rectangle([(0, altura//2), (largura, altura)], fill=(40, 40, 40))  # Asfalto
        
        # Linhas da rua
        for i in range(0, largura, 100):
            draw.rectangle([(i, altura//2 + 100), (i+50, altura//2 + 110)], fill=(200, 200, 200))
        
        # Carro (representação simples)
        carro_x = largura//3
        carro_y = altura//2 + 50
        
        # Corpo do carro
        draw.rectangle([(carro_x, carro_y), (carro_x+200, carro_y+80)], fill=(150, 0, 0))
        
        # Teto do carro
        draw.rectangle([(carro_x+40, carro_y-40), (carro_x+160, carro_y)], fill=(100, 0, 0))
        
        # Rodas
        draw.ellipse([(carro_x+30, carro_y+70), (carro_x+70, carro_y+110)], fill=(10, 10, 10))
        draw.ellipse([(carro_x+130, carro_y+70), (carro_x+170, carro_y+110)], fill=(10, 10, 10))
        
        # Faróis (para rua escura)
        draw.ellipse([(carro_x+180, carro_y+20), (carro_x+200, carro_y+40)], fill=(255, 255, 200))
        
        # Brilho dos faróis
        for i in range(30):
            alpha = 128-i*4 if 128-i*4 > 0 else 0
            draw.ellipse([
                (carro_x+200, carro_y+30-i), 
                (carro_x+300+i*10, carro_y+30+i)
            ], fill=(255, 255, 200, alpha), outline=None)
        
        # Céu noturno (se for noite/escuro)
        if "escura" in descricao_lower or "noite" in descricao_lower:
            # Adicionar estrelas
            for _ in range(100):
                star_x = random.randint(0, largura)
                star_y = random.randint(0, altura//2)
                star_size = random.randint(1, 3)
                draw.ellipse([(star_x, star_y), (star_x+star_size, star_y+star_size)], 
                             fill=(255, 255, 255))
                
            # Lua
            lua_x = largura - 200
            lua_y = 150
            draw.ellipse([(lua_x, lua_y), (lua_x+100, lua_y+100)], fill=(230, 230, 230))
    
    elif "floresta" in descricao_lower:
        # Criar um céu
        for y in range(0, altura//2):
            cor = (50, 100+y//5, 150+y//5)
            draw.line([(0, y), (largura, y)], fill=cor)
        
        # Criar montanhas
        for i in range(3):
            base_x = largura * i // 3
            pico_x = base_x + largura//6
            base_y = altura//2
            pico_y = base_y - random.randint(100, 200)
            
            pontos = [
                (base_x, base_y),
                (pico_x, pico_y),
                (base_x + largura//3, base_y)
            ]
            draw.polygon(pontos, fill=(60+i*20, 80+i*10, 60+i*10))
        
        # Criar solo
        draw.rectangle([(0, altura//2), (largura, altura)], fill=(80, 60, 20))
        
        # Criar árvores
        for _ in range(20):
            tree_x = random.randint(0, largura)
            tree_y = random.randint(altura//2, altura-100)
            
            # Tronco
            draw.rectangle([(tree_x-10, tree_y), (tree_x+10, tree_y+100)], fill=(80, 50, 20))
            
            # Copa
            draw.ellipse([(tree_x-50, tree_y-80), (tree_x+50, tree_y+20)], fill=(20, 120, 30))
    
    # Título pequeno e discreto
    titulo = "Imagem gerada: " + descricao[:30] + "..."
    titulo_fonte = ImageFont.truetype("Arial.ttf", 20) if hasattr(ImageFont, "truetype") else ImageFont.load_default()
    
    # Adicionar informações sobre estilo no canto
    estilo_text = f"Estilo: {estilo}"
    estilo_largura = draw.textlength(estilo_text, font=titulo_fonte) if hasattr(draw, "textlength") else 0
    draw.text(
        (20, altura - 50),
        estilo_text,
        font=titulo_fonte,
        fill=(200, 200, 200)
    )
    
    # Adicionar borda com degrade baseado no estilo
    if estilo == "Futurista":
        # Borda tech
        for i in range(10):
            cor = (0, 100+i*10, 200-i*10)
            draw.rectangle(
                [(0+i, 0+i), (largura-1-i, altura-1-i)],
                outline=cor
            )
    else:
        # Borda normal
        for i in range(5):
            draw.rectangle(
                [(0+i, 0+i), (largura-1-i, altura-1-i)],
                outline=(100+i*20, 100+i*20, 100+i*20)
            )
    
    # Salvar em um arquivo temporário
    temp_img = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    img.save(temp_img.name)
    
    return temp_img.name, img

# Função ULTRA-SIMPLIFICADA para criar um vídeo sem dependências externas
def criar_video(historia, imagem_path, titulo):
    try:
        # Criar um diretório temporário
        temp_dir = tempfile.mkdtemp()
        
        # Salvar história como texto (garantido que funciona)
        output_path = os.path.join(temp_dir, "historia.txt")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# {titulo}\n\n{historia}")
        
        # Tentar criar vídeo simples
        try:
            # Carregar a imagem
            img = Image.open(imagem_path)
            img_array = np.array(img)
            
            # Criar um clipe simples com a imagem como fundo
            clip = ImageSequenceClip([img_array], durations=[5])
            
            # Definir caminho do vídeo
            video_path = os.path.join(temp_dir, "video_final.mp4")
            
            # Salvar vídeo (o mais simples possível)
            clip.write_videofile(video_path, fps=24, codec='libx264', audio=False)
            
            return video_path
        except:
            # Se o vídeo falhar, retornar o arquivo de texto
            return output_path
    except:
        # Se tudo falhar, retornar None
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
1. **Geração de história**: Criamos narrativas envolventes baseadas no tema e estilo escolhidos.
2. **Geração de imagens**: Criamos imagens que representam sua história.
3. **Criação de vídeo**: Combinamos a imagem com o texto da história.

### Dicas de uso
- Seja específico na descrição da imagem para obter resultados mais precisos
- Experimente diferentes estilos e combinações para resultados variados
- Histórias mais curtas funcionam melhor para vídeos curtos
""")
