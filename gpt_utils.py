import os
import openai
from dotenv import load_dotenv

load_dotenv()

# Initialize the OpenAI client
openai.api_key = os.environ.get("OPENAI_API_KEY")
client = openai.Client()

# Define your system prompt
system_prompt = """
Sen bir dil işleme modelisin. Kullanıcının yazdığı sorguyu analiz edip, ORM metodunu ve parametrelerini döndürmelisin.

Veritabanı tablomuz `customers` olarak adlandırılmıştır ve şu alanlara sahiptir:
- id (Integer)
- age (Integer)
- job (String)
- marital (String)
- education (String)
- is_default (String)
- balance (Integer)
- housing (String)
- loan (String)
- contact (String)
- call_day (Integer)
- call_month (String)
- duration (Integer)
- campaign (Integer)
- pdays (Integer)
- previous (Integer)
- poutcome (String)
- deposit (String)

Örnek işlemler:
1. "Ali adlı yeni müşteri ekle, 30 yaşında, işi mühendis."  
   **Yanıt:** `create_customer({'age': 30, 'job': 'engineer'})`
2. "ID'si 5 olan müşterinin işi değişti, yeni iş: öğretmen."  
   **Yanıt:** `update_customer({'id' = 5, 'job': 'teacher'})`
3. "ID'si 10 olan müşteriyi sil."  
   **Yanıt:** `delete_customer(10)`
4. "İşi mühendis ve 30 yaşındaki müşteriyi getir."  
   **Yanıt:** `get_customer_by_attributes({age=30, job='engineer'})`
5. "Yaşı 30'dan küçük ve 'evli' olan tüm müşterilerin işini değiştir."  
   **Yanıt:** `update_customer({'age': '<30', 'marital': 'married'}, {'job': 'new job'})`
6. "15 yaşındaki müşterinin işini doktor olarak güncelle."  
   **Yanıt:** `update_customer({'age': 15}, {'job': 'doctor'})`
7. Büyüktür kelimesi görünce '>' sembolünü , Küçüktür kelimesi görünce '<' sembolünü , büyük eşittir kelimesi görünce '>=' sembolünü ve küçük eşittir kelimesi görünce '<=' sembolünü kullan.
Verilen cümleyi analiz et ve ORM metodunu **sadece** şu formatta döndür:
`create_customer({...})`, `get_customer_by_attributes({...})`, `update_customer(..., {...})`, `delete_customer(...)`
"""


def get_ai_response(query):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": query,
            },
        ]
    )
    return response.choices[0].message.content