import tkinter as tk
from tkinter import messagebox, ttk
import os
import json
import requests
import markdown  # 用于解析Markdown文件
from bs4 import BeautifulSoup  # 用于HTML解析
import subprocess
import sys
from packaging import version  # 用于版本号比较
from bank_GUI_2 import QuizApp  # 导入答题程序
import subprocess


class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("题库选择")
        self.root.geometry("900x600")
        self.root.configure(bg="#E6F7FF")
        self.current_version = "1.4"  # 当前版本号
        self.setup_ui()
        self.check_for_updates()

    def setup_ui(self):
        """设置主界面"""
        self.main_frame = tk.Frame(self.root, bg="#E6F7FF")
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)  # 使用 pack 代替 grid

        # 在主界面上方添加标题
        self.title_label = tk.Label(self.main_frame, text="欢迎使用答题程序", font=("KaiTi", 26), bg="#E6F7FF", fg="#333333")
        self.title_label.pack(pady=(10, 20), anchor="center")  # 使用 pack 设置标题并居中

        # 创建左侧标签框架，宽度固定，防止扩展
        self.sidebar = tk.Frame(self.main_frame, bg="#AEEEEE", width=205)
        self.sidebar.pack(side="left", fill="y", padx=(10, 20))  # 使用 pack 设置左侧栏框架并固定宽度

        # 创建右侧内容区域
        self.content_frame = tk.Frame(self.main_frame, bg="#E6F7FF")
        self.content_frame.pack(side="left", fill="both", expand=True)  # 使用 pack 设置右侧内容框架

        # 设置按钮样式
        button_style = ttk.Style()
        button_style.configure("TButton", font=("Helvetica", 12), padding=8, relief="flat", background="#AEEEEE", foreground="#333333")
        button_style.map("TButton", background=[("active", "#B0E0E6")])  # 悬停效果

        # 创建标签按钮
        self.label_intro = ttk.Button(self.sidebar, text="简介", command=self.show_intro, style="TButton", width=20)  # 设置宽度
        self.label_intro.pack(fill="x", pady=15)

        self.label_practice = ttk.Button(self.sidebar, text="试卷练习", command=self.show_practice, style="TButton", width=20)  # 设置宽度
        self.label_practice.pack(fill="x", pady=15)

        self.label_mock_exam = ttk.Button(self.sidebar, text="模拟考试", command=self.show_mock_exam, style="TButton", width=20)  # 设置宽度
        self.label_mock_exam.pack(fill="x", pady=15)

        self.label_review = ttk.Button(self.sidebar, text="考试回顾", command=self.show_review, style="TButton", width=20)  # 设置宽度
        self.label_review.pack(fill="x", pady=15)


        # 在标签栏底部添加两行内容
        self.bottom_frame = tk.Frame(self.sidebar, bg="#AEEEEE")  # 创建一个底部框架
        self.bottom_frame.pack(side="bottom", fill="x", pady=10)

        # 添加"浩然制作"标签
        self.label_creator = tk.Label(self.bottom_frame, text="浩然制作", font=("Arial", 10), bg="#AEEEEE", fg="#333333")
        self.label_creator.pack(anchor="center")

        # 添加版本号标签
        self.version_label = tk.Label(self.bottom_frame, text=f"版本号: {self.current_version}", font=("Arial", 10), bg="#AEEEEE", fg="#333333")
        self.version_label.pack(anchor="center")
        # 初始化显示简介
        self.show_intro()


    def show_intro(self):
        """显示简介内容"""
        self.clear_content_frame()  # 清除之前的内容
        # 创建Text控件用于显示Markdown内容
        text_widget = tk.Text(self.content_frame, wrap="word", font=("Arial", 12), bg="#FFFFFF", fg="#333333", padx=10, pady=10)
        text_widget.pack(fill="both", expand=True)

        try:
            # 从指定的 URL 获取 Markdown 内容
            response = requests.get("https://h3c-bank.pages.dev/README.md")
            response.raise_for_status()  # 检查请求是否成功
            md_content = response.text
            html_content = markdown.markdown(md_content)  # 将Markdown转换为HTML

            # 配置不同HTML标签的样式
            text_widget.tag_configure("h1", font=("Arial", 18, "bold"), foreground="#007ACC")
            text_widget.tag_configure("h2", font=("Arial", 16, "bold"), foreground="#005A99")
            text_widget.tag_configure("h3", font=("Arial", 14, "bold"), foreground="#003366")
            text_widget.tag_configure("p", font=("Arial", 12), foreground="#333333")
            text_widget.tag_configure("li", font=("Arial", 12), foreground="#333333")

            # 为 <code> 标签设置等宽字体
            text_widget.tag_configure("code", font=("Courier New", 12), foreground="#FF5733", background="#F5F5F5")
            # 为 <strong> 标签设置加粗效果
            text_widget.tag_configure("strong", font=("Arial", 12, "bold"), foreground="#333333")

            # 插入HTML内容到Text控件
            self.insert_html(text_widget, html_content)

        except Exception as e:
            messagebox.showerror("错误", f"加载简介时出错：{e}")

    def insert_html(self, text_widget, html_content):
        """解析并插入HTML内容"""
        # 使用BeautifulSoup来解析HTML，避免手动处理标签
        soup = BeautifulSoup(html_content, "html.parser")
        
        # 处理标题
        for tag in soup.find_all(['h1', 'h2', 'h3']):
            text_widget.insert(tk.END, tag.get_text() + "\n", tag.name)

        # 处理段落
        for tag in soup.find_all('p'):
            text_widget.insert(tk.END, tag.get_text() + "\n", "p")
        
        # 处理列表项
        for tag in soup.find_all(['li']):
            text_widget.insert(tk.END, "- " + tag.get_text() + "\n", "li")
        
        # # 处理代码
        # for tag in soup.find_all('code'):
        #     text_widget.insert(tk.END, tag.get_text() + "\n", "code")
        
        # # 处理加粗文本
        # for tag in soup.find_all('strong'):
        #     text_widget.insert(tk.END, tag.get_text() + "\n", "strong")
        
        # 处理超链接
        for tag in soup.find_all('a'):
            text_widget.insert(tk.END, tag.get_text() + "\n", "a")

    def clear_content_frame(self):
        """清除content_frame中的所有控件"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_practice(self):
        """显示试卷练习内容"""
        self.clear_content_frame()  # 清除之前的内容
        # 创建“进入答题”按钮
        self.enter_quiz_button = ttk.Button(self.content_frame, text="进入答题", command=self.start_quiz, style="TButton")
        self.enter_quiz_button.pack(side=tk.BOTTOM, pady=(0, 20)) 

        self.content_listbox = tk.Listbox(self.content_frame, font=("Helvetica", 12))
        self.content_listbox.pack(fill="both", expand=True, padx=10, pady=10)
        question_files = self.scan_question_files()
        if not question_files:
            messagebox.showerror("错误", "未在 'bank' 文件夹下找到题库文件！")
            return

        for file in question_files:
            self.content_listbox.insert(tk.END, file)  # 将文件名添加到 Listbox

    def show_mock_exam(self):
        """显示模拟考试信息"""
        self.clear_content_frame()  # 清除之前的内容
        # 创建“进入考试”按钮
        self.enter_mock_exam_button = ttk.Button(self.content_frame, text="进入考试", command=self.start_mock_exam, style="TButton")
        self.enter_mock_exam_button.pack(side=tk.BOTTOM, pady=(0, 20)) 

        # 创建Label控件用于显示信息
        exam_info = "欢迎使用模拟考试系统\n总分1000分，考试时间90分钟\n"
        self.exam_info_label = tk.Label(self.content_frame, text=exam_info, font=("KaiTi", 24), bg="#E6F7FF", fg="#333333", justify="center")
        self.exam_info_label.pack(expand=True)  # 使用pack并设置expand=True以居中显示

    def show_review(self):
        """显示错题回顾内容"""
        self.clear_content_frame()  # 清除之前的内容
        # 创建“进入错题回顾”按钮
        self.enter_review_button = ttk.Button(self.content_frame, text="进入错题回顾", command=self.start_review, style="TButton")
        self.enter_review_button.pack(side=tk.BOTTOM, pady=(0, 20)) 

        self.content_listbox = tk.Listbox(self.content_frame, font=("Helvetica", 12))
        self.content_listbox.pack(fill="both", expand=True, padx=10, pady=10)
        review_files = self.scan_review_files()
        if not review_files:
            self.content_listbox.insert(tk.END, "未在 'bank/exam' 文件夹下找到错题记录！")
            return

        self.content_listbox.insert(tk.END, "请选择错题记录文件：\n\n")
        for file in review_files:
            self.content_listbox.insert(tk.END, file)  # 将文件名添加到 Listbox

    def scan_question_files(self):
        """扫描题库文件夹"""
        folder = "bank"
        if not os.path.exists(folder):
            os.makedirs(folder)
        return [file for file in os.listdir(folder) if file.endswith(".json")]

    def scan_review_files(self):
        """扫描错题记录文件夹"""
        folder = "bank/exam"
        if not os.path.exists(folder):
            os.makedirs(folder)
        return [file for file in os.listdir(folder) if file.endswith(".json")]

    def start_quiz(self):
        """进入答题界面"""
        selected_index = self.content_listbox.curselection()  # 获取选中的文件索引
        if not selected_index:
            messagebox.showwarning("提示", "请选择一个题库！")
            return

        selected_file = self.content_listbox.get(selected_index[0])  # 获取选中的文件名
        file_path = os.path.join("bank", selected_file)

        if not os.path.exists(file_path):
            messagebox.showerror("错误", f"文件未找到: {file_path}")
            return

        with open(file_path, "r", encoding="utf-8") as f:
            questions = json.load(f)

        self.root.destroy()
        quiz_root = tk.Tk()
        file_name_without_extension = os.path.splitext(selected_file)[0]
        QuizApp(quiz_root, questions, file_name=file_name_without_extension, record_file=f"records/{file_name_without_extension}_record.json")
        quiz_root.mainloop()

    def start_mock_exam(self):
        """进入模拟考试界面"""
        self.root.destroy()  # 销毁主窗口
        from mock import run_mock_exam  # 导入并运行模拟考试程序
        run_mock_exam()

    def start_review(self):
        """进入错题回顾界面"""
        pass

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
            # else:
                # messagebox.showinfo("提示", "当前已是最新版本。")
        except Exception as e:
            messagebox.showerror("检查更新失败", f"检查更新时出错：{e}")

    def run_updater(self, download_url):
        """运行更新程序并退出当前程序"""
        try:
            updater_path = os.path.join(os.getcwd(), "updater.exe")
            subprocess.Popen([updater_path, "--target", "main.exe", "--url", download_url], shell=False)
            self.root.destroy()
            sys.exit(0)
        except Exception as e:
            messagebox.showerror("启动更新程序失败", f"无法启动更新程序：{e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()