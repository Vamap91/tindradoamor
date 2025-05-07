# Sistema de Geração Automática de Conteúdo

## Visão Geral
Este sistema desenvolvido com Streamlit e Python permite a geração automática de histórias, imagens e vídeos a partir de prompts fornecidos pelo usuário. O projeto utiliza APIs de inteligência artificial para criar conteúdo original e oferece integração com GitHub para armazenamento dos arquivos gerados.

## Funcionalidades
- **Geração de histórias**: Cria narrativas personalizadas baseadas em temas e estilos escolhidos pelo usuário
- **Geração de imagens**: Produz imagens que representam visualmente a história
- **Criação de vídeos**: Combina imagens e texto para criar vídeos automáticos
- **Integração com GitHub**: Salva todo o conteúdo gerado em um repositório

## Pré-requisitos
- Python 3.8+
- Conta em serviços de API (OpenAI, Stability AI, Google AI)
- Conta GitHub (para integração)

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/gerador-automatico-conteudo.git
cd gerador-automatico-conteudo
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure as variáveis de ambiente criando um arquivo `.env` na raiz do projeto:
```
OPENAI_API_KEY=sua_chave_openai
STABILITY_API_KEY=sua_chave_stability
GEMINI_API_KEY=sua_chave_gemini
GITHUB_TOKEN=seu_token_github
```

## Uso

Para executar o aplicativo localmente:
```bash
streamlit run app.py
```

Acesse o aplicativo em seu navegador em `http://localhost:8501`.

## Implantação no GitHub

### Configurando o repositório:

1. Crie um novo repositório no GitHub
2. Adicione os arquivos ao repositório:
```bash
git add .
git commit -m "Versão inicial do gerador de conteúdo"
git push origin main
```

### GitHub Actions para automação:

Para configurar uma pipeline de CI/CD, crie um arquivo `.github/workflows/deploy.yml` com o seguinte conteúdo:

```yaml
name: Deploy Streamlit App

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
    - name: Test application
      run: |
        pytest
```

## Estrutura do Projeto
```
.
├── app.py                # Aplicativo Streamlit principal
├── requirements.txt      # Dependências Python
├── .env                  # Variáveis de ambiente (não incluído no git)
├── .gitignore            # Arquivos a serem ignorados pelo git
├── README.md             # Documentação
└── .github/              # Configurações do GitHub Actions
    └── workflows/
        └── deploy.yml    # Pipeline de CI/CD
```

## Contribuição
Contribuições são bem-vindas! Por favor, sinta-se à vontade para enviar um Pull Request.

## Licença
Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.

## Créditos
- OpenAI API - Geração de texto
- Stability AI - Geração de imagens
- Google AI (Gemini) - Processamento de conteúdo
- Streamlit - Framework de interface

## Contato
Para quaisquer dúvidas ou sugestões, abra uma issue no GitHub ou entre em contato através de [seu-email@exemplo.com].
