import requests
import json
import ast

# LER json com a API key (string pura)
with open("misc/apikeychatgpt.json", "r", encoding="utf8") as arcapikey:
    apikey = json.load(arcapikey)  # Isso retorna diretamente a string da chave

# LER json com o prompt do relatório (string pura)
with open("misc/promt_site_relatorio.json", "r", encoding="utf8") as arcpromtgpt:
    promtchatgpt_relatorio = json.load(arcpromtgpt)  # Isso retorna diretamente o prompt como string

# DEFINIR FUNCAO DE ANALISE GPT
def consultar_analise_gpt_relatorio(site):
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
                {"role": "system", "content": promtchatgpt_relatorio},
                {"role": "system", "content": "Não insira nenhum hyperlink na sua resposta!"},
                {"role": "user", "content": site}
            ],
            "temperature": 0,
            "max_tokens": 600,
            "top_p": 1
        }

        try:
            response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
            response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
            response_data = response.json()

            total_tokens = response_data.get('usage', {}).get('total_tokens', 'N/A')
            print(f'O custo total de tokens do processo foi de: {total_tokens} tokens')
            print(response_data)
            if response_data and 'choices' in response_data and response_data['choices']:
                retorno_gpt_relatorio = response_data['choices'][0]['message']['content'].strip()

                if retorno_gpt_relatorio:
                    try:
                        # Ensure the string is a valid Python literal (e.g., a dictionary)
                        output_gpt_disc = ast.literal_eval(retorno_gpt_relatorio)
                        print(output_gpt_disc)
                        print(type(output_gpt_disc))
                        return output_gpt_disc
                    except (ValueError, SyntaxError) as e:
                        print("Erro ao converter com ast.literal_eval:", e)
                        print(f"String retornada pelo GPT: {retorno_gpt_relatorio}")
                        return 0
                else:
                    return 0
            else:
                print("No valid response from GPT for report.")
                return 0

        except requests.exceptions.RequestException as e:
            print(f"Erro na requisição para a API do OpenAI (relatório): {e}")
            return 0
        except json.JSONDecodeError:
            print("Erro ao decodificar a resposta JSON da API (relatório).")
            return 0
        except Exception as e:
            print(f"Ocorreu um erro inesperado (relatório): {e}")
            return 0