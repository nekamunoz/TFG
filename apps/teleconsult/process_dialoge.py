import ollama

def summarize_medical_conversation(conversation):
    client = ollama.Client()
    model = "llama2"
    
    prompt = f"""
    Below is a conversation between a doctor and a patient. 
    Please create a **concise and factual medical report** that only separates and lists the following:
    Medical Session Notes
    - Patient's description:
    - Reason for visit:
    - Symptoms:
    - Past medical history:
    - Current medications:

    Data must follow the previous structure and be concise.
    The response should only contain the **medical summary**, with no added information or reasoning.

    Here's the conversation:
    {conversation}
    """
    print(f"Executing model {model}")
    response = client.generate(model=model, prompt=prompt)
    print(f"Model {model} executed successfully")
    return response.response


# Example usage
if __name__ == "__main__":
    doctor_patient_conversation = """
    doctor: Good morning, what brings you in today?
    patient: I've been having severe headaches for the past week, and they're getting worse.
    doctor: I'm sorry to hear that. Can you describe the pain?
    patient: It's throbbing, mainly on the right side. Light makes it worse.
    doctor: Any nausea or visual changes?
    patient: Yes, I feel nauseated when it's bad, and sometimes I see flashing lights before it starts.
    doctor: Have you had migraines before?
    patient: No, this is new for me.
    doctor: Let's check your vitals and do a neurological exam...
    """
    
    summary = summarize_medical_conversation(doctor_patient_conversation)
    print("=== MEDICAL CONVERSATION SUMMARY ===\n")
    print(summary)