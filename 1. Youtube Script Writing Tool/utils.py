from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.tools import DuckDuckGoSearchRun
from langchain.llms import GooglePalm

def generate_script(prompt,video_length,creativity,api_key):

    # Template for generating 'Title'
    title_template = PromptTemplate(
        input_variables = ['subject'], 
        template='Please come up with a title for a YouTube video on the  {subject}.'
        )
    
    # Template for generating 'Video Script' using search engine
    script_template = PromptTemplate(
        input_variables = ['title', 'DuckDuckGo_Search','duration'], 
        template='Create a script for a YouTube video based on this title for me. TITLE: {title} of duration: {duration} minutes using this search data {DuckDuckGo_Search} '
    )


    # Create Google Palm LLM model
    llm = GooglePalm(google_api_key=api_key, temperature=creativity)

    #Creating chain for 'Title' & 'Video Script'
    title_chain = LLMChain(llm=llm, prompt=title_template, verbose=True)
    script_chain = LLMChain(llm=llm, prompt=script_template, verbose=True)

    # https://python.langchain.com/docs/modules/agents/tools/integrations/ddg
    search = DuckDuckGoSearchRun()

    # Executing the chains we created for 'Title'
    title = title_chain.invoke(prompt)

    # Executing the chains we created for 'Video Script' by taking help of search engine 'DuckDuckGo'
    search_result = search.run(prompt) 
    script = script_chain.run(title=title, DuckDuckGo_Search=search_result,duration=video_length)

    # Returning the output
    return search_result,title,script
