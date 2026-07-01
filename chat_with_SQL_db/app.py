import streamlit as st
from pathlib import Path
from sqlalchemy import create_engine
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_classic.agents import AgentType
from langchain_classic.callbacks import StreamlitCallbackHandler
from langchain_groq import ChatGroq
import sqlite3

#----------page configuration----------
st.set_page_config(page_title="Chat with SQL Database", page_icon=":robot:")
st.title("Chat with SQL Database :robot:")

api_key = st.text_input(label="Enter your Groq API Key", type="password")

#----------Database connection----------
if not api_key:
    st.info("Please enter your Groq API Key to continue.")

else:
    llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=api_key, streaming=True)
    
    @st.cache_resource(ttl="2h")
    def configure_database():
        db_path = (Path(__file__).parent / "student.db").absolute()
        print(f"Database path: {db_path}")
        creator = lambda: sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        engine = create_engine("sqlite:///", creator=creator)
        return SQLDatabase(engine=engine, include_tables=["STUDENT"])
    
    db = configure_database()
    #toolkit
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)

    agent = create_sql_agent(
        llm=llm,
        toolkit=toolkit,
        verbose=True,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION
    )

    if "messages" not in st.session_state or st.sidebar.button("Clear Chat History"):
        st.session_state["messages"] = [
            {"role":"assistent", "content":"Hello, How can I help you?"}
        ]
    
    for message in st.session_state.messages:
        st.chat_message(message["role"]).write(message["content"])

    user_input = st.chat_input("Ask me anything from the STUDENT database")
    if user_input:
        st.session_state.messages.append({"role":"user", "content":user_input})
        st.chat_message("user").write(user_input)

        with st.chat_message("assistant"):
            st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
            response = agent.run(user_input, callbacks=[st_cb])
            st.session_state.messages.append({"role":"assistant", "content":response})
            st.write(response)