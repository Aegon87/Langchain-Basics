import streamlit as st
from langchain_groq import ChatGroq
from langchain_community.tools import WikipediaQueryRun, DuckDuckGoSearchRun
from langchain_community.utilities import WikipediaAPIWrapper
import arxiv
import wikipedia
from langchain_core.tools import tool
from langchain_classic.agents import initialize_agent, AgentType
from langchain_classic.callbacks import StreamlitCallbackHandler
import os 
from dotenv import load_dotenv
load_dotenv()

#----------Wikipedia tools---------
@tool
def wiki_tool(query: str) -> str:
    """A wrapper around Wikipedia. Useful for when you need to answer general questions 
    about people, places, companies, facts, historical events, or other subjects. 
    Input should be a simple search query string.
    """
    try:
        # Enforce your custom limit (equivalent to doc_content_chars_max)
        # We fetch the summary directly, which is clean and concise
        summary = wikipedia.summary(query, sentences=3, auto_suggest=False)
        return summary
        
    except wikipedia.exceptions.DisambiguationError as e:
        # If the query matches multiple pages, pass the options back to the agent
        return f"The term '{query}' is ambiguous. Did you mean one of these: {', '.join(e.options[:3])}?"
    except wikipedia.exceptions.PageError:
        return f"No Wikipedia page found matching the query: '{query}'."
    except Exception as e:
        return f"Error executing Wikipedia lookup: {str(e)}"

#----------Arxiv tool----------
@tool
def arxiv_tool(query: str) -> str:
    """A wrapper around Arxiv.org. Useful for when you need to answer questions 
    about Physics, Mathematics, Computer Science, Quantitative Biology, Quantitative Finance, 
    Statistics, Electrical Engineering, and Economics from scientific articles on arxiv.org.
    Input should be an arXiv paper ID or a search query string.
    """
    try:
        # Force the modern client wrapper to handle secure transactions safely
        client = arxiv.Client()
        
        # Enforce your custom limit: top_k_results=1
        search = arxiv.Search(query=query, max_results=1)
        results = list(client.results(search))
        
        if not results:
            return f"No papers found matching the query: {query}"
            
        paper = results[0]
        full_payload = (
            f"Title: {paper.title}\n"
            f"Published: {paper.published.date()}\n"
            f"Abstract: {paper.summary}\n"
            f"Link: {paper.pdf_url}"
        )
        
        # Enforce your custom character limit: doc_content_chars_max=250
        return full_payload[:250]
        
    except Exception as e:
        return f"Error executing ArXiv lookup safely: {str(e)}"

#----------Web search tool-----------
search_tool = DuckDuckGoSearchRun(name="Search")

#----------Streamlit APP----------
st.title("🔎 LangChain - Chat with search")
## Sidebar for settings
st.sidebar.title("Settings")
api_key=st.sidebar.text_input("Enter your Groq API Key:",type="password")

#----------Initializing Chat History Memory----------
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role":"assistent", "content":"Hi, I am a chatbot who can search the web. How can I help you?"}
    ]

for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

#-----------Handling User Text Inputs----------
if prompt:=st.chat_input(placeholder="What is Machine Learning"):
    st.session_state.messages.append({"role":"user", "content":prompt})
    st.chat_message("user").write(prompt)

    llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=api_key, streaming=True)
    tools = [wiki_tool, arxiv_tool, search_tool]

    search_agent = initialize_agent(tools,llm,agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,handle_parsing_errors=True)

    with st.chat_message("assistant"):
        st_cb = StreamlitCallbackHandler(st.container(),expand_new_thoughts=False)
        response = search_agent.run(st.session_state.messages, callbacks=[st_cb])
        st.session_state.messages.append({"role":"assistant", "content":response})
        st.write(response)