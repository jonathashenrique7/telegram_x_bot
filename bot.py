#   1 > Crie um arquivo chamado ".env" onde você informará seu Token pessoal do Telegram e também a chave para sua conta na "Stripe" ( Caso utilize esta plataforma de pagamentos! )
#   2 > Crie variáveis no arquivo ".env" com os mesmos nomes informados nas funções "config()" 
#   3 > Informe no arquivo ".env" o token do telegram: TOKEN_BOT=''
#   4 > Informe também no arquivo ".env" a chave para pagamentos de sua plataforma de escolha: TOKEN_PROVIDER='' 
#   5 > Não se esqueça de configurar uma imagem para o produto vendido na função "comprar()": IMG_PRODUTO=
#   6 > Instale as bibliotecas para que o código funcione apropriadamente ... 

import telebot, csv
from telebot.types import LabeledPrice
from decouple import config             # pip install --upgrade python-decouple
from datetime import datetime

token           = config('TOKEN_BOT')       # Token => Telegram X 
bot             = telebot.TeleBot(token)
token_provider  = config('TOKEN_PROVIDER')  # Escolha uma plataforma para administrar a venda via cartão de crédito ... 

respostas = {
    'oi': 'Olá! Em que posso ajudar?',
    'Oi!': 'Oi! Em que posso ser útil!',
    'ola': 'Olá! Em que posso ajudar?',
    'olá': 'Olá! Em que posso ajudar?',
    'bom dia': 'Bom dia! Me diga como posso ajudá-lo(a)!',
    'Bom dia!': 'Bom dia! Me diga como posso ajudá-lo(a)!',
    'boa tarde': 'Boa tarde! Me diga como posso ajudá-lo(a)!',
    'boa noite': 'Boa noite! Me diga como posso ajudá-lo(a)!',
    'Olá!': 'Tudo bom? Posso ajusá-lo(a)?'
}

precos = [
    LabeledPrice(label='Meu e-Book', amount=600)
]

def salvar(arquivo_destino, dados: list) -> None:
    with open(arquivo_destino, 'a') as ids:
        e = csv.writer(ids)
        e.writerow(dados)

@bot.message_handler(commands=['bot', 'loja'])
def start(message) -> None:
    salvar('ids_telegram.csv', [message.from_user.id])
    bot.send_message(message.chat.id, 'Olá, tudo bom ?\nDeseja comprar meu livro em pdf ?\nClick /comprar para realizar a compra do livro.')

@bot.message_handler(commands=['comprar'])
def comprar(message) -> None:
    bot.send_invoice(
        message.from_user.id,
        title='Robô Vendedor',
        description='Já pensou em aprender Python3 de maneira simples?',
        provider_token=token_provider,
        currency='BRL',
        photo_url=config('IMG_PRODUTO'), # O endereço para a imagem estará no arquivo ".env", junto aos tokens do telegram e pagamentos ... 
        photo_height=512,
        photo_size=512,
        photo_width=512,
        is_flexible=False,
        prices=precos,
        start_parameter='gerente-robot',
        invoice_payload='PAYLOAD'
    )

@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query) -> None:
    bot.answer_pre_checkout_query(
        pre_checkout_query.id, ok=True, error_message="Alguem tentou utilizar o CVV do seu cartão, mas protegemos com sucesso suas credenciais. Tente pagar novamente em poucos minutos, precisamos de um pequeno descanso.")

@bot.message_handler(content_types=['successful_payment'])
def pagou(message) -> None: 
    salvar('ids_telegram_compra_ok.csv', [message.from_user.id, datetime.now().strftime('%d/%m/%Y %H:%M:%S')])
    doc = open('teste.pdf', 'rb')
    bot.send_document(message.chat.id, doc)
    bot.send_message(message.from_user.id, 'Show! Muito obrigado pela compra!')

@bot.message_handler(commands=['download'])
def download(message) -> None:
    doc = open('teste.pdf', 'rb')
    bot.send_document(message.chat.id, doc)

@bot.message_handler(func=lambda m: True)
def tudo(message) -> None:
    print("Mensagem >> ", message.text)
    salvar('historico_chat_telegram_.csv', [message.from_user.id, message.text, datetime.now().strftime('%d/%m/%Y %H:%M:%S')])
    resp = respostas.get(str(message.text).lower(), 'Não entendi o que quiz dizer. Por gentileza, tente novamete!')
    bot.send_message(message.from_user.id, resp)

bot.skip_pending = True

bot.polling(none_stop=True, interval=0)

