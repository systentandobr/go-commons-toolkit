from setuptools import setup, find_packages

setup(
    name="ecommerce-agente-autonomo",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.103.1",
        "uvicorn>=0.23.2",
        "pydantic>=2.3.0",
        "httpx>=0.24.1",
        "python-dotenv>=1.0.0",
        "openai>=0.28.0",
        "tiktoken>=0.4.0",
        "aiohttp>=3.8.5",
        "requests>=2.31.0",
        "python-dateutil>=2.8.2",
        "pytz>=2023.3",
        "pydash>=7.0.6",
        "tenacity>=8.2.3",
    ],
    author="Desenvolvedor Backend",
    author_email="dev@exemplo.com",
    description="Agente autônomo para e-commerce integrado com WhatsApp",
    keywords="ecommerce, whatsapp, ai, autonomous agent, nlp",
    url="https://github.com/seu-usuario/ecommerce-agente-autonomo",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.10",
)
