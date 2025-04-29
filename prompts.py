STUDENT_FEEDBACK_PROMPT = """Please provide a comprehensive feedback for the following student:

Student Information:
Name: {name}
Year: {year}
Department: {department}

Academic Performance:
Marks:
{marks}

Assignments:
{assignments}

Attendance:
{attendance}

Please analyze the student's performance and provide:
1. Overall academic performance assessment
2. Strengths and areas for improvement
3. Specific recommendations for better performance
4. Attendance analysis and its impact on academics

Keep the response concise and within 500 tokens.""" 