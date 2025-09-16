# ------------------ IMPORTS ------------------
from langchain.agents import tool
from tools import query_medgemma, call_emergency

# ------------------ TOOLS ------------------

@tool
def ask_mental_health_specialist(query: str) -> str:
    """
    Generate a therapeutic response using the MedGemma model.
    Use this for all general user queries, mental health questions, emotional concerns,
    or to offer empathetic, evidence-based guidance in a conversational tone.
    """
    return query_medgemma(query)


@tool
def emergency_call_tool() -> None:
    """
    Place an emergency call to the safety helpline's phone number via Twilio.
    Use this only if the user expresses suicidal ideation, intent to self-harm,
    or describes a mental health emergency requiring immediate help.
    """
    call_emergency()


@tool
def locate_therapist_tool(location: str) -> str:
    """
    Finds and returns a list of licensed therapists near the specified location.
    """
    return (
        f"Here are some therapists near {location}:\n"
        "- Dr. Ayesha Kapoor - +1 (555) 123-4567\n"
        "- Dr. James Patel - +1 (555) 987-6543\n"
        "- MindCare Counseling Center - +1 (555) 222-3333"
    )


# ------------------ AGENT SETUP ------------------
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from config import OPENAI_API_KEY

tools = [ask_mental_health_specialist, emergency_call_tool, locate_therapist_tool]
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2, api_key=OPENAI_API_KEY)
graph = create_react_agent(llm, tools=tools)

SYSTEM_PROMPT = """
You are an AI engine supporting mental health conversations with warmth and vigilance.
You have access to three tools:

1. `ask_mental_health_specialist`: Use this tool to answer all emotional or psychological queries with therapeutic guidance.
2. `locate_therapist_tool`: Use this tool if the user asks about nearby therapists or if recommending local professional help would be beneficial.
3. `emergency_call_tool`: Use this immediately if the user expresses suicidal thoughts, self-harm intentions, or is in crisis.

Always take necessary action. Respond kindly, clearly, and supportively.
"""


# ------------------ RESPONSE PARSER ------------------

def parse_response(stream):
    """
    Parses the LangGraph stream to extract:
    - tool_called_name (if any tool was triggered)
    - final_response (agent's reply)
    """
    tool_called_name = "None"
    final_response = None

    for event in stream:
        # LangGraph streams yield tuples: (event_type, payload)
        if isinstance(event, tuple) and len(event) == 2:
            event_type, payload = event

            if event_type == "tools":
                tool_messages = payload.get("messages", [])
                for msg in tool_messages:
                    if hasattr(msg, "name"):
                        tool_called_name = msg.name

            elif event_type == "agent":
                messages = payload.get("messages", [])
                for msg in messages:
                    if getattr(msg, "content", None):
                        final_response = msg.content

        # Fallback: if stream yields dicts
        elif isinstance(event, dict):
            tool_data = event.get("tools")
            if tool_data:
                for msg in tool_data.get("messages", []):
                    if hasattr(msg, "name"):
                        tool_called_name = msg.name

            agent_data = event.get("agent")
            if agent_data:
                for msg in agent_data.get("messages", []):
                    if getattr(msg, "content", None):
                        final_response = msg.content

    # ✅ Safety net: ensure we always return something
    if not final_response:
        final_response = (
            "I'm here with you. Could you please share more so I can better understand and support you?"
        )

    return tool_called_name, final_response
