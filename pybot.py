from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import random
import time
import os

TOKEN: Final = os.getenv('BOTTOKEN')
BOT_USERNAME: Final = '@Quiz112233bot'

quiz_data = [
    {
        "question": "What is the capital of France?",
        "options": ["Paris", "London", "Berlin", "Madrid"],
        "correct_answer": "Paris",
        "points": 10
    },
    {
        "question": "Which planet is known as the Red Planet?",
        "options": ["Mars", "Venus", "Earth", "Jupiter"],
        "correct_answer": "Mars",
        "points": 10
    },
    {
        "question": "What is the largest mammal on Earth?",
        "options": ["Elephant", "Giraffe", "Blue Whale", "Lion"],
        "correct_answer": "Blue Whale",
        "points": 10
    }
]

user_data = {}

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id not in user_data:
        user_data[chat_id] = {"current_question_index": 0, "points": 0}
    user_data[chat_id]["start_time"] = time.time()
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
            start_time = user_data[chat_id]["start_time"]
            completion_time = int(time.time() - start_time)
            user_data[chat_id]["start_time"] = completion_time
            await display_leaderboard(update, context, chat_id, completion_time)
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
                        points = quiz_data[current_question_index]["points"]
                        user_data[chat_id]["points"] += points
                        await update.message.reply_text(f"Correct answer! 🎉 You earned {points} points.")
                    else:
                        await update.message.reply_text("Wrong answer. 😔")
                    user_data[chat_id]["current_question_index"] += 1
                    await quiz_command(update, context)
                else:
                    await update.message.reply_text("Please choose a valid option (1-4).")
            except ValueError:
                await update.message.reply_text("Please enter a valid number (1-4).")
    #     else:
    #         await update.message.reply_text("You have completed the quiz. Type /start to start over.")
    #         start_time = user_data["start_time"]
    #         completion_time = int(time.time() - start_time)
    #         await display_leaderboard(update,context,completion_time)
    # else:
    #     await update.message.reply_text("Please start the quiz with /start.")

async def display_leaderboard(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id, completion_time):
    for chat_id, data in user_data.items():
        user = await context.bot.get_chat(chat_id)
        points = data["points"]
        leaderboard_text += f"{user.first_name}: {points} points (Completed in {completion_time})\n"
    await update.message.reply_text(leaderboard_text)


if __name__ == '__main__':
    print("Starting bot...")
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('quiz', quiz_command))
    app.add_handler(MessageHandler(filters.TEXT, answer_question))

    print('Polling')
    app.run_polling(poll_interval=3)
