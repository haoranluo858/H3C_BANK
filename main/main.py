import tkinter as tk
from tkinter import messagebox
import os
import json
from bank_GUI_2 import QuizApp  # 导入答题程序
import requests
import subprocess
import sys
from packaging import version  # 用于版本号比较

class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("题库选择")
        self.root.geometry("600x400")
        self.root.configure(bg="#E6F7FF")
        self.current_version = "1.3"  # 当前版本号

        self.setup_ui()
        self.check_for_updates()

    def setup_ui(self):
        """设置主界面"""
        tk.Label(self.root, text="欢迎使用答题程序", font=("楷体", 24, "bold"), bg="#E6F7FF").grid(row=0, column=0, pady=20)

        # 加载题库
        self.question_files = self.scan_question_files()
        if not self.question_files:
            tk.messagebox.showerror("错误", "未在 'bank' 文件夹下找到题库文件！")
            return

        # 显示题库列表
        self.listbox = tk.Listbox(self.root, font=("Helvetica", 14))
        for file in self.question_files:
            self.listbox.insert(tk.END, file)
        self.listbox.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        # 开始答题按钮
        tk.Button(self.root, text="开始答题", font=("Helvetica", 14), command=self.start_quiz).grid(row=2, column=0, pady=20)

        # 底部标签
        tk.Label(self.root, text="浩然制作", font=("Helvetica", 10), bg="#E6F7FF").grid(row=3, column=0, sticky="se", padx=10, pady=30)
        tk.Label(self.root, text=f"版本号: {self.current_version}", font=("Helvetica", 10), bg="#E6F7FF").grid(row=3, column=0, sticky="se", padx=10, pady=10)

        # 配置行和列的权重
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

    def scan_question_files(self):
        """扫描题库文件夹"""
        folder = "bank"
        if not os.path.exists(folder):
            os.makedirs(folder)
        return [os.path.splitext(file)[0] for file in os.listdir(folder) if file.endswith(".json")]

    def start_quiz(self):
        """进入答题界面"""
        selected = self.listbox.curselection()
        if not selected:
            tk.messagebox.showwarning("提示", "请选择一个题库！")
            return

        selected_file = self.listbox.get(selected[0]) + ".json"
        file_path = os.path.join("bank", selected_file)

        with open(file_path, "r", encoding="utf-8") as f:
            questions = json.load(f)

        self.root.destroy()
        quiz_root = tk.Tk()
        file_name_without_extension = os.path.splitext(selected_file)[0]
        QuizApp(quiz_root, questions, file_name=file_name_without_extension, record_file=f"records/{file_name_without_extension}_record.json")
        quiz_root.mainloop()

    def check_for_updates(self):
        """检查更新"""
        try:
            version_info_url = "https://h3c-bank.pages.dev/version.json"
            response = requests.get(version_info_url, timeout=10)
            response.raise_for_status()

            version_info = response.json()
            latest_version = version_info.get("version")
            download_url = version_info.get("download_url")

            if latest_version and version.parse(latest_version) > version.parse(self.current_version):
                if messagebox.askyesno("更新可用", f"有新版本 {latest_version} 可用，是否更新？"):
                    self.run_updater(download_url)
            else:
                messagebox.showinfo("提示", "当前已是最新版本。")
        except Exception as e:
            messagebox.showerror("检查更新失败", f"检查更新时出错：{e}")

    def run_updater(self, download_url):
        """运行更新程序并退出当前程序"""
        try:
            updater_path = os.path.join(os.getcwd(), "updater.exe")
            # 启动更新程序，并传递目标文件和下载链接
            subprocess.Popen([updater_path, "--target", "main.exe", "--url", download_url], shell=False)
            # 确保当前程序退出
            self.root.destroy()
            sys.exit(0)
        except Exception as e:
            messagebox.showerror("启动更新程序失败", f"无法启动更新程序：{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()
