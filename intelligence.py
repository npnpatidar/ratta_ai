import openai
import ollama
from ollama import Client

class Brain:
    def __init__(self, system_instruction=None):
        self.default_host = "ollama"
        self.default_model = None
        self.available_models = None
        self.client = None

        self.set_host(self.default_host)

        self.previous_system_instruction = system_instruction or "You are a helpful assistant."
        self.messages = [{"role": "system", "content": self.previous_system_instruction}]

    def set_host(self, host=None, model=None):
        if host:
            self.default_host = host
        if model:
            self.default_model = model

        if self.default_host == "ollama":
            self.client = openai.OpenAI(api_key="API-KEY", base_url="http://localhost:11434/v1")
        elif self.default_host == "server":
            self.client = openai.OpenAI(api_key="API-KEY", base_url="https://ollama.naresh.world/v1")
        elif self.default_host == "groq":
            self.client = openai.OpenAI(api_key="", base_url="https://api.groq.com/openai/v1")
        elif self.default_host == "openrouter":
            self.client = openai.OpenAI(api_key="", base_url="https://openrouter.ai/api/v1")

        if self.default_host == "ollama":
            models_found = ollama.list()
            self.available_models = [model["name"] for model in models_found["models"]]
        elif self.default_host == "server":
            test_client = ollama.Client(host='https://ollama.naresh.world')
            models_found = test_client.list()
            self.available_models = [model["name"] for model in models_found["models"]]
        else:
            models_found = self.client.models.list()
            self.available_models = [model.id for model in models_found.data]

        if self.default_model not in self.available_models or self.default_model is None:
            print(f"{self.default_model} not found in {self.default_host}")
            print("Available models:")
            print(self.available_models)
            if self.available_models:
                self.default_model = self.available_models[0]
                print(f"I have set default model to {self.default_model}")

    def ask_question(self, question=None,system_instruction=None, host=None, model=None , json_format= False):
        if host or model:
            self.set_host(host, model)

        if system_instruction != self.previous_system_instruction:
            self.messages = [{"role": "system", "content": system_instruction or self.previous_system_instruction}]
        else:
            if system_instruction is None:
                system_instruction = self.previous_system_instruction

        if question:
            self.messages.append({"role": "user", "content": question})

        if len(self.messages) > 4:
            self.messages.pop(1)
            self.messages.pop(1)

        print("asking question to ")
        print(f"host - {self.default_host} model - {self.default_model}")
        # print(self.messages)
        # print("___________________________________________________________________________________________________________")

# pass response format only if json_format is true
        if json_format:
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=self.messages,
                response_format={"type": "json_object"}
            )
        else:
            response = self.client.chat.completions.create(
                model=self.default_model,
                messages=self.messages
            )

        assistant_response_content = response.choices[0].message.content
        # print("total tokens - " + str(response.usage.total_tokens))

        self.messages.append(
            {"role": "assistant", "content": assistant_response_content})

        self.previous_system_instruction = system_instruction

        return assistant_response_content

if __name__ == "__main__":
    chat_app = Brain("You are a very good assistant.")
    user_input = input("User: ")
    while user_input.lower() != "exit":
        assistant_response = chat_app.ask_question(question=user_input, host="openrouter" , model="mistralai/mistral-7b-instruct:free")
        print(f"Assistant: {assistant_response}")
        user_input = input("User: ")
