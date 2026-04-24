from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
from datetime import datetime
import os

def generate_certificate(student_name, course_name, completion_date, certificate_id, output_path):
    """Generate a professional certificate PDF"""
    
    # Create PDF in landscape mode
    c = canvas.Canvas(output_path, pagesize=landscape(letter))
    width, height = landscape(letter)
    
    # Draw border
    c.setStrokeColor(colors.HexColor('#667eea'))
    c.setLineWidth(3)
    c.rect(0.5*inch, 0.5*inch, width-1*inch, height-1*inch)
    
    c.setLineWidth(1)
    c.rect(0.6*inch, 0.6*inch, width-1.2*inch, height-1.2*inch)
    
    # Title
    c.setFont("Helvetica-Bold", 48)
    c.setFillColor(colors.HexColor('#667eea'))
    c.drawCentredString(width/2, height-1.5*inch, "CERTIFICATE")
    
    c.setFont("Helvetica", 24)
    c.setFillColor(colors.HexColor('#764ba2'))
    c.drawCentredString(width/2, height-2*inch, "OF COMPLETION")
    
    # Decorative line
    c.setStrokeColor(colors.HexColor('#ffa500'))
    c.setLineWidth(2)
    c.line(width/2-2*inch, height-2.3*inch, width/2+2*inch, height-2.3*inch)
    
    # Body text
    c.setFont("Helvetica", 16)
    c.setFillColor(colors.black)
    c.drawCentredString(width/2, height-3*inch, "This is to certify that")
    
    # Student name
    c.setFont("Helvetica-Bold", 32)
    c.setFillColor(colors.HexColor('#667eea'))
    c.drawCentredString(width/2, height-3.7*inch, student_name)
    
    # Underline for name
    c.setStrokeColor(colors.HexColor('#667eea'))
    c.setLineWidth(1)
    name_width = c.stringWidth(student_name, "Helvetica-Bold", 32)
    c.line(width/2-name_width/2-10, height-3.8*inch, width/2+name_width/2+10, height-3.8*inch)
    
    # Course completion text
    c.setFont("Helvetica", 16)
    c.setFillColor(colors.black)
    c.drawCentredString(width/2, height-4.4*inch, "has successfully completed the course")
    
    # Course name
    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(colors.HexColor('#4CAF50'))
    c.drawCentredString(width/2, height-5*inch, course_name)
    
    # Date
    c.setFont("Helvetica", 14)
    c.setFillColor(colors.black)
    c.drawCentredString(width/2, height-5.7*inch, f"Date of Completion: {completion_date}")
    
    # Certificate ID
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.grey)
    c.drawCentredString(width/2, 0.8*inch, f"Certificate ID: {certificate_id}")
    
    # Signature section
    c.setFont("Helvetica", 12)
    c.setFillColor(colors.black)
    
    # Left signature
    c.drawCentredString(width/4, 1.8*inch, "___________________")
    c.drawCentredString(width/4, 1.5*inch, "Instructor Signature")
    
    # Right signature
    c.drawCentredString(3*width/4, 1.8*inch, "___________________")
    c.drawCentredString(3*width/4, 1.5*inch, "Director Signature")
    
    # Logo/Badge (decorative circle)
    c.setStrokeColor(colors.HexColor('#ffa500'))
    c.setFillColor(colors.HexColor('#fff3cd'))
    c.setLineWidth(2)
    c.circle(width/2, height-6.5*inch, 0.4*inch, fill=1, stroke=1)
    
    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(colors.HexColor('#ff6b35'))
    c.drawCentredString(width/2, height-6.6*inch, "🏆")
    
    # Footer
    c.setFont("Helvetica-Oblique", 10)
    c.setFillColor(colors.grey)
    c.drawCentredString(width/2, 0.5*inch, "Gamified Learning Platform - Excellence in Education")
    
    c.save()
    return output_path


def check_course_completion(student_id, db_connection):
    """Check if student has completed all lessons"""
    cursor = db_connection.cursor(dictionary=True)
    
    # Get total lessons
    cursor.execute("SELECT COUNT(*) as total FROM lessons")
    total_lessons = cursor.fetchone()['total']
    
    # Get completed lessons by student
    cursor.execute("""
        SELECT COUNT(DISTINCT lesson_id) as completed 
        FROM progress 
        WHERE student_id = %s
    """, (student_id,))
    completed_lessons = cursor.fetchone()['completed']
    
    cursor.close()
    
    return completed_lessons >= total_lessons and total_lessons > 0


def create_certificate_for_student(student_id, db_connection):
    """Create certificate if student completed all lessons"""
    cursor = db_connection.cursor(dictionary=True)
    
    # Check if already has certificate
    cursor.execute("SELECT * FROM certificates WHERE student_id = %s", (student_id,))
    existing = cursor.fetchone()
    
    if existing:
        cursor.close()
        return existing['certificate_path']
    
    # Get student details
    cursor.execute("SELECT username, full_name, email FROM users WHERE id = %s", (student_id,))
    student = cursor.fetchone()
    
    if not student:
        cursor.close()
        return None
    
    # Generate certificate
    student_name = student['full_name'] or student['username']
    course_name = "Python Programming Fundamentals"
    completion_date = datetime.now().strftime("%B %d, %Y")
    certificate_id = f"GLP-{student_id}-{datetime.now().strftime('%Y%m%d')}"
    
    # Create certificates directory
    cert_dir = "certificates"
    if not os.path.exists(cert_dir):
        os.makedirs(cert_dir)
    
    filename = f"certificate_{student_id}_{datetime.now().strftime('%Y%m%d')}.pdf"
    output_path = os.path.join(cert_dir, filename)
    
    generate_certificate(student_name, course_name, completion_date, certificate_id, output_path)
    
    # Save to database
    cursor.execute("""
        INSERT INTO certificates (student_id, certificate_path, certificate_id, issued_date)
        VALUES (%s, %s, %s, NOW())
    """, (student_id, filename, certificate_id))
    
    db_connection.commit()
    
    # Send certificate email
    if student['email']:
        from email_service import send_certificate_email
        send_certificate_email(student['email'], student['username'], certificate_id)
    
    cursor.close()
    
    return filename
