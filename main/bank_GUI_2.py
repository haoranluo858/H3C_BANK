import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
import time


class QuizApp:
    def __init__(self, root, questions, file_name, record_file="record/quiz_record.json"):
        self.root = root
        self.questions = questions
        self.current_question_index = 0
        self.answers = [None] * len(questions)
        self.score = 0
        self.record_file = record_file
        self.file_name = file_name  # 接收传递的文件名

        # 初始化 elapsed_time 为 0，确保没有未定义的变量
        self.elapsed_time = 0   
        
        # 加载记录
        self.load_record()

        # 初始化计时器
        self.start_time = time.time() - self.elapsed_time

        # 设置窗口标题和大小
        self.root.title("答题程序")
        self.root.geometry("1200x800")
        self.root.configure(bg="#E6F7FF")  # 更柔和的背景颜色

        # 创建导航栏框架
        self.navbar = tk.Frame(self.root, bg="#AEEEEE")  # 淡蓝色背景
        self.navbar.pack(side="top", fill="x", pady=5)

        # 创建一个框架来放置标题、按钮和计时器
        self.navbar_content = tk.Frame(self.navbar, bg="#AEEEEE")
        self.navbar_content.pack(side="top", fill="x")

        # 显示题库名称
        self.question_bank_label = tk.Label(self.navbar_content, text=self.file_name, font=("楷体", 18, "bold"), fg="#333333", bg="#AEEEEE")
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

        # 上部分：题目显示区域
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

        # 确保右侧答题卡区域不受影响
        self.right_frame = tk.Frame(self.root, bg="#E6F7FF")
        self.right_frame.pack(side="right", fill="y", padx=10, pady=10)
        # 中部分：选项显示区域
        self.options_frame = tk.Frame(self.main_frame, bg="#E6F7FF")
        self.options_frame.pack(fill="both", expand=True)

        # 下部分：反馈显示区域
        self.feedback_label = tk.Label(self.main_frame, text="", font=("Helvetica", 12), fg="green", bg="#E6F7FF")
        self.feedback_label.pack(pady=10)

        # 底部：按钮区域
        self.button_frame = tk.Frame(self.main_frame, bg="#E6F7FF")
        self.button_frame.pack(pady=10)

        # 使用ttk.Button替代tk.Button并美化按钮
        button_style = ttk.Style()
        button_style.configure("TButton", font=("Helvetica", 12), padding=5, relief="flat", background="#AEEEEE", foreground="#333333")
        button_style.map("TButton", background=[("active", "#B0E0E6")])  # 悬停效果

        self.prev_button = ttk.Button(self.button_frame, text="上一题", command=self.prev_question, style="TButton")
        self.prev_button.pack(side="left", padx=10)
        self.submit_button = ttk.Button(self.button_frame, text="提交答案", command=self.submit_answer, style="TButton")
        self.submit_button.pack(side="left", padx=10)
        self.show_answer_button = ttk.Button(self.button_frame, text="显示答案", command=self.show_answer, style="TButton")
        self.show_answer_button.pack(side="left", padx=10)
        self.next_button = ttk.Button(self.button_frame, text="下一题", command=self.next_question, style="TButton")
        self.next_button.pack(side="left", padx=10)
        self.reset_button = ttk.Button(self.button_frame, text="清空所有选项", command=self.reset_answers, style="TButton")
        self.reset_button.pack(side="left", padx=10)

        # 右侧答题卡区域
        self.right_frame = tk.Frame(self.root, bg="#E6F7FF")
        self.right_frame.pack(side="right", fill="y", padx=10, pady=10)

        self.card_canvas = tk.Canvas(self.right_frame, width=260, bg="#FFFFFF", highlightthickness=0)
        self.card_canvas.pack(side="left", fill="both", expand=True)

        self.scrollbar = tk.Scrollbar(self.right_frame, orient="vertical", command=self.card_canvas.yview)
        self.scrollbar.pack(side="right", fill="y")

        self.card_inner_frame = tk.Frame(self.card_canvas, bg="#E6F7FF")
        self.card_canvas.create_window((0, 0), window=self.card_inner_frame, anchor="nw")
        self.card_inner_frame.bind("<Configure>", lambda e: self.card_canvas.configure(scrollregion=self.card_canvas.bbox("all")))

        # 绑定鼠标滚轮事件以滚动答题卡
        # self.card_canvas.bind("<MouseWheel>", self.on_mouse_wheel)

        # 存储当前题目选项的选择状态
        self.selected_options = {}

        # 初始化第一个问题和答题卡
        self.load_question()
        self.update_answer_card()

    def return_to_main(self):
        """销毁当前窗口并返回主程序"""
        from main import MainApp
        self.root.destroy()
        # 重新启动主程序的界面
        root = tk.Tk()
        main_app = MainApp(root)
        root.mainloop()

    # def on_mouse_wheel(self, event):
    #     """处理鼠标滚轮事件以滚动答题卡"""
    #     delta = event.delta
    #     if delta > 0:
    #         self.card_canvas.yview_scroll(-1, "units")  # 向上滚动
    #     elif delta < 0:
    #         self.card_canvas.yview_scroll(1, "units")   # 向下滚动

    def update_timer(self):
        """更新计时器"""
        elapsed_time = int(time.time() - self.start_time)  # 计算已用时间
        minutes, seconds = divmod(elapsed_time, 60)  # 计算分钟和秒
        self.time_label.config(text=f"已用时间: {minutes:02}:{seconds:02}")  # 格式化为 00:00
        self.root.after(1000, self.update_timer)  # 每秒更新一次

    def load_question(self):
        """加载当前问题"""
        if 0 <= self.current_question_index < len(self.questions):
            question = self.questions[self.current_question_index]
            
            # 确保问题是字典并且包含选项
            if isinstance(question, dict) and "options" in question:
                # 如果 options 是列表，则转换为字典
                if isinstance(question["options"], list):
                    question["options"] = {str(i + 1): option for i, option in enumerate(question["options"])}

                # 更新题目标签的字体为二号和楷体
                self.question_label.config(text=f"第 {self.current_question_index + 1} 题: {question['question']}", font=("楷体", 16))  # 二号字体大约为16pt
                
                # 清空反馈
                self.feedback_label.config(text="", fg="green")
                
                # 清空选项并初始化新选项
                for widget in self.options_frame.winfo_children():
                    widget.destroy()  # 清空选项

                self.selected_options = {}  # 重置选项状态
                
                # 创建复选框
                for key, value in question["options"].items():
                    var = tk.BooleanVar(value=False)  # 确保每次初始化为未选中状态
                    self.selected_options[key] = var
                    tk.Checkbutton(
                        self.options_frame,
                        text=f"{key}. {value}",
                        font=("Helvetica", 12),
                        variable=var,
                        anchor="w",
                        bg="#E6F7FF"  # 设置选项背景颜色
                    ).pack(fill="x", padx=5, pady=2)  # 增加间距

                # 如果已有答案，恢复选择状态
                if self.answers[self.current_question_index]:
                    for key in self.answers[self.current_question_index]:
                        if key in self.selected_options:
                            self.selected_options[key].set(True)
            else:
                messagebox.showerror("错误", "问题数据格式不正确！")

    def submit_answer(self):
        """提交答案"""
        # 收集用户选择的选项
        user_answer = [key for key, var in self.selected_options.items() if var.get()]
        if not user_answer:
            self.feedback_label.config(text="请选择至少一个选项！", fg="red")
            return

        # 检查答案
        question = self.questions[self.current_question_index]
        correct_answer_set = set(question["correct_answer"])
        user_answer_set = set(user_answer)

        if user_answer_set == correct_answer_set:
            self.feedback_label.config(text="回答正确！", fg="green")
            self.answers[self.current_question_index] = user_answer
            self.update_answer_card()
            self.next_question()  # 自动跳转到下一题
        else:
            correct_answer_str = ", ".join(correct_answer_set)
            self.feedback_label.config(text=f"回答错误！正确答案是: {correct_answer_str}", fg="red")
            self.answers[self.current_question_index] = user_answer
            self.clear_selections()  # 清空选项
            
            # 在这里添加更新答题卡的逻辑
            self.update_answer_card()  # 确保在回答错误时更新答题卡

        # 保存记录
        self.save_record()

    def show_answer(self):
        """显示当前题目的正确答案"""
        question = self.questions[self.current_question_index]
        correct_answer_str = ", ".join(question["correct_answer"])
        self.feedback_label.config(text=f"正确答案是: {correct_answer_str}", fg="blue")

    def clear_selections(self):
        """清空当前题目的选项"""
        for var in self.selected_options.values():
            var.set(False)

    def update_answer_card(self):
        """更新答题卡状态"""
        # 清空现有答题卡
        for widget in self.card_inner_frame.winfo_children():
            widget.destroy()

        # 添加状态说明（图例）
        legend_frame = tk.Frame(self.card_inner_frame, bg="#E6F7FF")
        legend_frame.grid(row=0, column=0, columnspan=5, pady=5, sticky="w")
        tk.Label(legend_frame, text="答题状态：", font=("Helvetica", 10), bg="#E6F7FF").grid(row=0, column=0, padx=5)
        tk.Label(legend_frame, text="未答", bg="white", width=6, relief="ridge").grid(row=0, column=1, padx=5)
        tk.Label(legend_frame, text="答对", bg="green", fg="white", width=6, relief="ridge").grid(row=0, column=2, padx=5)
        tk.Label(legend_frame, text="答错", bg="red", fg="white", width=6, relief="ridge").grid(row=0, column=3, padx=5)

        # 创建答题卡按钮
        row, col = 1, 0
        for i, answer in enumerate(self.answers):
            if answer is None:
                color = "white"  # 未答
            else:
                correct_answer = set(self.questions[i]["correct_answer"])
                color = "green" if set(answer) == correct_answer else "red"  # 答对时为绿色

            btn = tk.Button(
                self.card_inner_frame,
                text=f"{i + 1}",
                width=4,
                bg=color,
                fg="black",
                command=lambda idx=i: self.jump_to_question(idx)
            )
            btn.grid(row=row, column=col, padx=5, pady=5)  # 使用 grid 布局

            col += 1
            if col == 5:  # 每行显示5个按钮
                col = 0
                row += 1

    def jump_to_question(self, index):
        """跳转到指定题目"""
        self.current_question_index = index
        self.load_question()

    def prev_question(self):
        """上一题"""
        if self.current_question_index > 0:
            self.current_question_index -= 1
            self.load_question()

    def next_question(self):
        """下一题"""
        if self.current_question_index < len(self.questions) - 1:
            self.current_question_index += 1
            self.load_question()
        else:
            messagebox.showinfo("提示", "已经是最后一题！")

    def reset_answers(self):
        """清空所有作答"""
        self.answers = [None] * len(self.questions)
        self.save_record()  # 重置时保存记录
        self.update_answer_card()
        self.load_question()
        self.start_time = time.time()  # 重置计时器

    # def load_record(self):
    #     """加载答题记录"""
    #     if os.path.exists(self.record_file):
    #         with open(self.record_file, "r", encoding="utf-8") as f:
    #             record = json.load(f)
    #             self.answers = record.get("answers", [None] * len(self.questions))
    #             self.current_question_index = record.get("current_question_index", 0)
    #             self.elapsed_time = record.get("elapsed_time", 0)  # 加载已用时间
    def load_record(self):
        """加载答题记录"""
        if os.path.exists(self.record_file):
            with open(self.record_file, "r", encoding="utf-8") as f:
                record = json.load(f)
                self.answers = record.get("answers", [None] * len(self.questions))
                self.current_question_index = record.get("current_question_index", 0)
                self.elapsed_time = record.get("elapsed_time", 0)  # 从记录中加载已用时
                
    def save_record(self):
        """保存答题记录"""
        # 确保 records 文件夹存在
        if not os.path.exists("records"):
            os.makedirs("records")  # 创建 records 文件夹

        record = {
            "answers": self.answers,
            "current_question_index": self.current_question_index,
            "elapsed_time": int(time.time() - self.start_time)  # 保存已用时间
        }
        with open(self.record_file, "w", encoding="utf-8") as f:
            json.dump(record, f, ensure_ascii=False, indent=4)

# 加载题目数据
def load_questions(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


if __name__ == "__main__":
    # 加载题目文件
    questions_path = "bank/H3CNE-RS+（GB0-192）.json"  # 替换为您的JSON文件路径
    questions = load_questions(questions_path)

    # 创建主窗口
    root = tk.Tk()
    # 使用 os.path.splitext 去掉 .json 扩展名
    file_name_without_extension = os.path.splitext(os.path.basename(questions_path))[0]
    app = QuizApp(root, questions, file_name=file_name_without_extension)
    root.mainloop()