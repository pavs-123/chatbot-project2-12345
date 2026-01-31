"""
LangChain Chains - Connecting Chains in AI

This module demonstrates different ways to connect chains in LangChain:
1. LLMChain - Basic chain with LLM and prompt
2. SequentialChain - Chain multiple chains together
3. Chain composition with Runnable interface
"""

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnableSequence, RunnablePassthrough


def basic_llm_chain():
    """Example 1: Basic LLMChain"""
    llm = ChatOpenAI(model="gpt-3.5-turbo")
    
    prompt = PromptTemplate(
        template="Tell me a joke about {topic}",
        input_variables=["topic"]
    )
    
    chain = prompt | llm | StrOutputParser()
    
    result = chain.invoke({"topic": "programmers"})
    print("Basic LLMChain Result:")
    print(result)
    return chain


def sequential_chain():
    """Example 2: Sequential Chain - Multiple steps"""
    llm = ChatOpenAI(model="gpt-3.5-turbo")
    
    # Chain 1: Generate topic
    first_prompt = PromptTemplate(
        template="Generate a short topic for a story about {genre}",
        input_variables=["genre"]
    )
    first_chain = first_prompt | llm | StrOutputParser()
    
    # Chain 2: Write story based on topic
    second_prompt = PromptTemplate(
        template="Write a 2-sentence story about: {topic}",
        input_variables=["topic"]
    )
    second_chain = second_prompt | llm | StrOutputParser()
    
    # Combine chains
    sequential_chain = first_chain | second_chain
    
    result = sequential_chain.invoke({"genre": "adventure"})
    print("\nSequential Chain Result:")
    print(result)
    return sequential_chain


def parallel_chain():
    """Example 3: Parallel Chain Processing"""
    llm = ChatOpenAI(model="gpt-3.5-turbo")
    
    # Create multiple chains for parallel execution
    summarize_prompt = PromptTemplate(
        template="Summarize this text in one sentence: {text}",
        input_variables=["text"]
    )
    translate_prompt = PromptTemplate(
        template="Translate this text to Spanish: {text}",
        input_variables=["text"]
    )
    
    summarize_chain = summarize_prompt | llm | StrOutputParser()
    translate_chain = translate_prompt | llm | StrOutputParser()
    
    # Combine with RunnableParallel for parallel execution
    from langchain.schema.runnable import RunnableParallel
    
    parallel = RunnableParallel(
        summary=summarize_chain,
        translation=translate_chain
    )
    
    text = "Artificial intelligence is transforming how we work and live."
    result = parallel.invoke({"text": text})
    
    print("\nParallel Chain Result:")
    print(f"Summary: {result['summary']}")
    print(f"Spanish: {result['translation']}")
    return parallel


def chain_with_memory():
    """Example 4: Chain with Conversation Memory"""
    from langchain.memory import ConversationBufferMemory
    from langchain.chains import ConversationChain
    
    llm = ChatOpenAI(model="gpt-3.5-turbo")
    memory = ConversationBufferMemory()
    
    conversation = ConversationChain(
        llm=llm,
        memory=memory,
        verbose=True
    )
    
    result = conversation.predict(input="Hi, my name is Alice")
    print("\nConversation Chain Result:")
    print(result)
    
    result = conversation.predict(input="What's my name?")
    print(result)
    
    return conversation


def main():
    """Run all chain examples"""
    print("=" * 50)
    print("LangChain Chains Examples")
    print("=" * 50)
    
    try:
        basic_llm_chain()
    except Exception as e:
        print(f"Basic chain error: {e}")
    
    try:
        sequential_chain()
    except Exception as e:
        print(f"Sequential chain error: {e}")
    
    try:
        parallel_chain()
    except Exception as e:
        print(f"Parallel chain error: {e}")
    
    try:
        chain_with_memory()
    except Exception as e:
        print(f"Memory chain error: {e}")


if __name__ == "__main__":
    main()
