import ollama
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from queue import Queue

conversation_queue = Queue()

def summarize_and_return(text):
    start = time.time()
    summary = summarize_medical_conversation(text)
    duration = time.time() - start
    print("=== SUMMARY ===", duration)
    return summary
    
def summarize_medical_conversation(conversation):
    client = ollama.Client()
    model = "llama3.2:3b"
    
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

def process_conversation(conversation):
    try:
        if not conversation.processed_dialogue:
            if not conversation.dialogue:
                raise ValueError("The conversation dialogue is empty or None.")
            
            print(f"[Queue] Processing conversation for appointment {conversation.appointment.id}")
            conversation.processed_dialogue = summarize_medical_conversation(conversation.dialogue)
            conversation.save(update_fields=['processed_dialogue'])
            print("[Queue] Processing complete")
    except ValueError as ve:
        print(f"Validation error: {ve}")
        conversation.processed_dialogue = "Error: Dialogue is missing or invalid."
        conversation.save(update_fields=['processed_dialogue'])
    except Exception as e:
        print(f"Error processing conversation: {e}")
        conversation.processed_dialogue = "Error: An unexpected error occurred during processing."
        conversation.save(update_fields=['processed_dialogue'])

def conversation_worker():
    while True:
        conversation = conversation_queue.get()
        if conversation is None:
            break
        process_conversation(conversation)
        conversation_queue.task_done()

#Nekane: This controls the number of conversations that can be processed simultaneously (It depends on computer performance)
NUM_WORKERS = 2

for i in range(NUM_WORKERS):
    threading.Thread(target=conversation_worker, daemon=True).start()
        
# Example usage
if __name__ == "__main__":
    start_time = time.time()
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
    doctor: Remember to take 1 pill of paracetamol each 8 hours.
    patient: Will it affect my diabetes?
    doctor: No
    """
    
    """summary = summarize_medical_conversation(doctor_patient_conversation)
    print("=== MEDICAL CONVERSATION SUMMARY ===\n")
    print(summary)"""
    with ThreadPoolExecutor() as executor:
        results = executor.map(summarize_and_return, [doctor_patient_conversation, doctor_patient_conversation])

    for i, summary in enumerate(results):
        print(f"=== SUMMARY {i+1} ===")
        print(summary)

    total_time = time.time() - start_time
    print(f"Total time: {total_time:.2f} seconds")