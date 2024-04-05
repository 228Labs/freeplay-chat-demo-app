from freeplay import Freeplay, RecordPayload, CallInfo, ResponseInfo, SessionInfo, CallInfo
import openai
from anthropic import Anthropic
from vectorSearch import vector_search
from dotenv import load_dotenv
import os
import time
import json
import asyncio

load_dotenv("./.env")
freeplay_key = os.getenv("FREEPLAY_KEY")
freeplay_url = os.getenv("FREEPLAY_URL")
freeplay_project_id = os.getenv("FREEPLAY_PROJECT_ID")
openai_key = os.getenv("OPENAI_API_KEY")
anthropic_key = os.getenv("ANTHROPIC_API_KEY")
# create the anthropic client
anthropicClient = Anthropic(
    api_key=anthropic_key,
)

# configure top k
top_k = 5
cosine_threshold = 0.75

# create a new freeplay client
fpClient = Freeplay(
    freeplay_api_key=freeplay_key,
    api_base=freeplay_url
)


def newConvo(convoId: str, customer_id: str, rag_version="rag-v1.2"):
    # create a new session w/ custom metadata
    session = fpClient.sessions.create(custom_metadata={
        "thread_id": convoId,
        "customer_id": customer_id,
        "rag_version": rag_version
    })
    # instantiate the history
    history = []
    return session, history


def getCompletion(message, session, history, tag=["docs", "blogs"], title=None):
    # start timer for logging latency of the full chain
    start = time.time()
    # run semantic search
    search_res, filter = vector_search(message, top_k=top_k,
                               cosine_threshold=cosine_threshold,
                               tag=tag, title=title)
    
    # get the formatted prompt
    prompt_vars = {
        "question": message,
        "supporting_information": str(search_res),
        "history": str(history)
    }

    # get prompt template
    formatted_prompt = fpClient.prompts.get_formatted(
        project_id=freeplay_project_id,
        template_name="rag-qa",
        environment="prod",
        variables=prompt_vars
    )
    #print(json.dumps(prompt_vars, indent=2))

    # run the completion
    if formatted_prompt.prompt_info.provider == "openai":
        chat_completion = openai.chat.completions.create(
            model=formatted_prompt.prompt_info.model,
            messages = formatted_prompt.messages,
            **formatted_prompt.prompt_info.model_parameters
        )
        content = chat_completion.choices[0].message.content
        # update messages
        messages = formatted_prompt.all_messages(
            {'role': chat_completion.choices[0].message.role,
            'content': content}
        )
    elif formatted_prompt.prompt_info.provider == "anthropic":
        chat_completion = anthropicClient.messages.create(
            model=formatted_prompt.prompt_info.model,
            system=formatted_prompt.system_content,
            messages=formatted_prompt.llm_prompt,
            **formatted_prompt.prompt_info.model_parameters
        )
        content = chat_completion.content[0].text
        messages = formatted_prompt.all_messages(
            {'role': chat_completion.role,
             'content': content}
        )
    else:
        raise ValueError(f"Invalid provider: {formatted_prompt.provider}")
    # log latency
    end = time.time()

    # create an async record call payload
    record_payload = RecordPayload(
        all_messages=messages,
        inputs=prompt_vars,
        session_info=session,
        prompt_info=formatted_prompt.prompt_info,
        call_info=CallInfo.from_prompt_info(formatted_prompt.prompt_info, start_time=start, end_time=end),
        response_info=ResponseInfo(
            is_complete=True
        )
    )
    # record the call
    completion_log = fpClient.recordings.create(record_payload)
    completion_id = completion_log.completion_id

    # record the filter used
    fpClient.customer_feedback.update(
        completion_id=completion_id,
        feedback={"search_filter": json.dumps(filter)}
    )

    return content, completion_id


def record_customer_feedback(completion_id, feedback):
    # record the customer feedback
    fpClient.customer_feedback.update(
        completion_id=completion_id,
        feedback=feedback
    )



#session = newConvo("test", "test", "test")
#print(getCompletion("How do I record customer feedback?", session))
