import json
import os

def extract_code_from_ipynb(ipynb_path, output_py_path):
    """
    从单个 .ipynb 文件中提取 Python 代码并保存为 .py 文件
    """
    with open(ipynb_path, "r", encoding="utf-8") as f:
        nb_data = json.load(f)

    code_lines = []
    for cell in nb_data.get("cells", []):
        if cell.get("cell_type") == "code":
            # 拼接单元格内的所有代码行
            cell_code = "".join(cell.get("source", []))
            code_lines.append(cell_code)
            # 加分隔线区分不同单元格
            code_lines.append("\n\n# -------------------------\n\n")

    with open(output_py_path, "w", encoding="utf-8") as f:
        f.writelines(code_lines)

    print(f"✅ 提取完成：{ipynb_path} → {output_py_path}")
    return code_lines

def extract_all_ipynb_in_folder(folder_path="."):
    """
    遍历文件夹里所有 .ipynb 文件，批量提取代码
    """
    all_code = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".ipynb"):
            ipynb_path = os.path.join(folder_path, filename)
            # 生成对应的 .py 文件名
            py_filename = filename.replace(".ipynb", ".py")
            py_path = os.path.join(folder_path, py_filename)
            
            # 提取单个文件代码
            code = extract_code_from_ipynb(ipynb_path, py_path)
            # 加入到总代码里，加上文件分隔
            all_code.append(f"# ========== 来自文件：{filename} ==========\n")
            all_code.extend(code)

    # 保存合并后的所有代码
    if all_code:
        all_py_path = os.path.join(folder_path, "all_extracted_code.py")
        with open(all_py_path, "w", encoding="utf-8") as f:
            f.writelines(all_code)
        print(f"\n📦 所有代码已合并保存为：{all_py_path}")
    else:
        print("\n❌ 没有找到 .ipynb 文件")

if __name__ == "__main__":
    # 把脚本放在你的项目根目录运行（也就是你截图里的 ds2026-G04-T-B2_FedPolicyAssets 文件夹）
    # 脚本会自动提取当前文件夹里所有的 .ipynb 文件
    extract_all_ipynb_in_folder()