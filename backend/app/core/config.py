"""Core configuration settings"""

import os
from typing import List
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from pathlib import Path

# Load .env file from backend directory
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "LawAI Legal Assistant API"
    APP_DESCRIPTION: str = "RAG-based legal assistant for Indian laws"
    VERSION: str = "1.0.0"

    # API
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    # OpenAI
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # LLM Configuration
    LLM_MODEL: str = "gpt-4-turbo-preview"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    TEMPERATURE: float = 0.1

    # Vector Store
    VECTOR_STORE_PATH: str = "./data/combined/vector_store"

    # Document Processing
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K_RESULTS: int = 5

    # Legal Sources Configuration
    LEGAL_SOURCES_CONFIG: str = "./data/legal_sources.json"
    
    # Legal Sources (Legacy - use LEGAL_SOURCES_CONFIG instead)
    LEGAL_SOURCES: List[dict] = [
        {
            "act_name": "Bharatiya Nyaya Sanhita, 2023 (BNS)",
            "url": "https://www.indiacode.nic.in/show-data?actid=AC_CEN_45_76_00001_202345_1704269116555&sectionId=&sectionno=&orderno=",
            "description": "The Bharatiya Nyaya Sanhita, 2023 (BNS) replaces the Indian Penal Code, 1860. It is India's new criminal code with 358 sections.",
        },
        {
            "act_name": "Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS)",
            "url": "https://www.indiacode.nic.in/show-data?actid=AC_CEN_46_77_00001_202346_1704269231333&sectionId=&sectionno=&orderno=",
            "description": "The Bharatiya Nagarik Suraksha Sanhita, 2023 (BNSS) replaces the Code of Criminal Procedure, 1973. It governs criminal procedure in India.",
        },
        {
            "act_name": "Bharatiya Sakshya Adhiniyam, 2023 (BSA)",
            "url": "https://www.indiacode.nic.in/show-data?actid=AC_CEN_47_78_00001_202347_1704269298820&sectionId=&sectionno=&orderno=",
            "description": "The Bharatiya Sakshya Adhiniyam, 2023 (BSA) replaces the Indian Evidence Act, 1872. It deals with law of evidence in India.",
        },
        {
            "act_name": "Hindu Marriage Act, 1955",
            "url": "https://www.indiacode.nic.in/handle/123456789/1618",
            "description": "Governs marriage and divorce among Hindus, Buddhists, Jains, and Sikhs in India. Covers marriage validity, divorce grounds, judicial separation, and matrimonial relief.",
        },
        {
            "act_name": "Hindu Succession Act, 1956",
            "url": "https://www.indiacode.nic.in/handle/123456789/1623",
            "description": "Governs intestate succession and inheritance among Hindus. Covers property rights, succession rules, and rights of daughters in ancestral property.",
        },
        {
            "act_name": "Hindu Adoption and Maintenance Act, 1956",
            "url": "https://www.indiacode.nic.in/handle/123456789/1617",
            "description": "Regulates adoption of children and maintenance of wife, children, and parents among Hindus.",
        },
        {
            "act_name": "Hindu Minority and Guardianship Act, 1956",
            "url": "https://www.indiacode.nic.in/handle/123456789/1619",
            "description": "Provides for guardianship of minors and their property among Hindus.",
        },
        {
            "act_name": "Muslim Personal Law (Shariat) Application Act, 1937",
            "url": "https://www.indiacode.nic.in/handle/123456789/1719",
            "description": "Governs succession, inheritance, marriage, dissolution of marriage, maintenance, guardianship, gifts, and wakfs among Muslims.",
        },
        {
            "act_name": "Indian Succession Act, 1925",
            "url": "https://www.indiacode.nic.in/handle/123456789/2247",
            "description": "Governs succession and inheritance for Christians, Parsis, and others not covered by personal laws. Includes wills, intestate succession, and probate.",
        },
        {
            "act_name": "Transfer of Property Act, 1882",
            "url": "https://www.indiacode.nic.in/handle/123456789/2338",
            "description": "Governs transfer of property in India including sale, mortgage, lease, exchange, and gift of immovable property.",
        },
        {
            "act_name": "Registration Act, 1908",
            "url": "https://www.indiacode.nic.in/handle/123456789/2268",
            "description": "Regulates registration of documents related to property transactions, ensuring legal validity and public record.",
        },
        {
            "act_name": "Indian Easements Act, 1882",
            "url": "https://www.indiacode.nic.in/handle/123456789/2142",
            "description": "Governs easements and licenses related to property, including rights of way and water rights.",
        },
        {
            "act_name": "Partition Act, 1893",
            "url": "https://www.indiacode.nic.in/handle/123456789/2259",
            "description": "Provides procedure for partition of immovable property held by co-owners or joint family members.",
        },
        {
            "act_name": "Real Estate (Regulation and Development) Act, 2016",
            "url": "https://www.indiacode.nic.in/handle/123456789/2149",
            "description": "RERA regulates real estate sector, protects homebuyers, and ensures transparency in property transactions.",
        },
        {
            "act_name": "Benami Transactions (Prohibition) Act, 1988",
            "url": "https://www.indiacode.nic.in/handle/123456789/1666",
            "description": "Prohibits benami property transactions and provides for confiscation of benami properties.",
        },
        {
            "act_name": "Protection of Women from Domestic Violence Act, 2005",
            "url": "https://www.indiacode.nic.in/handle/123456789/2063",
            "description": "Provides protection to women from domestic violence and covers residence rights, maintenance, and custody.",
        },
        {
            "act_name": "Guardians and Wards Act, 1890",
            "url": "https://www.indiacode.nic.in/handle/123456789/2121",
            "description": "Governs appointment and duties of guardians for minors and their property.",
        },
        {
            "act_name": "Special Marriage Act, 1954",
            "url": "https://www.indiacode.nic.in/handle/123456789/1590",
            "description": "Provides special form of marriage for inter-faith and inter-caste couples, regardless of religion.",
        },
        {
            "act_name": "Indian Divorce Act, 1869",
            "url": "https://www.indiacode.nic.in/handle/123456789/2143",
            "description": "Governs divorce and matrimonial relief among Christians in India.",
        },
        {
            "act_name": "Parsi Marriage and Divorce Act, 1936",
            "url": "https://www.indiacode.nic.in/handle/123456789/1724",
            "description": "Governs marriage and divorce among Parsis in India.",
        },
        {
            "act_name": "Information Technology Act, 2000",
            "url": "https://www.indiacode.nic.in/handle/123456789/15442",
            "description": "The Information Technology Act, 2000 provides legal framework for electronic governance and e-commerce",
        },
        {
            "act_name": "Indian Penal Code, 1860 (IPC) - Historical Reference",
            "url": "https://www.indiacode.nic.in/handle/123456789/12850",
            "description": "The Indian Penal Code was the official criminal code of India until replaced by BNS in 2024",
        },
    ]

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env files


settings = Settings()
