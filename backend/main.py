# ------------------ IMPORTS ------------------
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

# Import agent setup
from ai_agent import graph, SYSTEM_PROMPT, parse_response


# ------------------ FASTAPI APP ------------------
app = FastAPI()


# ------------------ REQUEST MODEL ------------------
class Query(BaseModel):
    message: str


# ------------------ ROUTES ------------------
@app.post("/ask")
async def ask(query: Query):
    """
    Endpoint to receive user messages and return AI responses.
    Always returns { "response": str, "tool_called": str }.
    """
    try:
        # Prepare inputs for the agent
        inputs = {"messages": [("system", SYSTEM_PROMPT), ("user", query.message)]}

        # Stream agent response
        stream = graph.stream(inputs, stream_mode="updates")
        tool_called_name, final_response = parse_response(stream)

        return {
            "response": final_response,
            "tool_called": tool_called_name,
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        # ✅ Always return consistent schema
        return {
            "response": f"⚠️ Sorry, something went wrong: {str(e)}",
            "tool_called": "None",
        }


# ------------------ ENTRY POINT ------------------
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
