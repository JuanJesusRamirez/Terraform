
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from app.agents.agent_a import graph as graph_a
from app.agents.agent_b import graph as graph_b

class AgentHandler:
    def __init__(self):
        self.graph = None

    def execute_agent(self, agent_name, user_input, prev_messages, config) -> str:
        # Seleccionar el grafo del agente basado en el nombre del agente
        
        if agent_name == 'agent_a':
            self.graph = graph_a
        elif agent_name == 'agent_b':
            self.graph = graph_b
        else:
            raise ValueError("Nombre de agente no válido")

        # Invocar el grafo del agente con los parámetros
        
        messages = []
        for i, msg in enumerate(prev_messages):
            if i % 2 == 0:
                messages.append(HumanMessage(content=msg))
            else:
                messages.append(AIMessage(content=msg))
                
        messages.append(HumanMessage(content=user_input)) 
        

        # Ejecutar el grafo y obtener el resultado
        result = self.graph.invoke({"messages": messages}, config)
        response = result['messages'][-1].content
        print(response)
        token_usage_dict = result['messages'][-1].usage_metadata
        input_tokens = token_usage_dict['input_tokens']
        output_tokens = token_usage_dict['output_tokens']
   
        return {
            "response": response,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens
        }
