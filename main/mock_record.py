
import json
import os
import tkinter as tk
from tkinter import ttk, messagebox

class ReviewApp:
    def __init__(self, root, file_path):
        self.root = root
        self.root.title("错题回顾模块")
        self.root.geometry("800x600")
        self.root.configure(bg="#E6F7FF")
        self.exam_data = self.load_exam_data(file_path)  # 加载考试数据
        self.user_answers = {}  # 存储用户答案
        self.mistakes = []  # 存储错题
        self.file_name = os.path.basename(file_path)  # 获取文件名
        self.setup_ui()  # 设置UI

    def load_exam_data(self, file_path):
        """加载考试数据"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            messagebox.showerror("错误", f"加载考试数据时出错：{e}")
            return {}

    def setup_ui(self):
        """设置UI界面"""
        # 创建框架和控件
        self.style = ttk.Style(self.root)
        self.style.configure("TFrame", background="#E6F7FF")  # 设置背景颜色

        self.top_frame = ttk.Frame(self.root, padding=10)
        self.top_frame.pack(fill=tk.X, padx=10, pady=5)

        self.middle_frame = ttk.Frame(self.root, padding=10)
        self.middle_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.bottom_frame = ttk.Frame(self.root, padding=10)
        self.bottom_frame.pack(fill=tk.X, padx=10, pady=5)

        # 创建标签显示考试数据
        self.exam_label = tk.Label(self.top_frame, text=f"考试数据: {self.file_name}", font=("KaiTi", 18),bg="#E6F7FF")
        self.exam_label.pack(side=tk.LEFT, padx=5)
        
        # 添加返回按钮
        self.back_button = ttk.Button(self.top_frame, text="返回主界面", command=self.go_back)
        self.back_button.pack(side=tk.RIGHT, padx=5)  # 将按钮放在右侧

        # 显示错题列表
        self.question_listbox = tk.Listbox(self.middle_frame, height=10, font=("Arial", 12))
        self.question_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.question_listbox.bind("<<ListboxSelect>>", self.display_question)

        self.scrollbar = ttk.Scrollbar(self.middle_frame, orient=tk.VERTICAL, command=self.question_listbox.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.question_listbox.config(yscrollcommand=self.scrollbar.set)

        # 题目详情
        self.question_detail = tk.Text(self.middle_frame, wrap=tk.WORD, state=tk.DISABLED, height=15, font=("KaiTi", 16))
        self.question_detail.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 创建答案显示区域，放在题目详情区域的底部
        self.answer_display = tk.Text(self.middle_frame, wrap=tk.WORD, state=tk.DISABLED, height=5, font=("Arial", 12))  # 设置背景为红色
        self.answer_display.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=False, padx=5, pady=5)


        self.identify_mistakes()  # 识别错题

    def identify_mistakes(self):
        """识别错题"""
        self.mistakes = []
        self.question_listbox.delete(0, tk.END)

        for idx, question in enumerate(self.exam_data):
            correct_answer = question.get("correct_answer", [])
            user_answer = self.user_answers.get(str(idx), "未作答")

            if user_answer != correct_answer:
                self.mistakes.append((idx, question, user_answer))
                self.question_listbox.insert(tk.END, f"题目 {idx + 1}")

        if not self.mistakes:
            messagebox.showinfo("提示", "没有错题！")

    def display_question(self, event):
        """显示选中错题详情"""
        if not self.mistakes:
            return

        selection = self.question_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        unique_id, question, user_answer = self.mistakes[index]

        question_content = question.get('question', '未知题目')
        correct_answer = ", ".join(question.get('correct_answer', []))
        user_answer_display = user_answer if user_answer != "未作答" else '未作答'

        options = question.get('options', {})
        options_display = "\n".join([f"{key}: {value}" for key, value in options.items()])

        self.question_detail.config(state=tk.NORMAL)
        self.question_detail.delete(1.0, tk.END)

        details = (
            f"题目编号: {unique_id}\n"
            f"题目内容: \n{question_content}\n"
            f"\n选项:\n{options_display}\n"
        )

        self.question_detail.insert(tk.END, details)
        self.question_detail.config(state=tk.DISABLED)

        # 在红色方框区域显示考生答案和正确答案
        self.answer_display.config(state=tk.NORMAL)
        self.answer_display.delete(1.0, tk.END)
        answer_details = (
            f"考生答案: {user_answer_display}\n"
            f"正确答案: {correct_answer}\n"
        )
        self.answer_display.insert(tk.END, answer_details)
        self.answer_display.config(state=tk.DISABLED)
    
    def go_back(self):
        """销毁当前窗口并返回主程序"""
        from main import MainApp
        self.root.destroy()
        root = tk.Tk()
        main_app = MainApp(root)
        root.mainloop()
if __name__ == "__main__":
    root = tk.Tk()
    file_path = "path/to/your/exam_data.json"  # 这行可以删除
    app = ReviewApp(root, file_path)  # 这行可以删除
    root.mainloop()