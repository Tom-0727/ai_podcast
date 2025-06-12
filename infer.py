import yaml
import argparse

from writer.agent import QwenScriptAgent, API2DScriptAgent
from writer.files_processor import process_markdown_file


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--key_path", type=str, required=True)
    parser.add_argument("--arch", type=str, required=True)
    parser.add_argument("--model", type=str, required=True)
    parser.add_argument("--doc_path", type=str, required=True)
    parser.add_argument("--output_path", type=str, required=True)
    args = parser.parse_args()

    with open(args.key_path, "r") as f:
        keys = yaml.load(f, Loader=yaml.FullLoader)
        api_key = keys[args.arch]["key"]

    if args.arch == "qwen":
        agent = QwenScriptAgent(key=api_key, model=args.model)
    else:
        agent = API2DScriptAgent(forward_key=api_key, model=args.model)

    blocks = process_markdown_file("./assets/docs/营销学.md")
    messages = agent.script_make(blocks)
    response = agent.one_shot(messages)
    with open(args.output_path, "w") as f:
        f.write(response)