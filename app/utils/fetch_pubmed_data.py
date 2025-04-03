import os
import time
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import requests
import xml.etree.ElementTree as ET
from datetime import datetime

from app.models import Article

# 加载环境变量
load_dotenv()

# 数据库配置
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# PubMed API 配置
BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
DB = "pubmed"
RETMAX = 1000  # 获取的最大文献数量

def fetch_batch_details(batch_ids: list) -> list:
    """获取一批文章的详细信息"""
    id_string = ",".join(batch_ids)
    article_url = f"{BASE_URL}efetch.fcgi?db={DB}&id={id_string}&rettype=abstract&retmode=xml"
    response = requests.get(article_url)
    response.raise_for_status()
    return parse_batch_xml(response.text, batch_ids)

def parse_batch_xml(xml_text: str, batch_ids: list) -> list:
    """解析批量返回的 XML 数据"""
    articles = []
    root = ET.fromstring(xml_text)
    for pubmed_article in root.findall(".//PubmedArticle"):
        pmid_elem = pubmed_article.find(".//PMID")
        pmid = pmid_elem.text if pmid_elem is not None else None
        if not pmid or pmid == "Unknown PMID":
            print(f"Skipping invalid PMID")
            continue

        title_elem = pubmed_article.find(".//ArticleTitle")
        title = title_elem.text.strip() if title_elem is not None and title_elem.text else "No Title"

        doi_elem = pubmed_article.find(".//ELocationID[@EIdType='doi']")
        doi = doi_elem.text.strip() if doi_elem is not None and doi_elem.text else ""

        publication_date_elem = pubmed_article.find(".//PubDate")
        publication_date = None
        if publication_date_elem is not None:
            year = publication_date_elem.find("Year").text if publication_date_elem.find("Year") is not None else ""
            month = publication_date_elem.find("Month").text if publication_date_elem.find("Month") is not None else "Jan"
            day = publication_date_elem.find("Day").text if publication_date_elem.find("Day") is not None else "01"
            # 修改日期格式为 '%Y-%b-%d'
            publication_date = datetime.strptime(f"{year}-{month}-{day}", "%Y-%b-%d").date()

        journal_name_elem = pubmed_article.find(".//Title")
        journal_name = journal_name_elem.text.strip() if journal_name_elem is not None and journal_name_elem.text else "Unknown Journal"

        authors = []
        for author in pubmed_article.findall(".//Author"):
            last_name = author.find("LastName").text if author.find("LastName") is not None else ""
            fore_name = author.find("ForeName").text if author.find("ForeName") is not None else ""
            affiliation = author.find("AffiliationInfo/Affiliation").text if author.find("AffiliationInfo/Affiliation") is not None else ""
            authors.append(f"{last_name} {fore_name} ({affiliation})")
        authors = ", ".join(authors).strip() if authors else "Unknown Authors"

        abstract_texts = []
        for abstract_text in pubmed_article.findall(".//AbstractText"):
            abstract_texts.append(abstract_text.text.strip() if abstract_text.text else "")
        abstract = "\n".join(abstract_texts).strip() if abstract_texts else "No Abstract"

        article_url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"

        article_data = {
            'pmid': pmid,
            'title': title,
            'doi': doi,
            'pub_date': publication_date,
            'journal_name': journal_name,
            'authors': authors,
            'abstract': abstract,
            'article_url': article_url,
            'review_status': 'pending',
            'review_reason': '',
        }

        articles.append(article_data)
    return articles

def fetch_articles_in_batches(id_list: list, batch_size=200):
    """分批获取文章数据"""
    for i in range(0, len(id_list), batch_size):
        batch_ids = id_list[i:i + batch_size]
        yield fetch_batch_details(batch_ids)

def fetch_pubmed_data():
    """从PubMed获取数据并存储到数据库"""
    db = SessionLocal()
    try:
        # Step 1: 查询PubMed ID列表
        search_url = f"{BASE_URL}esearch.fcgi?db={DB}&term=science&retmax={RETMAX}&retmode=json"
        response = requests.get(search_url)
        response.raise_for_status()
        data = response.json()

        id_list = data['esearchresult']['idlist']
        print(f"Found {len(id_list)} PubMed IDs.")

        # Step 2: 分批获取详细信息
        for batch_articles in fetch_articles_in_batches(id_list, batch_size=200):
            for article_details in batch_articles:
                # 检查是否已存在相同PMID的文章
                existing_article = db.query(Article).filter_by(pmid=article_details['pmid']).first()
                if not existing_article and article_details['pmid'] != "Unknown PMID":
                    db_article = Article(**article_details)
                    db.add(db_article)

            # 每批请求后暂停 1 秒
            time.sleep(1)

        # 提交事务
        db.commit()
        print("PubMed data fetched and stored successfully.")
    except Exception as e:
        print(f"Error fetching PubMed data: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fetch_pubmed_data()