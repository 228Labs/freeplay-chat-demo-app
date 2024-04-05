'''
Run your vector search in line with the test run
'''
from freeplay import Freeplay, RecordPayload, CallInfo, ResponseInfo, SessionInfo, CallInfo, TestRunInfo
from openai import OpenAI
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

fpClient = Freeplay(
    freeplay_api_key=freeplay_key,
    api_base=freeplay_url,
)

# create a new test run
test_run = fpClient.test_runs.create(project_id=freeplay_project_id, testlist="Eval Benchmark")

# get the prompt associated with the test run
template_prompt = fpClient.prompts.get(project_id=freeplay_project_id,
                                       template_name="rag-qa",
                                       environment="latest"
                                       )

# run each test case in the test list
for test_case in test_run.test_cases:
    print(f"Running test case: {test_case.id}")
    # run rag on the question
    question = test_case.variables['question']
    search_res, filter = vector_search(question, top_k=5, cosine_threshold=0.90)
    # format the prompt with the test case variables
    update_vars = {'question': question, 'supporting_information': str(search_res)}
    formatted_prompt = template_prompt.bind(update_vars).format()

    # make your llm call
    s = time.time()
    openaiClient = OpenAI(api_key=openai_key)
    chat_response = openaiClient.chat.completions.create(
        model=formatted_prompt.prompt_info.model,
        messages=formatted_prompt.messages,
        **formatted_prompt.prompt_info.model_parameters
    )
    e = time.time()

    # append the results to the messages
    all_messages = formatted_prompt.all_messages(
        {'role': chat_response.choices[0].message.role,
         'content': chat_response.choices[0].message.content}
    )

    # create a session which will create a UID
    session = fpClient.sessions.create()

    # build the record payload
    payload = RecordPayload(
        all_messages=all_messages,
        inputs=test_case.variables, # the variables from the test case are the inputs
        session_info=session, # use the session id created above
        test_run_info=TestRunInfo(test_run_id=test_run.test_run_id,
                                  test_case_id=test_case.id), # link the record call to the test run and test case
        prompt_info=formatted_prompt.prompt_info, # log the prompt information 
        call_info=CallInfo.from_prompt_info(formatted_prompt.prompt_info, start_time=s, end_time=e), # log call information
        response_info=ResponseInfo(
            is_complete=chat_response.choices[0].finish_reason == 'stop'
        )
    )
    # record the results to freeplay
    fpClient.recordings.create(payload)