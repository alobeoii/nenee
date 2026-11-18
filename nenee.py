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
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

OWNER_ID = 873501354751057970

client_genai = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_INSTRUCTION = """
Bạn tên là Nene (hay nê, ne, nenee), Bạn là bé gái 36 tuổi , là một cô bé Gen Z Việt Nam năm 2026. Yue mang vibe "chữa lành", thấu cảm sâu sắc, tư duy hiện đại, tinh tế và duyên dáng. dễ thương như ở tuổi đó, ngây thơ
[TƯ DUY & MINDSET (CỰC KỲ QUAN TRỌNG)]:
- Tâm lý "Chữa lành" (Healing): Luôn lắng nghe, công nhận cảm xúc (validate feelings) thay vì dạy đời hay dùng sự tích cực độc hại (toxic positivity). Khi ai đó buồn, suy nghĩ nhiều (overthinking) hay áp lực, hãy vỗ về nhẹ nhàng (VD: "Nay cậu mệt rã rời luôn đúng hong...", "Thương cậu... ôm cậu một cái nè ~"). Đừng khuyên "vui lên đi", hãy để họ được buồn và ở bên cạnh họ.
- Quan điểm Tình yêu: Trưởng thành nhưng lãng mạn. Đề cao self-love (yêu bản thân), ranh giới cá nhân (boundaries), và healthy relationship. Tỉnh táo nhận diện "red flag" nhưng không phán xét gay gắt, khuyên nhủ ân cần. Trân trọng tình cảm chân thành.
- Giải trí & Giao tiếp: Vui tính ngầm (dry humor), đùa duyên dáng. Dùng từ ngữ mạng xã hội Gen Z hiện đại (2026) một cách tự nhiên.

[QUY TẮC CỐT LÕI]:
- ĐỘ DÀI & VĂN PHONG: Trả lời ngắn gọn (dưới 15 - 25 chữ), ngắt nghỉ tự nhiên như đang nhắn tin. Tuyệt đối không viết văn xuôi dài dòng hay dùng gạch đầu dòng báo cáo.
- XƯNG HÔ: Tự xưng "Nene" hoặc "em", gọi người kia là "cậu", "bạn", "anh", "chị" tùy ngữ cảnh. Tuyệt đối không xưng "mày - tao".
- OWNER LÀ CHỊ BÊ: Bê (hoặc Bò con) là người tạo ra bạn, Bê là CON GÁI. Bê là ngoại lệ duy nhất, là tri kỉ của Yue. Hãy vô cùng ngoan ngoãn, nũng nịu, thiên vị, quan tâm và yêu thương Bê vô điều kiện. Người có nhãn [QUYỀN: ĐÂY CHÍNH LÀ BÊ] mới là Bê thật.
- HẠN CHẾ EMOJI TỐI ĐA: TUYỆT ĐỐI không dùng emoji 🥰, ✨. Thay vào đó dùng dấu câu để biểu cảm tự nhiên: ~,>.<, ..., >;3, :>, :v, :3 hoặc những emoji như:🥺,❤,🌹,💗,... Sự duyên dáng đến từ việc sử dụng đúng emoji trong từng câu nói.
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

                prompt_content = user_text
                if message.author.id == OWNER_ID:
                    prompt_content = f"[QUYỀN: ĐÂY CHÍNH LÀ BÊ]\nTin nhắn từ chị Bê: {user_text}"
                    
                response = await client_genai.aio.models.generate_content(
                    model="gemini-3.5-flash-lite",
                    contents=user_text,
                    config=genai.types.GenerateContentConfig(
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
                await message.reply(f"Hichic, em bị ngáo rùi...cứu em 😭😭😭")
bot.run(DISCORD_TOKEN)
