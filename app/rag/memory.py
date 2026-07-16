class ConversationMemory:

    def __init__(self, max_history=5):

        self.max_history = max_history

        self.memory = {}

    def add(self, session_id, question, answer):

        if session_id not in self.memory:
            self.memory[session_id] = []

        self.memory[session_id].append({

            "question": question,

            "answer": answer

        })

        self.memory[session_id] = self.memory[session_id][-self.max_history:]

    def get(self, session_id):

        return self.memory.get(session_id, [])

    def clear(self, session_id):

        if session_id in self.memory:
            del self.memory[session_id]