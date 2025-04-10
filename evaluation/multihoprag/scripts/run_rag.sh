current_dir=$(dirname "$(readlink -f "$0")")

cd $current_dir
cd ../
export DOCKER_WORKPLACE_NAME=workplace_rag
export EVAL_MODE=True
export DEBUG=True
export BASE_IMAGES=tjbtech1/gaia-bookworm:v2
export COMPLETION_MODEL=hosted_vllm/Qwen/QwQ-32B-AWQ   
export API_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
# claude-3-5-sonnet-20241022


# export OPENAI_API_KEY=
# model=gpt-4o-2024-08-06
# model=gpt-4o-mini-2024-07-18


# export MISTRAL_API_KEY=\
# model=mistral/mistral-large-2407

# export DEEPSEEK_API_KEY=
# model=deepseek/deepseek-chat
# model=deepseek/deepseek-coder

python run_rag.py --model hosted_vllm/Qwen/QwQ-32B-AWQ
# python AAAtestRAG_exp.py
