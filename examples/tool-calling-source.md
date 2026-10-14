# Tool calls and application code

This is a small source for the starter's narration and draft examples.

A model can return a structured request to use a tool. The application receives the request and its arguments, decides whether it is permitted, runs the corresponding code, and sends the result back to the model. A later model response can use that result.

The application must validate arguments and permissions at the execution boundary. A tool request does not prove that an action was executed successfully. Inspect the operation's result before claiming completion.

Reference: https://platform.openai.com/docs/guides/function-calling

This example contains no customer, account, credential or benchmark data.
