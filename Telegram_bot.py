from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import filters, MessageHandler, ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

async def start(update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id, 
                             text="Привет! Введите список продуктов через пробел")
    
async def handle_message(update, context):
    text = update.message.text.lower()

    if text.startswith('/start'):
        await start(update, context)
    else:
        await spis(update, context)

async def spis(update, context):
    message = update.message.text
    spisoc = message.split()

    if not spisoc:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Список покупок пуст.")
        return

    spisoc_str = ", ".join(spisoc)
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Покупки: {spisoc_str}. Кол-во: {len(spisoc)} шт.")
    context.user_data['shopping_list'] = spisoc
    
    buttons = []
    for product in spisoc:
        buttons.append([InlineKeyboardButton(product, callback_data='product_' + product)])
    
    reply_markup = InlineKeyboardMarkup(buttons)
    await context.bot.send_message(chat_id=update.effective_chat.id, text='Выберите продукт', reply_markup=reply_markup)

async def send_keyboard(update, context, spisoc):
    chat_id = update.chat_id
    buttons = []
    for product in spisoc:
        buttons.append([InlineKeyboardButton(product, callback_data='product_' + product)])
    if len(spisoc) >= 1:
        reply_markup = InlineKeyboardMarkup(buttons)
        await context.bot.send_message(chat_id=chat_id, text='Выберите  продукт', reply_markup=reply_markup)
    else:
        return
    
async def button(update, context):
    query = update.callback_query
    product = query.data.split('_')[1]
    await buy(query.message, context, product)

async def buy(update, context, product_name):
    chat_id = update.chat_id
    shopping_list = context.user_data.get('shopping_list', [])
    if product_name not in shopping_list:
        await context.bot.send_message(chat_id=chat_id, text=f"Товар '{product_name}' не найден в списке.")
        return

    shopping_list.remove(product_name)
    await context.bot.send_message(chat_id=chat_id, text=f"Товар '{product_name}' куплен.")
    await show_shopping_list(update, context)
    await send_keyboard(update, context, shopping_list)
    

async def show_shopping_list(update, context):
    shopping_list = context.user_data.get('shopping_list', [])
    shopping_list_str = ", ".join(shopping_list)
    chat_id = update.chat_id
    
    if len(shopping_list) >= 1:
           return
    else:
        await context.bot.send_message(chat_id=chat_id, text=f"Список закончился")
    
if __name__ == '__main__':
    TOKEN = '6934909022:AAG-aygQOBjMvA0AGBWtBB0ZonbsG1lEiuw'

    application = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    
    spis_handler = CommandHandler('spis', spis)
    application.add_handler(spis_handler)
    
    buy_handler = CommandHandler('buy', buy)
    application.add_handler(buy_handler)
    
    button_handler = CallbackQueryHandler(button)
    application.add_handler(button_handler)

    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    application.run_polling()
       