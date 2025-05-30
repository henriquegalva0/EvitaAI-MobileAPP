import openai
import ast

# LER TXT COM API
with open("misc/apikeychatgpt.txt", "r", encoding="utf8") as arcapikey:
    apikey = arcapikey.read()

# LER TXT COM PROMT
with open("misc/promt_site_relatorio.txt", "r", encoding="utf8") as arcpromtgpt:
    promtchatgpt_relatorio = arcpromtgpt.read()

# DEFINIR FUNCAO DE ANALISE GPT
def consultar_analise_gpt_relatorio(site):

    if isinstance(site, int):
        return 0
    elif len(site)<=3:
        return 0
    else:
        client = openai.OpenAI(api_key=f"{apikey}")

        response = client.responses.create(
            model="gpt-4.1-mini",
            
            input=[{

                "role": "system",
                "content": [
                    {
                    "type": "input_text",
                    "text": f"{promtchatgpt_relatorio}" # VARIAVEL QUE IMPORTEI DO TXT
                    }]},
                {
                "role": "system",
                "content": [{
                    "type": "input_text",
                    "text": "Não insira nenhum hyperlink na sua resposta!!!!!"
                    }]},
                {
                "role": "user",
                "content": [{
                    "type": "input_text",
                    "text": f"{site}" # VARIAVEL QUE ESTOU REQUISITANDO NA FUNÇÃO
                    }]}],

            text={
                "format": {
                "type": "text"
                }},

            reasoning={},

            tools=[{
                "type": "web_search_preview",
                "user_location": {
                    "type": "approximate"
                },
                "search_context_size": "medium"
                }],

            temperature=0,
            max_output_tokens=600,
            top_p=1,
            store=False
            )
        
        print(f'O custo total de tokens do processo foi de: {response.usage.total_tokens} tokens')

        retorno_gpt_relatorio = response.output_text.strip()

        if retorno_gpt_relatorio:
            try:
                output_gpt_disc = ast.literal_eval(retorno_gpt_relatorio)
                print(output_gpt_disc)
                print(type(output_gpt_disc))
                return output_gpt_disc
            except (ValueError, SyntaxError) as e:
                print("Erro ao converter com ast.literal_eval:", e)
                return 0
        else:
            return 0
