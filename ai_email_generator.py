from langchain.chat_models import init_chat_model
from dotenv import load_dotenv

load_dotenv()

model = init_chat_model(
    model="gemini-2.5-flash",
    model_provider="google_genai",
)

def generate_email(company_name="Company"):
    try:
        prompt = f"""
Write a professional job inquiry email.

Candidate Details:

Name: Harsha Vardhan

Experience:
4 Years

Skills:
Python, Django, FastAPI, PostgreSQL, AWS, Snowflake

Phone:
+91 6302146916

Email:
harshavardhanb448@gmail.com

LinkedIn:
https://www.linkedin.com/in/harsha2323

Company:
{company_name}

nstructions:
1. Use my actual phone number.
2. Use my actual email address.
3. Use my actual LinkedIn URL.
4. Do not use placeholders.
5. Keep it professional and concise.
"""

        response = model.invoke(prompt)

        return response.content + """

Regards,
Harsha Vardhan

Phone: +91 6302146916
Email: harshavardhanb448@gmail.com
LinkedIn: https://www.linkedin.com/in/harsha2323
"""

    except Exception as e:
        print("AI Generation Failed:", e)

        return f"""
Hello,

I am Harsha Vardhan, a Python Developer with 4 years of experience in Django, FastAPI, PostgreSQL, AWS and Snowflake.

I have worked on scalable REST APIs, ETL pipelines, and real-time data processing systems in projects like Profitero and Royalty Exchange.

I am currently looking for Python Developer opportunities at {company_name}.

LinkedIn:
https://www.linkedin.com/in/harsha2323

Phone:
+91 6302146916

Thanks & Regards,
Harsha Vardhan
"""