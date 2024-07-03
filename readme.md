# Projeto Financeiro

Este projeto tem como objetivo criar uma aplicação web para análise de dados financeiros utilizando Flask, MongoDB e Bokeh. A aplicação conecta-se ao Yahoo Finance para recuperar dados históricos de ações, armazena esses dados no MongoDB (uma base de dados NoSQL) e exibe visualizações gráficas desses dados juntamente com recomendações de compra, venda ou manutenção com base em médias móveis simples.

## Funcionalidades

1. **Conexão ao Yahoo Finance:**
   - A aplicação conecta-se à API do Yahoo Finance para recuperar dados históricos de ações com base no símbolo fornecido pelo utilizador.

2. **Armazenamento no MongoDB:**
   - Os dados recuperados do Yahoo Finance são armazenados no MongoDB. Cada ação é armazenada como um documento na coleção `stocks` na base de dados `stock_data`.

3. **Análise de Investimento e Recomendação:**
   - Com base nos dados históricos das ações, a aplicação calcula médias móveis de 20 e 50 dias.
   - É feita uma recomendação de "Compra" se a média móvel de 20 dias estiver acima da média móvel de 50 dias.
   - É feita uma recomendação de "Venda" se a média móvel de 20 dias estiver abaixo da média móvel de 50 dias.
   - É feita uma recomendação de "Manutenção" se as médias móveis não mostrarem um padrão claro.

4. **Visualização Gráfica com Bokeh:**
   - Utiliza a biblioteca Bokeh para criar gráficos interativos dos preços de fechamento das ações e suas médias móveis.
   - Os gráficos são incorporados na página web para fácil visualização e compreensão dos dados.

5. **Autenticação de Utilizadores:**
   - Implementa um sistema simples de login para restringir o acesso à aplicação a utilizadores autenticados.

6. **Alertas:**
   - Os utilizadores podem definir alertas de preço para ações específicas. Quando uma ação atinge a condição de preço especificada (acima ou abaixo), o utilizador é notificado.

7. **Atualizações em Tempo Real:**
   - Utiliza o Socket.IO para fornecer atualizações em tempo real para os dados das ações e alertas.

## Pré-requisitos

Para executar esta aplicação localmente, é necessário ter o Python instalado juntamente com as bibliotecas especificadas no ficheiro `requirements.txt`. Além disso, um servidor MongoDB deve estar em execução na máquina local ou numa máquina remota acessível.

## Instalação e Execução

1. **Clonar o repositório:**
   - Execute o comando `git clone https://github.com/Dark1nessss/Finance-Bot`
   - Navegue para o diretório do projeto com o comando `cd Finance-Bot`

2. **Instalar as dependências:**
   - Execute o comando `pip install -r requirements.txt`

3. **Configurar o MongoDB:**
   - Certifique-se de que o servidor MongoDB está em execução.

4. **Executar a aplicação:**
   - Execute o comando `python app.py`

5. **Aceder à aplicação:**
   - Abra o navegador e vá para `http://localhost:5000`.

## Utilização

1. **Buscar dados de ações:**
   - Na página inicial, insira o símbolo de uma ação (por exemplo, AAPL para Apple) e clique em "Fetch Data".
   - Isto buscará os dados mais recentes das ações do Yahoo Finance e armazená-los-á no MongoDB.

2. **Visualizar dados e recomendação:**
   - Após buscar os dados, pode clicar em "Show Data" para visualizar os dados históricos das ações, um gráfico com médias móveis e uma recomendação de investimento.

## Ferramentas e Bibliotecas

- **Flask:** Framework web que ajuda a interagir com HTML usando Python.
  - [Documentação Flask](https://flask.palletsprojects.com/en/2.0.x/)

- **Flask-SocketIO:** Adiciona suporte para comunicação em tempo real entre o servidor e os clientes.
  - [Documentação Flask-SocketIO](https://flask-socketio.readthedocs.io/en/latest/)

- **Bokeh:** Ajuda na criação de imagens/gráficos e muito mais.
  - [Documentação Bokeh](https://docs.bokeh.org/en/latest/index.html)

- **pymongo:** Framework que facilita a conexão entre Python e MongoDB.
  - [Documentação pymongo](https://pymongo.readthedocs.io/en/stable/)

- **yfinance:** API do Yahoo Finance para auxiliar com bots e mais.
  - [Repositório GitHub yfinance](https://github.com/ranaroussi/yfinance)

- **pandas:** Biblioteca de manipulação e análise de dados.
  - [Documentação pandas](https://pandas.pydata.org/docs/)

- **datetime:** Biblioteca para manipulação de datas em Python.
  - [Documentação datetime](https://docs.python.org/3/library/datetime.html)

- **SweetAlert:** Biblioteca para substituição de caixas de diálogo JavaScript por pop-ups bonitos, responsivos, personalizáveis e acessíveis (WAI-ARIA).
  - [Documentação SweetAlert](https://sweetalert.js.org/)

## Sistema de Alertas

A aplicação inclui uma funcionalidade onde os utilizadores podem definir alertas para preços específicos de ações. Quando o preço da ação ultrapassa o limite definido, o utilizador recebe uma notificação.

### Definir Alertas

1. **Navegar para a Página de Alertas:**
   - Utilize a barra de navegação para ir para a página "Alerts".

2. **Definir um Novo Alerta:**
   - Insira o símbolo da ação (por exemplo, AAPL para Apple).
   - Selecione a condição ("above" ou "below").
   - Insira o preço-alvo para o alerta.
   - Clique em "Set Alert".

### Visualizar e Gerir Alertas

- A página de alertas exibe todos os alertas definidos pelo utilizador.
- Os utilizadores podem remover um alerta clicando no botão "Remove" ao lado do respetivo alerta.

### Notificações em Tempo Real

- A aplicação utiliza WebSockets para fornecer notificações em tempo real quando uma ação atinge o limite de alerta.
- As notificações aparecem como pop-ups no canto superior direito da tela.

## Simular Alertas

Para fins de teste, a aplicação inclui uma funcionalidade para simular alterações no preço das ações e acionar alertas.

1. **Simular uma Alteração de Preço:**
   - Navegue para a página de Alertas.
   - Insira o símbolo da ação para a qual deseja simular uma alteração de preço.
   - Clique no botão "Simulate Alert".
   - A aplicação gerará um preço aleatório para a ação e verificará os alertas definidos.
   - Se o preço simulado atender a qualquer condição de alerta, uma notificação será exibida.

## Estrutura do Código

- `app.py`: O ficheiro principal da aplicação que inicializa a aplicação Flask, configura a base de dados e inicia o servidor.
- `routes.py`: Define as rotas para a aplicação web, incluindo buscar dados de ações, exibir dados, definir alertas e gerir a autenticação de utilizadores.
- `operations.py`: Contém as operações principais para buscar dados de ações do Yahoo Finance, armazenar dados no MongoDB, gerar recomendações e gerir alertas.
- `initdb.py`: Inicializa a base de dados MongoDB com as coleções e índices necessários.
- `insert_data.py`: Insere dados iniciais na base de dados MongoDB, incluindo utilizadores e dados de ações de exemplo.
- `templates/`: Diretório contendo os templates HTML para a aplicação web.
- `static/`: Diretório contendo ficheiros estáticos como CSS e JavaScript.

## Melhorias Futuras

- **Segurança Aprimorada:**
  - Implementar hashing de senhas para a autenticação de utilizadores.
  - Adicionar controlo de acesso baseado em funções para restringir certas funcionalidades a utilizadores administradores.

- **Análise de Dados Avançada:**
  - Incluir indicadores técnicos adicionais para uma análise de investimento mais abrangente.
  - Implementar modelos de machine learning para previsão de preços de ações.

- **Melhorias na Interface de Utilizador:**
  - Melhorar o design e a usabilidade da aplicação web.
  - Adicionar gráficos mais interativos e personalizáveis.

- **Notificações:**
  - Implementar notificações por email ou SMS para alertas de ações.
  - Fornecer opções para os utilizadores personalizarem as preferências de notificações.

## Contribuição

Contribuições são bem-vindas! Se tiver ideias para melhorias ou novas funcionalidades, sinta-se à vontade para fazer um fork do repositório e submeter um pull request.
