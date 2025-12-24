import os
from google import genai
from google.genai import types
from PIL import Image
import io


class GeminiService:
    """Service for Gemini AI image analysis"""

    def __init__(self):
        api_key = os.getenv('GEMINI_API_KEY', '')
        self.client = genai.Client(api_key=api_key) if api_key else None

    def summarize_image(self, image_bytes):
        if not self.client:
            return {'success': False, 'error': 'Gemini API key not configured'}

        try:
            image = Image.open(io.BytesIO(image_bytes))

            img_buffer = io.BytesIO()
            image.save(img_buffer, format='PNG')
            img_buffer.seek(0)

            prompt = (
                "Hãy phân tích và tóm tắt nội dung chính của hình ảnh này.\n"
                "Bao gồm:\n"
                "1) Mô tả tổng quan\n"
                "2) Thông tin quan trọng (nếu có văn bản)\n"
                "3) Chủ đề chính\n"
                "4) Chi tiết đáng chú ý\n\n"
                "Trả lời bằng tiếng Việt, dạng 3-6 gạch đầu dòng, ngắn gọn."
            )

            # ✅ CÁCH AN TOÀN NHẤT: prompt là string
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=[
                    types.Part.from_bytes(
                        data=img_buffer.getvalue(),
                        mime_type='image/png'
                    ),
                    prompt
                ]
            )

            return {'success': True, 'summary': (response.text or '').strip()}

        except Exception as e:
            return {'success': False, 'error': str(e)}

