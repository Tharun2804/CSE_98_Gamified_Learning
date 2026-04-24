import google.generativeai as genai
import os
from PyPDF2 import PdfReader
import docx

# Configure Gemini API
GEMINI_API_KEY = "AIzaSyBHY2IVA8CiFYyzmO4PRnvBnO5_pMn2q1c"  # Get from https://makersuite.google.com/app/apikey
genai.configure(api_key=GEMINI_API_KEY)

# Initialize model
model = genai.GenerativeModel('gemini-2.0-flash')

def get_ai_response(user_message, student_name="Student"):
    """Get AI response for student doubts and questions"""
    
    prompt = f"""You are a friendly and helpful AI tutor for students in a gamified learning platform.
    
Student: {student_name}
Question: {user_message}

Provide a clear, educational, and encouraging response. Include:
- Simple explanations
- Examples when helpful
- Encouragement and motivation
- Use emojis occasionally to make it friendly

Keep responses concise but informative (2-4 paragraphs max).

Response:"""
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}. Please try again or contact your teacher."

def extract_text_from_file(file_path):
    """Extract text content from PPT, PDF, or DOCX files"""
    
    file_ext = os.path.splitext(file_path)[1].lower()
    text_content = ""
    
    try:
        if file_ext == '.pdf':
            reader = PdfReader(file_path)
            for page in reader.pages:
                text_content += page.extract_text() + "\n"
        
        elif file_ext in ['.docx', '.doc']:
            doc = docx.Document(file_path)
            for paragraph in doc.paragraphs:
                text_content += paragraph.text + "\n"
        
        elif file_ext in ['.ppt', '.pptx']:
            # For PPT files, we'll use the filename and ask teacher to provide summary
            text_content = f"Presentation file: {os.path.basename(file_path)}"
        
        else:
            text_content = "Unable to extract text from this file format."
    
    except Exception as e:
        text_content = f"Error extracting text: {str(e)}"
    
    return text_content

def generate_quiz_from_content(content, title, num_questions=5):
    """Generate quiz questions automatically from presentation/document content"""
    
    prompt = f"""Based on the following educational content, generate {num_questions} multiple choice quiz questions.

Content Title: {title}
Content: {content[:3000]}  

Generate exactly {num_questions} questions in this EXACT format:

QUESTION 1:
Question: [Write the question here]
A) [Option A]
B) [Option B]
C) [Option C]
D) [Option D]
Correct: [A/B/C/D]

QUESTION 2:
[Continue same format...]

Requirements:
- Questions should test understanding of key concepts
- Make questions clear and educational
- Ensure one correct answer per question
- Difficulty: Moderate (suitable for students)
- Cover different aspects of the content
"""
    
    try:
        response = model.generate_content(prompt)
        return parse_quiz_questions(response.text)
    except Exception as e:
        return None, f"Error generating quiz: {str(e)}"

def parse_quiz_questions(ai_response):
    """Parse AI response into structured quiz questions"""
    
    questions = []
    lines = ai_response.strip().split('\n')
    
    current_question = {}
    
    for line in lines:
        line = line.strip()
        
        if line.startswith('Question:'):
            if current_question:
                questions.append(current_question)
            current_question = {'question': line.replace('Question:', '').strip()}
        
        elif line.startswith('A)'):
            current_question['option_a'] = line.replace('A)', '').strip()
        elif line.startswith('B)'):
            current_question['option_b'] = line.replace('B)', '').strip()
        elif line.startswith('C)'):
            current_question['option_c'] = line.replace('C)', '').strip()
        elif line.startswith('D)'):
            current_question['option_d'] = line.replace('D)', '').strip()
        
        elif line.startswith('Correct:'):
            correct = line.replace('Correct:', '').strip().upper()
            if correct in ['A', 'B', 'C', 'D']:
                current_question['correct_answer'] = correct
    
    if current_question and 'correct_answer' in current_question:
        questions.append(current_question)
    
    return questions, None

def generate_simple_quiz(title, num_questions=3):
    """Generate quiz questions based on title when content extraction fails"""
    
    prompt = f"""Generate {num_questions} multiple choice quiz questions about: {title}

Format each question EXACTLY like this:

QUESTION 1:
Question: [Write question here]
A) [Option A]
B) [Option B]
C) [Option C]
D) [Option D]
Correct: [A/B/C/D]

Make questions educational and appropriate for students."""
    
    try:
        response = model.generate_content(prompt)
        return parse_quiz_questions(response.text)
    except Exception as e:
        return None, f"Error: {str(e)}"

def get_lesson_help(lesson_title):
    """Get detailed explanation for a lesson"""
    
    prompt = f"""Explain the topic "{lesson_title}" in a simple, student-friendly way.

Include:
1. What it is (simple definition)
2. Why it's important
3. A real-world example
4. Key points to remember

Keep it concise and easy to understand. Use emojis to make it engaging.

Explanation:"""
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error getting explanation: {str(e)}"

def get_study_tips(topic="general"):
    """Get personalized study tips"""
    
    prompt = f"""Provide 5 effective study tips for learning {topic}.

Make them:
- Practical and actionable
- Suitable for students
- Motivating and encouraging
- Include emojis

Format as a numbered list."""
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error getting study tips: {str(e)}"

def get_quiz_hint(question, student_answer):
    """Provide hint for quiz question without giving away answer"""
    
    prompt = f"""A student answered a quiz question incorrectly. Provide a helpful hint without revealing the answer.

Question: {question}
Student's Answer: {student_answer}

Provide a hint that:
- Guides them to think about the concept
- Doesn't give away the answer directly
- Encourages them to try again
- Is supportive and motivating

Hint:"""
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return "Think about the key concepts in the lesson. You can do this! 💪"
