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

LEARNING_RESOURCES_PROMPT = """Based on the student's performance and feedback, generate personalized learning resources and industry statistics.

Student Information:
Name: {name}
Year: {year}
Department: {department}

Feedback Analysis:
{feedback}

Please provide a JSON response with exactly this structure:
{{
    "personalized_message": "A personalized message addressing the student's weak areas and career prospects",
    "articles": [
        {{
            "title": "Article Title",
            "source": "Website/Publication Name",
            "description": "Brief description of the article",
            "url": "https://example.com/article"
        }},
        // Add 2-4 more articles
    ],
    "statistics": [
        {{
            "metric": "Metric Name",
            "value": "Specific Value",
            "description": "Brief explanation of the metric"
        }},
        // Add 4-5 more statistics
    ],
    "career_advice": {{
        "weak_areas": ["List of 2-3 specific weak areas identified"],
        "improvement_suggestions": ["List of 2-3 specific suggestions for improvement"],
        "job_market_insights": "Brief analysis of job market prospects",
        "salary_expectations": "Information about salary expectations and growth"
    }}
}}

Requirements:
1. Personalized Message:
   - Address the student by name
   - Highlight their specific weak areas
   - Provide encouragement and motivation
   - Include specific improvement suggestions
   - Mention career prospects in their field

2. Articles (3-5 total):
   - Focus on topics that address the student's weak areas
   - Include beginner-friendly resources if the student is in early years
   - Include advanced topics if the student is in later years
   - Ensure URLs are valid and accessible

3. Statistics (4-5 total):
   - Focus on the student's specific department/field
   - Include current market trends
   - Include in-demand skills
   - Include salary information
   - Include growth projections
   - Include key challenges and opportunities

4. Career Advice:
   - List specific weak areas identified from their performance
   - Provide concrete suggestions for improvement
   - Include relevant job market insights
   - Mention salary expectations and growth potential

Make sure the response is valid JSON and can be parsed by json.loads().""" 