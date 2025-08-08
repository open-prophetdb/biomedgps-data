import subprocess

def get_staged_files():
    """获取已暂存（staged）的文件列表"""
    result = subprocess.run(["git", "diff", "--cached", "--name-only"],
                            capture_output=True, text=True)
    files = result.stdout.strip().split('\n')
    return [f for f in files if f]  # 排除空行

def categorize_file(file_path):
    """根据文件路径和类型推测说明"""
    if file_path.endswith(".ipynb"):
        return f"- {file_path}: 更新 Jupyter Notebook"
    elif file_path.endswith(".tsv"):
        return f"- {file_path}: 更新 TSV 数据文件"
    elif file_path.endswith(".py"):
        return f"- {file_path}: 修改 Python 脚本"
    elif file_path.endswith(".sh"):
        return f"- {file_path}: 修改 Shell 脚本"
    elif file_path.endswith(".json"):
        return f"- {file_path}: 更新 JSON 配置或数据"
    else:
        return f"- {file_path}: 内容更新"

def generate_commit_message(files):
    header = "data: 更新多个文件，包含脚本、数据与笔记本\n"
    details = "\n".join([categorize_file(f) for f in files])
    return f"{header}\n{details}"

if __name__ == "__main__":
    staged_files = get_staged_files()
    if not staged_files:
        print("❗没有已暂存的文件，请先执行 `git add`。")
    else:
        commit_msg = generate_commit_message(staged_files)
        print("\n✅ 建议的 commit message:\n")
        print(commit_msg)

