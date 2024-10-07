import requests

class PlugNotasAPI:
    def __init__(self, api_key, homologation=True):
        self.api_key = '2da392a6-79d2-4304-a8b7-959572c7e44d' if homologation else api_key

        self.base_url = "https://api.sandbox.plugnotas.com.br/nfse" if homologation else "https://api.plugnotas.com.br/nfse"
        self.headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key
        }
    
    def send_nfse(self, data):
        response = requests.post(self.base_url, headers=self.headers, json=data)
        return response.status_code, response.json()
    
    def get_nfse(self, nfse_id):
        url = f"{self.base_url}/{nfse_id}"
        response = requests.get(url, headers=self.headers)
        return response.status_code, response.json()
    def get_pdf_nfse(self, nfse_id):
        url = f"{self.base_url}/pdf/{nfse_id}"
        self.headers = {
            "Content-Type": "application/pdf",
            "x-api-key": self.api_key
        }
        response = requests.get(url, headers=self.headers,stream=True)
        # Abrir o arquivo localmente em modo de escrita binária
        with open("pdf_baixado.pdf", 'wb') as file:
            # Iterar sobre o conteúdo baixado em chunks (blocos de dados)
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:  # Verifica se o chunk não está vazio
                    file.write(chunk)  # Escreve o chunk no arquivo

        print(f"Arquivo  baixado com sucesso.")
        return response.status_code, response

# Dados para requisição
data = [
    {
        "prestador": {
            "cpfCnpj": "05108721000133"
        },
        "tomador": {
            "cpfCnpj": "79159001372",
            "razaoSocial": "AFONSO FLÁVIO RIBEIRO DE CARVALHO",
            "email": "afonso@jgma.com.br",
            "endereco": {
                "descricaoCidade": "São Luis",
                "cep": "65066190",
                "tipoLogradouro": "Rua",
                "logradouro": "Boa Esperanca",
                "codigoCidade": "2111300",
                "complemento": "sala 01",
                "estado": "MA",
                "numero": "102",
                "bairro": "Turu"
            },
            "telefone": {
                "ddd": "98",
                "numero": "981599692"
            }
        },
        "servico": {
            "codigo": "0801",
            "descricaoLC116": "ENSINO REGULAR PRE-ESCOLAR, FUNDAMENTAL, MEDIO E SUPERIOR.",
            "discriminacao": "EDUCACAO PROFISSIONAL DE NIVEL TECNICO",
            "cnae": "854140000",
            "codigoTributacao": "4115200",
            "codigoCidadeIncidencia": "921",
            "descricaoCidadeIncidencia": "MARINGA",
            "iss": {
                "aliquota": 5,
                "tipoTributacao": 6
            },
            "valor": {
                "deducoes": 0,
                "baseCalculo": 0.1,
                "servico": 1,
                "liquido": 0.1
            }
        },
        "enviarEmail": True
    }
]

# Uso da classe
api_key = "d17733293ad43d4054204a1d73a811a6"  # Token da NETCOM
plugnotas_api = PlugNotasAPI(api_key, homologation=False)

# Enviar NFS-e
# status_code, response_json = plugnotas_api.send_nfse(data)
# print(f"Status Code: {status_code}")
# print(f"Response JSON: {response_json}")

# Se precisar buscar uma NFS-e
nfse_id = "6702f13a72ffd16e793bae6d"  # ID de exemplo
status_code, response = plugnotas_api.get_pdf_nfse(nfse_id)
print(f"Status Code: {status_code}")
print(f"Response JSON: {response}")
