from certificate_service import generate_certificate
from datetime import datetime

# Generate a sample certificate
student_name = "John Doe"
course_name = "Python Programming Fundamentals"
completion_date = datetime.now().strftime("%B %d, %Y")
certificate_id = "GLP-SAMPLE-20240208"
output_path = "certificates/sample_certificate.pdf"

generate_certificate(student_name, course_name, completion_date, certificate_id, output_path)

print(f"Sample certificate generated: {output_path}")
print("Open the PDF to see your certificate!")
