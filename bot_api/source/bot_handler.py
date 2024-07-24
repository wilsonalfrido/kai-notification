from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, KeyboardButton,InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode

from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler
)

from apscheduler.schedulers.background import BackgroundScheduler

from source.get_ticket_data import get_ticket_data, get_ticket_data_str, get_list_ticket
from source.scheduler import run_notif_scheduler_task,get_list_notif_scheduler_str,run_all_active_scheduler,get_dict_notif_scheduler,get_scheduler_by_id_str,update_scheduler_status
from source.logger import create_logger

from databases.sqlalchemy.utils import insert_db_scheduler_tasks

from source.calendar import create_calendar, process_calendar_selection
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP

from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor

logger = create_logger(__name__)

test_data = {
    "origin": "sukabumi",
    "destination": "bogor",
    "depart_date" : "15-04-2024"
}
CHECK_TICKET,ADD_SCHEDULER,INPUT_BOOK_DATA,ORIGIN,DESTINATION,DATE,LIST_TICKET,LIST_TICKET_CONFIRMATION,INTERVAL_SCHEDULER,DELETE_SCHEDULER_CONFIRMATION,DELETE_SCHEDULER_ACTION = range(11)

executors = {
    'default': ThreadPoolExecutor(5),
    'processpool': ProcessPoolExecutor(5)
}
job_defaults = {
    'coalesce': False,
    'max_instances': 3,
    'misfire_grace_time': 15*60
}

class KaiNotifBot:
    def __init__(self,token,stage) -> None:
        self.token = token
        self.stage=stage
        self.scheduler = BackgroundScheduler(logger=logger,
                                             job_defaults=job_defaults,
                                             executors=executors)
        self.application = Application.builder().token(token).build()
        self.scheduler.start()

        logger.info(f'Run all active scheduler')
        run_all_active_scheduler(self.token,self.scheduler)

    def start_bot(self): 
        # for handler in list_handler:
        self.application.add_handler(self.get_conv_handler())
        self.application.add_handler(self.get_list_notif_scheduler_handler())
        self.application.add_handler(self.delete_scheduler_handler())
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

    async def start(self,update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Starts the conversation and asks the user about their gender."""
        reply_keyboard = [["Add Notif Scheduler","Check Ticket"]]

        await update.message.reply_text(
            "Hi! My name is KAI notif Bot. I will hold a conversation with you. "
            "Send /cancel to stop talking to me.\n\n"
            "What can I help you with?",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard, one_time_keyboard=True, input_field_placeholder="Features?"
            ),
        )

        return ORIGIN

    async def input_origin(self,update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data["mode"] = update.message.text
        
        await update.message.reply_text("Please enter the origin (departure city).")

        return DESTINATION

    async def input_destination(self,update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data["origin"] = update.message.text
        await update.message.reply_text("Please enter the destination (arrival city).")

        return DATE

    async def input_depart_date(self,update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data["destination"] = update.message.text

        await update.message.reply_text("Please enter the departure date (DD-MM-YYYY).")

        return LIST_TICKET

    
    async def input_list_ticket(self,update:Update,context:ContextTypes.DEFAULT_TYPE):
        context.user_data["depart_date"] = update.message.text

        
        input_book_data = {
            "origin": context.user_data["origin"],
            "destination": context.user_data["destination"],
            "depart_date" : context.user_data["depart_date"]
        }

        ticket_dict = get_list_ticket(input_book_data)
        context.user_data["ticket_dict"] = ticket_dict


        keyboards = []
        for ticket_code in ticket_dict:
            keyboard = [InlineKeyboardButton(f'{ticket_dict[ticket_code]}', callback_data=f'{ticket_code}')]
            keyboards.append(keyboard)
        keyboards.append([InlineKeyboardButton("Submit", callback_data='submit')])
        reply_markup = InlineKeyboardMarkup(keyboards)
        await update.message.reply_text('Please choose schedule:', reply_markup=reply_markup)

        return LIST_TICKET_CONFIRMATION
    
    def generate_checklist_keyboard(self,selected_tickets, ticket_dict):
        keyboards = []
        for ticket_code, ticket_info in ticket_dict.items():
            if ticket_code in selected_tickets:
                keyboard = [InlineKeyboardButton(f"[x] {ticket_info}", callback_data=ticket_code)]
            else:
                keyboard = [InlineKeyboardButton(f"[ ] {ticket_info}", callback_data=ticket_code)]
            keyboards.append(keyboard)
        keyboards.append([InlineKeyboardButton("Submit", callback_data='submit')])
        return InlineKeyboardMarkup(keyboards)

    async def input_list_ticket(self,update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data["depart_date"] = update.message.text

        input_book_data = {
            "origin": context.user_data.get("origin"),
            "destination": context.user_data.get("destination"),
            "depart_date": context.user_data["depart_date"]
        }

        ticket_dict = get_list_ticket(input_book_data)
        context.user_data['ticket_dict'] = ticket_dict
        context.user_data['selected_tickets'] = set()

        reply_markup = self.generate_checklist_keyboard(context.user_data['selected_tickets'], ticket_dict)
        await update.message.reply_text('Please choose schedule:', reply_markup=reply_markup)

        return LIST_TICKET_CONFIRMATION

    async def list_ticket_confirmation(self,update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        mode = context.user_data["mode"]
        await query.answer()

        ticket_dict = context.user_data['ticket_dict']
        selected_ticket_code = query.data

        if selected_ticket_code == 'submit':
            if context.user_data['selected_tickets']:
                selected_tickets_info = [ticket_dict[code] for code in context.user_data['selected_tickets']]
                await query.edit_message_text(text=f"You have selected tickets:\n" + "\n".join(selected_tickets_info))
                
                if(mode == "Add Notif Scheduler"):
                    return INTERVAL_SCHEDULER
                elif(mode == "Check Ticket"):
                    return CHECK_TICKET
        else:
            if selected_ticket_code in context.user_data['selected_tickets']:
                context.user_data['selected_tickets'].remove(selected_ticket_code)
            else:
                context.user_data['selected_tickets'].add(selected_ticket_code)
            
            reply_markup = self.generate_checklist_keyboard(context.user_data['selected_tickets'], ticket_dict)
            await query.edit_message_text(text="Please choose schedule:", reply_markup=reply_markup)
        
            return LIST_TICKET_CONFIRMATION
    
    async def check_ticket_available(self,update: Update, context: ContextTypes.DEFAULT_TYPE):
        context_book_data = f'Mode : {context.user_data["mode"]}\n\nOrigin : {context.user_data["origin"]}\nDestination : {context.user_data["destination"]}\nDepart Date : {context.user_data["depart_date"]}\nProcessing ... \n'
        await update.message.reply_text(context_book_data) 

        input_book_data = {
            "origin": context.user_data["origin"],
            "destination": context.user_data["destination"],
            "depart_date" : context.user_data["depart_date"]
        }
        list_filter_ticket_code = context.user_data['selected_tickets']
        df_ticket_data = get_ticket_data(input_book_data,self.stage,list_filter_ticket_code)
        ticket_data_str = get_ticket_data_str(df_ticket_data,input_book_data)
            
        await update.message.reply_text(
            ticket_data_str,
            parse_mode=ParseMode.MARKDOWN_V2
        )
    
        return ConversationHandler.END
        
    async def input_interval_scheduler(self,update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Please enter interval scheduler (in minutes): ")

        return ADD_SCHEDULER

    async def add_scheduler(self,update: Update, context: ContextTypes.DEFAULT_TYPE):  
        context.user_data["interval_scheduler"] = int(update.message.text)
        chat_id = update.message.chat_id
        context_book_data = f'Mode : {context.user_data["mode"]}\n\nOrigin : {context.user_data["origin"]}\nDestination : {context.user_data["destination"]}\nDepart Date : {context.user_data["depart_date"]}\nInterval Scheduler : {context.user_data["interval_scheduler"]}\nProcessing ... '
        await update.message.reply_text(context_book_data) 

        id = insert_db_scheduler_tasks(chat_id=chat_id,
                            origin=context.user_data["origin"],
                            destination=context.user_data["destination"],
                            depart_date=context.user_data["depart_date"],
                            depart_time="",
                            interval_scheduler=context.user_data["interval_scheduler"],
                            list_ticket_code=",".join(context.user_data['selected_tickets']))

        input_book_data = {
            "origin": context.user_data["origin"],
            "destination": context.user_data["destination"],
            "depart_date" : context.user_data["depart_date"]
        }

        logger.info(f'Add scheduler task of user with id : {chat_id}')
        self.scheduler.add_job(func= run_notif_scheduler_task,args=(self.scheduler,id,self.token,chat_id,input_book_data,self.stage,context.user_data["interval_scheduler"]), 
                               trigger='interval',
                               minutes=int(context.user_data["interval_scheduler"]), 
                               id=id)
        logger.info(f'Succesfully Add scheduler task of user with id : {chat_id}')

        return ConversationHandler.END

    async def cancel(self,update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Cancels and ends the conversation."""
        user = update.message.from_user
        # logger.info("User %s canceled the conversation.", user.first_name)
        await update.message.reply_text(
            "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
        )

        return ConversationHandler.END

    async def get_list_notif_scheduler(self,update: Update, context: ContextTypes.DEFAULT_TYPE):
        list_notif_scheduler_str = get_list_notif_scheduler_str(chat_id=update.message.chat_id)

        await update.message.reply_text(
            list_notif_scheduler_str,
            parse_mode="Markdown"
        ) 
    
    async def delete_notif_scheduler(self,update: Update, context: ContextTypes.DEFAULT_TYPE):


        dict_notif = get_dict_notif_scheduler(update.message.chat_id)
        keyboard = []
        for id in dict_notif.keys():
            temp = [InlineKeyboardButton(dict_notif[id], callback_data=id)]
            keyboard.append(temp)

        # Create the InlineKeyboardMarkup object
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            "<code>Please choose scheduler to be deleted</code>", reply_markup=reply_markup,parse_mode=ParseMode.HTML
        )
    
        return DELETE_SCHEDULER_CONFIRMATION 

    async def button_delete_confirmation(self,update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        button_yes = InlineKeyboardButton("YES", callback_data=f"yes_{query.data}")
        button_no = InlineKeyboardButton("NO", callback_data=f"no_{query.data}")

        keyboard = [[button_yes,button_no]]

        reply_markup = InlineKeyboardMarkup(keyboard)

        text = get_scheduler_by_id_str(id=query.data)
        await query.answer()
        await query.edit_message_text(text=f"Are you sure you want to delete the scheduler ? : {text}",
                                      reply_markup=reply_markup,parse_mode=ParseMode.MARKDOWN_V2)
        
        return DELETE_SCHEDULER_ACTION

    async def button_delete_action(self,update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        # status_str = update_scheduler_status(id=query.data)
        
        data = query.data.split("_")
        answer = data[0]
        id = data[1]
        if(answer == "yes"):
            status,status_str = update_scheduler_status(id=id)
            if(status == "success"):
                self.scheduler.remove_job(job_id=id)
        else:
            status_str = f'Cancelled deletion of scheduler with ID : `{id}`'
        await query.edit_message_text(text=status_str,parse_mode=ParseMode.MARKDOWN_V2)

        return ConversationHandler.END

    #HANDLER

    def get_conv_handler(self):

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("start", self.start)],
            states={
                ORIGIN : [MessageHandler(filters.TEXT & ~filters.COMMAND, self.input_origin)],
                DESTINATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.input_destination)],
                DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.input_depart_date)],
                LIST_TICKET: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.input_list_ticket)],
                LIST_TICKET_CONFIRMATION: [CallbackQueryHandler(self.list_ticket_confirmation)],
                ADD_SCHEDULER: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.add_scheduler)],
                CHECK_TICKET: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.check_ticket_available)],
                INTERVAL_SCHEDULER : [MessageHandler(filters.TEXT & ~filters.COMMAND, self.input_interval_scheduler)]
            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
        )

        return conv_handler
    
    def get_list_notif_scheduler_handler(self):

        get_list_notif_scheduler = CommandHandler("list_scheduler",self.get_list_notif_scheduler)

        return get_list_notif_scheduler

    def delete_scheduler_handler(self):

        # delete_scheduler = CommandHandler("delete_scheduler",self.delete_notif_scheduler)

        delete_scheduler = ConversationHandler(
            entry_points=[CommandHandler("delete_scheduler",self.delete_notif_scheduler)],
            states={
                # DELETE_SCHEDULER_CONFIRMATION : [MessageHandler(filters.TEXT & ~filters.COMMAND, self.delete_confirmation)],
                DELETE_SCHEDULER_CONFIRMATION : [CallbackQueryHandler(self.button_delete_confirmation)],
                DELETE_SCHEDULER_ACTION: [CallbackQueryHandler(self.button_delete_action)]

            },
            fallbacks=[CommandHandler("cancel", self.cancel)],
        )

        return delete_scheduler