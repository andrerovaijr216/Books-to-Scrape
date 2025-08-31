#!/usr/bin/env python3
"""
books_rpa.py

Script completo para:
- Raspar https://books.toscrape.com usando Selenium + webdriver_manager
- Extrair: título, preço, disponibilidade, classificação em estrelas
- Salvar dados em CSV e JSON
- Aplicar análise: classificar Alto/Baixo (mediana) + exemplo de cluster KMeans
- Gerar relatório PDF com resumo e gráficos
"""

import time
import re
import os
from io import BytesIO

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans

import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

# -----------------------------
# Configuração
# -----------------------------
BASE_URL = "https://books.toscrape.com"
OUTPUT_DIR = "output_books"
CSV_PATH = os.path.join(OUTPUT_DIR, "books_data.csv")
JSON_PATH = os.path.join(OUTPUT_DIR, "books_data.json")
PDF_REPORT_PATH = os.path.join(OUTPUT_DIR, "books_report.pdf")

HEADLESS = True  # coloque False se quiser assistir o navegador abrindo

os.makedirs(OUTPUT_DIR, exist_ok=True)

# -----------------------------
# Funções auxiliares
# -----------------------------
def parse_price(price_str):
    if not price_str:
        return None
    s = re.sub(r'[^\d.,]', '', price_str.strip()).replace(',', '')
    try:
        return float(s)
    except ValueError:
        return None

def parse_availability(avail_str):
    if not avail_str:
        return 0
    m = re.search(r'(\d+)', avail_str)
    if m:
        return int(m.group(1))
    return 1 if "In stock" in avail_str else 0

def parse_star_rating(star_class):
    mapping = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
    for k, v in mapping.items():
        if k in star_class:
            return v
    return None

# -----------------------------
# Selenium: inicializar driver
# -----------------------------
def init_driver(headless=True):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_page_load_timeout(30)
    return driver

# -----------------------------
# Raspagem
# -----------------------------
def extract_books_from_listing_page(driver):
    books = []
    elems = driver.find_elements(By.CSS_SELECTOR, "article.product_pod")
    for el in elems:
        try:
            title_el = el.find_element(By.CSS_SELECTOR, "h3 > a")
            title = title_el.get_attribute("title").strip()
            link = title_el.get_attribute("href")
        except NoSuchElementException:
            title, link = None, None

        try:
            price_raw = el.find_element(By.CSS_SELECTOR, "p.price_color").text.strip()
            price = parse_price(price_raw)
        except NoSuchElementException:
            price_raw, price = None, None

        try:
            avail_raw = el.find_element(By.CSS_SELECTOR, "p.instock.availability").text.strip()
            availability = parse_availability(avail_raw)
        except NoSuchElementException:
            avail_raw, availability = None, None

        try:
            star_class = el.find_element(By.CSS_SELECTOR, "p.star-rating").get_attribute("class")
            stars = parse_star_rating(star_class)
        except NoSuchElementException:
            star_class, stars = None, None

        books.append({
            "title": title,
            "link": link,
            "price_raw": price_raw,
            "price": price,
            "availability_raw": avail_raw,
            "availability": availability,
            "stars": stars
        })
    return books

def scrape_all_books(headless=True, pause_between_pages=0.5):
    driver = init_driver(headless=headless)
    driver.get(BASE_URL)

    all_books = []
    page_count = 0

    while True:
        page_count += 1
        print(f"[INFO] Página {page_count} - {driver.current_url}")
        books = extract_books_from_listing_page(driver)
        all_books.extend(books)

        try:
            next_button = driver.find_element(By.CSS_SELECTOR, "li.next > a")
            driver.get(next_button.get_attribute("href"))
            time.sleep(pause_between_pages)
        except NoSuchElementException:
            print("[INFO] Última página alcançada.")
            break

    driver.quit()
    print(f"[INFO] Total livros raspados: {len(all_books)}")
    return all_books

# -----------------------------
# Salvamento
# -----------------------------
def save_data(all_books):
    df = pd.DataFrame(all_books)
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df.to_csv(CSV_PATH, index=False)
    df.to_json(JSON_PATH, orient='records', force_ascii=False, indent=2)
    print(f"[INFO] Salvo CSV em {CSV_PATH} e JSON em {JSON_PATH}")
    return df

# -----------------------------
# Análise
# -----------------------------
def analyze_data(df):
    summary = {}
    prices = df['price'].dropna()
    summary['total_books'] = len(df)
    summary['price_mean'] = prices.mean()
    summary['price_median'] = prices.median()
    summary['price_min'] = prices.min()
    summary['price_max'] = prices.max()

    median_val = summary['price_median']
    df['value_category'] = df['price'].apply(
        lambda p: "Alto Valor" if p > median_val else "Baixo Valor"
    )

    summary['value_category_distribution'] = df['value_category'].value_counts().to_dict()

    # Clusterização simples com KMeans
    if len(prices) >= 10:
        X = prices.values.reshape(-1, 1)
        kmeans = KMeans(n_clusters=2, random_state=42, n_init='auto')
        df.loc[df['price'].notnull(), 'kmeans_cluster'] = kmeans.fit_predict(X)
        summary['kmeans_centers'] = kmeans.cluster_centers_.flatten().tolist()
    else:
        df['kmeans_cluster'] = np.nan
        summary['kmeans_centers'] = []

    return df, summary

# -----------------------------
# Relatório PDF
# -----------------------------
def generate_pdf_report(df, summary):
    images = {}

    # Histograma de preços
    if not df['price'].dropna().empty:
        plt.figure(figsize=(6,4))
        plt.hist(df['price'].dropna(), bins=20)
        plt.title("Distribuição de Preços")
        buf = BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        images['hist'] = buf
        plt.close()

    # Pizza Alto/Baixo
    plt.figure(figsize=(4,4))
    df['value_category'].value_counts().plot.pie(autopct="%1.1f%%")
    plt.title("Alto Valor vs Baixo Valor")
    buf2 = BytesIO()
    plt.savefig(buf2, format="png")
    buf2.seek(0)
    images['pie'] = buf2
    plt.close()

    c = canvas.Canvas(PDF_REPORT_PATH, pagesize=letter)
    width, height = letter
    y = height - 50

    c.setFont("Helvetica-Bold", 16)
    c.drawString(40, y, "Relatório - Books to Scrape")
    y -= 30

    c.setFont("Helvetica", 11)
    c.drawString(40, y, f"Total de livros: {summary['total_books']}")
    y -= 15
    c.drawString(40, y, f"Preço médio: {summary['price_mean']:.2f}")
    y -= 15
    c.drawString(40, y, f"Preço mediana: {summary['price_median']:.2f}")
    y -= 15
    c.drawString(40, y, f"Preço mínimo: {summary['price_min']:.2f}")
    y -= 15
    c.drawString(40, y, f"Preço máximo: {summary['price_max']:.2f}")
    y -= 30

    for name, buf in images.items():
        img = ImageReader(buf)
        c.drawImage(img, 40, y-200, width-80, 200, preserveAspectRatio=True)
        y -= 220

    c.save()
    print(f"[INFO] Relatório PDF salvo em {PDF_REPORT_PATH}")

# -----------------------------
# Main
# -----------------------------
def main():
    print("Iniciando raspagem...")
    books = scrape_all_books(headless=HEADLESS, pause_between_pages=0.3)
    df = save_data(books)
    df, summary = analyze_data(df)
    generate_pdf_report(df, summary)
    print("Fim do processamento.")

if __name__ == "__main__":
    main()
