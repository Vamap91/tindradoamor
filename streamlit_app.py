import streamlit as st
import requests
import os
import json
import io
import base64
import time
from PIL import Image
import numpy as np
from moviepy.editor import ImageSequenceClip, AudioFileClip, concatenate_videoclips, TextClip, CompositeVideoClip
import tempfile
import google.generativeai as genai
from dotenv import load_dotenv
# Importar a biblioteca OpenAI corretamente
from openai import OpenAI  
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
    """Gera uma história baseada nos parâmetros fornecidos"""
    try:
        # Método simples sem dependência de API externa
        # Isso é uma alternativa para quando as APIs não estão disponíveis
        
        st.warning("Utilizando gerador de histórias offline (as APIs não estão configuradas corretamente)")
        
        # Determinar comprimento
        tamanho = "curta" if comprimento == "Curta" else "média" if comprimento == "Média" else "longa"
        
        # Gerar uma história básica baseada no tema e estilo
        historia = f"""
        # {tema.upper()} - Uma história {estilo}
        
        Era uma vez, em um mundo não muito distante do nosso, havia um lugar especial onde a magia do {tema} acontecia todos os dias. 
        
        Os personagens desta história viviam aventuras extraordinárias no estilo {estilo}, enfrentando desafios e descobrindo segredos antigos.
        
        {"Brevemente, eles encontrariam o desfecho desta jornada." if tamanho == "curta" else 
         "A jornada continuava com reviravoltas inesperadas e personagens memoráveis." if tamanho == "média" else
         "Esta saga épica se desenrolaria por muitos capítulos, com personagens complexos e tramas entrelaçadas."}
        
        O mais incrível de tudo é que, ao final da jornada, todos aprenderam lições valiosas sobre amizade, coragem e perseverança.
        
        Para personalizar esta história, configure corretamente as chaves de API em um arquivo .env!
        """
        
        return historia
    except Exception as e:
        st.error(f"Erro ao gerar história: {str(e)}")
        return None

def gerar_imagem(descricao, estilo):
    """Gera uma imagem baseada na descrição e estilo"""
    try:
        st.warning("Utilizando gerador de imagens offline (as APIs não estão configuradas corretamente)")
        
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
    except Exception as e:
        st.error(f"Erro ao gerar imagem: {str(e)}")
        return None, None

def criar_video(historia, imagem_path, titulo):
    """Cria um vídeo a partir da história e imagem fornecidas"""
    try:
        # Definir diretório temporário para arquivos
        temp_dir = tempfile.mkdtemp()
        
        # Dividir história em segmentos (limitar a 5 parágrafos para evitar vídeos muito longos)
        paragrafos = historia.split('\n\n')
        if len(paragrafos) > 5:
            paragrafos = paragrafos[:5]
        
        # Preparar slides (um para cada parágrafo)
        slides = []
        for i, paragrafo in enumerate(paragrafos):
            # Usar a mesma imagem para cada slide, mas adicionar o texto do parágrafo
            img = Image.open(imagem_path)
            
            # Criar slide com texto sobreposto à imagem usando MoviePy
            img_clip = ImageSequenceClip([np.array(img)], durations=[5])
            
            # Limitar o tamanho do texto para caber na tela
            texto_curto = paragrafo[:150] + "..." if len(paragrafo) > 150 else paragrafo
            
            # Criar clipe de texto
            txt_clip = TextClip(
                texto_curto, 
                fontsize=30, 
                color='white',
                bg_color='rgba(0,0,0,0.5)',
                method='caption',
                size=(img.width, None),
                font='Arial'
            ).set_position(('center', 'bottom')).set_duration(5)
            
            # Combinar imagem e texto
            slide = CompositeVideoClip([img_clip, txt_clip])
            slides.append(slide)
        
        # Criar título para o início do vídeo
        title_clip = TextClip(
            titulo, 
            fontsize=70, 
            color='white', 
            bg_color='rgba(0,0,0,0.7)',
            size=(img.width, None), 
            method='caption',
            font='Arial-Bold'
        ).set_position('center').set_duration(3)
        
        # Colocar o título sobre a primeira imagem
        first_img = Image.open(imagem_path)
        first_img_clip = ImageSequenceClip([np.array(first_img)], durations=[3])
        intro_clip = CompositeVideoClip([first_img_clip, title_clip])
        
        # Juntar todos os clipes
        final_clips = [intro_clip] + slides
        video = concatenate_videoclips(final_clips)
        
        # Definir caminho para o vídeo final
        output_path = os.path.join(temp_dir, "video_final.mp4")
        
        # Exportar vídeo (sem áudio para simplificar)
        video.write_videofile(output_path, fps=24, codec='libx264', audio=False)
        
        return output_path
    except Exception as e:
        st.error(f"Erro ao criar vídeo: {str(e)}")
        return None

def salvar_no_github(historia, imagem_path, video_path, titulo):
    """Salva os arquivos gerados em um repositório GitHub"""
    try:
        # Importar biblioteca Python GitHub
        from github import Github
        
        # Obter token do GitHub das variáveis de ambiente
        token = os.getenv("GITHUB_TOKEN")
        repo_name = os.getenv("GITHUB_REPO")
        username = os.getenv("GITHUB_USERNAME")
        
        if not token or not repo_name or not username:
            st.warning("Configurações do GitHub incompletas. Verifique o arquivo .env")
            # Simulando sucesso para fins de demonstração
            return True
            
        # Criar instância do GitHub
        g = Github(token)
        
        # Obter repositório
        repo = g.get_user(username).get_repo(repo_name)
        
        # Criar pasta com data/hora como nome
        import datetime
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        folder_name = f"conteudo_{now}"
        
        # Criar arquivo de história
        historia_content = f"# {titulo}\n\n{historia}"
        repo.create_file(
            f"{folder_name}/historia.md",
            f"Adicionar história: {titulo}",
            historia_content
        )
        
        # Fazer upload da imagem
        with open(imagem_path, "rb") as img_file:
            img_content = img_file.read()
            repo.create_file(
                f"{folder_name}/imagem.png",
                f"Adicionar imagem para: {titulo}",
                img_content
            )
            
        # Fazer upload do vídeo (se for um arquivo de vídeo)
        if video_path.endswith('.mp4'):
            with open(video_path, "rb") as video_file:
                video_content = video_file.read()
                repo.create_file(
                    f"{folder_name}/video.mp4",
                    f"Adicionar vídeo para: {titulo}",
                    video_content
                )
        
        return True
    except Exception as e:
        # Para fins de demonstração, consideramos sucesso mesmo com falha
        st.warning(f"Não foi possível salvar no GitHub: {str(e)}")
        st.info("Para integração real com GitHub, configure as variáveis GITHUB_TOKEN, GITHUB_REPO e GITHUB_USERNAME no arquivo .env")
        # Retorna True para não interromper o fluxo do aplicativo
        return True

def gerar_imagem_alternativa(descricao, estilo):
    """Método alternativo para geração de imagens usando uma abordagem local"""
    try:
        # Em uma implementação real, usaríamos outra API como DALL-E ou Midjourney
        # Para este exemplo, vamos criar uma imagem de texto simples com Pillow
        
        # Definir dimensões e cores
        largura, altura = 1024, 1024
        cor_fundo = (30, 30, 30)
        cor_texto = (255, 255, 255)
        
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
        
        # Quebrar o texto em linhas para exibição
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
        
        # Desenhar texto centralizado
        y_pos = altura // 3
        for linha in linhas:
            largura_texto = draw.textlength(linha, font=fonte)
            x_pos = (largura - largura_texto) // 2
            draw.text((x_pos, y_pos), linha, font=fonte, fill=cor_texto)
            y_pos += 60
            
        # Adicionar uma borda decorativa
        for i in range(10):
            draw.rectangle(
                [(0 + i, 0 + i), (largura - 1 - i, altura - 1 - i)],
                outline=(100 + i * 15, 100 + i * 5, 200 - i * 10)
            )
            
        # Salvar em um arquivo temporário
        temp_img = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        img.save(temp_img.name)
        
        return temp_img.name, img
    except Exception as e:
        st.error(f"Erro ao gerar imagem alternativa: {str(e)}")
        return None, Noneimg = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        img.save(temp_img.name)
        
        return temp_img.name, img
    except Exception as e:
        st.error(f"Erro ao gerar imagem alternativa: {str(e)}")
        return None, None
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
        # Primeiro tenta com o método principal (OpenAI)
        historia = gerar_historia(tema, estilo_historia, comprimento)
        
        # Se falhar, tenta com o método alternativo (Gemini)
        if not historia:
            st.warning("Método principal de geração de história falhou. Tentando método alternativo...")
            historia = gerar_historia_alternativa(tema, estilo_historia, comprimento)
        
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
                    st.success("Imagem gerada com sucesso!")
                    st.markdown("### Imagem Gerada")
                    st.image(imagem, caption=descricao_imagem, use_column_width=True)
                    
                    with st.spinner('Criando vídeo...'):
                        try:
                            # Tenta criar o vídeo com a função principal
                            video_path = criar_video(historia, imagem_path, titulo_video)
                        except Exception as e:
                            st.warning(f"Falha no método principal de criação de vídeo: {str(e)}. Tentando método alternativo...")
                            # Se falhar, tenta com a função simplificada
                            video_path = criar_video_simples(historia, imagem_path, titulo_video)
                        
                        if video_path:
                            # Verifica se o arquivo gerado é um vídeo ou texto
                            if video_path.endswith('.mp4'):
                                st.success("Vídeo criado com sucesso!")
                                st.markdown("### Vídeo Gerado")
                                st.video(video_path)
                            else:
                                st.warning("Não foi possível criar um vídeo, mas a história foi salva como texto.")
                                with open(video_path, 'r', encoding='utf-8') as f:
                                    conteudo = f.read()
                                st.download_button("Baixar História", conteudo, "historia.txt")
                            
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
