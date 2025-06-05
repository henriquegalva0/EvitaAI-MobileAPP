import requests
import json

# LER json com a API key (string pura)
with open("misc/apikeychatgpt.json", "r", encoding="utf8") as arcapikey:
    apikey = json.load(arcapikey)  # Isso retorna diretamente a string da chave

# LER json com o prompt do relatório (string pura)
with open("misc/promt_site_classificacao.json", "r", encoding="utf8") as arcpromtgpt:
    promtchatgpt_classificacao = json.load(arcpromtgpt)  # Isso retorna diretamente o prompt como string


def tratamento_output_classificacao(output_gpt):
    a = output_gpt.lower()
    b = a.replace('\\n', '')
    c = b.replace("'", '')
    d = c.strip()
    return d

# DEFINIR FUNCAO DE ANALISE GPT
def classificacao_analise_gpt(site):
    if isinstance(site, int):
        return 0
    elif len(site) <= 3:
        return 0
    else:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {apikey}"
        }

        payload = {
            "model": "gpt-3.5-turbo",  # Using a standard model name
            "messages": [
                {"role": "system", "content": promtchatgpt_classificacao},
                {"role": "user", "content": site}
            ],
            "temperature": 0,
            "max_tokens": 900,
            "top_p": 1
        }

        try:
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
            response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
            response_data = response.json()

            total_tokens = response_data.get('usage', {}).get('total_tokens', 'N/A')
            print(f'O custo total de tokens do processo foi de: {total_tokens} tokens')

            if response_data and 'choices' in response_data and response_data['choices']:
                output_text = response_data['choices'][0]['message']['content']
                classificacao_retorno = tratamento_output_classificacao(output_text)

                if isinstance(classificacao_retorno, str):
                    if len(classificacao_retorno) < 10:
                        return {'classificacao': classificacao_retorno}
                    else:
                        return 0
                else:
                    return 0
            else:
                print("No valid response from GPT for classification.")
                return 0

        except requests.exceptions.RequestException as e:
            print(f"Erro na requisição para a API do OpenAI (classificação): {e}")
            return 0
        except json.JSONDecodeError:
            print("Erro ao decodificar a resposta JSON da API (classificação).")
            return 0
        except Exception as e:
            print(f"Ocorreu um erro inesperado (classificação): {e}")
            return 0