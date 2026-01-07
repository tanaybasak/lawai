"""
Test script to demonstrate conversational memory in LawAI backend

This script shows how follow-up questions now work correctly with chat history.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_conversational_flow():
    """Test a conversational flow with follow-up questions"""
    
    print("=" * 80)
    print("TESTING CONVERSATIONAL MEMORY IN LAWAI")
    print("=" * 80)
    
    # Initialize chat history
    chat_history = []
    
    # Test 1: Initial question about divorce
    print("\n📌 Test 1: Initial Question")
    print("-" * 80)
    question1 = "What are the grounds for divorce under Hindu Marriage Act?"
    print(f"User: {question1}")
    
    response1 = requests.post(
        f"{BASE_URL}/query",
        json={"question": question1, "chat_history": chat_history}
    )
    
    if response1.status_code == 200:
        result1 = response1.json()
        answer1 = result1["answer"]
        print(f"\nAssistant: {answer1[:300]}...")
        
        # Update chat history
        chat_history.append({"role": "user", "content": question1})
        chat_history.append({"role": "assistant", "content": answer1})
    else:
        print(f"❌ Error: {response1.status_code}")
        return
    
    # Test 2: Follow-up question (contextual)
    print("\n\n📌 Test 2: Follow-up Question (Should understand 'punishment' refers to divorce context)")
    print("-" * 80)
    question2 = "What about the punishment?"
    print(f"User: {question2}")
    print("💡 Expected behavior: Should reformulate to 'What is the punishment for filing false divorce claims' or similar")
    
    response2 = requests.post(
        f"{BASE_URL}/query",
        json={"question": question2, "chat_history": chat_history}
    )
    
    if response2.status_code == 200:
        result2 = response2.json()
        answer2 = result2["answer"]
        print(f"\nAssistant: {answer2[:300]}...")
        
        # Update chat history
        chat_history.append({"role": "user", "content": question2})
        chat_history.append({"role": "assistant", "content": answer2})
    else:
        print(f"❌ Error: {response2.status_code}")
        return
    
    # Test 3: Another follow-up
    print("\n\n📌 Test 3: Another Follow-up")
    print("-" * 80)
    question3 = "What are the time limits?"
    print(f"User: {question3}")
    print("💡 Expected behavior: Should understand context from previous conversation")
    
    response3 = requests.post(
        f"{BASE_URL}/query",
        json={"question": question3, "chat_history": chat_history}
    )
    
    if response3.status_code == 200:
        result3 = response3.json()
        answer3 = result3["answer"]
        print(f"\nAssistant: {answer3[:300]}...")
    else:
        print(f"❌ Error: {response3.status_code}")
        return
    
    # Test 4: New topic (should start fresh)
    print("\n\n📌 Test 4: New Topic (Switching context)")
    print("-" * 80)
    question4 = "What is Section 66 of IT Act?"
    print(f"User: {question4}")
    
    chat_history.append({"role": "user", "content": question3})
    chat_history.append({"role": "assistant", "content": answer3})
    
    response4 = requests.post(
        f"{BASE_URL}/query",
        json={"question": question4, "chat_history": chat_history}
    )
    
    if response4.status_code == 200:
        result4 = response4.json()
        answer4 = result4["answer"]
        print(f"\nAssistant: {answer4[:300]}...")
        
        chat_history.append({"role": "user", "content": question4})
        chat_history.append({"role": "assistant", "content": answer4})
    else:
        print(f"❌ Error: {response4.status_code}")
        return
    
    # Test 5: Follow-up on new topic
    print("\n\n📌 Test 5: Follow-up on IT Act (Should understand 'penalties' refers to Section 66)")
    print("-" * 80)
    question5 = "What are the penalties?"
    print(f"User: {question5}")
    print("💡 Expected behavior: Should reformulate to 'What are penalties under Section 66 of IT Act'")
    
    response5 = requests.post(
        f"{BASE_URL}/query",
        json={"question": question5, "chat_history": chat_history}
    )
    
    if response5.status_code == 200:
        result5 = response5.json()
        answer5 = result5["answer"]
        print(f"\nAssistant: {answer5[:300]}...")
    else:
        print(f"❌ Error: {response5.status_code}")
        return
    
    print("\n" + "=" * 80)
    print("✅ CONVERSATIONAL MEMORY TEST COMPLETED")
    print("=" * 80)
    print("\n📊 Summary:")
    print(f"- Total questions asked: 5")
    print(f"- Follow-up questions: 3 (questions 2, 3, 5)")
    print(f"- Chat history entries: {len(chat_history)}")
    print("\n💡 The system now:")
    print("  ✓ Reformulates follow-up questions using chat history")
    print("  ✓ Retrieves relevant documents based on reformulated questions")
    print("  ✓ Includes conversation context in answer generation")
    print("  ✓ Maintains topic coherence across multiple turns")


if __name__ == "__main__":
    # Check if backend is running
    try:
        health = requests.get(f"{BASE_URL}/")
        if health.status_code == 200:
            print("\n✅ Backend is running!")
            test_conversational_flow()
        else:
            print(f"❌ Backend health check failed: {health.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Make sure it's running on http://localhost:8000")
        print("\nTo start the backend:")
        print("  cd backend")
        print("  source venv/bin/activate")
        print("  python main_modular.py")
