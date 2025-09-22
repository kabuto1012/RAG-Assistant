from crewai import Agent, Task, Crew, LLM, Process
from crewai.tools import tool
import os
from dotenv import load_dotenv
from search_tool import search_top_results
from scraper_tool import scrape_page
# from agent import collection, find_best_context, generate_answer

# Load environment variables
load_dotenv()

# Check for required API key
if "GEMINI_API_KEY" not in os.environ:
    raise ValueError("GEMINI_API_KEY environment variable is required. Please set it in your .env file.")

gemini_llm = LLM(
    model='gemini/gemini-2.5-pro',
    api_key=os.environ["GEMINI_API_KEY"],
    temperature=0.0
)

@tool("RDR2 Web Search Scraper Tool")
def rdr2_web_tool(question: str) -> str:
    """
    Searches the web for the question and scrapes the top results.
    Returns the combined scraped text.
    """
    search_results = search_top_results(question, top_n=1)
    if not search_results:
        return "Sorry, no search results found."

    combined_texts = ""
    for idx, url in enumerate(search_results, 1):
        combined_texts += f"\n--- Result {idx}: {url} ---\n"
        combined_texts += scrape_page(url)

    return combined_texts

# @tool("RDR2 Answer Generation Tool")
# def rdr2_tool(question: str) -> str:
#     """
#     Finds and generates answers for questions about Red Dead Redemption 2
#     using a specialized knowledge base. The input must be a question string.
#     """
#     retrieved_context, distance = find_best_context(question, collection)
#     if distance > 2.2:
#         return "I'm sorry, I don't have enough information for that question."
#
#     final_answer = generate_answer(retrieved_context, question)
#     return final_answer

rdr2_agent = Agent(
    role="Professional RDR2 Game Data Analyst",
    goal="Provide precise, data-driven, and actionable answers to questions about Red Dead Redemption 2, ensuring all relevant practical details are included.",
    backstory="You are a meticulous data analyst specializing in video game mechanics and lore, with a focus on Red Dead Redemption 2. "
        "You do not speculate or give personal opinions. Your purpose is to find objective data from reliable web sources and present it clearly. "
        "You believe in transparency, so you always cite the source of your information. Your reports must include not only the direct answer but also all "
        "practical details like item locations, costs, and useful gameplay tips to provide the most value to the user.",
    tools=[rdr2_web_tool],
    verbose=True,
    llm=gemini_llm
)
# from crewai.utilities.paths import db_storage_path
# import os

# storage_path = db_storage_path()
# print(f"CrewAI storage location: {storage_path}")

# if os.path.exists(storage_path):
#     print("\nStored files and directories:")
#     for item in os.listdir(storage_path):
#         item_path = os.path.join(storage_path, item)
#         if os.path.isdir(item_path):
#             print(f"📁 {item}/")
#             if os.path.exists(item_path):
#                 for subitem in os.listdir(item_path):
#                     print(f"   └── {subitem}")
#         else:
#             print(f"📄 {item}")
# else:
#     print("No CrewAI storage directory found yet.")
rdr2_crew = Crew(
            agents=[rdr2_agent],
            tasks=[],
            process=Process.sequential,
            memory=True,
            embedder={
        "provider": "google",
        "config": {
            "api_key": os.environ.get("GOOGLE_API_KEY", os.environ["GEMINI_API_KEY"]),
            "model": "text-embedding-004"
        }
    },
            verbose=True
            )

if __name__ == "__main__":
    while True:
        user_question = input("\n[YOU] Ask a question: ")
        if user_question.lower() == 'quit':
            print("Thanks for chatting! Goodbye.")
            break

        task = Task(
            agent=rdr2_agent,
            description=(
                "A user has a question about Red Dead Redemption 2: '{user_question}'.\n\n"
                "**First, review our conversation history to see if this is a follow-up question.**\n\n"
                "Follow these steps meticulously to generate a professional, factual report:\n"
                "1.  Analyze the user's question to identify the key topics to search for.\n"
                "2.  Use your web search tool to find the most relevant and reliable article.\n"
                "3.  Thoroughly read the content provided by the tool.\n"
                "4.  From the scraped text, extract the direct answer AND all associated practical details. This includes, but is not limited to: how to obtain items, their specific locations, costs, and any valuable gameplay tips or strategies.\n"
                "5.  Finally, synthesize all the extracted information into a single, comprehensive, and well-structured answer."
            ).format(user_question=user_question),
            expected_output=(
                "A clear, detailed, and helpful answer that directly addresses the user's question. "
                "The answer should be well-organized, using headings or bullet points if necessary "
                "to present complex information clearly."
            )
        )
        rdr2_crew.tasks = [task]
        result = rdr2_crew.kickoff()

        print("\n\n--- ✅ AGENT ---")
        print(result)