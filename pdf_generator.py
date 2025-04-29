from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import io

def create_student_report_pdf(student_data, feedback):
    # Create a buffer to store the PDF
    buffer = io.BytesIO()
    
    # Create the PDF object using the buffer
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    heading_style = styles['Heading2']
    normal_style = styles['Normal']
    
    # Add title
    elements.append(Paragraph("Student Academic Report", title_style))
    elements.append(Spacer(1, 20))
    
    # Add student information
    elements.append(Paragraph("Student Information", heading_style))
    student_info = [
        ["Name:", student_data['name']],
        ["Year:", str(student_data['year'])],
        ["Department:", student_data['department']]
    ]
    student_table = Table(student_info, colWidths=[2*inch, 4*inch])
    student_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(student_table)
    elements.append(Spacer(1, 20))
    
    # Add marks section
    if student_data['marks']:
        elements.append(Paragraph("Academic Performance", heading_style))
        marks_data = [["Subject", "Score"]] + [
            [mark['subject'], str(mark['score'])]
            for mark in student_data['marks']
        ]
        marks_table = Table(marks_data, colWidths=[4*inch, 2*inch])
        marks_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(marks_table)
        elements.append(Spacer(1, 20))
    
    # Add assignments section
    if student_data['assignments']:
        elements.append(Paragraph("Assignments", heading_style))
        assignments_data = [["Title", "Grade"]] + [
            [assignment['title'], assignment['grade']]
            for assignment in student_data['assignments']
        ]
        assignments_table = Table(assignments_data, colWidths=[4*inch, 2*inch])
        assignments_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(assignments_table)
        elements.append(Spacer(1, 20))
    
    # Add attendance section
    if student_data['attendance']:
        elements.append(Paragraph("Attendance", heading_style))
        attendance_data = [["Subject", "Percentage"]] + [
            [attendance['subject'], f"{attendance['percentage']}%"]
            for attendance in student_data['attendance']
        ]
        attendance_table = Table(attendance_data, colWidths=[4*inch, 2*inch])
        attendance_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('PADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(attendance_table)
        elements.append(Spacer(1, 20))
    
    # Add AI feedback section
    elements.append(Paragraph("AI Generated Feedback", heading_style))
    elements.append(Paragraph(feedback, normal_style))
    
    # Build PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer
    pdf = buffer.getvalue()
    buffer.close()
    
    return pdf 