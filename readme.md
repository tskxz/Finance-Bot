# Projeto DBNoSql Financial

Este projeto tem como objetivo criar uma aplicação web para análise de dados financeiros utilizando Flask, MongoDB e Bokeh. A aplicação se conecta ao Yahoo Finance para obter dados históricos de ações, armazena esses dados no MongoDB (um banco de dados NoSQL) e exibe visualizações gráficas desses dados junto com recomendações de compra, venda ou manutenção das ações com base em médias móveis simples.

## Funcionalidades

1. **Conexão com Yahoo Finance:**
   - A aplicação se conecta à API do Yahoo Finance para obter dados históricos de ações com base no símbolo fornecido pelo usuário.

2. **Armazenamento em MongoDB:**
   - Os dados obtidos do Yahoo Finance são armazenados no MongoDB. Cada ação é armazenada como um documento na coleção `stocks` no banco de dados `stock_data`.

3. **Análise e Recomendação de Investimentos:**
   - Com base nos dados históricos das ações, a aplicação calcula médias móveis de 20 dias e 50 dias.
   - Uma recomendação de "Compra" é feita se a média móvel de 20 dias estiver acima da média móvel de 50 dias.
   - Uma recomendação de "Venda" é feita se a média móvel de 20 dias estiver abaixo da média móvel de 50 dias.
   - Uma recomendação de "Manutenção" é feita se as médias móveis não mostrarem um padrão claro.

4. **Visualização Gráfica com Bokeh:**
   - Utiliza a biblioteca Bokeh para criar gráficos interativos de preços de fechamento das ações e suas médias móveis.
   - Os gráficos são incorporados na página web para visualização fácil e compreensão dos dados.

## Pré-requisitos

Para executar esta aplicação localmente, é necessário ter o Python instalado juntamente com as bibliotecas especificadas no arquivo `requirements.txt`. Além disso, um servidor MongoDB deve estar em execução na máquina local ou em uma máquina remota acessível.

## Instalação e Execução

1. **Clone o repositório:**
git clone https://github.com/seu-usuario/projeto-db-nosql-financial.git
cd projeto-db-nosql-financial

2. **Instale as dependências:**
pip install -r requirements.txt

3. **Configure o MongoDB:**
- Certifique-se de que o servidor MongoDB esteja em execução.

4. **Execute a aplicação:**
python app.py

5. **Acesse a aplicação:**
- Abra o navegador e vá para `http://localhost:5000`.

## Utilização

1. **Buscar dados de uma ação:**
- Na página inicial, digite o símbolo de uma ação (por exemplo, AAPL para Apple) e clique em "Fetch Data".
- Isso buscará os dados mais recentes da ação do Yahoo Finance e os armazenará no MongoDB.

2. **Visualizar dados e recomendação:**
- Após buscar os dados, você pode clicar em "Show Data" para visualizar os dados históricos da ação, um gráfico com médias móveis e uma recomendação de investimento.

# Conclusão
- Este projeto "Projeto DBNoSql Financial" foi desenvolvido por Dmytro Bohutskyy como parte do trabalho final da disciplina de Banco de Dados NoSQL.