# S3 Service API
Serviço desenvolvido em FastAPI para realzar operações básicas no S3 com o propósito de não expor o storage diretamente

# Dependências para o desenvolvimento
- [UV](https://docs.astral.sh/uv/getting-started/installation/)
- [Docker compose](https://docs.docker.com/compose/install/)

# Ambiente de desenvolvimento
No docker-compose.yml configurado temos alguns serviços como:
- api -> API em FastAPI
- minio -> Storage compatível com o s3
- nginx -> proxy

## Passos para configurar o ambiente
1. Execute o seguinte comando para subir todos os serviços:
    ```bash
    make up
    ```
2. Após todos os serviços estarem de pé, acesse o [console do minio](http://localhost:9001) no navegador e crie um bucket com o nome `localbucket`

3. Para conseguir acessar as urls pré assinadas geradas pelo minio é preciso adicionar a seguinte linha no `/etc/hosts`:
    ```
    127.0.0.1 minio
    ```
