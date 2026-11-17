"""
Initial Sample Data Seeder
Populates initial sample companies and approved interview experiences for realistic exploration.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from database import init_db
from models.user import User
from dao.user_dao import UserDAO
from dao.company_dao import CompanyDAO
from dao.experience_dao import ExperienceDAO

def seed_sample_data():
    init_db()
    
    # 1. Ensure test student user exists
    test_student = UserDAO.get_by_email("student@example.com")
    if not test_student:
        uid = UserDAO.create_user("John Doe", "student@example.com", User.hash_password("Student123!"), role='student')
    else:
        uid = test_student.id

    # 2. Seed initial companies
    companies_data = [
        ("Google", "Multinational technology company focusing on search engine technology, cloud computing, and AI.", "https://careers.google.com"),
        ("Microsoft", "Global software developer known for Windows, Azure, Office, and Surface devices.", "https://careers.microsoft.com"),
        ("Amazon", "E-commerce and cloud computing giant with AWS powering modern infrastructure.", "https://amazon.jobs"),
        ("TCS", "Tata Consultancy Services - Indian multinational IT services and consulting company.", "https://tcs.com/careers"),
        ("Infosys", "Global leader in next-generation digital services and consulting.", "https://infosys.com/careers")
    ]

    company_ids = {}
    for name, desc, web in companies_data:
        cid = CompanyDAO.get_or_create(name, desc, web)
        company_ids[name] = cid

    # 3. Seed sample experiences if none exist
    if ExperienceDAO.count_approved() == 0:
        experiences = [
            {
                "user_id": uid,
                "company_id": company_ids["Google"],
                "job_role": "Software Development Engineer (SDE 1)",
                "interview_date": "2026-02-15",
                "interview_type": "Online",
                "difficulty": "Hard",
                "experience_level": "Fresher",
                "interview_rounds": 4,
                "technical_questions": "1. Invert a binary tree and find lowest common ancestor in O(N) time.\n2. Design a rate limiter using Token Bucket algorithm in Python.\n3. Dynamic Programming problem on Longest Increasing Subsequence with binary search optimization O(N log N).",
                "hr_questions": "1. Why do you want to join Google over startups?\n2. Tell me about a time you handled disagreement in an engineering team project.\n3. How do you approach continuous learning with new tech?",
                "overall_experience": "The interview process was thorough and focused heavily on algorithmic efficiency, clean code practices, and solid communication. The interviewers gave helpful hints when I got stuck on the DP edge case.",
                "preparation_tips": "Focus on LeetCode Medium/Hard graphs and trees. Practice writing clean code while speaking aloud your thought process. Study system design basics even for entry roles.",
                "result": "Selected",
                "approval_status": "approved"
            },
            {
                "user_id": uid,
                "company_id": company_ids["Amazon"],
                "job_role": "Backend Developer",
                "interview_date": "2026-03-01",
                "interview_type": "Online",
                "difficulty": "Medium",
                "experience_level": "Entry Level",
                "interview_rounds": 3,
                "technical_questions": "1. Implement an LRU Cache with O(1) get and put operations using Doubly Linked List and Hash Map.\n2. SQL query to find employees with second highest salary in each department.\n3. Explain ACID properties, database isolation levels, and concurrency conflicts.",
                "hr_questions": "1. Tell me about a time you failed to meet a deadline and how you handled it (Amazon Leadership Principle: Deliver Results).\n2. Give an example of Customer Obsession in your past project.",
                "overall_experience": "Very focused on Amazon Leadership Principles (LP). Half of every round was behavioral with STAR methodology. Technical rounds were standard data structures and database systems.",
                "preparation_tips": "Prepare 2-3 detailed stories for each Amazon Leadership Principle. Practice SQL subqueries, indexing, and object-oriented design patterns.",
                "result": "Selected",
                "approval_status": "approved"
            },
            {
                "user_id": uid,
                "company_id": company_ids["Microsoft"],
                "job_role": "Full Stack Engineer",
                "interview_date": "2026-01-20",
                "interview_type": "Offline",
                "difficulty": "Medium",
                "experience_level": "Mid Level",
                "interview_rounds": 4,
                "technical_questions": "1. Build an autocomplete Trie with prefix frequency search.\n2. Explain REST vs GraphQL and when to choose each.\n3. Concurrency in Python and async/await event loops.",
                "hr_questions": "1. Where do you see yourself in 3 years?\n2. What is your favorite technology stack and why?",
                "overall_experience": "Great interview experience on campus. Friendly interviewers who focused on architectural design and code modularity.",
                "preparation_tips": "Brush up on web architecture, data structures (Tries, Heaps), and modern asynchronous patterns.",
                "result": "Selected",
                "approval_status": "approved"
            }
        ]

        for exp in experiences:
            ExperienceDAO.create(**exp)
        print(f"[INFO] Seeded {len(experiences)} sample interview experiences.")
    else:
        print("[INFO] Sample experiences already present.")

if __name__ == "__main__":
    seed_sample_data()
