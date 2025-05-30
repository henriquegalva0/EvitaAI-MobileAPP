import openai

# LER TXT COM API
with open("misc/apikeychatgpt.txt", "r", encoding="utf8") as arcapikey:
    apikey = arcapikey.read()

# LER TXT COM PROMT
with open("misc/promt_site_relatorio.txt", "r", encoding="utf8") as arcpromtgpt:
    promtchatgpt_relatorio = arcpromtgpt.read()

def tratamento_output_relatorio(output_gpt):

    listar_partes_output_relatorio = [parte.strip() for parte in output_gpt.split('/////')]

    print(listar_partes_output_relatorio)

    if len(listar_partes_output_relatorio)>=3:

        del listar_partes_output_relatorio[3:]

        reputacao=listar_partes_output_relatorio[0].replace('\\n', '').replace("'",'').capitalize()
        justificativa=listar_partes_output_relatorio[1].replace('\\n','').capitalize()
        seguranca=listar_partes_output_relatorio[2].replace('\\n','').replace("'",'').capitalize()

        return {'reputacao':reputacao,'justificativa':justificativa,'seguranca':seguranca}
    else:
        return {'reputacao':0}

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
        
        retorno_gpt_relatorio=str(repr(response.output_text))

        dicionario_output_tratado_relatorio=tratamento_output_relatorio(retorno_gpt_relatorio)
        print(dicionario_output_tratado_relatorio)
        if isinstance(dicionario_output_tratado_relatorio['reputacao'], int):
            return 0
        else:
            return dicionario_output_tratado_relatorio