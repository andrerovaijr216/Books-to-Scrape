# 📘 Projeto RPA - Books to Scrape

## 👥 Integrantes
- Ana Carolina Martins - RM555762  
- Andre Rovai Jr - RM555848  
- Lancelot Chagas Rodrigues - RM554707  

---

## 📌 Descrição do Projeto
Este projeto foi desenvolvido como parte do exercício de **Automação de Processos com Selenium e IA**.  
O objetivo é criar um robô de **RPA (Robotic Process Automation)** capaz de:

1. Acessar o site [Books to Scrape](https://books.toscrape.com).  
2. Percorrer todas as páginas da listagem de livros.  
3. Extrair informações relevantes:
   - Título do livro  
   - Preço  
   - Disponibilidade em estoque  
   - Classificação em estrelas  
4. Salvar os dados em **CSV** e **JSON**.  
5. Realizar análises com **Pandas**, **NumPy** e **Scikit-learn**:
   - Classificação de livros em **Alto Valor** (preço acima da mediana) ou **Baixo Valor** (preço abaixo ou igual).  
   - Clusterização simples via **KMeans**.  
6. Gerar um **Relatório em PDF** com:
   - Resumo estatístico (número total de livros, preço médio, mediana, mínimo e máximo).  
   - Distribuição de categorias (Alto Valor x Baixo Valor).  
   - Gráficos de apoio (histograma de preços e pizza das categorias).  

---

## 📂 Estrutura do Projeto
- `rpa_books.py` → Script principal de automação, coleta, análise e geração do relatório.  
- `books_data.csv` → Dados coletados em formato CSV.  
- `books_data.json` → Dados coletados em formato JSON.  
- `books_report.pdf` → Relatório final com resumo e análises.  
- `README.md` → Documentação do projeto.  
- `requirements.txt` → Lista de dependências do projeto.  

---

## ⚙️ Tecnologias Utilizadas
- **Python 3**  
- **Selenium** + `webdriver_manager`  
- **Pandas**  
- **NumPy**  
- **Scikit-learn**  
- **Matplotlib**  
- **ReportLab**  

---

## 🚀 Como Executar
1. Clone este repositório:  
   ```bash
   git clone <url-do-repositorio>
   cd projeto-rpa-books

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt

3. Execute o script principal:
   ```bash
   python rpa_books.py

4. Os arquivos de saída serão gerados na pasta `output_books/`.

📊 Resultados Obtidos

Total de livros: 1000
Preço médio: 35.07
Preço mediana: 35.98
Preço mínimo: 10.00
Preço máximo: 59.99

📝 Observações

-O fluxo da automação foi estruturado em funções modulares para raspagem, salvamento, análise e geração de relatórios.
-O uso de IA (via KMeans e análise estatística) permitiu identificar padrões de precificação e agrupar os livros por faixas de valor.

Desafios enfrentados:
  -Controle do Selenium para navegação entre páginas.
  -Tratamento de preços e disponibilidade com expressões regulares.
  -Geração de gráficos e integração ao relatório em PDF.

📌 Status: ✅ Concluído

📦 requirements.txt
```bash
selenium
webdriver-manager
pandas
numpy
scikit-learn
matplotlib
reportlab
