import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email Configuration
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USER = 'tharunsaisai2@gmail.com'
EMAIL_PASSWORD = 'xtwk zhwc vete vdzx'
EMAIL_FROM = 'Gamified Learning Platform'

def send_email(to_email, subject, body):
    """Send email to user"""
    try:
        msg = MIMEMultipart()
        msg['From'] = f"{EMAIL_FROM} <{EMAIL_USER}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

def send_registration_email(to_email, username, role):
    """Send registration confirmation email"""
    subject = "Registration Submitted - Gamified Learning"
    body = f"""
    <html>
        <body style="font-family: Arial; padding: 20px;">
            <h2 style="color: #667eea;">Welcome to Gamified Learning Platform!</h2>
            <p>Hello <strong>{username}</strong>,</p>
            <p>Your registration as a <strong>{role}</strong> has been submitted successfully.</p>
            <p>Your account is pending admin approval. You will receive another email once approved.</p>
            <br>
            <p>Thank you for joining us!</p>
            <p style="color: #666;">- Gamified Learning Team</p>
        </body>
    </html>
    """
    return send_email(to_email, subject, body)

def send_approval_email(to_email, username, role):
    """Send account approval email"""
    subject = "Account Approved - Gamified Learning"
    body = f"""
    <html>
        <body style="font-family: Arial; padding: 20px;">
            <h2 style="color: #4CAF50;">Your Account Has Been Approved!</h2>
            <p>Hello <strong>{username}</strong>,</p>
            <p>Great news! Your <strong>{role}</strong> account has been approved by the admin.</p>
            <p>You can now login and start using the platform.</p>
            <br>
            <p><a href="http://localhost:5000/login" style="background: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Login Now</a></p>
            <br>
            <p>Happy Learning!</p>
            <p style="color: #666;">- Gamified Learning Team</p>
        </body>
    </html>
    """
    return send_email(to_email, subject, body)

def send_streak_milestone_email(to_email, username, streak_days):
    """Send streak milestone achievement email"""
    subject = f"🔥 {streak_days} Day Streak Achievement!"
    body = f"""
    <html>
        <body style="font-family: Arial; padding: 20px;">
            <h2 style="color: #ff6b35;">🔥 Congratulations {username}!</h2>
            <p>You've achieved a <strong>{streak_days}-day learning streak</strong>!</p>
            <p>Keep up the amazing work and continue your learning journey.</p>
            <br>
            <p style="background: #fff3cd; padding: 15px; border-left: 4px solid #ffa500;">
                <strong>Tip:</strong> Login daily and complete lessons or quizzes to maintain your streak!
            </p>
            <br>
            <p>Keep learning!</p>
            <p style="color: #666;">- Gamified Learning Team</p>
        </body>
    </html>
    """
    return send_email(to_email, subject, body)

def send_quiz_created_email(to_email, username, quiz_title):
    """Send notification when teacher creates new quiz"""
    subject = f"New Quiz Available: {quiz_title}"
    body = f"""
    <html>
        <body style="font-family: Arial; padding: 20px;">
            <h2 style="color: #667eea;">📝 New Quiz Available!</h2>
            <p>Hello <strong>{username}</strong>,</p>
            <p>A new quiz has been posted: <strong>{quiz_title}</strong></p>
            <p>Login now to attempt the quiz and earn points!</p>
            <br>
            <p><a href="http://localhost:5000/student" style="background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">View Quiz</a></p>
            <br>
            <p>Good luck!</p>
            <p style="color: #666;">- Gamified Learning Team</p>
        </body>
    </html>
    """
    return send_email(to_email, subject, body)

def send_video_posted_email(to_email, username, video_title):
    """Send notification when teacher posts new video"""
    subject = f"New Video Posted: {video_title}"
    body = f"""
    <html>
        <body style="font-family: Arial; padding: 20px;">
            <h2 style="color: #2196F3;">📹 New Video Available!</h2>
            <p>Hello <strong>{username}</strong>,</p>
            <p>A new educational video has been posted: <strong>{video_title}</strong></p>
            <p>Login now to watch and learn!</p>
            <br>
            <p><a href="http://localhost:5000/student" style="background: #2196F3; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Watch Now</a></p>
            <br>
            <p>Happy Learning!</p>
            <p style="color: #666;">- Gamified Learning Team</p>
        </body>
    </html>
    """
    return send_email(to_email, subject, body)

def send_parent_weekly_report(to_email, parent_name, student_name, points, streak, quizzes_attempted):
    """Send weekly progress report to parents"""
    subject = f"Weekly Progress Report - {student_name}"
    body = f"""
    <html>
        <body style="font-family: Arial; padding: 20px;">
            <h2 style="color: #667eea;">📊 Weekly Progress Report</h2>
            <p>Hello <strong>{parent_name}</strong>,</p>
            <p>Here's <strong>{student_name}'s</strong> progress this week:</p>
            <br>
            <table style="border-collapse: collapse; width: 100%;">
                <tr style="background: #f0f0f0;">
                    <td style="padding: 10px; border: 1px solid #ddd;"><strong>Total Points</strong></td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{points}</td>
                </tr>
                <tr>
                    <td style="padding: 10px; border: 1px solid #ddd;"><strong>Current Streak</strong></td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{streak} days 🔥</td>
                </tr>
                <tr style="background: #f0f0f0;">
                    <td style="padding: 10px; border: 1px solid #ddd;"><strong>Quizzes Attempted</strong></td>
                    <td style="padding: 10px; border: 1px solid #ddd;">{quizzes_attempted}</td>
                </tr>
            </table>
            <br>
            <p>Keep encouraging your child to maintain their learning streak!</p>
            <br>
            <p style="color: #666;">- Gamified Learning Team</p>
        </body>
    </html>
    """
    return send_email(to_email, subject, body)

def send_streak_reminder_email(to_email, username, current_streak):
    """Send reminder to maintain streak"""
    subject = "⚠️ Don't Break Your Streak!"
    body = f"""
    <html>
        <body style="font-family: Arial; padding: 20px;">
            <h2 style="color: #ff6b35;">🔥 Streak Reminder</h2>
            <p>Hello <strong>{username}</strong>,</p>
            <p>You haven't logged in today! Your current streak is <strong>{current_streak} days</strong>.</p>
            <p style="background: #fff3cd; padding: 15px; border-left: 4px solid #ffa500;">
                <strong>Don't break your streak!</strong> Login now and complete a lesson or quiz to keep it going.
            </p>
            <br>
            <p><a href="http://localhost:5000/student" style="background: #ff6b35; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Continue Learning</a></p>
            <br>
            <p style="color: #666;">- Gamified Learning Team</p>
        </body>
    </html>
    """
    return send_email(to_email, subject, body)

def send_certificate_email(to_email, username, certificate_id):
    """Send certificate achievement email"""
    subject = "🎓 Congratulations! Your Certificate is Ready"
    body = f"""
    <html>
        <body style="font-family: Arial; padding: 20px;">
            <h2 style="color: #28a745;">🎓 Certificate of Completion</h2>
            <p>Hello <strong>{username}</strong>,</p>
            <p>Congratulations on completing the course!</p>
            <p style="background: #d4edda; padding: 15px; border-left: 4px solid #28a745;">
                <strong>Your certificate is ready!</strong><br>
                Certificate ID: <strong>{certificate_id}</strong>
            </p>
            <p>Login to your dashboard to download your certificate.</p>
            <br>
            <p><a href="http://localhost:5000/student" style="background: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Download Certificate</a></p>
            <br>
            <p>We're proud of your achievement!</p>
            <p style="color: #666;">- Gamified Learning Team</p>
        </body>
    </html>
    """
    return send_email(to_email, subject, body)
