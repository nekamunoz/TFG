import ollama


def summarize_medical_conversation(conversation):
    client = ollama.Client()
    model = "llama2"
    
    prompt = f"""
    Below is a conversation between a doctor and a patient. 
    Please create a **concise and factual medical report** that only separates and lists the following:

    - Patient's description
    - Reason for visit
    - Symptoms
    - Past medical history
    - Current medications
    
    **Do not include any additional explanations, solutions, mathematical analysis, or diagnostic hypotheses beyond the conversation details.**
    
    The response should only contain the **medical summary**, with no added information or reasoning.

    Here's the conversation:
    {conversation}
    """
    
    response = client.generate(model=model, prompt=prompt)
    return response.response


# Example usage
if __name__ == "__main__":
    # Sample conversation - replace with actual doctor-patient conversation
    doctor_patient_conversation = """
    Doctor: Good morning, what brings you in today?
    Patient: I've been having severe headaches for the past week, and they're getting worse.
    Doctor: I'm sorry to hear that. Can you describe the pain?
    Patient: It's throbbing, mainly on the right side. Light makes it worse.
    Doctor: Any nausea or visual changes?
    Patient: Yes, I feel nauseated when it's bad, and sometimes I see flashing lights before it starts.
    Doctor: Have you had migraines before?
    Patient: No, this is new for me.
    Doctor: Let's check your vitals and do a neurological exam...
    """
    
    summary = summarize_medical_conversation(doctor_patient_conversation)
    print("=== MEDICAL CONVERSATION SUMMARY ===\n")
    print(summary)