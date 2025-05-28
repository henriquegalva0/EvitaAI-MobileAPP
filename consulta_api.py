import openai

# LER TXT COM API
with open("misc/apikeychatgpt.txt", "r", encoding="utf8") as arcapikey:
    apikey = arcapikey.read()

# LER TXT COM PROMT
with open("misc/promt_site.txt", "r", encoding="utf8") as arcpromtgpt:
    promtchatgpt = arcpromtgpt.read()

def tratamento_output(output_gpt):

    listar_partes_output = [parte.strip() for parte in output_gpt.split('/////')]

    if len(listar_partes_output)>=4:

        del listar_partes_output[4:]

        classificacao=listar_partes_output[0].replace('\\n', '').replace("'",'').lower()
        reputacao=listar_partes_output[1].replace('\\n','')
        justificativa=listar_partes_output[2].replace('\\n','')
        seguranca=listar_partes_output[3].replace('\\n','').replace("'",'')

        return {'classificacao':classificacao,'reputacao':reputacao,'justificativa':justificativa,'seguranca':seguranca}
    
    else:
        return {'classificacao':0}

# DEFINIR FUNCAO DE ANALISE GPT
def consultar_analise_gpt(site):

    if len(site)<=1:
        return 0

    client = openai.OpenAI(api_key=f"{apikey}")

    response = client.responses.create(
        model="gpt-4.1-mini",
        
        input=[{

            "role": "system",
            "content": [
                {
                "type": "input_text",
                "text": f"{promtchatgpt}" # VARIAVEL QUE IMPORTEI DO TXT
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
        max_output_tokens=1000,
        top_p=1,
        store=False
        )
    
    print(f'O custo total de tokens do processo foi de: {response.usage.total_tokens} tokens')
    
    retorno_gpt=str(repr(response.output_text))

    dicionario_output_tratado=tratamento_output(retorno_gpt)

    if dicionario_output_tratado['classificacao'] != 0:
        return dicionario_output_tratado
    else:
        return 0