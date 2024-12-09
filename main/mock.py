import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
import random
import time

class MockExamApp:
    def __init__(self, root, questions, exam_file, record_folder="records/exam"):
        self.root = root
        self.questions = questions
        self.current_question_index = 0
        self.answers = [None] * len(questions)
        self.score = 0
        self.record_folder = record_folder
        self.exam_file = exam_file
        self.time_limit = 90 * 60  # 90分钟限制
        self.start_time = time.time()  # 设置考试开始时间

        # 设置窗口标题和大小
        self.root.title("模拟考试")
        self.root.geometry("1000x600")
        self.root.configure(bg="#E6F7FF")

        # 创建导航栏框架
        self.navbar = tk.Frame(self.root, bg="#AEEEEE")  # 淡蓝色背景
        self.navbar.pack(side="top", fill="x", pady=5)

        # 创建一个框架来放置标题、按钮和计时器
        self.navbar_content = tk.Frame(self.navbar, bg="#AEEEEE")
        self.navbar_content.pack(side="top", fill="x")

        # 显示题库名称
        self.question_bank_label = tk.Label(self.navbar_content, text=self.exam_file, font=("楷体", 18, "bold"), fg="#333333", bg="#AEEEEE")
        self.question_bank_label.pack(side="left", padx=10)

        # 创建返回主程序按钮
        self.back_button = tk.Button(self.navbar_content, text="返回界面", command=self.return_to_main, bg="red", fg="white", font=("Helvetica", 12), relief="raised")
        self.back_button.pack(side="right", padx=10)

        # 显示已用时间
        self.time_label = tk.Label(self.navbar_content, text="", font=("Helvetica", 12, "bold"), bg="#AEEEEE", fg="#333333")
        self.time_label.pack(side="left", padx=100)

        # 启动计时器
        self.update_timer()

        # 主界面分为左右两部分
        self.main_frame = tk.Frame(self.root, bg="#E6F7FF")
        self.main_frame.pack(side="left", fill="both", expand=True, padx=20, pady=10)

        # 题目显示区域
        self.question_frame = tk.Frame(self.main_frame, bg="white")
        self.question_frame.pack(fill="both", expand=True)

        self.question_canvas = tk.Canvas(self.question_frame, bg="white", highlightthickness=0)
        self.question_canvas.pack(side="left", fill="both", expand=True)

        # 添加水平滚动条
        self.question_scrollbar_x = tk.Scrollbar(self.question_frame, orient="horizontal", command=self.question_canvas.xview)
        self.question_scrollbar_x.pack(side="bottom", fill="x")

        self.question_canvas.configure(xscrollcommand=self.question_scrollbar_x.set)

        self.question_inner_frame = tk.Frame(self.question_canvas, bg="white")
        self.question_canvas.create_window((0, 0), window=self.question_inner_frame, anchor="nw")
        self.question_inner_frame.bind("<Configure>", lambda e: self.question_canvas.configure(scrollregion=self.question_canvas.bbox("all")))

        self.question_label = tk.Label(self.question_inner_frame, text="", wraplength=900, font=("楷体", 16), justify="left", bg="white", fg="#333333")
        self.question_label.pack(pady=10)

        # 选项显示区域
        self.options_frame = tk.Frame(self.main_frame, bg="#E6F7FF")
        self.options_frame.pack(fill="both", expand=True)

        # 反馈区域
        self.feedback_label = tk.Label(self.main_frame, text="", font=("Helvetica", 12), fg="green", bg="#E6F7FF")
        self.feedback_label.pack(pady=10)

        # 底部按钮区域
        self.button_frame = tk.Frame(self.main_frame, bg="#E6F7FF")
        self.button_frame.pack(pady=10)

        # 使用ttk.Button替代tk.Button并美化按钮
        button_style = ttk.Style()
        button_style.configure("TButton", font=("Helvetica", 12), padding=5, relief="flat", background="#AEEEEE", foreground="#333333")
        button_style.map("TButton", background=[("active", "#B0E0E6")])  # 悬停效果

        self.prev_button = ttk.Button(self.button_frame, text="上一题", command=self.prev_question, style="TButton")
        self.prev_button.pack(side="left", padx=10)

        self.submit_button = ttk.Button(self.button_frame, text="交卷", command=self.submit_exam, style="TButton")
        self.submit_button.pack(side="left", padx=10)

        self.next_button = ttk.Button(self.button_frame, text="下一题", command=self.next_question, style="TButton")
        self.next_button.pack(side="left", padx=10)

        # 右侧答题卡区域
        self.right_frame = tk.Frame(self.root, bg="#E6F7FF")
        self.right_frame.pack(side="right", fill="y", padx=10, pady=10)

        self.card_canvas = tk.Canvas(self.right_frame, width=235, bg="#FFFFFF", highlightthickness=0)
        self.card_canvas.pack(side="left", fill="both", expand=True)

        self.scrollbar = tk.Scrollbar(self.right_frame, orient="vertical", command=self.card_canvas.yview)
        self.scrollbar.pack(side="right", fill="y")

        self.card_inner_frame = tk.Frame(self.card_canvas, bg="#E6F7FF")
        self.card_canvas.create_window((0, 0), window=self.card_inner_frame, anchor="nw")
        self.card_inner_frame.bind("<Configure>", lambda e: self.card_canvas.configure(scrollregion=self.card_canvas.bbox("all")))

        # 初始化第一个问题和答题卡
        self.load_question()
        self.update_answer_card()

    def return_to_main(self):
        """销毁当前窗口并返回主程序"""
        from main import MainApp
        self.root.destroy()
        root = tk.Tk()
        main_app = MainApp(root)
        root.mainloop()

    def update_timer(self):
        """更新计时器"""
        elapsed_time = int(time.time() - self.start_time)
        remaining_time = self.time_limit - elapsed_time
        if remaining_time <= 0:
            self.submit_exam()
        else:
            minutes, seconds = divmod(remaining_time, 60)
            self.time_label.config(text=f"倒计时: {minutes:02}:{seconds:02}")
            self.root.after(1000, self.update_timer)

    def load_question(self):
        """加载当前问题"""
        if 0 <= self.current_question_index < len(self.questions):
            question = self.questions[self.current_question_index]
            self.question_label.config(text=f"第 {self.current_question_index + 1} 题: {question['question']}")
            self.feedback_label.config(text="", fg="green")

            # 更新题库名称，去掉前缀
            self.question_bank_label.config(text=os.path.basename(self.exam_file))  # 只保留文件名

            # 清空选项
            for widget in self.options_frame.winfo_children():
                widget.destroy()

            # 创建复选框选项
            self.selected_options = {}
            for key, value in question["options"].items():
                # 检查当前题目的答案是否已保存
                is_selected = key in self.answers[self.current_question_index] if self.answers[self.current_question_index] else False
                var = tk.BooleanVar(value=is_selected)
                self.selected_options[key] = var
                tk.Checkbutton(
                    self.options_frame,
                    text=f"{key}. {value}",
                    font=("Helvetica", 12),
                    variable=var,
                    anchor="w",
                    bg="#E6F7FF"
                ).pack(fill="x", padx=5, pady=2)

            # 更新答题卡
            self.update_answer_card()

    def update_answer_card(self):
        """更新答题卡"""
        for widget in self.card_inner_frame.winfo_children():
            widget.destroy()

        # 创建答题卡按钮，每行五个按钮
        for i in range(len(self.questions)):
            status = "未答"
            if self.answers[i] is not None and len(self.answers[i]) > 0:  # 如果已经作答且有选项
                status = "已答"
            color = "green" if status == "已答" else "white"

            # 每行最多五个按钮
            button = tk.Button(self.card_inner_frame, text=f"{i + 1}", width=4, height=2, bg=color, fg="black", command=lambda idx=i: self.jump_to_question(idx))
            button.grid(row=i // 5, column=i % 5, padx=5, pady=5)

    def jump_to_question(self, index):
        """跳转到指定的题目"""
        self.save_current_answer()  # 保存当前题目的答案
        self.current_question_index = index
        self.load_question()  # 加载选定的题目

    def prev_question(self):
        """上一题"""
        # 保存当前题目的答案
        self.save_current_answer()
        if self.current_question_index > 0:
            self.current_question_index -= 1
            self.load_question()

    def next_question(self):
        """下一题"""
        # 保存当前题目的答案
        self.save_current_answer()
        if self.current_question_index < len(self.questions) - 1:
            self.current_question_index += 1
            self.load_question()
        else:
            messagebox.showinfo("提示", "已经是最后一题！")

    def save_current_answer(self):
        """保存当前题目的答案"""
        selected_answers = []
        for key, var in self.selected_options.items():
            if var.get():  # 如果复选框被选中
                selected_answers.append(key)
        self.answers[self.current_question_index] = selected_answers  # 保存当前题目的答案
        self.update_answer_card()  # 更新答题卡

        # 每次保存答案时更新记录
        self.save_record()  # 调用保存记录的方法

    def save_record(self):
        """保存答题记录"""
        # 创建记录文件夹，如果不存在
        if not os.path.exists(self.record_folder):
            os.makedirs(self.record_folder)

        # 更新记录内容
        record = {
            "answers": self.answers,
            "exam_file": self.exam_file,
            "score": self.score
        }

        # 使用考试文件名作为记录文件名，去掉扩展名
        base_filename = os.path.splitext(os.path.basename(self.exam_file))[0]
        record_filename = os.path.join(self.record_folder, f"{base_filename}_record.json")
        with open(record_filename, "w", encoding="utf-8") as f:
            json.dump(record, f, ensure_ascii=False, indent=4)

    def calculate_score(self):
        """计算分数"""
        self.score = 0  # 重置分数
        total_questions = len(self.questions)  # 题目总数
        points_per_question = 1000 / total_questions if total_questions > 0 else 0  # 每题分值

        for i, answer in enumerate(self.answers):
            if answer == self.questions[i]["correct_answer"]:
                self.score += points_per_question  # 每题得分

        self.score = round(self.score, 2)  # 保留两位小数

    def show_score_window(self):
        """显示分数窗口"""
        score_window = tk.Toplevel(self.root)
        score_window.title("考试结果")
        score_window.geometry("600x400")

        # 添加标题标签
        title_label = tk.Label(score_window, text="考试结果", font=("Helvetica", 16, "bold"))
        title_label.pack(pady=10)

        # 创建表格
        tree = ttk.Treeview(score_window, columns=("序号", "分值", "得分", "正确答案", "考生答案"), show="headings", height=15)
        tree.heading("序号", text="序号")
        tree.heading("分值", text="分值")
        tree.heading("得分", text="得分")
        tree.heading("正确答案", text="正确答案")
        tree.heading("考生答案", text="考生答案")

        # 设置列宽和对齐方式
        tree.column("序号", width=50, anchor="center")
        tree.column("分值", width=50, anchor="center")
        tree.column("得分", width=50, anchor="center")
        tree.column("正确答案", width=100, anchor="center")
        tree.column("考生答案", width=100, anchor="center")

        # 设置样式
        style = ttk.Style()
        style.configure("Treeview", rowheight=25, bordercolor="#000000", borderwidth=1)  # 设置边框颜色和宽度
        style.configure("Treeview.Heading", font=("Helvetica", 12, "bold"), background="#007ACC", foreground="black", bordercolor="#000000", borderwidth=1)  # 设置表头样式
        style.map("Treeview.Heading", background=[("active", "#005A99")])

        # 插入数据
        total_questions = len(self.questions)
        points_per_question = 1000 / total_questions if total_questions > 0 else 0  # 每题分值

        for i, answer in enumerate(self.answers):
            correct = self.questions[i]["correct_answer"]
            score = points_per_question if answer == correct else 0
            tree.insert("", "end", values=(i + 1, round(points_per_question, 2), round(score, 2), correct, answer))

        tree.pack(expand=True, fill="both", padx=10, pady=10)

        # 添加滚动条
        scrollbar = ttk.Scrollbar(score_window, orient="vertical", command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # 显示窗口
        score_window.mainloop()

    def submit_exam(self):
        """交卷并显示分数"""
        self.calculate_score()
        self.show_score_window()  # 显示评分窗口
        self.save_record()


def generate_exam(exam_number):
    """从所有题库中随机抽取125道题目生成新的考试文件"""
    question_files = [file for file in os.listdir("bank") if file.endswith(".json")]
    all_questions = []
    for file in question_files:
        with open(os.path.join("bank", file), "r", encoding="utf-8") as f:
            questions = json.load(f)
            all_questions.extend(questions)

    random.shuffle(all_questions)
    selected_questions = all_questions[:125]

    exam_folder = "bank/exam"
    if not os.path.exists(exam_folder):
        os.makedirs(exam_folder)

    # 使用传入的exam_number生成文件名
    exam_filename = os.path.join(exam_folder, f"考试_{exam_number}.json")
    with open(exam_filename, "w", encoding="utf-8") as f:
        json.dump(selected_questions, f, ensure_ascii=False, indent=4)

    # 创建记录文件夹，如果不存在
    record_folder = "records/exam"
    if not os.path.exists(record_folder):
        os.makedirs(record_folder)

    # 创建一个空的答题记录
    record = {
        "answers": [],
        "exam_file": exam_filename,
        "score": 0
    }

    # 使用考试文件名作为记录文件名，去掉扩展名
    base_filename = os.path.splitext(os.path.basename(exam_filename))[0]
    record_filename = os.path.join(record_folder, f"{base_filename}_record.json")
    with open(record_filename, "w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=4)

    return exam_filename


def run_mock_exam():
    """开始模拟考试"""
    exam_number = int(time.time())  # 使用当前时间戳作为考试编号
    exam_file = generate_exam(exam_number)  # 生成新的考试文件
    with open(exam_file, "r", encoding="utf-8") as f:
        questions = json.load(f)

    root = tk.Tk()
    app = MockExamApp(root, questions, exam_file)
    root.mainloop()


if __name__ == "__main__":
    run_mock_exam()  # 启动模拟考试
