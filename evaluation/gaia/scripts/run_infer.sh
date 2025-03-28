current_dir=$(dirname "$(readlink -f "$0")")

cd $current_dir
cd ../../../
export DOCKER_WORKPLACE_NAME=workplace
export EVAL_MODE=True
export DEBUG=True
export BASE_IMAGES=tjbtech1/gaia-bookworm:v2
export COMPLETION_MODEL=hosted_vllm/Qwen/QwQ-32B-AWQ   
export API_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
# claude-3-5-sonnet-20241022

python evaluation/gaia/run_infer.py --container_name gaia_lite_eval --model ${COMPLETION_MODEL} --test_pull_name main --debug --eval_num_workers 1 --port 12345 --data_split validation --level 2023_all --agent_func get_system_triage_agent --git_clone
# python /Users/tangjiabin/Documents/reasoning/metachain/test_gaia_tool.py