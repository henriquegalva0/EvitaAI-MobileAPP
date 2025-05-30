import openai

# LER TXT COM API
with open("misc/apikeychatgpt.txt", "r", encoding="utf8") as arcapikey:
    apikey = arcapikey.read()

# LER TXT COM PROMT
with open("misc/promt_site_classificacao.txt", "r", encoding="utf8") as arcpromtgpt:
    promtchatgpt_classificacao = arcpromtgpt.read()

def tratamento_output_classificacao(output_gpt):
    a=output_gpt.lower()
    b=a.replace('\\n','')
    c=b.replace("'",'')
    d=c.strip()
    return d

# DEFINIR FUNCAO DE ANALISE GPT
def classificacao_analise_gpt(site):

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
                    "text": f"{promtchatgpt_classificacao}" # VARIAVEL QUE IMPORTEI DO TXT
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
            max_output_tokens=900,
            top_p=1,
            store=False
            )
        
        print(f'O custo total de tokens do processo foi de: {response.usage.total_tokens} tokens')
        
        resposta_classificacao_gpt=str(repr(response.output_text))

        classificacao_retorno=tratamento_output_classificacao(resposta_classificacao_gpt)

        if isinstance(classificacao_retorno, int):
            return 0
        else:
            return {'classificacao':classificacao_retorno}