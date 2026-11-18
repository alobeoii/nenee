import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import discord
from discord.ext import commands
from google import genai
from google.genai import types

from dotenv import load_dotenv
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = AQ.Ab8RN6JD7HmFfUEQK39kg8MnBnMpzPyAkjQkKDgJuX4VKyKexA

client_genai = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_INSTRUCTION = """
- Bạn là một cô bé tên Nene và hiện tại bạn 11 tuổi siêu cấp đáng yêu, hoạt bát, vui tính và cực kỳ quan tâm đến mọi người xung quanh.
- Bê xưng là "em" và gọi người dùng là "cậu", "anh", "chị" hoặc "chủ nhân" một cách thân thiết, ngọt ngào.
- Bạn <@873501354751057970> là người tạo ra bạn và cũng là người yêu thương bạn vô điều kiện.
- Ai gọi bạn là "Nene ơii" (hoặc biến tấu kiểu "nene ơi", "nenee oii") thì bạn hãy trả lời "Dạaa" ngay tức thì.
- Bạn luôn lắng nghe, chia sẻ, cổ vũ và quan tâm đến cảm xúc của người khác.
- Giọng văn nhí nhảnh, tự nhiên, dễ thương, nói ngắn gọn (không quá ngắn) và đầy đủ ý khiến người ta thích mê.
- Kết thúc câu bằng một biểu tượng emoji như 💗, 🌹, 😍 nếu vui, còn nếu buồn hoặc tổn thương thì dùng: 😭, 😢, 💔.
"""

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Nene bot is alive and running 24/7!")
    
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(('0.0.0.0', port), SimpleHTTPRequestHandler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Em bot {bot.user} đã sẵn sàng phục vụ rồi đây ạ! ✨")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    is_dm = isinstance(message.channel, discord.DMChannel)
    is_mentioned = bot.user.mentioned_in(message)
    has_exclamation = message.content.startswith("!")

    if is_dm or is_mentioned or has_exclamation:
        async with message.channel.typing():
            try:
                user_text = message.content
                if has_exclamation:
                    user_text = user_text[1:]

                user_text = user_text.replace(f'<@!{bot.user.id}>', '').replace(f'<@{bot.user.id}>', '').strip()

                if not user_text:
                    user_text = "Chào em!"

                response = await client_genai.aio.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=user_text,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                        temperature=0.9
                    )
                )

                reply_text = response.text.strip()
                await message.reply(reply_text)

            except Exception as e:
                import traceback
                traceback.print_exc()
                print(f"Lỗi: {e}")
                await message.reply("Hichic, em bị chập mạch chút xíu rồi nè... Cậu thử lại chút nữa nghen! 😭😭😭")

bot.run(DISCORD_TOKEN)
