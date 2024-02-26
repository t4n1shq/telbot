from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import random
impor os

TOKEN: Final = os.getenv('BOTTOKEN')#'6505672082:AAFmlvQV-Igz6AqOQQf2ugN0JGs-2OtoKVI'
BOT_USERNAME: Final = '@Quiz112233bot'

quiz_data = [
    {
        "question": "What is the capital of France?",
        "options": ["Paris", "London", "Berlin", "Madrid"],
        "correct_answer": "Paris"
    },
    {
        "question": "Which planet is known as the Red Planet?",
        "options": ["Mars", "Venus", "Earth", "Jupiter"],
        "correct_answer": "Mars"
    },
    {
        "question": "What is the largest mammal on Earth?",
        "options": ["Elephant", "Giraffe", "Blue Whale", "Lion"],
        "correct_answer": "Blue Whale"
    }
]

user_data = {}

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data[update.message.chat_id] = {"current_question_index": 0}
    await update.message.reply_text('Hello, Welcome to the quiz bot. Type /quiz to start the quiz.')

async def quiz_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    user = user_data.get(chat_id)
    
    if user:
        current_question_index = user["current_question_index"]
        if current_question_index < len(quiz_data):
            question_data = quiz_data[current_question_index]
            question = question_data["question"]
            options = question_data["options"]
            
            random.shuffle(options)
            
            user_data[chat_id]["correct_answer"] = question_data["correct_answer"]
            
            reply_text = f"Question {current_question_index + 1}: {question}\n\n"
            for i, option in enumerate(options):
                reply_text += f"{i + 1}. {option}\n"
            reply_text += "\nReply with the number of your answer."
            
            await update.message.reply_text(reply_text)
        else:
            await update.message.reply_text("You have completed the quiz. Type /start to start over.")
    else:
        await update.message.reply_text("Please start the quiz with /start.")

async def answer_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    user = user_data.get(chat_id)
    
    if user:
        current_question_index = user["current_question_index"]
        if current_question_index < len(quiz_data):
            try:
                chosen_option = int(update.message.text)
                correct_answer = user["correct_answer"]
                if chosen_option >= 1 and chosen_option <= 4:
                    if quiz_data[current_question_index]["options"][chosen_option - 1] == correct_answer:
                        await update.message.reply_text("Correct answer! 🎉")
                    else:
                        await update.message.reply_text("Wrong answer. 😔")
                    user_data[chat_id]["current_question_index"] += 1
                    quiz_command(update, context) 
                else:
                    await update.message.reply_text("Please choose a valid option (1-4).")
            except ValueError:
                await update.message.reply_text("Please enter a valid number (1-4).")
        else:
            await update.message.reply_text("You have completed the quiz. Type /start to start over.")
    else:
        await update.message.reply_text("Please start the quiz with /start.")

if __name__ == '__main__':
    print("Starting bot...")
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('quiz', quiz_command))
    app.add_handler(MessageHandler(filters.TEXT, answer_question))

    print('Polling')
    app.run_polling(poll_interval=3)
