from autoagent.types import Agent
from autoagent.registry import register_plugin_agent
from autoagent.types import Result  

@register_plugin_agent(name = "Agentic_RAG_Orchestrator", func_name="get_agentic_rag_orchestrator")
def get_agentic_rag_orchestrator(model: str):
    '''
    The Agentic_RAG_Orchestrator manages the workflow of Initialization Agent, Query Processor Agent, Retrieval Agent, Generation Agent, and Aggregation Agent to perform advanced RAG tasks.
    '''
    
    from autoagent.agents import get_initialization_agent

    from autoagent.agents import get_query_processor_agent

    from autoagent.agents import get_retrieval_agent

    from autoagent.agents import get_generation_agent

    from autoagent.agents import get_aggregation_agent

    instructions = "Your task is to orchestrate the workflow of the given sub-agents to produce a final, cohesive response addressing the user's query. Ensure multi-agent collaboration, dynamic tool orchestration, and context-aware retrieval."
    
    agentic_rag_orchestrator = Agent(
    name="Agentic_RAG_Orchestrator",
    model=model,
    instructions=instructions,
    )


    
    initialization_agent: Agent = get_initialization_agent(model)
    initialization_agent.tool_choice = "required"
    # 更新初始化代理的instructions
    initialization_agent.instructions += " After completing your task, use the transfer_back_to_agentic_rag_orchestrator tool to return your results to the orchestrator."

    

    query_processor_agent: Agent = get_query_processor_agent(model)
    query_processor_agent.tool_choice = "required"
    # 更新查询处理代理的instructions
    query_processor_agent.instructions += " After processing the query, use the transfer_back_to_agentic_rag_orchestrator tool to return your processed query to the orchestrator."


    retrieval_agent: Agent = get_retrieval_agent(model)
    retrieval_agent.tool_choice = "required"
    # 更新检索代理的instructions
    retrieval_agent.instructions += " After retrieving relevant documents, use the transfer_back_to_agentic_rag_orchestrator tool to return the retrieved documents to the orchestrator."


    generation_agent: Agent = get_generation_agent(model)
    generation_agent.tool_choice = "required"
    # 更新生成代理的instructions
    generation_agent.instructions += " After generating your response, use the transfer_back_to_agentic_rag_orchestrator tool to return your generated response to the orchestrator."


    aggregation_agent: Agent = get_aggregation_agent(model)
    aggregation_agent.tool_choice = "required"
    # 更新聚合代理的instructions
    aggregation_agent.instructions += " After aggregating all responses into a final answer, use the transfer_back_to_agentic_rag_orchestrator tool to return your final response to the orchestrator."

    print(initialization_agent.instructions)
    print(query_processor_agent.instructions)
    print(retrieval_agent.instructions)
    print(generation_agent.instructions)
    print(aggregation_agent.instructions)


    
    def transfer_to_initialization_agent(init_request: str):
        '''
        Use this tool to transfer the request to the `initialization_agent` agent.

        Args:
            init_request: the request to be transferred to the `initialization_agent` agent. It should be a string.
        '''
        return Result(value = init_request, agent = initialization_agent)

    def transfer_to_query_processor_agent(user_query: str):
        '''
        Use this tool to transfer the request to the `query_processor_agent` agent.

        Args:
            user_query: the request to be transferred to the `query_processor_agent` agent. It should be a string.
        '''
        return Result(value = user_query, agent = query_processor_agent)

    def transfer_to_retrieval_agent(processed_query: str):
        '''
        Use this tool to transfer the request to the `retrieval_agent` agent.

        Args:
            processed_query: the request to be transferred to the `retrieval_agent` agent. It should be a string.
        '''
        return Result(value = processed_query, agent = retrieval_agent)

    def transfer_to_generation_agent(retrieved_docs: str):
        '''
        Use this tool to transfer the request to the `generation_agent` agent.

        Args:
            retrieved_docs: the request to be transferred to the `generation_agent` agent. It should be a string.
        '''
        return Result(value = retrieved_docs, agent = generation_agent)

    def transfer_to_aggregation_agent(responses: str):
        '''
        Use this tool to transfer the request to the `aggregation_agent` agent.

        Args:
            responses: the request to be transferred to the `aggregation_agent` agent. It should be a string.
        '''
        return Result(value = responses, agent = aggregation_agent)

    
    def transfer_back_to_agentic_rag_orchestrator(init_confirmation: str):
        '''
        Use this tool to transfer the response back to the `Agentic_RAG_Orchestrator` agent. You can only use this tool when you have tried your best to do the task the orchestrator agent assigned to you.

        Args:
            init_confirmation: the response to be transferred back to the `Agentic_RAG_Orchestrator` agent. It should be a string.
        '''
        return Result(value = init_confirmation, agent = agentic_rag_orchestrator) 
    initialization_agent.functions.append(transfer_back_to_agentic_rag_orchestrator)

    def transfer_back_to_agentic_rag_orchestrator(processed_query: str):
        '''
        Use this tool to transfer the response back to the `Agentic_RAG_Orchestrator` agent. You can only use this tool when you have tried your best to do the task the orchestrator agent assigned to you.

        Args:
            processed_query: the response to be transferred back to the `Agentic_RAG_Orchestrator` agent. It should be a string.
        '''
        return Result(value = processed_query, agent = agentic_rag_orchestrator) 
    query_processor_agent.functions.append(transfer_back_to_agentic_rag_orchestrator)

    def transfer_back_to_agentic_rag_orchestrator(retrieved_docs: str):
        '''
        Use this tool to transfer the response back to the `Agentic_RAG_Orchestrator` agent. You can only use this tool when you have tried your best to do the task the orchestrator agent assigned to you.

        Args:
            retrieved_docs: the response to be transferred back to the `Agentic_RAG_Orchestrator` agent. It should be a string.
        '''
        return Result(value = retrieved_docs, agent = agentic_rag_orchestrator) 
    retrieval_agent.functions.append(transfer_back_to_agentic_rag_orchestrator)

    def transfer_back_to_agentic_rag_orchestrator(generated_response: str):
        '''
        Use this tool to transfer the response back to the `Agentic_RAG_Orchestrator` agent. You can only use this tool when you have tried your best to do the task the orchestrator agent assigned to you.

        Args:
            generated_response: the response to be transferred back to the `Agentic_RAG_Orchestrator` agent. It should be a string.
        '''
        return Result(value = generated_response, agent = agentic_rag_orchestrator) 
    generation_agent.functions.append(transfer_back_to_agentic_rag_orchestrator)

    def transfer_back_to_agentic_rag_orchestrator(final_response: str):
        '''
        Use this tool to transfer the response back to the `Agentic_RAG_Orchestrator` agent. You can only use this tool when you have tried your best to do the task the orchestrator agent assigned to you.

        Args:
            final_response: the response to be transferred back to the `Agentic_RAG_Orchestrator` agent. It should be a string.
        '''
        return Result(value = final_response, agent = agentic_rag_orchestrator) 
    aggregation_agent.functions.append(transfer_back_to_agentic_rag_orchestrator)


    agentic_rag_orchestrator.functions = [transfer_to_initialization_agent, transfer_to_query_processor_agent, transfer_to_retrieval_agent, transfer_to_generation_agent, transfer_to_aggregation_agent]
    return agentic_rag_orchestrator
